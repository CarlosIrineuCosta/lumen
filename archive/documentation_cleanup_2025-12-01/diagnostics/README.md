# Lumen Platform Diagnostic Tests

This directory contains comprehensive diagnostic tests for debugging system issues in the Lumen photography platform.

## Overview

The diagnostic system is designed to systematically identify and resolve issues, particularly the current problem: **"User can authenticate via Firebase OAuth but photos don't display"**.

## Quick Start

### 1. Quick Health Check
```bash
cd opusdev/backend
python tests/tools/system_health_check.py
```

### 2. Full Diagnostic Suite  
```bash
cd opusdev/backend
python tests/tools/run_diagnostics.py
```

### 3. Create Test Data (if needed)
```bash
cd opusdev/backend
python tests/tools/create_test_data.py
```

## Diagnostic Test Categories

### Database Authentication (`test_database_auth.py`)
**Purpose**: Diagnose database connectivity issues that prevent photo retrieval

**Key Tests**:
- Environment variable validation
- Cloud SQL connection testing
- SQLAlchemy engine functionality  
- Database schema accessibility
- Authentication method validation (personal vs service account)

**Common Issues Identified**:
- "password authentication failed for user postgres"
- Missing environment variables
- GCP authentication problems

### Photo Pipeline (`test_photo_pipeline.py`)
**Purpose**: Test end-to-end photo display pipeline from auth to display

**Key Tests**:
- Database photo retrieval
- PhotoService initialization
- GCS signed URL generation with ID validation
- API endpoint functionality (authenticated and unauthenticated)
- Photo-User relationship integrity

**Common Issues Identified**:
- Empty photo database
- ID validation failures
- GCS bucket access problems
- Authentication token issues

### Live System Health (`test_live_system.py`)
**Purpose**: Test live running system accessibility and performance

**Key Tests**:
- Server accessibility (backend/frontend)
- API endpoint response times
- CORS configuration
- Frontend-backend integration
- Concurrent request handling

**Common Issues Identified**:
- Server not running
- Network connectivity problems
- CORS misconfiguration
- Performance bottlenecks

## Test Execution Tools

### `run_diagnostics.py`
Comprehensive test runner with options:
```bash
# Run all diagnostics
python tests/tools/run_diagnostics.py

# Quick tests only
python tests/tools/run_diagnostics.py --quick

# Database tests only
python tests/tools/run_diagnostics.py --db-only

# Live system tests only  
python tests/tools/run_diagnostics.py --live-only

# Skip external service tests
python tests/tools/run_diagnostics.py --no-external
```

### `system_health_check.py`
Rapid health assessment:
```bash
python tests/tools/system_health_check.py
```

Checks in 30 seconds:
- Server accessibility
- Database connectivity
- Environment configuration
- Photo data availability
- GCS access

### `create_test_data.py`
Test data creation for empty systems:
```bash
# Create users and photos
python tests/tools/create_test_data.py

# Users only
python tests/tools/create_test_data.py --users-only

# Photos only
python tests/tools/create_test_data.py --photos-only

# Skip GCS file creation
python tests/tools/create_test_data.py --no-gcs
```

## Addressing Current Issue

The user reports: **"logged in OAuth but not connected to the backend"**

### Systematic Diagnosis Process

1. **Run Health Check**:
   ```bash
   python tests/tools/system_health_check.py
   ```
   
2. **Focus on Failing Checks**:
   - If "Database Connection" fails → Database auth issue
   - If "Photo Data" fails → Empty database 
   - If "GCS Access" fails → GCP credentials issue

3. **Run Targeted Diagnostics**:
   ```bash
   # For database issues
   python tests/tools/run_diagnostics.py --db-only
   
   # For photo pipeline issues
   python tests/tools/run_diagnostics.py
   ```

4. **Fix Identified Issues**:
   - Database auth: `gcloud auth login carlos.irineu@gmail.com`
   - Empty database: `python tests/tools/create_test_data.py`
   - GCS access: `gcloud auth application-default login`

## Legacy Scripts

The `legacy_scripts/` directory contains migrated diagnostic scripts from the project root:
- `check_database_uids.py` - Database UID format analysis
- `check_portfolio.py` - Portfolio photo verification
- `create_dummy_simple.py` - Test user creation

These are preserved for reference but superseded by the comprehensive diagnostic tests.

## Test Markers

Use pytest markers to run specific test categories:

```bash
# Database diagnostics only
pytest -m "diagnostics and database"

# Photo pipeline tests
pytest -m "diagnostics and photos"

# Live system tests
pytest -m "diagnostics and live"

# Skip external services
pytest -m "diagnostics and not external"

# Authentication tests
pytest -m "diagnostics and auth"
```

## Integration with Existing Tests

The diagnostic tests complement the existing test structure:

```
tests/
├── unit/                    # Fast isolated tests
├── integration/             # API & database integration tests  
├── diagnostics/             # System diagnostic tests (NEW)
│   ├── test_database_auth.py
│   ├── test_photo_pipeline.py
│   ├── test_live_system.py
│   └── legacy_scripts/
├── fixtures/                # Test data & utilities
└── tools/                   # Test execution helpers (NEW)
    ├── run_diagnostics.py
    ├── system_health_check.py
    └── create_test_data.py
```

## Debugging Tips

### 1. Database Authentication Issues
```bash
# Check current GCP auth
gcloud auth list

# Use personal authentication
gcloud auth login carlos.irineu@gmail.com
unset GOOGLE_APPLICATION_CREDENTIALS

# Test connection
python tests/tools/system_health_check.py
```

### 2. Empty Photo Database
```bash
# Check data availability
python tests/tools/system_health_check.py

# Create test data if needed
python tests/tools/create_test_data.py

# Verify data creation
python tests/tools/system_health_check.py
```

### 3. GCS Access Problems
```bash
# Check bucket access
gsutil ls gs://lumen-photos-20250731/photos/

# Fix credentials if needed
gcloud auth application-default login

# Test GCS access
python tests/tools/system_health_check.py
```

## Contributing

When adding new diagnostic tests:

1. Use appropriate markers (`@pytest.mark.diagnostics`)
2. Include clear error messages and hints
3. Provide specific remediation steps
4. Test both success and failure scenarios
5. Update this README with new test descriptions