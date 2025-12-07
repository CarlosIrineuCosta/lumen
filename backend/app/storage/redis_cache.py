"""
Redis-based caching service for Lumen image storage.

This module implements the ICacheService interface using Redis
for high-performance caching of image metadata and URLs.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import hashlib

try:
    import redis.asyncio as redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

from .interfaces import ICacheService, ImageMetadata

logger = logging.getLogger(__name__)


class RedisCacheService(ICacheService):
    """
    Redis-based cache service for image metadata and URLs.
    
    Features:
    - Async Redis operations
    - JSON serialization for complex objects
    - Configurable TTL per data type
    - Connection pooling
    - Cache statistics tracking
    """

    def __init__(self, 
                 redis_url: str = "redis://localhost:6379",
                 password: Optional[str] = None,
                 db: int = 0,
                 max_connections: int = 10,
                 default_ttl: int = 3600):
        """
        Initialize Redis cache service.
        
        Args:
            redis_url: Redis connection URL
            password: Redis password if required
            db: Redis database number
            max_connections: Maximum connections in pool
            default_ttl: Default TTL in seconds
        """
        if not HAS_REDIS:
            raise ImportError("redis package required for Redis cache service")
        
        self.redis_url = redis_url
        self.password = password
        self.db = db
        self.max_connections = max_connections
        self.default_ttl = default_ttl
        
        # Key prefixes
        self.prefixes = {
            'urls': 'lumen:urls:',
            'metadata': 'lumen:meta:',
            'stats': 'lumen:stats:',
            'user_info': 'lumen:user:',
            'temp': 'lumen:temp:'
        }
        
        # Statistics
        self.stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'errors': 0
        }
        
        self._redis_pool = None

    async def _get_redis(self):
        """Get Redis connection from pool"""
        if not self._redis_pool:
            try:
                self._redis_pool = redis.ConnectionPool.from_url(
                    self.redis_url,
                    password=self.password,
                    db=self.db,
                    max_connections=self.max_connections,
                    decode_responses=True
                )
                logger.info(f"Redis connection pool initialized: {self.redis_url}")
            except Exception as e:
                logger.error(f"Failed to initialize Redis pool: {e}")
                raise
        
        return redis.Redis(connection_pool=self._redis_pool)

    async def get_cached_urls(self, photo_id: str) -> Optional[Dict[str, str]]:
        """Get cached image URLs for a photo"""
        try:
            r = await self._get_redis()
            key = f"{self.prefixes['urls']}{photo_id}"
            
            cached_data = await r.get(key)
            if cached_data:
                self.stats['hits'] += 1
                return json.loads(cached_data)
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to get cached URLs for {photo_id}: {e}")
            return None

    async def cache_urls(self, 
                        photo_id: str, 
                        urls: Dict[str, str], 
                        ttl: int = None) -> None:
        """Cache image URLs for a photo"""
        try:
            r = await self._get_redis()
            key = f"{self.prefixes['urls']}{photo_id}"
            ttl = ttl or self.default_ttl
            
            # Add timestamp for debugging
            cache_data = {
                'urls': urls,
                'cached_at': datetime.utcnow().isoformat(),
                'ttl': ttl
            }
            
            await r.setex(key, ttl, json.dumps(cache_data))
            self.stats['sets'] += 1
            
            logger.debug(f"Cached URLs for {photo_id} with TTL {ttl}s")
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to cache URLs for {photo_id}: {e}")

    async def get_cached_metadata(self, photo_id: str) -> Optional[ImageMetadata]:
        """Get cached image metadata"""
        try:
            r = await self._get_redis()
            key = f"{self.prefixes['metadata']}{photo_id}"
            
            cached_data = await r.get(key)
            if cached_data:
                self.stats['hits'] += 1
                data = json.loads(cached_data)
                
                # Convert back to ImageMetadata object
                metadata = ImageMetadata(
                    filename=data['filename'],
                    original_filename=data['original_filename'],
                    file_size=data['file_size'],
                    width=data['width'],
                    height=data['height'],
                    content_type=data['content_type'],
                    created_at=datetime.fromisoformat(data['created_at']),
                    user_id=data['user_id'],
                    photo_id=data['photo_id'],
                    checksum=data['checksum']
                )
                return metadata
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to get cached metadata for {photo_id}: {e}")
            return None

    async def cache_metadata(self, 
                           photo_id: str, 
                           metadata: ImageMetadata, 
                           ttl: int = None) -> None:
        """Cache image metadata"""
        try:
            r = await self._get_redis()
            key = f"{self.prefixes['metadata']}{photo_id}"
            ttl = ttl or self.default_ttl
            
            # Convert ImageMetadata to dict
            data = {
                'filename': metadata.filename,
                'original_filename': metadata.original_filename,
                'file_size': metadata.file_size,
                'width': metadata.width,
                'height': metadata.height,
                'content_type': metadata.content_type,
                'created_at': metadata.created_at.isoformat(),
                'user_id': metadata.user_id,
                'photo_id': metadata.photo_id,
                'checksum': metadata.checksum,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            await r.setex(key, ttl, json.dumps(data))
            self.stats['sets'] += 1
            
            logger.debug(f"Cached metadata for {photo_id} with TTL {ttl}s")
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to cache metadata for {photo_id}: {e}")

    async def invalidate_photo(self, photo_id: str) -> None:
        """Remove all cached data for a photo with comprehensive invalidation"""
        try:
            r = await self._get_redis()

            # Delete all photo-related cache entries
            keys_to_delete = [
                f"{self.prefixes['urls']}{photo_id}",
                f"{self.prefixes['metadata']}{photo_id}"
            ]

            # Also invalidate any user-specific cache entries that might reference this photo
            # Find user cache keys that might contain references to this photo
            user_keys_pattern = f"{self.prefixes['user_info']}*"
            user_keys = await r.keys(user_keys_pattern)

            # Check and invalidate user storage info caches (since photo count might change)
            for user_key in user_keys:
                try:
                    cached_data = await r.get(user_key)
                    if cached_data:
                        data = json.loads(cached_data)
                        # If this is storage info, it might contain photo count
                        if 'photo_count' in data or 'total_files' in data:
                            await r.delete(user_key)
                            logger.debug(f"Invalidated user cache key: {user_key}")
                except Exception:
                    # Continue if individual key processing fails
                    continue

            # Delete the main photo cache entries
            deleted_count = await r.delete(*keys_to_delete)
            self.stats['deletes'] += deleted_count

            # Add to invalidation log for debugging
            invalidation_key = f"{self.prefixes['temp']}invalidation_log:{photo_id}"
            await r.setex(invalidation_key, 300, json.dumps({
                'photo_id': photo_id,
                'timestamp': datetime.utcnow().isoformat(),
                'entries_deleted': deleted_count,
                'user_keys_invalidated': len(user_keys)
            }))

            logger.info(f"Invalidated {deleted_count} cache entries for photo {photo_id}")

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to invalidate cache for {photo_id}: {e}")

    async def invalidate_user_cache(self, user_id: str) -> None:
        """
        Invalidate all cache entries related to a user

        This should be called when:
        - User profile is updated
        - User photos are added/deleted
        - User storage quota changes
        """
        try:
            r = await self._get_redis()

            # Delete user-specific cache entries
            user_keys_to_delete = [
                f"{self.prefixes['user_info']}{user_id}:storage",
                f"{self.prefixes['user_info']}{user_id}:profile",
                f"{self.prefixes['user_info']}{user_id}:stats"
            ]

            # Find and delete any other user-related keys
            user_keys_pattern = f"{self.prefixes['user_info']}{user_id}:*"
            additional_keys = await r.keys(user_keys_pattern)
            user_keys_to_delete.extend(additional_keys)

            # Remove duplicates and delete
            unique_keys = list(set(user_keys_to_delete))
            if unique_keys:
                deleted_count = await r.delete(*unique_keys)
                self.stats['deletes'] += deleted_count
                logger.info(f"Invalidated {deleted_count} user cache entries for {user_id}")

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to invalidate user cache for {user_id}: {e}")

    async def invalidate_recent_photos_cache(self) -> None:
        """
        Invalidate recent photos cache and other global caches

        This should be called when:
        - New public photos are uploaded
        - Photos are made public/private
        - Global photo rankings change
        """
        try:
            r = await self._get_redis()

            # Delete global/recent photos caches
            global_patterns = [
                f"{self.prefixes['temp']}recent_photos:*",
                f"{self.prefixes['temp']}popular_photos:*",
                f"{self.prefixes['temp']}trending_photos:*",
                f"{self.prefixes['temp']}photo_feed:*"
            ]

            total_deleted = 0
            for pattern in global_patterns:
                keys = await r.keys(pattern)
                if keys:
                    deleted = await r.delete(*keys)
                    total_deleted += deleted

            # Invalidate home page caches
            home_patterns = [
                f"{self.prefixes['temp']}home_page:*",
                f"{self.prefixes['temp']}featured_photos:*"
            ]

            for pattern in home_patterns:
                keys = await r.keys(pattern)
                if keys:
                    deleted = await r.delete(*keys)
                    total_deleted += deleted

            self.stats['deletes'] += total_deleted
            logger.info(f"Invalidated {total_deleted} global cache entries")

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to invalidate recent photos cache: {e}")

    async def smart_cache_warmup(self, photo_ids: List[str], user_id: str = None) -> None:
        """
        Proactively warm up cache for frequently accessed photos

        This should be called after:
        - Bulk photo operations
        - User profile views
        - Popular photo updates
        """
        try:
            r = await self._get_redis()

            warmed_count = 0
            for photo_id in photo_ids:
                try:
                    # Check if photo is already cached
                    urls_key = f"{self.prefixes['urls']}{photo_id}"
                    if await r.exists(urls_key):
                        continue  # Already cached

                    # Add to warmup queue (this would be processed by background workers)
                    warmup_key = f"{self.prefixes['temp']}warmup_queue"
                    warmup_data = {
                        'photo_id': photo_id,
                        'user_id': user_id,
                        'priority': 'normal',
                        'timestamp': datetime.utcnow().isoformat()
                    }

                    # Use list for queue semantics
                    await r.lpush(warmup_key, json.dumps(warmup_data))
                    await r.expire(warmup_key, 3600)  # Expire queue after 1 hour

                    warmed_count += 1

                except Exception as e:
                    logger.warning(f"Failed to queue warmup for photo {photo_id}: {e}")
                    continue

            logger.info(f"Queued {warmed_count} photos for cache warmup")

        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to setup cache warmup: {e}")

    async def get_invalidation_log(self, photo_id: str = None) -> List[Dict]:
        """Get recent cache invalidation logs for debugging"""
        try:
            r = await self._get_redis()

            if photo_id:
                # Get specific photo invalidation log
                log_key = f"{self.prefixes['temp']}invalidation_log:{photo_id}"
                log_data = await r.get(log_key)
                if log_data:
                    return [json.loads(log_data)]
                return []
            else:
                # Get all recent invalidation logs
                pattern = f"{self.prefixes['temp']}invalidation_log:*"
                keys = await r.keys(pattern)

                logs = []
                for key in keys[:50]:  # Limit to 50 most recent
                    try:
                        log_data = await r.get(key)
                        if log_data:
                            logs.append(json.loads(log_data))
                    except Exception:
                        continue

                # Sort by timestamp (newest first)
                logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                return logs

        except Exception as e:
            logger.error(f"Failed to get invalidation log: {e}")
            return []

    async def get_cache_stats(self) -> Dict[str, Union[int, float]]:
        """Get cache performance statistics"""
        try:
            r = await self._get_redis()
            
            # Get Redis info
            info = await r.info('memory')
            memory_usage = info.get('used_memory', 0)
            
            # Calculate hit rate
            total_requests = self.stats['hits'] + self.stats['misses']
            hit_rate = (self.stats['hits'] / total_requests * 100) if total_requests > 0 else 0
            
            # Get key counts
            urls_count = 0
            metadata_count = 0
            
            try:
                # Count keys by prefix (may be slow on large datasets)
                urls_keys = await r.keys(f"{self.prefixes['urls']}*")
                metadata_keys = await r.keys(f"{self.prefixes['metadata']}*")
                urls_count = len(urls_keys)
                metadata_count = len(metadata_keys)
            except Exception:
                # Skip key counting if it fails (Redis might be busy)
                pass
            
            return {
                'hit_rate_percent': round(hit_rate, 2),
                'total_hits': self.stats['hits'],
                'total_misses': self.stats['misses'],
                'total_sets': self.stats['sets'],
                'total_deletes': self.stats['deletes'],
                'total_errors': self.stats['errors'],
                'memory_usage_bytes': memory_usage,
                'cached_urls_count': urls_count,
                'cached_metadata_count': metadata_count,
                'uptime_seconds': await self._get_uptime()
            }
            
        except Exception as e:
            logger.error(f"Failed to get cache stats: {e}")
            return {
                'hit_rate_percent': 0,
                'total_hits': self.stats['hits'],
                'total_misses': self.stats['misses'],
                'total_errors': self.stats['errors'] + 1,
                'error': str(e)
            }

    async def _get_uptime(self) -> int:
        """Get Redis server uptime in seconds"""
        try:
            r = await self._get_redis()
            info = await r.info('server')
            return info.get('uptime_in_seconds', 0)
        except Exception:
            return 0

    async def cache_user_storage_info(self, 
                                    user_id: str, 
                                    storage_info: Dict[str, Union[int, float]], 
                                    ttl: int = 300) -> None:
        """Cache user storage information (shorter TTL since it changes frequently)"""
        try:
            r = await self._get_redis()
            key = f"{self.prefixes['user_info']}{user_id}:storage"
            
            cache_data = {
                **storage_info,
                'cached_at': datetime.utcnow().isoformat()
            }
            
            await r.setex(key, ttl, json.dumps(cache_data))
            self.stats['sets'] += 1
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to cache storage info for {user_id}: {e}")

    async def get_cached_user_storage_info(self, user_id: str) -> Optional[Dict[str, Union[int, float]]]:
        """Get cached user storage information"""
        try:
            r = await self._get_redis()
            key = f"{self.prefixes['user_info']}{user_id}:storage"
            
            cached_data = await r.get(key)
            if cached_data:
                self.stats['hits'] += 1
                data = json.loads(cached_data)
                # Remove cache metadata before returning
                data.pop('cached_at', None)
                return data
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to get cached storage info for {user_id}: {e}")
            return None

    async def cache_temp_data(self, 
                            key: str, 
                            data: Union[Dict, List, str, int], 
                            ttl: int = 3600) -> None:
        """Cache temporary data with custom TTL"""
        try:
            r = await self._get_redis()
            cache_key = f"{self.prefixes['temp']}{key}"
            
            if isinstance(data, (dict, list)):
                data = json.dumps(data)
            
            await r.setex(cache_key, ttl, data)
            self.stats['sets'] += 1
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to cache temp data {key}: {e}")

    async def get_temp_data(self, key: str, parse_json: bool = True) -> Optional[Union[str, Dict, List]]:
        """Get temporary cached data"""
        try:
            r = await self._get_redis()
            cache_key = f"{self.prefixes['temp']}{key}"
            
            data = await r.get(cache_key)
            if data:
                self.stats['hits'] += 1
                if parse_json:
                    try:
                        return json.loads(data)
                    except json.JSONDecodeError:
                        return data
                return data
            
            self.stats['misses'] += 1
            return None
            
        except Exception as e:
            self.stats['errors'] += 1
            logger.error(f"Failed to get temp data {key}: {e}")
            return None

    async def health_check(self) -> Dict[str, Union[bool, str]]:
        """Check Redis connection health"""
        try:
            r = await self._get_redis()
            
            # Test basic operations
            test_key = f"{self.prefixes['temp']}health_check"
            await r.set(test_key, "test", ex=60)
            result = await r.get(test_key)
            await r.delete(test_key)
            
            if result == "test":
                return {
                    'healthy': True,
                    'message': 'Redis connection healthy',
                    'latency_ms': 0  # Could implement ping timing here
                }
            else:
                return {
                    'healthy': False,
                    'message': 'Redis read/write test failed'
                }
                
        except Exception as e:
            return {
                'healthy': False,
                'message': f"Redis health check failed: {str(e)}"
            }

    async def close(self):
        """Close Redis connection pool"""
        if self._redis_pool:
            await self._redis_pool.disconnect()
            logger.info("Redis connection pool closed")


class NullCacheService(ICacheService):
    """
    Null cache implementation for when Redis is not available.
    
    This provides the same interface but doesn't actually cache anything,
    allowing the application to run without Redis.
    """

    async def get_cached_urls(self, photo_id: str) -> Optional[Dict[str, str]]:
        return None

    async def cache_urls(self, photo_id: str, urls: Dict[str, str], ttl: int = 3600) -> None:
        pass

    async def get_cached_metadata(self, photo_id: str) -> Optional[ImageMetadata]:
        return None

    async def cache_metadata(self, photo_id: str, metadata: ImageMetadata, ttl: int = 3600) -> None:
        pass

    async def invalidate_photo(self, photo_id: str) -> None:
        pass

    async def get_cache_stats(self) -> Dict[str, Union[int, float]]:
        return {
            'hit_rate_percent': 0,
            'total_hits': 0,
            'total_misses': 0,
            'error': 'Cache disabled (Redis not available)'
        }


def create_cache_service(redis_url: str = None, 
                        redis_password: str = None) -> ICacheService:
    """
    Factory function to create appropriate cache service.
    
    Returns RedisCacheService if Redis is available and configured,
    otherwise returns NullCacheService.
    """
    if not HAS_REDIS or not redis_url:
        logger.warning("Redis not available, using null cache service")
        return NullCacheService()
    
    try:
        return RedisCacheService(redis_url=redis_url, password=redis_password)
    except Exception as e:
        logger.error(f"Failed to create Redis cache service: {e}")
        logger.warning("Falling back to null cache service")
        return NullCacheService()