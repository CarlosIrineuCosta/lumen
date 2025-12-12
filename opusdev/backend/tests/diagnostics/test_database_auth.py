"""
Database Authentication Diagnostic Tests

This module contains comprehensive tests for diagnosing database authentication issues
that prevent photo retrieval in the Lumen platform.

The tests systematically check:
1. Database connection establishment
2. Authentication methods (personal vs service account)
3. Cloud SQL permissions and connectivity
4. Environment variable configuration
5. Database schema accessibility

This addresses the core issue where photos aren't displaying due to:
"password authentication failed for user postgres"
"""

import pytest
import os
import logging
from unittest.mock import patch, Mock
from sqlalchemy import create_engine, text
from google.cloud.sql.connector import Connector
import pg8000

from app.database.connection import SessionLocal, getconn, engine
from app.models.user import User
from app.models.photo import Photo

logger = logging.getLogger(__name__)


@pytest.mark.diagnostics
@pytest.mark.database
class TestDatabaseAuthentication:
    """Comprehensive database authentication diagnostics"""
    
    def test_environment_variables(self):
        """Test that required database environment variables are set"""
        required_vars = [
            'DB_USER',
            'DB_PASSWORD', 
            'DB_NAME',
            'INSTANCE_CONNECTION_NAME'
        ]
        
        missing_vars = []
        for var in required_vars:
            value = os.getenv(var)
            if not value:
                missing_vars.append(var)
            else:
                logger.info(f"✅ {var}: {'*' * len(value) if 'PASSWORD' in var else value}")
        
        if missing_vars:
            pytest.fail(f"Missing required environment variables: {missing_vars}")
    
    def test_database_connection_direct(self):
        """Test direct database connection using Cloud SQL Connector"""
        try:
            # Test the direct connection function
            conn = getconn()
            assert conn is not None, "Connection should not be None"
            
            # Test a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 as test_value")
            result = cursor.fetchone()
            assert result[0] == 1, "Simple query should return 1"
            
            cursor.close()
            conn.close()
            logger.info("✅ Direct database connection successful")
            
        except Exception as e:
            pytest.fail(f"Direct database connection failed: {e}")
    
    def test_sqlalchemy_engine_connection(self):
        """Test SQLAlchemy engine connection"""
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT 1 as test_value"))
                row = result.fetchone()
                assert row[0] == 1, "SQLAlchemy query should return 1"
            
            logger.info("✅ SQLAlchemy engine connection successful")
            
        except Exception as e:
            pytest.fail(f"SQLAlchemy engine connection failed: {e}")
    
    def test_session_local_functionality(self):
        """Test SessionLocal database session creation"""
        try:
            db = SessionLocal()
            
            # Test basic query
            result = db.execute(text("SELECT 1 as test_value"))
            row = result.fetchone()
            assert row[0] == 1, "Session query should return 1"
            
            db.close()
            logger.info("✅ SessionLocal functionality working")
            
        except Exception as e:
            pytest.fail(f"SessionLocal creation failed: {e}")
    
    def test_database_schema_access(self):
        """Test access to required database tables"""
        db = SessionLocal()
        try:
            # Test access to users table
            user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            logger.info(f"✅ Users table accessible: {user_count} records")
            
            # Test access to photos table  
            photo_count = db.execute(text("SELECT COUNT(*) FROM photos")).scalar()
            logger.info(f"✅ Photos table accessible: {photo_count} records")
            
            # Test table structure
            users_columns = db.execute(text("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = 'users'
                ORDER BY ordinal_position
            """)).fetchall()
            
            assert len(users_columns) > 0, "Users table should have columns"
            logger.info(f"✅ Users table structure: {len(users_columns)} columns")
            
        except Exception as e:
            pytest.fail(f"Database schema access failed: {e}")
        finally:
            db.close()
    
    def test_user_model_operations(self):
        """Test basic User model database operations"""
        db = SessionLocal()
        try:
            # Test querying users with SQLAlchemy models
            users = db.query(User).limit(1).all()
            logger.info(f"✅ User model query successful: {len(users)} users found")
            
            if users:
                user = users[0]
                assert hasattr(user, 'id'), "User should have id attribute"
                assert hasattr(user, 'email'), "User should have email attribute"
                logger.info(f"✅ User model attributes accessible: ID={str(user.id)[:8]}...")
                
        except Exception as e:
            pytest.fail(f"User model operations failed: {e}")
        finally:
            db.close()
    
    def test_photo_model_operations(self):
        """Test basic Photo model database operations"""
        db = SessionLocal()
        try:
            # Test querying photos with SQLAlchemy models
            photos = db.query(Photo).limit(1).all()
            logger.info(f"✅ Photo model query successful: {len(photos)} photos found")
            
            if photos:
                photo = photos[0]
                assert hasattr(photo, 'id'), "Photo should have id attribute"
                assert hasattr(photo, 'user_id'), "Photo should have user_id attribute"
                logger.info(f"✅ Photo model attributes accessible: ID={str(photo.id)[:8]}...")
                
        except Exception as e:
            pytest.fail(f"Photo model operations failed: {e}")
        finally:
            db.close()


@pytest.mark.diagnostics  
@pytest.mark.database
@pytest.mark.auth
class TestAuthenticationMethods:
    """Test different authentication methods for Cloud SQL"""
    
    def test_gcp_personal_auth_status(self):
        """Check if personal GCP authentication is active"""
        try:
            # Test if gcloud auth is working
            import subprocess
            result = subprocess.run(['gcloud', 'auth', 'list', '--format=json'], 
                                  capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                import json
                accounts = json.loads(result.stdout)
                active_accounts = [acc for acc in accounts if acc.get('status') == 'ACTIVE']
                
                if active_accounts:
                    logger.info(f"✅ Personal GCP auth active: {active_accounts[0]['account']}")
                else:
                    logger.warning("⚠️ No active GCP accounts found")
                    
            else:
                logger.warning(f"⚠️ gcloud auth check failed: {result.stderr}")
                
        except Exception as e:
            logger.warning(f"⚠️ Could not check personal auth status: {e}")
    
    def test_service_account_file_exists(self):
        """Check if service account file exists and is readable"""
        sa_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
        
        if sa_path:
            if os.path.exists(sa_path):
                logger.info(f"✅ Service account file exists: {sa_path}")
                try:
                    with open(sa_path, 'r') as f:
                        import json
                        sa_data = json.load(f)
                        assert 'client_email' in sa_data, "Service account should have client_email"
                        logger.info(f"✅ Service account valid: {sa_data['client_email']}")
                except Exception as e:
                    logger.warning(f"⚠️ Service account file invalid: {e}")
            else:
                logger.warning(f"⚠️ Service account file not found: {sa_path}")
        else:
            logger.info("ℹ️ GOOGLE_APPLICATION_CREDENTIALS not set (using personal auth)")
    
    @patch.dict(os.environ, {'GOOGLE_APPLICATION_CREDENTIALS': ''}, clear=False)
    def test_connection_with_personal_auth(self):
        """Test database connection using personal GCP authentication"""
        try:
            # Temporarily clear service account to force personal auth
            connector = Connector()
            conn = connector.connect(
                os.getenv('INSTANCE_CONNECTION_NAME'),
                "pg8000",
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', ''),
                db=os.getenv('DB_NAME', 'lumen'),
            )
            
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            assert result[0] == 1
            
            cursor.close()
            conn.close()
            connector.close()
            
            logger.info("✅ Personal auth connection successful")
            
        except Exception as e:
            logger.warning(f"⚠️ Personal auth connection failed: {e}")


@pytest.mark.diagnostics
@pytest.mark.database
@pytest.mark.slow
class TestDatabasePerformance:
    """Test database performance and connection health"""
    
    def test_connection_pool_health(self):
        """Test database connection pool behavior"""
        connections = []
        try:
            # Create multiple connections to test pooling
            for i in range(3):
                db = SessionLocal()
                result = db.execute(text("SELECT 1")).scalar()
                assert result == 1
                connections.append(db)
                logger.info(f"✅ Connection {i+1} successful")
            
        except Exception as e:
            pytest.fail(f"Connection pooling test failed: {e}")
        finally:
            for db in connections:
                db.close()
    
    def test_query_performance(self):
        """Test basic query performance"""
        import time
        
        db = SessionLocal()
        try:
            start_time = time.time()
            
            # Test a simple query performance
            db.execute(text("SELECT COUNT(*) FROM users")).scalar()
            
            query_time = time.time() - start_time
            logger.info(f"✅ Query performance: {query_time:.3f}s")
            
            # Queries should be reasonably fast
            assert query_time < 5.0, f"Query too slow: {query_time:.3f}s"
            
        except Exception as e:
            pytest.fail(f"Query performance test failed: {e}")
        finally:
            db.close()


if __name__ == "__main__":
    # Allow running diagnostics directly
    pytest.main([__file__, "-v", "-s"])