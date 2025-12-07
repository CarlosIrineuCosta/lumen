#!/bin/bash
# Test runner script for Edis environment
# This script sets up the PostgreSQL test environment and runs tests

set -e

# Load test environment variables
export $(grep -v '^#' .env.test | xargs)

# Ensure test database exists
echo "Setting up test database..."
createdb -h $TEST_DB_HOST -p $TEST_DB_PORT -U $TEST_DB_USER $TEST_DB_NAME || echo "Database may already exist"

# Create test storage directory
mkdir -p /tmp/test_storage

echo "Running tests..."
python -m pytest -v --tb=short

echo "Tests completed!"