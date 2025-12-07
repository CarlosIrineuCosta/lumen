"""
Test suite for Location Service security fixes.

This test suite validates that the Location Service is secure
against injection attacks and handles input validation properly.
"""

import pytest
from unittest.mock import Mock, patch
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.services.location_service import LocationService
from app.models.lookup_tables import City


class TestLocationServiceSecurity:
    """Test Location Service security implementation"""

    @pytest.fixture
    def mock_db(self):
        """Create mock database session"""
        db = Mock(spec=Session)
        return db

    @pytest.fixture
    def location_service(self, mock_db):
        """Create LocationService instance with mock DB"""
        return LocationService(mock_db)

    @pytest.fixture
    def sample_cities(self):
        """Create sample city data for testing"""
        return [
            City(id=1, name="New York", country="United States"),
            City(id=2, name="London", country="United Kingdom"),
            City(id=3, name="Paris", country="France"),
            City(id=4, name="Tokyo", country="Japan"),
        ]

    def test_valid_location_input_accepted(self, location_service):
        """Test that valid location inputs are properly accepted"""
        valid_inputs = [
            "New York",
            "London, UK",
            "Paris, France",
            "São Paulo",
            "St. Louis",
            "New York City",
            "Los Angeles",
            "Mt. Everest",
        ]

        for location in valid_inputs:
            result = location_service._validate_location_input(location)
            assert result is not None
            assert result == location.strip()

    def test_invalid_input_rejected(self, location_service):
        """Test that invalid inputs are properly rejected"""
        invalid_inputs = [
            None,
            "",
            "   ",  # Only whitespace
            "New York; DROP TABLE cities; --",  # SQL injection attempt
            "Paris' OR '1'='1",  # SQL injection attempt
            "New York\x00",  # Null byte
            "City" * 30,  # Too long (> 100 chars)
            "Chicago@#$%^&*()",  # Invalid characters
            "<script>alert('xss')</script>",  # XSS attempt
            "New York\n\r\t",  # Control characters (after normalization)
        ]

        for invalid_input in invalid_inputs:
            result = location_service._validate_location_input(invalid_input)
            assert result is None

    def test_input_length_validation(self, location_service):
        """Test input length validation"""
        # Test minimum length
        assert location_service._validate_location_input("") is None
        assert location_service._validate_location_input("N") is not None  # 1 character is valid
        assert location_service._validate_location_input(" ") is None  # Space only

        # Test maximum length
        long_valid = "A" * 100  # Exactly 100 characters
        assert location_service._validate_location_input(long_valid) is not None

        long_invalid = "A" * 101  # 101 characters
        assert location_service._validate_location_input(long_invalid) is None

    def test_character_validation(self, location_service):
        """Test that only allowed characters are accepted"""
        # Allowed characters
        allowed_chars = [
            "New York",  # Letters and space
            "St. Louis",  # Period
            "O'Fallon",  # Apostrophe
            "Los-Angeles",  # Hyphen
            "Paris, France",  # Comma
            "New York 2023",  # Numbers
        ]

        for text in allowed_chars:
            result = location_service._validate_location_input(text)
            assert result is not None

        # Disallowed characters
        disallowed_chars = [
            "City;DROP",  # Semicolon
            "Paris' OR '1'='1",  # Single quotes for SQL injection
            "New York#hashtag",  # Hash
            "City@domain.com",  # At symbol
            "Los%20Angeles",  # Percent (potential URL encoding)
            "City\\Path",  # Backslash
            "City/Path",  # Forward slash
            "City|Pipe",  # Pipe
            "City&Amp",  # Ampersand
        ]

        for text in disallowed_chars:
            result = location_service._validate_location_input(text)
            assert result is None

    def test_whitespace_normalization(self, location_service):
        """Test that whitespace is properly normalized"""
        input_text = "  New   York  \t  City  "
        result = location_service._validate_location_input(input_text)
        assert result == "New York City"

    def test_exact_city_match(self, location_service, mock_db, sample_cities):
        """Test exact city matching functionality"""
        # Mock database query for exact match
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = sample_cities[0]  # New York

        # Check cache first (should be empty)
        assert location_service._get_cached_city("new york") is None

        result = location_service.resolve_city("New York")
        assert result == 1  # New York's ID

        # Verify database query was called correctly
        mock_db.query.assert_called_with(City)
        mock_query.filter.assert_called()

        # Check that it was cached
        cached_result = location_service._get_cached_city("new york")
        assert cached_result == 1

    def test_city_country_match(self, location_service, mock_db, sample_cities):
        """Test city, country matching functionality"""
        # Mock database query for city,country match
        mock_query = Mock()
        mock_db.query.return_value = mock_query

        # First call (exact match) returns None
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [None, sample_cities[1]]  # London

        result = location_service.resolve_city("London, UK")
        assert result == 2  # London's ID

    def test_safe_prefix_matching(self, location_service, mock_db, sample_cities):
        """Test safe prefix matching (instead of contains)"""
        # Mock database queries
        mock_query = Mock()
        mock_db.query.return_value = mock_query

        # First call (exact match) returns None
        # Second call (city,country) returns None
        # Third call (prefix match) returns result
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = [None, None, sample_cities[2]]  # Paris

        result = location_service.resolve_city("Par")
        assert result == 3  # Paris's ID

        # Verify that LIKE was used with proper parameters
        calls = mock_query.filter.call_args_list
        prefix_call = None
        for call in calls:
            if 'like' in str(call).lower():
                prefix_call = call
                break

        assert prefix_call is not None

    def test_no_sql_injection_via_contains(self, location_service, mock_db):
        """Test that SQL injection is prevented by avoiding contains"""
        malicious_input = "New York'; DROP TABLE cities; --"

        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None  # No matches found

        result = location_service.resolve_city(malicious_input)
        assert result is None

        # Verify that no dangerous SQL patterns were used
        calls = str(mock_query.filter.call_args_list)
        assert "contains" not in calls.lower()
        assert "like" in calls.lower()  # Should use LIKE with proper escaping

    def test_search_cities_input_validation(self, location_service):
        """Test search_cities method input validation"""
        # Test invalid inputs
        invalid_inputs = [
            None,
            "",
            "   ",
            "N",  # Too short
            "City; DROP TABLE",
            "<script>",
            "A" * 101,  # Too long
        ]

        for invalid_input in invalid_inputs:
            result = location_service.search_cities(invalid_input)
            assert result == []

    def test_search_cities_limit_validation(self, location_service, mock_db):
        """Test search_cities method limit validation"""
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = []

        # Test various limit values
        test_limits = [-5, 0, 5, 51, 100, "invalid", None]

        for limit in test_limits:
            location_service.search_cities("Test", limit)

            # Verify limit was normalized to valid range
            call_args = mock_query.limit.call_args[0][0]
            assert 1 <= call_args <= 50

    def test_search_cities_safe_query(self, location_service, mock_db, sample_cities):
        """Test that search_cities uses safe queries"""
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.all.return_value = sample_cities[:2]

        result = location_service.search_cities("New")

        # Should return results
        assert len(result) == 2
        assert result[0]['name'] == "New York"
        assert result[1]['name'] == "London"

        # Verify safe query was used
        calls = str(mock_query.filter.call_args_list)
        assert "like" in calls.lower()
        assert "%" in calls  # Should use LIKE with wildcard

    def test_location_name_normalization(self, location_service):
        """Test location name normalization"""
        test_cases = [
            ("Saint Louis", "st. louis"),
            ("Mount Vernon", "mt. vernon"),
            ("Fort Worth", "ft. worth"),
            ("San Francisco", "sao francisco"),  # Portuguese/Spanish variation
            ("New York City", "new york"),
            ("Los Angeles", "l.a."),
        ]

        for input_name, expected_normalized in test_cases:
            result = location_service._normalize_location_name(input_name)
            assert result == expected_normalized

    def test_cache_functionality(self, location_service, mock_db, sample_cities):
        """Test caching functionality"""
        city_name = "Test City"
        city_id = 999

        # Test empty cache
        assert location_service._get_cached_city(city_name.lower()) is None

        # Test caching
        location_service._cache_city(city_name.lower(), city_id)
        assert location_service._get_cached_city(city_name.lower()) == city_id

        # Test cache size limits
        large_cache = {}
        location_service._city_cache = large_cache
        location_service._cache_max_size = 5

        # Add more items than max size
        for i in range(10):
            location_service._cache_city(f"city_{i}", i)

        # Cache should not exceed max size
        assert len(location_service._city_cache) <= location_service._cache_max_size

    def test_error_handling(self, location_service, mock_db):
        """Test error handling in database operations"""
        # Mock database to raise exception
        mock_query = Mock()
        mock_db.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.first.side_effect = Exception("Database error")

        result = location_service.resolve_city("Test City")
        assert result is None

        # Test search_cities error handling
        mock_query.all.side_effect = Exception("Database error")
        result = location_service.search_cities("Test")
        assert result == []

    @patch('app.services.location_service.logger')
    def test_logging_of_invalid_inputs(self, mock_logger, location_service):
        """Test that invalid inputs are properly logged"""
        invalid_input = "City; DROP TABLE"

        location_service._validate_location_input(invalid_input)

        # Should log warning for invalid characters
        mock_logger.warning.assert_called()
        warning_message = str(mock_logger.warning.call_args[0][0])
        assert "invalid characters" in warning_message.lower()

    def test_case_insensitive_matching(self, location_service, mock_db, sample_cities):
        """Test case insensitive matching"""
        test_cases = [
            ("new york", "New York"),
            ("LONDON", "London"),
            ("paris", "Paris"),
            ("TOKYO", "Tokyo"),
        ]

        for input_name, expected_name in test_cases:
            # Mock database query
            mock_query = Mock()
            mock_db.query.return_value = mock_query
            mock_query.filter.return_value = mock_query

            # Find the matching city
            expected_city = next((city for city in sample_cities if city.name == expected_name), None)
            mock_query.first.return_value = expected_city

            result = location_service.resolve_city(input_name)
            if expected_city:
                assert result == expected_city.id

    def test_special_unicode_characters(self, location_service):
        """Test handling of special unicode characters"""
        unicode_inputs = [
            "São Paulo",  # Portuguese
            "München",    # German
            "Kraków",     # Polish
            "Zürich",     # Swiss
            "Québec",     # French Canadian
        ]

        for city_name in unicode_inputs:
            # These should be valid inputs (unicode characters are allowed)
            result = location_service._validate_location_input(city_name)
            assert result is not None
            assert result == city_name.strip()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])