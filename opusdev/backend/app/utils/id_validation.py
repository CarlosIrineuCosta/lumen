"""
ID Validation and Management Utilities

This module provides comprehensive validation and formatting utilities for managing
Firebase UIDs, UUIDs, and other identifier formats throughout the application.

Critical for ensuring consistency between:
- Firebase Authentication (28-char alphanumeric UIDs)
- PostgreSQL database (String and UUID columns)  
- Google Cloud Storage file paths

Design Principles:
- Fail-fast validation to catch format mismatches early
- Explicit type conversion with clear error messages
- Comprehensive logging for troubleshooting
- Future-proof for additional ID formats
"""

import re
import uuid
import logging
from typing import Union, Optional, TypeVar, Type
from enum import Enum

logger = logging.getLogger(__name__)

# Type hints for better code clarity
FirebaseUID = str
UUIDString = str
UUIDObject = uuid.UUID

class IDType(Enum):
    """Supported identifier types in the system"""
    FIREBASE_UID = "firebase_uid"
    UUID_STRING = "uuid_string" 
    UUID_OBJECT = "uuid_object"
    UNKNOWN = "unknown"

class IDValidationError(Exception):
    """Raised when ID validation fails"""
    def __init__(self, message: str, id_value: any, expected_type: IDType):
        self.id_value = id_value
        self.expected_type = expected_type
        super().__init__(f"{message}. Got: '{id_value}' (type: {type(id_value).__name__}), expected: {expected_type.value}")

# Firebase UID validation (28-character alphanumeric strings)
FIREBASE_UID_PATTERN = re.compile(r'^[a-zA-Z0-9]{28}$')

# UUID validation (standard UUID4 format)
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$', re.IGNORECASE)

def detect_id_type(value: any) -> IDType:
    """
    Detect the type of an identifier value
    
    Args:
        value: The identifier to analyze
        
    Returns:
        IDType enum indicating the detected type
    """
    if value is None:
        return IDType.UNKNOWN
        
    if isinstance(value, uuid.UUID):
        return IDType.UUID_OBJECT
        
    if not isinstance(value, str):
        return IDType.UNKNOWN
        
    if FIREBASE_UID_PATTERN.match(value):
        return IDType.FIREBASE_UID
        
    if UUID_PATTERN.match(value):
        return IDType.UUID_STRING
        
    return IDType.UNKNOWN

def is_valid_firebase_uid(value: any) -> bool:
    """
    Check if value is a valid Firebase UID format
    
    Args:
        value: Value to validate
        
    Returns:
        True if valid Firebase UID, False otherwise
    """
    return detect_id_type(value) == IDType.FIREBASE_UID

def is_valid_uuid(value: any) -> bool:
    """
    Check if value is a valid UUID (string or object)
    
    Args:
        value: Value to validate
        
    Returns:
        True if valid UUID, False otherwise
    """
    detected_type = detect_id_type(value)
    return detected_type in [IDType.UUID_STRING, IDType.UUID_OBJECT]

def validate_firebase_uid(value: any, context: str = "") -> FirebaseUID:
    """
    Validate and return a Firebase UID, raising exception if invalid
    
    Args:
        value: Value to validate as Firebase UID
        context: Additional context for error messages
        
    Returns:
        Validated Firebase UID string
        
    Raises:
        IDValidationError: If value is not a valid Firebase UID
    """
    if not is_valid_firebase_uid(value):
        raise IDValidationError(
            f"Invalid Firebase UID{' in ' + context if context else ''}", 
            value, 
            IDType.FIREBASE_UID
        )
    
    logger.debug(f"Validated Firebase UID{' in ' + context if context else ''}: {value}")
    return str(value)

def validate_uuid(value: any, context: str = "") -> UUIDObject:
    """
    Validate and return a UUID object, raising exception if invalid
    
    Args:
        value: Value to validate as UUID
        context: Additional context for error messages
        
    Returns:
        Validated UUID object
        
    Raises:
        IDValidationError: If value is not a valid UUID
    """
    detected_type = detect_id_type(value)
    
    if detected_type == IDType.UUID_OBJECT:
        logger.debug(f"Validated UUID object{' in ' + context if context else ''}: {value}")
        return value
    elif detected_type == IDType.UUID_STRING:
        try:
            uuid_obj = uuid.UUID(value)
            logger.debug(f"Converted UUID string to object{' in ' + context if context else ''}: {value}")
            return uuid_obj
        except ValueError as e:
            raise IDValidationError(
                f"Invalid UUID string{' in ' + context if context else ''}: {e}", 
                value, 
                IDType.UUID_OBJECT
            )
    else:
        raise IDValidationError(
            f"Invalid UUID{' in ' + context if context else ''}", 
            value, 
            IDType.UUID_OBJECT
        )

def uuid_to_string(value: Union[UUIDObject, UUIDString], context: str = "") -> UUIDString:
    """
    Convert UUID (object or string) to string format
    
    Args:
        value: UUID to convert
        context: Additional context for error messages
        
    Returns:
        UUID in string format
        
    Raises:
        IDValidationError: If value is not a valid UUID
    """
    detected_type = detect_id_type(value)
    
    if detected_type == IDType.UUID_STRING:
        logger.debug(f"UUID already string{' in ' + context if context else ''}: {value}")
        return str(value)
    elif detected_type == IDType.UUID_OBJECT:
        result = str(value)
        logger.debug(f"Converted UUID object to string{' in ' + context if context else ''}: {result}")
        return result
    else:
        raise IDValidationError(
            f"Cannot convert to UUID string{' in ' + context if context else ''}", 
            value, 
            IDType.UUID_STRING
        )

def ensure_string_format(*values, context: str = "") -> tuple:
    """
    Ensure all provided values are in string format for safe path construction
    
    Args:
        *values: Values to convert to strings
        context: Additional context for error messages
        
    Returns:
        Tuple of values converted to strings
        
    Raises:
        IDValidationError: If any value cannot be safely converted
    """
    results = []
    
    for i, value in enumerate(values):
        if value is None:
            raise IDValidationError(
                f"None value at position {i}{' in ' + context if context else ''}", 
                value, 
                IDType.UNKNOWN
            )
        
        detected_type = detect_id_type(value)
        
        if detected_type == IDType.FIREBASE_UID:
            results.append(str(value))
        elif detected_type in [IDType.UUID_STRING, IDType.UUID_OBJECT]:
            results.append(str(value))
        elif isinstance(value, (str, int)):
            # Allow other string/numeric types but log for monitoring
            logger.warning(f"Converting non-ID value to string at position {i}{' in ' + context if context else ''}: {value} (type: {type(value).__name__})")
            results.append(str(value))
        else:
            raise IDValidationError(
                f"Cannot convert value at position {i} to string{' in ' + context if context else ''}", 
                value, 
                IDType.UNKNOWN
            )
    
    return tuple(results)

def log_id_context(operation: str, **kwargs):
    """
    Log ID values and types for debugging purposes
    
    Args:
        operation: Description of the operation being performed
        **kwargs: Named ID values to log
    """
    id_info = []
    for name, value in kwargs.items():
        detected_type = detect_id_type(value)
        id_info.append(f"{name}={value} (type={type(value).__name__}, detected={detected_type.value})")
    
    logger.debug(f"ID Context - {operation}: {', '.join(id_info)}")

# Convenience functions for common validation scenarios

def validate_user_id(user_id: any, context: str = "user lookup") -> FirebaseUID:
    """Validate user_id as Firebase UID"""
    return validate_firebase_uid(user_id, context)

def validate_photo_id(photo_id: any, context: str = "photo lookup") -> UUIDObject:
    """Validate photo_id as UUID"""
    return validate_uuid(photo_id, context)

def format_gcs_path(*path_parts, context: str = "GCS path construction") -> str:
    """
    Safely construct GCS file path from ID components
    
    Args:
        *path_parts: Path components (Firebase UID, UUID, filename parts)
        context: Additional context for error messages
        
    Returns:
        Safe GCS path string
        
    Raises:
        IDValidationError: If any path component is invalid
    """
    safe_parts = ensure_string_format(*path_parts, context=context)
    path = "/".join(safe_parts)
    
    logger.debug(f"Constructed GCS path{' for ' + context if context else ''}: {path}")
    return path

def validate_id_consistency(user_id: any, photo_id: any, context: str = "") -> tuple[FirebaseUID, UUIDString]:
    """
    Validate user_id and photo_id consistency for operations
    
    Args:
        user_id: User identifier (should be Firebase UID)
        photo_id: Photo identifier (should be UUID)
        context: Additional context for error messages
        
    Returns:
        Tuple of (validated_user_id, validated_photo_id_string)
        
    Raises:
        IDValidationError: If either ID is invalid
    """
    validated_user_id = validate_firebase_uid(user_id, f"user_id{' in ' + context if context else ''}")
    validated_photo_uuid = validate_uuid(photo_id, f"photo_id{' in ' + context if context else ''}")
    validated_photo_id = uuid_to_string(validated_photo_uuid, f"photo_id conversion{' in ' + context if context else ''}")
    
    log_id_context(f"ID consistency validation{' for ' + context if context else ''}", 
                   user_id=validated_user_id, photo_id=validated_photo_id)
    
    return validated_user_id, validated_photo_id