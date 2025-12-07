"""
Centralized ID Management Service

This service provides high-level operations for managing IDs throughout the application,
building on the foundation of the ID validation utilities.

Key Features:
- Centralized ID conversion and validation
- GCS path generation and validation
- ID format migration support
- Audit and consistency checking utilities
- Integration with database and storage systems

Design Goals:
- Single source of truth for ID operations
- Consistent error handling and logging
- Future-proof for additional ID formats or migration needs
- Easy integration with existing services
"""

import logging
import uuid
from typing import Dict, List, Optional, Tuple, Union, Any
from sqlalchemy import text
from sqlalchemy.orm import Session
from google.cloud import storage

from app.utils import (
    validate_firebase_uid, validate_uuid, validate_id_consistency,
    format_gcs_path, log_id_context, IDValidationError, IDType,
    detect_id_type, is_valid_firebase_uid, is_valid_uuid, uuid_to_string
)
from app.database.connection import SessionLocal

logger = logging.getLogger(__name__)


class IDMismatchError(Exception):
    """Raised when ID formats don't match between systems"""
    pass


class IDManagementService:
    """
    Centralized service for managing ID formats and consistency across the application
    """
    
    def __init__(self, db: Session = None, storage_client: storage.Client = None):
        self.db = db if db else SessionLocal()
        self.storage_client = storage_client if storage_client else storage.Client()
        
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()
    
    # Core ID Operations
    
    def normalize_user_id(self, user_id: Any, context: str = "") -> str:
        """
        Normalize any user ID input to a validated Firebase UID string
        
        Args:
            user_id: User identifier (should be Firebase UID)
            context: Additional context for error messages
            
        Returns:
            Validated Firebase UID string
            
        Raises:
            IDValidationError: If user_id is not a valid Firebase UID
        """
        return validate_firebase_uid(user_id, context)
    
    def normalize_photo_id(self, photo_id: Any, context: str = "", return_uuid: bool = False) -> Union[str, uuid.UUID]:
        """
        Normalize any photo ID input to a validated UUID
        
        Args:
            photo_id: Photo identifier (should be UUID)
            context: Additional context for error messages
            return_uuid: If True, return UUID object; if False, return string
            
        Returns:
            Validated UUID (object or string based on return_uuid)
            
        Raises:
            IDValidationError: If photo_id is not a valid UUID
        """
        validated_uuid = validate_uuid(photo_id, context)
        return validated_uuid if return_uuid else str(validated_uuid)
    
    def prepare_ids_for_operation(self, user_id: Any, photo_id: Any, context: str = "") -> Tuple[str, str, uuid.UUID]:
        """
        Prepare and validate both user and photo IDs for database/storage operations
        
        Args:
            user_id: User identifier
            photo_id: Photo identifier
            context: Operation context for error messages
            
        Returns:
            Tuple of (firebase_uid_string, photo_id_string, photo_uuid_object)
            
        Raises:
            IDValidationError: If either ID is invalid
        """
        firebase_uid, photo_id_str = validate_id_consistency(user_id, photo_id, context)
        photo_uuid = validate_uuid(photo_id, context)
        
        return firebase_uid, photo_id_str, photo_uuid
    
    # GCS Path Operations
    
    def generate_photo_storage_path(self, user_id: Any, photo_id: Any, file_extension: str = "jpg") -> str:
        """
        Generate standardized storage path for photo files
        
        Args:
            user_id: User identifier (Firebase UID)
            photo_id: Photo identifier (UUID)
            file_extension: File extension (default: jpg)
            
        Returns:
            GCS storage path string
            
        Raises:
            IDValidationError: If IDs are invalid
        """
        firebase_uid, photo_id_str, _ = self.prepare_ids_for_operation(
            user_id, photo_id, context="photo storage path"
        )
        
        return format_gcs_path("photos", firebase_uid, f"{photo_id_str}.{file_extension}",
                              context="photo storage")
    
    def generate_thumbnail_storage_path(self, user_id: Any, photo_id: Any, file_extension: str = "jpg") -> str:
        """
        Generate standardized storage path for thumbnail files
        
        Args:
            user_id: User identifier (Firebase UID) 
            photo_id: Photo identifier (UUID)
            file_extension: File extension (default: jpg)
            
        Returns:
            GCS thumbnail storage path string
            
        Raises:
            IDValidationError: If IDs are invalid
        """
        firebase_uid, photo_id_str, _ = self.prepare_ids_for_operation(
            user_id, photo_id, context="thumbnail storage path"
        )
        
        return format_gcs_path("thumbnails", firebase_uid, f"{photo_id_str}_thumb.{file_extension}",
                              context="thumbnail storage")
    
    def generate_storage_paths(self, user_id: Any, photo_id: Any, file_extension: str = "jpg") -> Tuple[str, str]:
        """
        Generate both photo and thumbnail storage paths
        
        Args:
            user_id: User identifier (Firebase UID)
            photo_id: Photo identifier (UUID)  
            file_extension: File extension (default: jpg)
            
        Returns:
            Tuple of (photo_path, thumbnail_path)
            
        Raises:
            IDValidationError: If IDs are invalid
        """
        photo_path = self.generate_photo_storage_path(user_id, photo_id, file_extension)
        thumbnail_path = self.generate_thumbnail_storage_path(user_id, photo_id, file_extension)
        
        return photo_path, thumbnail_path
    
    def parse_storage_path(self, storage_path: str) -> Dict[str, str]:
        """
        Parse a storage path to extract user_id and photo_id
        
        Args:
            storage_path: GCS storage path (e.g., "photos/firebase_uid/photo_id.jpg")
            
        Returns:
            Dict with keys: type, user_id, photo_id, file_extension
            
        Raises:
            ValueError: If path format is invalid
        """
        parts = storage_path.strip('/').split('/')
        
        if len(parts) < 3:
            raise ValueError(f"Invalid storage path format: {storage_path}")
        
        path_type = parts[0]  # "photos" or "thumbnails"
        user_id = parts[1]    # Firebase UID
        filename = parts[2]   # "photo_id.extension" or "photo_id_thumb.extension"
        
        # Extract photo_id and extension from filename
        if '_thumb.' in filename:
            # Thumbnail file
            photo_id_part, extension = filename.rsplit('_thumb.', 1)
        elif '.' in filename:
            # Regular photo file
            photo_id_part, extension = filename.rsplit('.', 1)
        else:
            raise ValueError(f"Invalid filename format in path: {storage_path}")
        
        # Validate extracted IDs
        try:
            validate_firebase_uid(user_id, f"parsed from path: {storage_path}")
            validate_uuid(photo_id_part, f"parsed from path: {storage_path}")
        except IDValidationError as e:
            raise ValueError(f"Invalid ID format in storage path {storage_path}: {e}")
        
        return {
            "type": path_type,
            "user_id": user_id,
            "photo_id": photo_id_part,
            "file_extension": extension
        }
    
    # Database Consistency Operations
    
    def check_user_id_consistency(self, limit: int = 100) -> Dict[str, Any]:
        """
        Check consistency of user IDs in the database
        
        Args:
            limit: Maximum number of records to check
            
        Returns:
            Dict with consistency check results
        """
        logger.info(f"Checking user ID consistency (limit: {limit})")
        
        results = {
            "total_checked": 0,
            "valid_ids": 0,
            "invalid_ids": 0,
            "invalid_records": []
        }
        
        # Query user records
        query_result = self.db.execute(
            text("SELECT id, email, handle FROM users LIMIT :limit"),
            {"limit": limit}
        ).fetchall()
        
        for record in query_result:
            user_id, email, handle = record
            results["total_checked"] += 1
            
            try:
                validate_firebase_uid(user_id, f"user record check (email: {email})")
                results["valid_ids"] += 1
            except IDValidationError as e:
                results["invalid_ids"] += 1
                results["invalid_records"].append({
                    "user_id": user_id,
                    "email": email,
                    "handle": handle,
                    "error": str(e)
                })
                logger.warning(f"Invalid user ID found: {user_id} (email: {email}) - {e}")
        
        logger.info(f"User ID consistency check complete: {results['valid_ids']}/{results['total_checked']} valid")
        return results
    
    def check_photo_id_consistency(self, limit: int = 100) -> Dict[str, Any]:
        """
        Check consistency of photo IDs and user_id references
        
        Args:
            limit: Maximum number of records to check
            
        Returns:
            Dict with consistency check results
        """
        logger.info(f"Checking photo ID consistency (limit: {limit})")
        
        results = {
            "total_checked": 0,
            "valid_photo_ids": 0,
            "invalid_photo_ids": 0,
            "valid_user_refs": 0,
            "invalid_user_refs": 0,
            "invalid_records": []
        }
        
        # Query photo records
        query_result = self.db.execute(
            text("SELECT id, user_id, title FROM photos LIMIT :limit"),
            {"limit": limit}
        ).fetchall()
        
        for record in query_result:
            photo_id, user_id, title = record
            results["total_checked"] += 1
            
            # Check photo ID
            try:
                validate_uuid(photo_id, f"photo record check (title: {title})")
                results["valid_photo_ids"] += 1
            except IDValidationError as e:
                results["invalid_photo_ids"] += 1
                results["invalid_records"].append({
                    "photo_id": str(photo_id),
                    "user_id": str(user_id),
                    "title": title,
                    "error": f"Invalid photo ID: {e}"
                })
                
            # Check user_id reference
            try:
                validate_firebase_uid(user_id, f"photo user_id reference (title: {title})")
                results["valid_user_refs"] += 1
            except IDValidationError as e:
                results["invalid_user_refs"] += 1
                results["invalid_records"].append({
                    "photo_id": str(photo_id),
                    "user_id": str(user_id),
                    "title": title,
                    "error": f"Invalid user_id reference: {e}"
                })
        
        logger.info(f"Photo ID consistency check complete: "
                   f"Photos: {results['valid_photo_ids']}/{results['total_checked']} valid, "
                   f"User refs: {results['valid_user_refs']}/{results['total_checked']} valid")
        return results
    
    def audit_database_consistency(self, user_limit: int = 100, photo_limit: int = 100) -> Dict[str, Any]:
        """
        Comprehensive audit of database ID consistency
        
        Args:
            user_limit: Maximum users to check
            photo_limit: Maximum photos to check
            
        Returns:
            Combined audit results
        """
        logger.info("Starting comprehensive database ID consistency audit")
        
        audit_results = {
            "audit_timestamp": logger.handlers[0].formatter.formatTime(logger.makeRecord(
                "", 0, "", 0, "", (), None
            ), None) if logger.handlers else "unknown",
            "users": self.check_user_id_consistency(user_limit),
            "photos": self.check_photo_id_consistency(photo_limit)
        }
        
        # Calculate overall health score
        total_records = audit_results["users"]["total_checked"] + audit_results["photos"]["total_checked"]
        total_valid = (audit_results["users"]["valid_ids"] + 
                      audit_results["photos"]["valid_photo_ids"] + 
                      audit_results["photos"]["valid_user_refs"])
        
        audit_results["overall"] = {
            "total_checks": total_records + audit_results["photos"]["total_checked"],  # Count user refs separately
            "total_valid": total_valid,
            "health_score": (total_valid / (total_records + audit_results["photos"]["total_checked"])) * 100 if total_records > 0 else 0
        }
        
        logger.info(f"Database audit complete. Health score: {audit_results['overall']['health_score']:.1f}%")
        return audit_results
    
    # Storage Audit Operations
    
    def verify_storage_path_format(self, bucket_name: str, prefix: str = "photos/", limit: int = 50) -> Dict[str, Any]:
        """
        Verify that storage file paths follow expected ID format conventions
        
        Args:
            bucket_name: GCS bucket name
            prefix: Path prefix to check (default: "photos/")
            limit: Maximum files to check
            
        Returns:
            Dict with verification results
        """
        logger.info(f"Verifying storage path formats in gs://{bucket_name}/{prefix} (limit: {limit})")
        
        results = {
            "total_checked": 0,
            "valid_paths": 0,
            "invalid_paths": 0,
            "invalid_files": []
        }
        
        try:
            bucket = self.storage_client.bucket(bucket_name)
            blobs = bucket.list_blobs(prefix=prefix, max_results=limit)
            
            for blob in blobs:
                results["total_checked"] += 1
                
                try:
                    self.parse_storage_path(blob.name)
                    results["valid_paths"] += 1
                except (ValueError, IDValidationError) as e:
                    results["invalid_paths"] += 1
                    results["invalid_files"].append({
                        "path": blob.name,
                        "error": str(e)
                    })
                    logger.warning(f"Invalid storage path: {blob.name} - {e}")
            
        except Exception as e:
            logger.error(f"Failed to verify storage paths: {e}")
            results["error"] = str(e)
        
        logger.info(f"Storage path verification complete: {results['valid_paths']}/{results['total_checked']} valid")
        return results
    
    # Utility Methods
    
    def log_operation_context(self, operation: str, **kwargs):
        """
        Log operation context with standardized ID information
        
        Args:
            operation: Description of the operation
            **kwargs: Named ID values to log
        """
        log_id_context(operation, **kwargs)
    
    def get_id_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about ID usage in the database
        
        Returns:
            Dict with ID usage statistics
        """
        stats = {}
        
        try:
            # User statistics
            user_count = self.db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            stats["users"] = {
                "total_count": user_count
            }
            
            # Photo statistics
            photo_count = self.db.execute(text("SELECT COUNT(*) FROM photos")).scalar()
            unique_photo_users = self.db.execute(text("SELECT COUNT(DISTINCT user_id) FROM photos")).scalar()
            stats["photos"] = {
                "total_count": photo_count,
                "unique_users": unique_photo_users
            }
            
            # Relationship statistics
            stats["relationships"] = {
                "photos_per_user": photo_count / user_count if user_count > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Failed to get ID statistics: {e}")
            stats["error"] = str(e)
        
        return stats