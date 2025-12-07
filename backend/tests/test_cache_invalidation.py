"""
Test suite for cache invalidation strategy fixes.

This test suite validates that the cache invalidation works correctly
and maintains data consistency during photo updates.
"""

import pytest
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta

from app.storage.redis_cache import RedisCacheService, NullCacheService
from app.storage.interfaces import ImageMetadata


class TestCacheInvalidationStrategy:
    """Test cache invalidation strategy implementation"""

    @pytest.fixture
    def mock_redis(self):
        """Create mock Redis client"""
        redis = Mock()
        redis.get = AsyncMock(return_value=None)
        redis.setex = AsyncMock(return_value=True)
        redis.delete = AsyncMock(return_value=1)
        redis.exists = AsyncMock(return_value=False)
        redis.keys = AsyncMock(return_value=[])
        redis.lpush = AsyncMock(return_value=1)
        redis.expire = AsyncMock(return_value=True)
        return redis

    @pytest.fixture
    def cache_service(self, mock_redis):
        """Create RedisCacheService with mock Redis"""
        # Mock the connection pool creation
        with patch('app.storage.redis_cache.redis.Redis', return_value=mock_redis):
            cache_service = RedisCacheService(redis_url="redis://localhost:6379")
            cache_service._redis_pool = Mock()
            return cache_service

    @pytest.fixture
    def sample_metadata(self):
        """Create sample image metadata"""
        return ImageMetadata(
            filename="test_photo.jpg",
            original_filename="original_test.jpg",
            file_size=1024000,
            width=1920,
            height=1080,
            content_type="image/jpeg",
            created_at=datetime.utcnow(),
            user_id="test_user_123",
            photo_id="test_photo_456",
            checksum="abc123def456"
        )

    @pytest.mark.asyncio
    async def test_invalidate_photo_comprehensive(self, cache_service, mock_redis):
        """Test comprehensive photo invalidation"""
        photo_id = "test_photo_123"
        user_id = "test_user_456"

        # Mock user cache keys that contain photo counts
        user_storage_key = "lumen:user:test_user_456:storage"
        user_storage_data = json.dumps({
            'photo_count': 25,
            'total_files': 50,
            'total_size': 1024000
        })

        mock_redis.keys.return_value = [user_storage_key]
        mock_redis.get.return_value = user_storage_data

        # Call invalidate_photo
        await cache_service.invalidate_photo(photo_id)

        # Verify photo-specific keys were deleted
        expected_deleted_keys = [
            f"lumen:urls:{photo_id}",
            f"lumen:meta:{photo_id}"
        ]

        delete_calls = mock_redis.delete.call_args_list
        # Should have called delete with photo keys
        assert len(delete_calls) >= 1
        delete_args = delete_calls[0][0][0]  # Get positional arguments

        for key in expected_deleted_keys:
            assert key in delete_args

        # Verify user storage cache was invalidated
        mock_redis.get.assert_called_with(user_storage_key)
        mock_redis.delete.assert_called()  # Should have called delete for user key

        # Verify invalidation log was created
        log_key = f"lumen:temp:invalidation_log:{photo_id}"
        mock_redis.setex.assert_called()
        setex_calls = [call for call in mock_redis.setex.call_args_list
                      if call[0][0] == log_key]
        assert len(setex_calls) == 1

    @pytest.mark.asyncio
    async def test_invalidate_user_cache(self, cache_service, mock_redis):
        """Test user cache invalidation"""
        user_id = "test_user_123"

        # Mock user-related keys
        user_keys = [
            f"lumen:user:{user_id}:storage",
            f"lumen:user:{user_id}:profile",
            f"lumen:user:{user_id}:stats",
            f"lumen:user:{user_id}:custom_data"
        ]

        mock_redis.keys.return_value = user_keys

        await cache_service.invalidate_user_cache(user_id)

        # Verify all user keys were targeted for deletion
        mock_redis.keys.assert_called_with(f"lumen:user:{user_id}:*")
        mock_redis.delete.assert_called_once()

        delete_args = mock_redis.delete.call_args[0][0]
        for key in user_keys:
            assert key in delete_args

    @pytest.mark.asyncio
    async def test_invalidate_recent_photos_cache(self, cache_service, mock_redis):
        """Test global recent photos cache invalidation"""
        # Mock global cache keys
        global_keys = [
            "lumen:temp:recent_photos:page_1",
            "lumen:temp:recent_photos:page_2",
            "lumen:temp:popular_photos:today",
            "lumen:temp:photo_feed:user_123",
            "lumen:temp:home_page:featured",
            "lumen:temp:featured_photos:main"
        ]

        # Mock keys to return different sets for different patterns
        def mock_keys_side_effect(pattern):
            if "recent_photos" in pattern:
                return global_keys[:2]
            elif "popular_photos" in pattern:
                return global_keys[2:3]
            elif "photo_feed" in pattern:
                return global_keys[3:4]
            elif "home_page" in pattern:
                return global_keys[4:5]
            elif "featured_photos" in pattern:
                return global_keys[5:6]
            return []

        mock_redis.keys.side_effect = mock_keys_side_effect
        mock_redis.delete.return_value = 2  # Return number of deleted keys

        await cache_service.invalidate_recent_photos_cache()

        # Verify multiple patterns were queried
        patterns_queried = [call[0][0] for call in mock_redis.keys.call_args_list]
        assert any("recent_photos" in pattern for pattern in patterns_queried)
        assert any("popular_photos" in pattern for pattern in patterns_queried)
        assert any("home_page" in pattern for pattern in patterns_queried)

        # Verify delete was called multiple times
        assert mock_redis.delete.call_count >= len(global_keys)

    @pytest.mark.asyncio
    async def test_smart_cache_warmup(self, cache_service, mock_redis):
        """Test smart cache warmup functionality"""
        photo_ids = ["photo_1", "photo_2", "photo_3"]
        user_id = "test_user"

        # Mock that photo_2 is already cached
        async def mock_exists_side_effect(key):
            return "photo_2" in key

        mock_redis.exists.side_effect = mock_exists_side_effect

        await cache_service.smart_cache_warmup(photo_ids, user_id)

        # Should check if photos are already cached
        assert mock_redis.exists.call_count == len(photo_ids)

        # Should queue only non-cached photos (photo_1 and photo_3)
        assert mock_redis.lpush.call_count == 2

        # Verify warmup data structure
        lpush_calls = mock_redis.lpush.call_args_list
        queued_photos = []
        for call in lpush_calls:
            warmup_data = json.loads(call[0][1])  # Get the data argument
            queued_photos.append(warmup_data['photo_id'])

        assert "photo_1" in queued_photos
        assert "photo_3" in queued_photos
        assert "photo_2" not in queued_photos  # Already cached

        # Verify warmup queue expiration
        warmup_key = "lumen:temp:warmup_queue"
        expire_call = [call for call in mock_redis.expire.call_args_list
                      if call[0][0] == warmup_key]
        assert len(expire_call) == 1
        assert expire_call[0][0][1] == 3600  # 1 hour TTL

    @pytest.mark.asyncio
    async def test_get_invalidation_log(self, cache_service, mock_redis):
        """Test cache invalidation logging"""
        photo_id = "test_photo_123"

        # Mock invalidation log data
        log_data = {
            'photo_id': photo_id,
            'timestamp': datetime.utcnow().isoformat(),
            'entries_deleted': 2,
            'user_keys_invalidated': 1
        }

        mock_redis.get.return_value = json.dumps(log_data)

        # Test specific photo log
        result = await cache_service.get_invalidation_log(photo_id)
        assert len(result) == 1
        assert result[0]['photo_id'] == photo_id
        assert result[0]['entries_deleted'] == 2

        # Test all logs
        mock_redis.keys.return_value = [
            f"lumen:temp:invalidation_log:{photo_id}",
            "lumen:temp:invalidation_log:photo_456"
        ]

        # Mock different log data for multiple keys
        def mock_get_side_effect(key):
            if photo_id in key:
                return json.dumps(log_data)
            else:
                return json.dumps({
                    'photo_id': 'photo_456',
                    'timestamp': (datetime.utcnow() - timedelta(hours=1)).isoformat(),
                    'entries_deleted': 1,
                    'user_keys_invalidated': 0
                })

        mock_redis.get.side_effect = mock_get_side_effect

        all_logs = await cache_service.get_invalidation_log()
        assert len(all_logs) == 2
        assert any(log['photo_id'] == photo_id for log in all_logs)

    @pytest.mark.asyncio
    async def test_cache_url_operations(self, cache_service, mock_redis, sample_metadata):
        """Test URL caching operations"""
        photo_id = "test_photo_123"
        test_urls = {
            'original': 'https://example.com/original.jpg',
            'thumb': 'https://example.com/thumb.jpg',
            'large': 'https://example.com/large.jpg'
        }

        # Test cache_urls
        await cache_service.cache_urls(photo_id, test_urls, ttl=1800)

        # Verify setex was called with correct parameters
        expected_key = f"lumen:urls:{photo_id}"
        mock_redis.setex.assert_called_once()
        call_args = mock_redis.setex.call_args[0]

        assert call_args[0] == expected_key
        assert call_args[1] == 1800  # TTL

        # Verify cache data structure
        cached_data = json.loads(call_args[2])
        assert 'urls' in cached_data
        assert cached_data['urls'] == test_urls
        assert 'cached_at' in cached_data
        assert cached_data['ttl'] == 1800

        # Test get_cached_urls
        mock_redis.get.return_value = json.dumps({
            'urls': test_urls,
            'cached_at': datetime.utcnow().isoformat()
        })

        result = await cache_service.get_cached_urls(photo_id)
        assert result == test_urls

    @pytest.mark.asyncio
    async def test_cache_metadata_operations(self, cache_service, mock_redis, sample_metadata):
        """Test metadata caching operations"""
        photo_id = "test_photo_123"

        # Test cache_metadata
        await cache_service.cache_metadata(photo_id, sample_metadata, ttl=3600)

        expected_key = f"lumen:meta:{photo_id}"
        mock_redis.setex.assert_called_once()

        call_args = mock_redis.setex.call_args[0]
        assert call_args[0] == expected_key
        assert call_args[1] == 3600

        # Verify metadata serialization
        cached_data = json.loads(call_args[2])
        assert cached_data['filename'] == sample_metadata.filename
        assert cached_data['user_id'] == sample_metadata.user_id
        assert cached_data['photo_id'] == sample_metadata.photo_id

        # Test get_cached_metadata
        mock_redis.get.return_value = json.dumps(cached_data)

        result = await cache_service.get_cached_metadata(photo_id)
        assert result is not None
        assert result.filename == sample_metadata.filename
        assert result.user_id == sample_metadata.user_id

    @pytest.mark.asyncio
    async def test_error_handling_in_invalidation(self, cache_service, mock_redis):
        """Test error handling in cache invalidation"""
        photo_id = "test_photo_123"

        # Mock Redis operations to raise exceptions
        mock_redis.delete.side_effect = Exception("Redis connection error")
        mock_redis.get.side_effect = Exception("Redis get error")

        # Should not raise exception, should handle gracefully
        await cache_service.invalidate_photo(photo_id)

        # Should log the error (would need logger mock to verify)
        assert mock_redis.delete.called  # Attempt was made

    @pytest.mark.asyncio
    async def test_cache_statistics_tracking(self, cache_service, mock_redis):
        """Test cache statistics tracking"""
        photo_id = "test_photo_123"
        test_urls = {'original': 'https://example.com/test.jpg'}

        # Test cache hit
        mock_redis.get.return_value = json.dumps({'urls': test_urls})
        await cache_service.get_cached_urls(photo_id)
        assert cache_service.stats['hits'] == 1

        # Test cache miss
        mock_redis.get.return_value = None
        await cache_service.get_cached_urls("nonexistent_photo")
        assert cache_service.stats['misses'] == 1

        # Test cache set
        await cache_service.cache_urls(photo_id, test_urls)
        assert cache_service.stats['sets'] == 1

        # Test cache delete
        mock_redis.delete.return_value = 2
        await cache_service.invalidate_photo(photo_id)
        assert cache_service.stats['deletes'] == 2

    @pytest.mark.asyncio
    async def test_null_cache_service_fallback(self):
        """Test NullCacheService fallback behavior"""
        null_cache = NullCacheService()
        photo_id = "test_photo_123"
        test_urls = {'original': 'https://example.com/test.jpg'}

        # All operations should be no-ops
        result = await null_cache.get_cached_urls(photo_id)
        assert result is None

        await null_cache.cache_urls(photo_id, test_urls)
        # Should not raise exception

        await null_cache.invalidate_photo(photo_id)
        # Should not raise exception

        stats = await null_cache.get_cache_stats()
        assert stats['hit_rate_percent'] == 0
        assert stats['total_hits'] == 0
        assert 'error' in stats

    @pytest.mark.asyncio
    async def test_health_check_functionality(self, cache_service, mock_redis):
        """Test Redis health check"""
        # Test successful health check
        mock_redis.get.return_value = "test"
        mock_redis.delete.return_value = 1

        result = await cache_service.health_check()
        assert result['healthy'] is True
        assert 'Redis connection healthy' in result['message']

        # Test failed health check
        mock_redis.get.side_effect = Exception("Connection failed")

        result = await cache_service.health_check()
        assert result['healthy'] is False
        assert 'Redis health check failed' in result['message']

    @pytest.mark.asyncio
    async def test_cache_key_prefix_consistency(self, cache_service):
        """Test that cache key prefixes are consistent"""
        photo_id = "test_photo_123"
        user_id = "test_user_456"

        # Expected key formats
        expected_urls_key = f"lumen:urls:{photo_id}"
        expected_metadata_key = f"lumen:meta:{photo_id}"
        expected_user_storage_key = f"lumen:user:{user_id}:storage"
        expected_invalidation_log_key = f"lumen:temp:invalidation_log:{photo_id}"

        # Test key generation consistency
        assert cache_service.prefixes['urls'] == "lumen:urls:"
        assert cache_service.prefixes['metadata'] == "lumen:meta:"
        assert cache_service.prefixes['user_info'] == "lumen:user:"
        assert cache_service.prefixes['temp'] == "lumen:temp:"

    @pytest.mark.asyncio
    async def test_concurrent_cache_operations(self, cache_service, mock_redis):
        """Test concurrent cache operations"""
        import asyncio

        photo_ids = [f"photo_{i}" for i in range(10)]
        test_urls = {'original': 'https://example.com/test.jpg'}

        # Simulate concurrent cache operations
        async def cache_photo(photo_id):
            await cache_service.cache_urls(photo_id, test_urls)
            await cache_service.get_cached_urls(photo_id)

        # Run multiple operations concurrently
        tasks = [cache_photo(pid) for pid in photo_ids]
        await asyncio.gather(*tasks)

        # Verify all operations were attempted
        assert mock_redis.setex.call_count == len(photo_ids)
        assert mock_redis.get.call_count == len(photo_ids)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])