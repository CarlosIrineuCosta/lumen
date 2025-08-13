#!/usr/bin/env python3
"""
Audit Google Cloud Storage files for ID format compliance

This script examines files in the GCS bucket to verify that all file paths
follow the expected ID format conventions:
- Firebase UID strings (28-char alphanumeric) for user folders
- UUID strings for photo filenames  
- Correct path structure (photos/{firebase_uid}/{photo_uuid}.{ext})

Usage:
    python scripts/audit_gcs_files.py [options]

Examples:
    # Basic audit of photos folder
    python scripts/audit_gcs_files.py

    # Audit with custom limits
    python scripts/audit_gcs_files.py --limit 1000 --verbose

    # Audit specific folder
    python scripts/audit_gcs_files.py --prefix thumbnails/ --limit 100

    # Generate detailed report
    python scripts/audit_gcs_files.py --report-file gcs_audit_report.json
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.id_management_service import IDManagementService
from app.utils import validate_firebase_uid, validate_uuid, IDValidationError
from google.cloud import storage

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GCSAuditor:
    """Audits GCS files for ID format compliance"""
    
    def __init__(self, bucket_name: str, verbose: bool = False):
        self.bucket_name = bucket_name
        self.verbose = verbose
        self.storage_client = storage.Client()
        self.id_service = IDManagementService(storage_client=self.storage_client)
        
        # Results tracking
        self.results = {
            "audit_timestamp": datetime.now().isoformat(),
            "bucket_name": bucket_name,
            "total_files": 0,
            "valid_files": 0,
            "invalid_files": 0,
            "invalid_paths": [],
            "errors": [],
            "summary": {}
        }
    
    def audit_files(self, prefix: str = "photos/", limit: Optional[int] = None) -> Dict[str, Any]:
        """
        Audit files in the GCS bucket for ID format compliance
        
        Args:
            prefix: Path prefix to audit (default: "photos/")
            limit: Maximum number of files to audit (None for no limit)
            
        Returns:
            Dict with audit results
        """
        logger.info(f"Starting GCS audit for gs://{self.bucket_name}/{prefix}")
        if limit:
            logger.info(f"Limiting audit to {limit} files")
        
        try:
            bucket = self.storage_client.bucket(self.bucket_name)
            
            # Configure blob listing
            list_kwargs = {"prefix": prefix}
            if limit:
                list_kwargs["max_results"] = limit
            
            blobs = bucket.list_blobs(**list_kwargs)
            
            for blob in blobs:
                self._audit_single_file(blob)
                
                # Progress logging for large audits
                if self.results["total_files"] % 100 == 0 and self.results["total_files"] > 0:
                    logger.info(f"Audited {self.results['total_files']} files...")
            
        except Exception as e:
            error_msg = f"Failed to audit GCS files: {str(e)}"
            logger.error(error_msg)
            self.results["errors"].append(error_msg)
        
        self._generate_summary()
        return self.results
    
    def _audit_single_file(self, blob):
        """Audit a single file for ID format compliance"""
        self.results["total_files"] += 1
        file_path = blob.name
        
        if self.verbose and self.results["total_files"] % 50 == 0:
            logger.debug(f"Auditing: {file_path}")
        
        try:
            # Skip directory markers (paths ending with /)
            if file_path.endswith('/'):
                self.results["valid_files"] += 1
                return
            
            # Parse and validate the path using IDManagementService
            parsed = self.id_service.parse_storage_path(file_path)
            
            # Additional validation
            self._validate_parsed_path(parsed, file_path)
            
            self.results["valid_files"] += 1
            
        except (ValueError, IDValidationError) as e:
            self.results["invalid_files"] += 1
            invalid_entry = {
                "path": file_path,
                "error": str(e),
                "error_type": type(e).__name__,
                "size": blob.size if hasattr(blob, 'size') else None,
                "created": blob.time_created.isoformat() if hasattr(blob, 'time_created') and blob.time_created else None
            }
            self.results["invalid_paths"].append(invalid_entry)
            
            if self.verbose:
                logger.warning(f"Invalid file path: {file_path} - {e}")
    
    def _validate_parsed_path(self, parsed: Dict[str, str], original_path: str):
        """Additional validation of parsed path components"""
        
        # Validate that the path type is expected
        expected_types = ["photos", "thumbnails"]
        if parsed["type"] not in expected_types:
            raise ValueError(f"Unexpected path type: {parsed['type']}, expected one of {expected_types}")
        
        # Validate Firebase UID format
        try:
            validate_firebase_uid(parsed["user_id"], f"in path {original_path}")
        except IDValidationError as e:
            raise ValueError(f"Invalid Firebase UID in path: {e}")
        
        # Validate UUID format
        try:
            validate_uuid(parsed["photo_id"], f"in path {original_path}")
        except IDValidationError as e:
            raise ValueError(f"Invalid photo UUID in path: {e}")
        
        # Validate file extension
        valid_extensions = ["jpg", "jpeg", "png", "gif", "webp"]
        if parsed["file_extension"].lower() not in valid_extensions:
            raise ValueError(f"Unexpected file extension: {parsed['file_extension']}, expected one of {valid_extensions}")
    
    def _generate_summary(self):
        """Generate summary statistics for the audit"""
        total = self.results["total_files"]
        valid = self.results["valid_files"]
        invalid = self.results["invalid_files"]
        
        self.results["summary"] = {
            "total_files_audited": total,
            "valid_files": valid,
            "invalid_files": invalid,
            "compliance_rate": (valid / total * 100) if total > 0 else 0,
            "error_rate": (invalid / total * 100) if total > 0 else 0
        }
        
        # Categorize errors
        error_categories = {}
        for invalid_path in self.results["invalid_paths"]:
            error_type = invalid_path["error_type"]
            error_categories[error_type] = error_categories.get(error_type, 0) + 1
        
        self.results["summary"]["error_categories"] = error_categories
        
        logger.info(f"Audit complete: {valid}/{total} files valid ({self.results['summary']['compliance_rate']:.1f}%)")
        if invalid > 0:
            logger.warning(f"Found {invalid} invalid files ({self.results['summary']['error_rate']:.1f}%)")


def main():
    """Main CLI interface for GCS file audit"""
    parser = argparse.ArgumentParser(
        description="Audit GCS files for ID format compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Basic audit of photos folder
  %(prog)s --limit 1000 --verbose           # Audit with custom limits  
  %(prog)s --prefix thumbnails/ --limit 100 # Audit specific folder
  %(prog)s --report-file audit_report.json  # Generate detailed report
        """
    )
    
    parser.add_argument(
        "--bucket", 
        default="lumen-photos-20250731",
        help="GCS bucket name (default: lumen-photos-20250731)"
    )
    
    parser.add_argument(
        "--prefix",
        default="photos/",
        help="Path prefix to audit (default: photos/)"
    )
    
    parser.add_argument(
        "--limit",
        type=int,
        help="Maximum number of files to audit (default: no limit)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--report-file",
        help="Save detailed audit report to JSON file"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress all output except errors"
    )
    
    args = parser.parse_args()
    
    # Configure logging level
    if args.quiet:
        logging.getLogger().setLevel(logging.ERROR)
    elif args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate bucket access
    try:
        storage_client = storage.Client()
        bucket = storage_client.bucket(args.bucket)
        # Test access
        list(bucket.list_blobs(max_results=1))
    except Exception as e:
        logger.error(f"Cannot access bucket gs://{args.bucket}: {e}")
        logger.error("Make sure you have the correct permissions and bucket name")
        return 1
    
    # Run audit
    auditor = GCSAuditor(args.bucket, verbose=args.verbose)
    results = auditor.audit_files(prefix=args.prefix, limit=args.limit)
    
    # Display results
    if not args.quiet:
        print("\n" + "="*60)
        print("GCS FILE AUDIT RESULTS")
        print("="*60)
        print(f"Bucket: gs://{args.bucket}")
        print(f"Prefix: {args.prefix}")
        print(f"Total files audited: {results['summary']['total_files_audited']}")
        print(f"Valid files: {results['summary']['valid_files']}")
        print(f"Invalid files: {results['summary']['invalid_files']}")
        print(f"Compliance rate: {results['summary']['compliance_rate']:.1f}%")
        
        if results['summary']['invalid_files'] > 0:
            print(f"\nError categories:")
            for error_type, count in results['summary']['error_categories'].items():
                print(f"  {error_type}: {count}")
            
            if args.verbose and len(results['invalid_paths']) <= 10:
                print(f"\nInvalid files:")
                for invalid in results['invalid_paths']:
                    print(f"  {invalid['path']}: {invalid['error']}")
            elif len(results['invalid_paths']) > 10:
                print(f"\nFirst 5 invalid files:")
                for invalid in results['invalid_paths'][:5]:
                    print(f"  {invalid['path']}: {invalid['error']}")
                print(f"  ... and {len(results['invalid_paths']) - 5} more")
    
    # Save report if requested
    if args.report_file:
        try:
            with open(args.report_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Detailed report saved to {args.report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return 1
    
    # Exit with error code if compliance issues found
    if results['summary']['invalid_files'] > 0:
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())