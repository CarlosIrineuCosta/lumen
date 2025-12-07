"""Location resolution service for Lumen Photography Platform"""

import re
import logging
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from app.models.lookup_tables import City

logger = logging.getLogger(__name__)


class LocationService:
    """Service for resolving location strings to city IDs with security and validation"""

    def __init__(self, db: Session):
        self.db = db
        # Cache for frequently accessed cities
        self._city_cache = {}
        self._cache_max_size = 1000

    def _validate_location_input(self, location_string: str) -> Optional[str]:
        """
        Validate and sanitize location input

        Args:
            location_string: Raw location input from user

        Returns:
            Sanitized location string or None if invalid
        """
        if not location_string or not isinstance(location_string, str):
            return None

        # Remove extra whitespace and normalize
        location = location_string.strip()

        # Length validation
        if len(location) < 1 or len(location) > 100:
            return None

        # Security: Remove potentially dangerous characters
        # Allow letters, numbers, spaces, commas, hyphens, apostrophes, and periods
        if not re.match(r"^[a-zA-Z0-9\s,\-'\.]+$", location):
            logger.warning(f"Invalid characters in location input: {location}")
            return None

        # Security: Block common SQL injection keywords and patterns
        # Only block suspicious combinations, not individual words that can be part of legitimate place names
        dangerous_patterns = [
            r'\bunion\b.*\bselect\b',
            r'\bselect\b.*\bfrom\b',
            r'\bdrop\b.*\btable\b',
            r'\bdelete\b.*\bfrom\b',
            r'\binsert\b.*\binto\b',
            r'\bupdate\b.*\bset\b',
            r'\bcreate\b.*\btable\b',
            r'\balter\b.*\btable\b',
            r'\bexec\b.*\b(\s*\w+\s*\()',
            r'[;\\\'"]\s*(union|select|drop|delete|insert|update|create|alter|exec)',
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
        ]

        location_lower = location.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, location_lower):
                logger.warning(f"Potentially dangerous pattern in location input: {location}")
                return None

        # Additional normalization
        location = re.sub(r'\s+', ' ', location)  # Normalize whitespace

        return location if location else None

    def _get_cached_city(self, cache_key: str) -> Optional[int]:
        """Get city from cache if available"""
        return self._city_cache.get(cache_key)

    def _cache_city(self, cache_key: str, city_id: int) -> None:
        """Cache city lookup result"""
        if len(self._city_cache) >= self._cache_max_size:
            # Simple LRU: remove oldest entries
            keys_to_remove = list(self._city_cache.keys())[:100]
            for key in keys_to_remove:
                del self._city_cache[key]

        self._city_cache[cache_key] = city_id

    def resolve_city(self, location_string: str) -> Optional[int]:
        """
        Resolve a location string to a city_id with security and performance optimizations

        Args:
            location_string: User input like "New York", "London, UK", "Paris, France"

        Returns:
            city_id if found, None otherwise
        """
        # Validate input
        location = self._validate_location_input(location_string)
        if not location:
            return None

        # Check cache first
        cache_key = location.lower()
        cached_city_id = self._get_cached_city(cache_key)
        if cached_city_id:
            return cached_city_id

        # Prepare search terms
        location_lower = location.lower()

        # Strategy 1: Exact match on city name
        city = self.db.query(City).filter(
            func.lower(City.name) == location_lower
        ).first()

        if city:
            self._cache_city(cache_key, city.id)
            return city.id

        # Strategy 2: Parse city,country format
        if ',' in location:
            parts = [part.strip() for part in location.split(',')]
            if len(parts) >= 2:
                city_name = parts[0].strip()
                country_name = parts[1].strip()

                # Validate parsed components
                if (city_name and country_name and
                    len(city_name) <= 50 and len(country_name) <= 50):

                    city = self.db.query(City).filter(
                        func.lower(City.name) == func.lower(city_name),
                        func.lower(City.country) == func.lower(country_name)
                    ).first()

                    if city:
                        self._cache_city(cache_key, city.id)
                        return city.id

        # Strategy 3: Safe prefix matching (instead of contains for injection protection)
        # Use parameterized queries for security
        try:
            # Use ILIKE for case-insensitive prefix matching
            city = self.db.query(City).filter(
                func.lower(City.name).like(f"{location_lower}%")
            ).first()

            if city:
                self._cache_city(cache_key, city.id)
                return city.id

        except Exception as e:
            logger.error(f"Database error during city lookup: {e}")
            return None

        # Strategy 4: Try normalized matching (remove common suffixes/prefixes)
        normalized_location = self._normalize_location_name(location)
        if normalized_location != location_lower:
            city = self.db.query(City).filter(
                func.lower(City.name) == normalized_location
            ).first()

            if city:
                self._cache_city(cache_key, city.id)
                return city.id

        return None

    def _normalize_location_name(self, location: str) -> str:
        """
        Normalize common location name variations

        Args:
            location: Location name to normalize

        Returns:
            Normalized location name
        """
        # Remove common prefixes and suffixes
        location = location.lower()

        # Common variations
        variations = {
            'saint': 'st.',
            'mount': 'mt.',
            'fort': 'ft.',
            'san': 'sao',  # Portuguese/Spanish variations
            'new york city': 'new york',
            'los angeles': 'l.a.',
        }

        for old, new in variations.items():
            if location.startswith(old):
                location = location.replace(old, new, 1)

        return location
    
    def get_city_info(self, city_id: int) -> Optional[Tuple[str, str]]:
        """
        Get city info by ID
        
        Returns:
            (city_name, country) tuple if found, None otherwise
        """
        city = self.db.query(City).filter(City.id == city_id).first()
        if city:
            return (city.name, city.country)
        return None
    
    def search_cities(self, query: str, limit: int = 10) -> List[dict]:
        """
        Search cities by name for autocomplete with security validation

        Args:
            query: Search query
            limit: Maximum results to return

        Returns:
            List of city dictionaries with id, name, country
        """
        # Validate input
        validated_query = self._validate_location_input(query)
        if not validated_query or len(validated_query) < 2:
            return []

        # Validate limit
        try:
            limit = min(max(int(limit), 1), 50)  # Between 1 and 50 results
        except (ValueError, TypeError):
            limit = 10

        query_lower = validated_query.lower()

        try:
            # Use prefix matching instead of contains for security and performance
            cities = self.db.query(City).filter(
                func.lower(City.name).like(f"{query_lower}%")
            ).limit(limit).all()

            return [
                {
                    "id": city.id,
                    "name": city.name,
                    "country": city.country,
                    "display": f"{city.name}, {city.country}"
                }
                for city in cities
            ]

        except Exception as e:
            logger.error(f"Database error during city search: {e}")
            return []