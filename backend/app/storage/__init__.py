"""
Storage module for Lumen image management.

This module provides a factory pattern for storage services,
allowing environment-based backend selection.
"""

import os
import logging
from typing import Optional

from .interfaces import IStorageService
from .local_storage import LocalStorageService

logger = logging.getLogger(__name__)

# Global storage instance (singleton pattern)
_storage_instance: Optional[IStorageService] = None


def get_storage_backend() -> IStorageService:
    """
    Get the configured storage backend.
    
    Returns:
        IStorageService: Configured storage service instance
        
    Environment Variables:
        STORAGE_MODE: 'local' (default), 'hybrid'
        STORAGE_BASE_PATH: Base path for storage (default: /var/www/lumen/storage)
        ENABLE_REDIS_CACHE: Enable Redis caching (default: true)
    """
    global _storage_instance
    
    if _storage_instance is None:
        storage_mode = os.getenv('STORAGE_MODE', 'local').lower()
        
        if storage_mode == 'local':
            _storage_instance = _create_local_storage()
        elif storage_mode == 'hybrid':
            _storage_instance = _create_hybrid_storage()
        else:
            logger.warning(f"Unknown storage mode '{storage_mode}', defaulting to local")
            _storage_instance = _create_local_storage()
            
        logger.info(f"Initialized storage backend: {type(_storage_instance).__name__}")
    
    return _storage_instance


def _create_local_storage() -> LocalStorageService:
    """Create local filesystem storage service."""
    base_path = os.getenv('STORAGE_BASE_PATH', '/var/www/lumen/storage')
    enable_cache = os.getenv('ENABLE_REDIS_CACHE', 'true').lower() == 'true'
    max_storage_gb = float(os.getenv('MAX_STORAGE_GB', '40.0'))
    
    return LocalStorageService(
        base_path=base_path,
        cache_ttl_days=7,
        max_storage_gb=max_storage_gb,
        enable_cache=enable_cache
    )


def _create_hybrid_storage() -> LocalStorageService:
    """Create hybrid storage with enhanced caching."""
    base_path = os.getenv('STORAGE_BASE_PATH', '/var/www/lumen/storage')
    max_storage_gb = float(os.getenv('MAX_STORAGE_GB', '40.0'))
    
    return LocalStorageService(
        base_path=base_path,
        cache_ttl_days=14,  # Longer cache for hybrid mode
        max_storage_gb=max_storage_gb,
        enable_cache=True  # Always enabled for hybrid
    )


def reset_storage_backend():
    """Reset storage backend (mainly for testing)."""
    global _storage_instance
    _storage_instance = None


# Export main interface
__all__ = ['get_storage_backend', 'reset_storage_backend', 'IStorageService']