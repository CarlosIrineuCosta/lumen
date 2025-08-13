#!/usr/bin/env python3
"""
Check database consistency for Firebase UID and UUID formats

This script examines the PostgreSQL database to verify that all ID fields
contain valid formats according to our ID contracts:
- Firebase UID strings (28-char alphanumeric) in user.id and user_id fields
- UUID format in photo.id and photo_id fields
- Referential integrity between tables

Usage:
    python scripts/check_db_consistency.py [options]

Examples:
    # Basic consistency check
    python scripts/check_db_consistency.py

    # Check with custom limits  
    python scripts/check_db_consistency.py --user-limit 1000 --photo-limit 2000

    # Generate detailed report
    python scripts/check_db_consistency.py --report-file db_consistency_report.json

    # Check specific tables only
    python scripts/check_db_consistency.py --tables users,photos --verbose
"""

import os
import sys
import json
import argparse
import logging
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# Add the parent directory to sys.path to import app modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.id_management_service import IDManagementService
from app.database.connection import SessionLocal
from app.utils import validate_firebase_uid, validate_uuid, IDValidationError
from sqlalchemy import text, inspect

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseConsistencyChecker:
    """Checks database consistency for ID formats and referential integrity"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.db = SessionLocal()
        self.id_service = IDManagementService(db=self.db)
        
        # Results tracking
        self.results = {
            "check_timestamp": datetime.now().isoformat(),
            "database_info": {},
            "tables_checked": [],
            "total_records_checked": 0,
            "total_errors": 0,
            "table_results": {},
            "referential_integrity": {},
            "summary": {}
        }
        
        # Get database info
        try:
            inspector = inspect(self.db.bind)
            self.results["database_info"] = {
                "engine": str(self.db.bind.engine),
                "tables": inspector.get_table_names()
            }
        except Exception as e:
            logger.warning(f"Could not get database info: {e}")
    
    def check_all_tables(self, 
                        user_limit: Optional[int] = None, 
                        photo_limit: Optional[int] = None,
                        tables: Optional[Set[str]] = None) -> Dict[str, Any]:
        """
        Check all relevant tables for ID format consistency
        
        Args:
            user_limit: Maximum users to check (None for no limit)
            photo_limit: Maximum photos to check (None for no limit) 
            tables: Set of table names to check (None for all)
            
        Returns:
            Dict with comprehensive check results
        """
        logger.info("Starting comprehensive database consistency check")
        
        # Define tables to check and their limits
        table_checks = {
            "users": {"limit": user_limit, "check_func": self._check_users_table},
            "photos": {"limit": photo_limit, "check_func": self._check_photos_table},
            "user_specialties": {"limit": None, "check_func": self._check_user_specialties_table},
            "photo_collaborators": {"limit": None, "check_func": self._check_photo_collaborators_table},
            "photo_interactions": {"limit": None, "check_func": self._check_photo_interactions_table},
            "user_connections": {"limit": None, "check_func": self._check_user_connections_table}
        }
        
        # Filter tables if specified
        if tables:
            table_checks = {name: config for name, config in table_checks.items() if name in tables}
        
        # Run checks for each table
        for table_name, config in table_checks.items():
            try:
                logger.info(f"Checking table: {table_name}")
                result = config["check_func"](config["limit"])
                self.results["table_results"][table_name] = result
                self.results["tables_checked"].append(table_name)
                self.results["total_records_checked"] += result.get("total_checked", 0)
                self.results["total_errors"] += result.get("total_errors", 0)
                
            except Exception as e:
                error_msg = f"Failed to check table {table_name}: {str(e)}"
                logger.error(error_msg)
                self.results["table_results"][table_name] = {
                    "error": error_msg,
                    "total_checked": 0,
                    "total_errors": 1
                }
                self.results["total_errors"] += 1
        
        # Check referential integrity
        self._check_referential_integrity()
        
        # Generate summary
        self._generate_summary()
        
        return self.results
    
    def _check_users_table(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Check users table for Firebase UID format compliance"""
        result = {
            "table": "users",
            "total_checked": 0,
            "valid_ids": 0,
            "invalid_ids": 0,
            "total_errors": 0,
            "invalid_records": []
        }
        
        # Build query
        query = "SELECT id, email, handle FROM users"
        params = {}
        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit
        
        try:
            records = self.db.execute(text(query), params).fetchall()
            
            for record in records:
                user_id, email, handle = record
                result["total_checked"] += 1
                
                try:
                    validate_firebase_uid(user_id, f"user record (email: {email})")
                    result["valid_ids"] += 1
                    
                except IDValidationError as e:
                    result["invalid_ids"] += 1
                    result["total_errors"] += 1
                    result["invalid_records"].append({
                        "id": str(user_id),
                        "email": email,
                        "handle": handle,
                        "error": str(e),
                        "error_type": "invalid_firebase_uid"
                    })
                    
                    if self.verbose:
                        logger.warning(f"Invalid user ID: {user_id} (email: {email}) - {e}")
        
        except Exception as e:
            logger.error(f"Failed to check users table: {e}")
            result["error"] = str(e)
            result["total_errors"] += 1
        
        logger.info(f"Users table: {result['valid_ids']}/{result['total_checked']} valid IDs")
        return result
    
    def _check_photos_table(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Check photos table for UUID and Firebase UID format compliance"""
        result = {
            "table": "photos",
            "total_checked": 0,
            "valid_photo_ids": 0,
            "invalid_photo_ids": 0,
            "valid_user_refs": 0,
            "invalid_user_refs": 0,
            "total_errors": 0,
            "invalid_records": []
        }
        
        # Build query
        query = "SELECT id, user_id, title FROM photos"
        params = {}
        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit
        
        try:
            records = self.db.execute(text(query), params).fetchall()
            
            for record in records:
                photo_id, user_id, title = record
                result["total_checked"] += 1
                
                # Check photo ID (should be UUID)
                try:
                    validate_uuid(photo_id, f"photo record (title: {title})")
                    result["valid_photo_ids"] += 1
                except IDValidationError as e:
                    result["invalid_photo_ids"] += 1
                    result["total_errors"] += 1
                    result["invalid_records"].append({
                        "photo_id": str(photo_id),
                        "user_id": str(user_id),
                        "title": title or "Untitled",
                        "error": f"Invalid photo ID: {str(e)}",
                        "error_type": "invalid_photo_uuid"
                    })
                
                # Check user_id reference (should be Firebase UID)
                try:
                    validate_firebase_uid(user_id, f"photo user_id reference (title: {title})")
                    result["valid_user_refs"] += 1
                except IDValidationError as e:
                    result["invalid_user_refs"] += 1
                    result["total_errors"] += 1
                    result["invalid_records"].append({
                        "photo_id": str(photo_id),
                        "user_id": str(user_id),
                        "title": title or "Untitled",
                        "error": f"Invalid user_id reference: {str(e)}",
                        "error_type": "invalid_user_reference"
                    })
                
                if self.verbose and (result["invalid_photo_ids"] > 0 or result["invalid_user_refs"] > 0):
                    logger.warning(f"Issues with photo {photo_id} (user: {user_id})")
        
        except Exception as e:
            logger.error(f"Failed to check photos table: {e}")
            result["error"] = str(e)
            result["total_errors"] += 1
        
        logger.info(f"Photos table: {result['valid_photo_ids']}/{result['total_checked']} valid photo IDs, "
                   f"{result['valid_user_refs']}/{result['total_checked']} valid user refs")
        return result
    
    def _check_user_specialties_table(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Check user_specialties table for Firebase UID format compliance"""
        return self._check_table_with_user_refs("user_specialties", "user_id", limit)
    
    def _check_photo_collaborators_table(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Check photo_collaborators table for UUID and Firebase UID compliance"""
        result = {
            "table": "photo_collaborators",
            "total_checked": 0,
            "valid_ids": 0,
            "invalid_ids": 0,
            "total_errors": 0,
            "invalid_records": []
        }
        
        query = "SELECT id, photo_id, user_id, display_name FROM photo_collaborators"
        params = {}
        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit
        
        try:
            records = self.db.execute(text(query), params).fetchall()
            
            for record in records:
                collab_id, photo_id, user_id, display_name = record
                result["total_checked"] += 1
                record_valid = True
                
                # Check collaborator ID (should be UUID)
                try:
                    validate_uuid(collab_id, f"collaborator record")
                except IDValidationError as e:
                    record_valid = False
                    result["invalid_records"].append({
                        "id": str(collab_id),
                        "photo_id": str(photo_id),
                        "user_id": str(user_id),
                        "display_name": display_name,
                        "error": f"Invalid collaborator ID: {str(e)}",
                        "error_type": "invalid_collaborator_uuid"
                    })
                
                # Check photo_id reference (should be UUID)
                try:
                    validate_uuid(photo_id, f"collaborator photo_id reference")
                except IDValidationError as e:
                    record_valid = False
                    result["invalid_records"].append({
                        "id": str(collab_id),
                        "photo_id": str(photo_id),
                        "user_id": str(user_id),
                        "display_name": display_name,
                        "error": f"Invalid photo_id reference: {str(e)}",
                        "error_type": "invalid_photo_reference"
                    })
                
                # Check user_id reference (should be Firebase UID, but can be NULL)
                if user_id is not None:
                    try:
                        validate_firebase_uid(user_id, f"collaborator user_id reference")
                    except IDValidationError as e:
                        record_valid = False
                        result["invalid_records"].append({
                            "id": str(collab_id),
                            "photo_id": str(photo_id),
                            "user_id": str(user_id),
                            "display_name": display_name,
                            "error": f"Invalid user_id reference: {str(e)}",
                            "error_type": "invalid_user_reference"
                        })
                
                if record_valid:
                    result["valid_ids"] += 1
                else:
                    result["invalid_ids"] += 1
                    result["total_errors"] += 1
        
        except Exception as e:
            logger.error(f"Failed to check photo_collaborators table: {e}")
            result["error"] = str(e)
            result["total_errors"] += 1
        
        logger.info(f"Photo collaborators table: {result['valid_ids']}/{result['total_checked']} valid records")
        return result
    
    def _check_photo_interactions_table(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Check photo_interactions table for UUID and Firebase UID compliance"""
        result = {
            "table": "photo_interactions",
            "total_checked": 0,
            "valid_ids": 0,
            "invalid_ids": 0,
            "total_errors": 0,
            "invalid_records": []
        }
        
        query = "SELECT id, photo_id, user_id, interaction_type FROM photo_interactions"
        params = {}
        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit
        
        try:
            records = self.db.execute(text(query), params).fetchall()
            
            for record in records:
                interaction_id, photo_id, user_id, interaction_type = record
                result["total_checked"] += 1
                record_valid = True
                
                # Check interaction ID (should be UUID)
                try:
                    validate_uuid(interaction_id, f"interaction record")
                except IDValidationError as e:
                    record_valid = False
                    result["invalid_records"].append({
                        "id": str(interaction_id),
                        "photo_id": str(photo_id),
                        "user_id": str(user_id),
                        "interaction_type": interaction_type,
                        "error": f"Invalid interaction ID: {str(e)}",
                        "error_type": "invalid_interaction_uuid"
                    })
                
                # Check photo_id reference (should be UUID)
                try:
                    validate_uuid(photo_id, f"interaction photo_id reference")
                except IDValidationError as e:
                    record_valid = False
                    result["invalid_records"].append({
                        "id": str(interaction_id),
                        "photo_id": str(photo_id),
                        "user_id": str(user_id),
                        "interaction_type": interaction_type,
                        "error": f"Invalid photo_id reference: {str(e)}",
                        "error_type": "invalid_photo_reference"
                    })
                
                # Check user_id reference (should be Firebase UID)
                try:
                    validate_firebase_uid(user_id, f"interaction user_id reference")
                except IDValidationError as e:
                    record_valid = False
                    result["invalid_records"].append({
                        "id": str(interaction_id),
                        "photo_id": str(photo_id),
                        "user_id": str(user_id),
                        "interaction_type": interaction_type,
                        "error": f"Invalid user_id reference: {str(e)}",
                        "error_type": "invalid_user_reference"
                    })
                
                if record_valid:
                    result["valid_ids"] += 1
                else:
                    result["invalid_ids"] += 1
                    result["total_errors"] += 1
        
        except Exception as e:
            logger.error(f"Failed to check photo_interactions table: {e}")
            result["error"] = str(e)
            result["total_errors"] += 1
        
        logger.info(f"Photo interactions table: {result['valid_ids']}/{result['total_checked']} valid records")
        return result
    
    def _check_user_connections_table(self, limit: Optional[int] = None) -> Dict[str, Any]:
        """Check user_connections table for Firebase UID format compliance"""
        result = {
            "table": "user_connections",
            "total_checked": 0,
            "valid_ids": 0,
            "invalid_ids": 0,
            "total_errors": 0,
            "invalid_records": []
        }
        
        query = "SELECT id, requester_id, target_id, status FROM user_connections"
        params = {}
        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit
        
        try:
            records = self.db.execute(text(query), params).fetchall()
            
            for record in records:
                connection_id, requester_id, target_id, status = record
                result["total_checked"] += 1
                record_valid = True
                
                # Check connection ID (should be UUID)
                try:
                    validate_uuid(connection_id, f"connection record")
                except IDValidationError as e:
                    record_valid = False
                    result["invalid_records"].append({
                        "id": str(connection_id),
                        "requester_id": str(requester_id),
                        "target_id": str(target_id),
                        "status": status,
                        "error": f"Invalid connection ID: {str(e)}",
                        "error_type": "invalid_connection_uuid"
                    })
                
                # Check requester_id (should be Firebase UID)
                try:
                    validate_firebase_uid(requester_id, f"connection requester_id")
                except IDValidationError as e:
                    record_valid = False
                    result["invalid_records"].append({
                        "id": str(connection_id),
                        "requester_id": str(requester_id),
                        "target_id": str(target_id),
                        "status": status,
                        "error": f"Invalid requester_id: {str(e)}",
                        "error_type": "invalid_requester_reference"
                    })
                
                # Check target_id (should be Firebase UID)
                try:
                    validate_firebase_uid(target_id, f"connection target_id")
                except IDValidationError as e:
                    record_valid = False
                    result["invalid_records"].append({
                        "id": str(connection_id),
                        "requester_id": str(requester_id),
                        "target_id": str(target_id),
                        "status": status,
                        "error": f"Invalid target_id: {str(e)}",
                        "error_type": "invalid_target_reference"
                    })
                
                if record_valid:
                    result["valid_ids"] += 1
                else:
                    result["invalid_ids"] += 1
                    result["total_errors"] += 1
        
        except Exception as e:
            logger.error(f"Failed to check user_connections table: {e}")
            result["error"] = str(e)
            result["total_errors"] += 1
        
        logger.info(f"User connections table: {result['valid_ids']}/{result['total_checked']} valid records")
        return result
    
    def _check_table_with_user_refs(self, table_name: str, user_id_column: str, limit: Optional[int] = None) -> Dict[str, Any]:
        """Generic check for tables with user_id references"""
        result = {
            "table": table_name,
            "total_checked": 0,
            "valid_ids": 0,
            "invalid_ids": 0,
            "total_errors": 0,
            "invalid_records": []
        }
        
        query = f"SELECT {user_id_column} FROM {table_name}"
        params = {}
        if limit:
            query += " LIMIT :limit"
            params["limit"] = limit
        
        try:
            records = self.db.execute(text(query), params).fetchall()
            
            for record in records:
                user_id = record[0]
                result["total_checked"] += 1
                
                try:
                    validate_firebase_uid(user_id, f"{table_name} {user_id_column}")
                    result["valid_ids"] += 1
                except IDValidationError as e:
                    result["invalid_ids"] += 1
                    result["total_errors"] += 1
                    result["invalid_records"].append({
                        user_id_column: str(user_id),
                        "error": str(e),
                        "error_type": "invalid_user_reference"
                    })
        
        except Exception as e:
            logger.error(f"Failed to check {table_name} table: {e}")
            result["error"] = str(e)
            result["total_errors"] += 1
        
        logger.info(f"{table_name} table: {result['valid_ids']}/{result['total_checked']} valid user references")
        return result
    
    def _check_referential_integrity(self):
        """Check referential integrity between tables"""
        logger.info("Checking referential integrity")
        
        self.results["referential_integrity"] = {
            "orphaned_photos": self._find_orphaned_photos(),
            "orphaned_photo_refs": self._find_orphaned_photo_references(),
            "orphaned_user_refs": self._find_orphaned_user_references()
        }
    
    def _find_orphaned_photos(self) -> Dict[str, Any]:
        """Find photos that reference non-existent users"""
        result = {"total_checked": 0, "orphaned_count": 0, "orphaned_records": []}
        
        try:
            query = """
                SELECT p.id, p.user_id, p.title 
                FROM photos p 
                LEFT JOIN users u ON p.user_id = u.id 
                WHERE u.id IS NULL
                LIMIT 100
            """
            
            records = self.db.execute(text(query)).fetchall()
            
            for record in records:
                photo_id, user_id, title = record
                result["total_checked"] += 1
                result["orphaned_count"] += 1
                result["orphaned_records"].append({
                    "photo_id": str(photo_id),
                    "user_id": str(user_id),
                    "title": title
                })
        
        except Exception as e:
            logger.error(f"Failed to check orphaned photos: {e}")
            result["error"] = str(e)
        
        return result
    
    def _find_orphaned_photo_references(self) -> Dict[str, Any]:
        """Find records that reference non-existent photos"""
        result = {"tables_checked": [], "total_orphaned": 0}
        
        tables_to_check = [
            ("photo_collaborators", "photo_id"),
            ("photo_interactions", "photo_id")
        ]
        
        for table, column in tables_to_check:
            try:
                query = f"""
                    SELECT {column}, COUNT(*) as count
                    FROM {table} t
                    LEFT JOIN photos p ON t.{column} = p.id
                    WHERE p.id IS NULL
                    GROUP BY {column}
                    LIMIT 50
                """
                
                records = self.db.execute(text(query)).fetchall()
                
                table_result = {
                    "table": table,
                    "column": column,
                    "orphaned_count": len(records),
                    "orphaned_refs": [{"photo_id": str(r[0]), "count": r[1]} for r in records]
                }
                
                result["tables_checked"].append(table_result)
                result["total_orphaned"] += len(records)
                
            except Exception as e:
                logger.error(f"Failed to check orphaned photo refs in {table}: {e}")
        
        return result
    
    def _find_orphaned_user_references(self) -> Dict[str, Any]:
        """Find records that reference non-existent users"""
        result = {"tables_checked": [], "total_orphaned": 0}
        
        tables_to_check = [
            ("photo_collaborators", "user_id"),
            ("photo_interactions", "user_id"),
            ("user_specialties", "user_id"),
            ("user_connections", "requester_id"),
            ("user_connections", "target_id")
        ]
        
        for table, column in tables_to_check:
            try:
                # Skip NULL user_id values for photo_collaborators
                where_clause = f"t.{column} IS NOT NULL AND u.id IS NULL"
                
                query = f"""
                    SELECT t.{column}, COUNT(*) as count
                    FROM {table} t
                    LEFT JOIN users u ON t.{column} = u.id
                    WHERE {where_clause}
                    GROUP BY t.{column}
                    LIMIT 50
                """
                
                records = self.db.execute(text(query)).fetchall()
                
                table_result = {
                    "table": table,
                    "column": column,
                    "orphaned_count": len(records),
                    "orphaned_refs": [{"user_id": str(r[0]), "count": r[1]} for r in records]
                }
                
                result["tables_checked"].append(table_result)
                result["total_orphaned"] += len(records)
                
            except Exception as e:
                logger.error(f"Failed to check orphaned user refs in {table}.{column}: {e}")
        
        return result
    
    def _generate_summary(self):
        """Generate summary statistics"""
        total_records = self.results["total_records_checked"]
        total_errors = self.results["total_errors"]
        
        # Calculate overall health score
        health_score = ((total_records - total_errors) / total_records * 100) if total_records > 0 else 0
        
        # Count orphaned records
        ref_integrity = self.results.get("referential_integrity", {})
        total_orphaned = (
            ref_integrity.get("orphaned_photos", {}).get("orphaned_count", 0) +
            ref_integrity.get("orphaned_photo_refs", {}).get("total_orphaned", 0) +
            ref_integrity.get("orphaned_user_refs", {}).get("total_orphaned", 0)
        )
        
        self.results["summary"] = {
            "total_records_checked": total_records,
            "total_errors": total_errors,
            "health_score": health_score,
            "tables_checked": len(self.results["tables_checked"]),
            "referential_integrity_issues": total_orphaned,
            "overall_status": "healthy" if total_errors == 0 and total_orphaned == 0 else "issues_found"
        }
        
        logger.info(f"Database consistency check complete:")
        logger.info(f"  Records checked: {total_records}")
        logger.info(f"  Errors found: {total_errors}")
        logger.info(f"  Health score: {health_score:.1f}%")
        logger.info(f"  Referential integrity issues: {total_orphaned}")
    
    def __del__(self):
        """Cleanup database connection"""
        if hasattr(self, 'db'):
            self.db.close()


def main():
    """Main CLI interface for database consistency check"""
    parser = argparse.ArgumentParser(
        description="Check database consistency for ID formats and referential integrity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                                    # Basic consistency check
  %(prog)s --user-limit 1000 --photo-limit 2000  # Check with custom limits
  %(prog)s --report-file db_report.json      # Generate detailed report
  %(prog)s --tables users,photos --verbose   # Check specific tables only
        """
    )
    
    parser.add_argument(
        "--user-limit",
        type=int,
        help="Maximum users to check (default: no limit)"
    )
    
    parser.add_argument(
        "--photo-limit",
        type=int,
        help="Maximum photos to check (default: no limit)"
    )
    
    parser.add_argument(
        "--tables",
        help="Comma-separated list of tables to check (default: all)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--report-file",
        help="Save detailed consistency report to JSON file"
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
    
    # Parse tables filter
    tables_filter = None
    if args.tables:
        tables_filter = set(t.strip() for t in args.tables.split(','))
    
    # Run consistency check
    try:
        checker = DatabaseConsistencyChecker(verbose=args.verbose)
        results = checker.check_all_tables(
            user_limit=args.user_limit,
            photo_limit=args.photo_limit,
            tables=tables_filter
        )
    except Exception as e:
        logger.error(f"Failed to run consistency check: {e}")
        return 1
    
    # Display results
    if not args.quiet:
        print("\n" + "="*60)
        print("DATABASE CONSISTENCY CHECK RESULTS")
        print("="*60)
        
        summary = results["summary"]
        print(f"Tables checked: {', '.join(results['tables_checked'])}")
        print(f"Total records checked: {summary['total_records_checked']}")
        print(f"Total errors found: {summary['total_errors']}")
        print(f"Health score: {summary['health_score']:.1f}%")
        print(f"Referential integrity issues: {summary['referential_integrity_issues']}")
        print(f"Overall status: {summary['overall_status']}")
        
        # Show table-specific results
        if args.verbose:
            print(f"\nTable-specific results:")
            for table_name, table_result in results["table_results"].items():
                if "error" in table_result:
                    print(f"  {table_name}: ERROR - {table_result['error']}")
                else:
                    valid_count = table_result.get("valid_ids", 0) or table_result.get("valid_photo_ids", 0) + table_result.get("valid_user_refs", 0)
                    total_count = table_result.get("total_checked", 0)
                    print(f"  {table_name}: {valid_count}/{total_count} valid")
    
    # Save report if requested
    if args.report_file:
        try:
            with open(args.report_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.info(f"Detailed report saved to {args.report_file}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return 1
    
    # Exit with error code if issues found
    if results["summary"]["overall_status"] != "healthy":
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())