# Legacy Diagnostic Scripts

This directory contains legacy diagnostic scripts that were moved from the project root for better organization.

## Moved Scripts

### Database Diagnostics
- `check_database_uids.py` - Analyzes Firebase UID formats in database vs GCS paths
- `check_portfolio.py` - Verifies portfolio photo flags in database

### Test Data Creation
- `create_dummy_simple.py` - Creates dummy photographers with Firebase auth
- Other `create_dummy_*.py` scripts - Various test data generation methods

## Usage

These scripts have been updated to work from their new location:
- Updated import paths to work from `tests/diagnostics/legacy_scripts/`
- Fixed relative paths for configuration files
- Maintained original functionality

## Migration to Modern Tests

These legacy scripts are being superseded by:
- `../test_database_auth.py` - Comprehensive database authentication testing
- `../test_photo_pipeline.py` - End-to-end photo display pipeline testing
- `../test_live_system.py` - Live system health monitoring

The legacy scripts are preserved for reference and emergency debugging.