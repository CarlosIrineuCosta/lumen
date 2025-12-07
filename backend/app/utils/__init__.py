"""
Utility modules for the Lumen application

This package contains various utility functions and classes to support
the core application functionality.
"""

from .id_validation import (
    # Core validation functions
    validate_firebase_uid,
    validate_uuid,
    uuid_to_string,
    ensure_string_format,
    
    # Type detection
    detect_id_type,
    is_valid_firebase_uid,
    is_valid_uuid,
    
    # Convenience functions
    validate_user_id,
    validate_photo_id,
    format_gcs_path,
    validate_id_consistency,
    
    # Logging utilities
    log_id_context,
    
    # Exception types
    IDValidationError,
    IDType,
)

__all__ = [
    'validate_firebase_uid',
    'validate_uuid', 
    'uuid_to_string',
    'ensure_string_format',
    'detect_id_type',
    'is_valid_firebase_uid',
    'is_valid_uuid',
    'validate_user_id',
    'validate_photo_id', 
    'format_gcs_path',
    'validate_id_consistency',
    'log_id_context',
    'IDValidationError',
    'IDType',
]