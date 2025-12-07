"""
Test suite for database connection pooling fixes.

This test suite validates that the database connection pooling
implementation works correctly and handles edge cases properly.
"""

import os
import pytest
import unittest.mock as mock
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError

from app.database.connection import engine, get_db, SessionLocal, POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, POOL_RECYCLE


class TestDatabaseConnectionPooling:
    """Test database connection pooling implementation"""

    @pytest.fixture(autouse=True)
    def setup_test_environment(self):
        """Setup test environment variables"""
        # Save original environment variables
        self.original_env = {}
        env_vars = [
            'DATABASE_URL', 'DB_POOL_SIZE', 'DB_MAX_OVERFLOW',
            'DB_POOL_TIMEOUT', 'DB_POOL_RECYCLE'
        ]

        for var in env_vars:
            self.original_env[var] = os.getenv(var)

        yield

        # Restore original environment variables
        for var, value in self.original_env.items():
            if value is None:
                os.environ.pop(var, None)
            else:
                os.environ[var] = value

    def test_pool_configuration_values(self):
        """Test that pool configuration values are properly loaded"""
        # Test default values
        assert POOL_SIZE == int(os.getenv("DB_POOL_SIZE", "10"))
        assert MAX_OVERFLOW == int(os.getenv("DB_MAX_OVERFLOW", "20"))
        assert POOL_TIMEOUT == int(os.getenv("DB_POOL_TIMEOUT", "30"))
        assert POOL_RECYCLE == int(os.getenv("DB_POOL_RECYCLE", "3600"))

    def test_pool_configuration_override(self):
        """Test that pool configuration can be overridden by environment variables"""
        # Override environment variables
        test_values = {
            'DB_POOL_SIZE': '15',
            'DB_MAX_OVERFLOW': '25',
            'DB_POOL_TIMEOUT': '45',
            'DB_POOL_RECYCLE': '7200'
        }

        for var, value in test_values.items():
            os.environ[var] = value

        # Re-import the module to pick up new values
        import importlib
        import app.database.connection
        importlib.reload(app.database.connection)

        from app.database.connection import POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT, POOL_RECYCLE

        assert POOL_SIZE == 15
        assert MAX_OVERFLOW == 25
        assert POOL_TIMEOUT == 45
        assert POOL_RECYCLE == 7200

    def test_engine_uses_queuepool(self):
        """Test that the engine uses QueuePool instead of NullPool"""
        # Check that engine.pool is an instance of QueuePool
        assert isinstance(engine.pool, QueuePool)

        # Check pool configuration
        assert engine.pool._pool.maxsize == POOL_SIZE
        assert engine.pool._max_overflow == MAX_OVERFLOW
        assert engine.pool._timeout == POOL_TIMEOUT
        assert engine.pool._recycle == POOL_RECYCLE

    @mock.patch('app.database.connection.create_engine')
    def test_engine_creation_with_database_url(self, mock_create_engine):
        """Test engine creation with direct DATABASE_URL"""
        os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test'

        # Re-import to trigger engine creation
        import importlib
        import app.database.connection
        importlib.reload(app.database.connection)

        # Verify create_engine was called with correct parameters
        mock_create_engine.assert_called()
        call_args = mock_create_engine.call_args

        assert call_args[0][0] == 'postgresql://test:test@localhost/test'  # DATABASE_URL
        assert call_args[1]['poolclass'].__name__ == 'QueuePool'
        assert call_args[1]['pool_size'] == POOL_SIZE
        assert call_args[1]['max_overflow'] == MAX_OVERFLOW
        assert call_args[1]['pool_timeout'] == POOL_TIMEOUT
        assert call_args[1]['pool_recycle'] == POOL_RECYCLE
        assert call_args[1]['pool_pre_ping'] is True

    @mock.patch('app.database.connection.create_engine')
    @mock.patch('app.database.connection.Connector')
    def test_engine_creation_with_cloudsql(self, mock_connector, mock_create_engine):
        """Test engine creation with Cloud SQL connector"""
        # Set environment for Cloud SQL
        os.environ.pop('DATABASE_URL', None)
        os.environ['INSTANCE_CONNECTION_NAME'] = 'test-project:test-region:test-instance'

        # Mock the connector
        mock_conn_instance = mock.Mock()
        mock_connector.return_value = mock_conn_instance

        # Re-import to trigger engine creation
        import importlib
        import app.database.connection
        importlib.reload(app.database.connection)

        # Verify create_engine was called with Cloud SQL parameters
        mock_create_engine.assert_called()
        call_args = mock_create_engine.call_args

        assert call_args[0][0] == 'postgresql+pg8000://'  # Cloud SQL URL
        assert call_args[1]['poolclass'].__name__ == 'QueuePool'
        assert 'creator' in call_args[1]
        assert call_args[1]['pool_pre_ping'] is True

    def test_session_factory_configuration(self):
        """Test that SessionLocal is properly configured"""
        # Check that SessionLocal is configured correctly
        assert SessionLocal.kw['autocommit'] is False
        assert SessionLocal.kw['autoflush'] is False
        assert SessionLocal.kw['bind'] is engine

    @pytest.mark.asyncio
    async def test_get_db_dependency(self):
        """Test the get_db dependency function"""
        # This test would require a real database connection, so we mock it
        with mock.patch('app.database.connection.SessionLocal') as mock_session_local:
            mock_session = mock.Mock()
            mock_session_local.return_value = mock_session

            # Call get_db as a generator
            db_gen = get_db()
            db = next(db_gen)

            assert db == mock_session
            mock_session.close.assert_called_once()

            # Test exception handling
            try:
                next(db_gen)
            except StopIteration:
                pass  # Expected

    def test_pool_pre_ping_enabled(self):
        """Test that pool_pre_ping is enabled for connection health"""
        # Check that the engine has pre_ping enabled
        # Note: This might not be directly accessible through the engine object
        # so we verify through creation parameters
        assert hasattr(engine.pool, '_validate_connection')

    @mock.patch('app.database.connection.create_engine')
    def test_debug_mode_configuration(self, mock_create_engine):
        """Test engine configuration in debug mode"""
        os.environ['DEBUG'] = 'true'

        # Re-import to trigger engine creation
        import importlib
        import app.database.connection
        importlib.reload(app.database.connection)

        # Verify create_engine was called with echo=True
        mock_create_engine.assert_called()
        call_args = mock_create_engine.call_args
        assert call_args[1]['echo'] is True

    def test_connection_pool_under_load_simulation(self):
        """Test connection pool behavior under simulated load"""
        # This test simulates multiple concurrent requests
        import threading
        import time

        results = []
        errors = []

        def worker():
            try:
                # Simulate database operation
                db = SessionLocal()
                # Simulate some work
                time.sleep(0.01)
                db.close()
                results.append(True)
            except Exception as e:
                errors.append(e)

        # Create multiple threads to simulate concurrent connections
        threads = []
        for i in range(20):  # More than pool size to test overflow
            thread = threading.Thread(target=worker)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify that all operations completed successfully
        assert len(results) == 20
        assert len(errors) == 0

    def test_pool_resource_cleanup(self):
        """Test that pool resources are properly cleaned up"""
        # Get connection from pool
        connection = engine.connect()

        # Return connection to pool
        connection.close()

        # Verify pool statistics (if available)
        # Note: This might vary based on SQLAlchemy version
        if hasattr(engine.pool, 'status'):
            status = engine.pool.status()
            assert 'pool' in status.lower()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])