---
description: Lumen database management and PostgreSQL operations
---

# Lumen Database Management

Handle PostgreSQL operations for $ARGUMENTS:

## 1. Schema Management

### Alembic Migration Operations
```bash
echo "=== DATABASE MIGRATION MANAGEMENT ==="

cd opusdev/backend
source venv/bin/activate

# Check current migration status
echo "Current migration status:"
alembic current -v

echo ""
echo "Migration history:"
alembic history --indicate-current | head -10

# Check for pending migrations
echo ""
echo "Checking for pending migrations..."
alembic upgrade --dry-run | grep "INFO"
```

### Create New Migration
```bash
echo "=== CREATING NEW MIGRATION ==="

# Generate migration for detected changes
echo "Generating migration for: $ARGUMENTS"

# Always backup before creating migration
BACKUP_FILE="/tmp/lumen_backup_$(date +%Y%m%d_%H%M%S).sql"
echo "Creating database backup: $BACKUP_FILE"

# Create backup (replace with actual connection details)
# pg_dump -h localhost -U lumen_user -d lumen_dev > "$BACKUP_FILE"

# Generate migration
alembic revision --autogenerate -m "$(echo $ARGUMENTS | tr ' ' '_')"

echo ""
echo "Review the generated migration file before applying!"
echo "Migration files location: opusdev/backend/alembic/versions/"
```

### Apply Migrations
```bash
echo "=== APPLYING MIGRATIONS ==="

# Safety check
echo "⚠️  IMPORTANT: Ensure you have a recent database backup!"
echo "Backup file: $BACKUP_FILE"

# Show what will be applied
echo "Migrations to apply:"
alembic upgrade --dry-run

# Apply migrations
echo ""
read -p "Apply migrations? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    alembic upgrade head
    echo "✅ Migrations applied successfully"
else
    echo "Migration cancelled"
fi
```

## 2. Data Operations

### User Profile Management
```bash
echo "=== USER PROFILE DATA OPERATIONS ==="

# Check user data integrity
echo "User profile statistics:"
python -c "
import sys
sys.path.append('app')
from database.connection import get_db_session
from sqlalchemy import text

with get_db_session() as db:
    # User counts by type
    result = db.execute(text('''
        SELECT 
            profile_data->>'user_type' as user_type,
            COUNT(*) as count
        FROM users 
        WHERE profile_data->>'user_type' IS NOT NULL
        GROUP BY profile_data->>'user_type'
        ORDER BY count DESC;
    '''))
    
    print('User Types:')
    for row in result:
        print(f'  {row.user_type}: {row.count}')
    
    # Profile completeness
    result = db.execute(text('''
        SELECT 
            CASE 
                WHEN profile_data ? 'age' AND profile_data ? 'location' THEN 'Complete'
                ELSE 'Incomplete' 
            END as completeness,
            COUNT(*) as count
        FROM users
        GROUP BY completeness;
    '''))
    
    print('\nProfile Completeness:')
    for row in result:
        print(f'  {row.completeness}: {row.count}')
" 2>/dev/null || echo "Could not connect to database"
```

### Photo Metadata Operations
```bash
echo "=== PHOTO METADATA MANAGEMENT ==="

# Photo database statistics
echo "Photo database statistics:"
python -c "
import sys
sys.path.append('app')
from database.connection import get_db_session
from sqlalchemy import text

with get_db_session() as db:
    # Photo counts and sizes
    result = db.execute(text('''
        SELECT 
            COUNT(*) as total_photos,
            AVG(metadata->>'file_size') as avg_size,
            COUNT(DISTINCT user_id) as photographers
        FROM photos;
    '''))
    
    for row in result:
        print(f'Total Photos: {row.total_photos}')
        print(f'Average Size: {row.avg_size} bytes')
        print(f'Photographers: {row.photographers}')
    
    # Photo formats
    result = db.execute(text('''
        SELECT 
            metadata->>'format' as format,
            COUNT(*) as count
        FROM photos 
        WHERE metadata ? 'format'
        GROUP BY format 
        ORDER BY count DESC;
    '''))
    
    print('\nPhoto Formats:')
    for row in result:
        print(f'  {row.format}: {row.count}')
" 2>/dev/null || echo "Could not connect to database"
```

### Geographic Data Management
```bash
echo "=== GEOGRAPHIC DATA OPERATIONS ==="

# City and location data
echo "Geographic data statistics:"
python -c "
import sys
sys.path.append('app')
from database.connection import get_db_session
from sqlalchemy import text

with get_db_session() as db:
    # Cities with most users
    result = db.execute(text('''
        SELECT 
            profile_data->>'city' as city,
            COUNT(*) as user_count
        FROM users 
        WHERE profile_data ? 'city'
        GROUP BY city 
        ORDER BY user_count DESC 
        LIMIT 10;
    '''))
    
    print('Top Cities by User Count:')
    for row in result:
        print(f'  {row.city}: {row.user_count} users')
    
    # Location privacy settings
    result = db.execute(text('''
        SELECT 
            profile_data->>'location_privacy' as privacy_level,
            COUNT(*) as count
        FROM users 
        WHERE profile_data ? 'location_privacy'
        GROUP BY privacy_level;
    '''))
    
    print('\nLocation Privacy Settings:')
    for row in result:
        print(f'  {row.privacy_level}: {row.count}')
" 2>/dev/null || echo "Could not connect to database"
```

## 3. Data Integrity Checks

### Validation and Cleanup
```bash
echo "=== DATA INTEGRITY VALIDATION ==="

# Check for orphaned records
echo "Checking for orphaned data..."
python -c "
import sys
sys.path.append('app')
from database.connection import get_db_session
from sqlalchemy import text

with get_db_session() as db:
    # Photos without users
    result = db.execute(text('''
        SELECT COUNT(*) as orphaned_photos
        FROM photos p
        LEFT JOIN users u ON p.user_id = u.id
        WHERE u.id IS NULL;
    '''))
    
    orphaned = result.fetchone().orphaned_photos
    print(f'Orphaned photos: {orphaned}')
    
    # Users without complete profile data
    result = db.execute(text('''
        SELECT COUNT(*) as incomplete_profiles
        FROM users 
        WHERE profile_data IS NULL 
           OR NOT (profile_data ? 'user_type');
    '''))
    
    incomplete = result.fetchone().incomplete_profiles
    print(f'Incomplete profiles: {incomplete}')
    
    # Duplicate email addresses
    result = db.execute(text('''
        SELECT email, COUNT(*) as count
        FROM users 
        GROUP BY email 
        HAVING COUNT(*) > 1;
    '''))
    
    duplicates = result.fetchall()
    if duplicates:
        print(f'Duplicate emails found: {len(duplicates)}')
        for row in duplicates:
            print(f'  {row.email}: {row.count} accounts')
    else:
        print('No duplicate emails found')
" 2>/dev/null || echo "Could not connect to database"
```

### Foreign Key Constraint Validation
```bash
echo "=== FOREIGN KEY VALIDATION ==="

# Validate all foreign key relationships
echo "Validating foreign key constraints..."
python -c "
import sys
sys.path.append('app')
from database.connection import get_db_session
from sqlalchemy import text

with get_db_session() as db:
    # Check constraint violations
    constraints_sql = '''
        SELECT 
            conname as constraint_name,
            conrelid::regclass as table_name
        FROM pg_constraint 
        WHERE contype = 'f'  -- foreign key constraints
        ORDER BY table_name;
    '''
    
    result = db.execute(text(constraints_sql))
    constraints = result.fetchall()
    
    print(f'Found {len(constraints)} foreign key constraints')
    for constraint in constraints:
        print(f'  {constraint.table_name}: {constraint.constraint_name}')
" 2>/dev/null || echo "Could not connect to database"
```

## 4. Performance Optimization

### Index Analysis
```bash
echo "=== DATABASE INDEX ANALYSIS ==="

# Check index usage and performance
echo "Index usage statistics:"
python -c "
import sys
sys.path.append('app')
from database.connection import get_db_session
from sqlalchemy import text

with get_db_session() as db:
    # Index usage statistics
    result = db.execute(text('''
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_tup_read,
            idx_tup_fetch
        FROM pg_stat_user_indexes 
        ORDER BY idx_tup_read DESC 
        LIMIT 10;
    '''))
    
    print('Most Used Indexes:')
    for row in result:
        print(f'  {row.tablename}.{row.indexname}: {row.idx_tup_read} reads')
    
    # Unused indexes
    result = db.execute(text('''
        SELECT 
            schemaname,
            tablename,
            indexname
        FROM pg_stat_user_indexes 
        WHERE idx_tup_read = 0 
        AND idx_tup_fetch = 0;
    '''))
    
    unused = result.fetchall()
    if unused:
        print('\nUnused Indexes:')
        for row in unused:
            print(f'  {row.tablename}.{row.indexname}')
    else:
        print('\nNo unused indexes found')
" 2>/dev/null || echo "Could not connect to database"
```

### Query Performance Monitoring
```bash
echo "=== QUERY PERFORMANCE MONITORING ==="

# Slow query analysis
echo "Analyzing query performance..."
python -c "
import sys
sys.path.append('app')
from database.connection import get_db_session
from sqlalchemy import text

with get_db_session() as db:
    # Table size analysis
    result = db.execute(text('''
        SELECT 
            tablename,
            pg_size_pretty(pg_total_relation_size(tablename::regclass)) as size,
            pg_stat_get_tuples_returned(c.oid) as tuples_returned,
            pg_stat_get_tuples_fetched(c.oid) as tuples_fetched
        FROM pg_tables pt
        JOIN pg_class c ON pt.tablename = c.relname
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(tablename::regclass) DESC;
    '''))
    
    print('Table Sizes and Access Patterns:')
    for row in result:
        print(f'  {row.tablename}: {row.size} ({row.tuples_returned} returned, {row.tuples_fetched} fetched)')
" 2>/dev/null || echo "Could not connect to database"
```

## 5. Backup and Recovery

### Database Backup Operations
```bash
echo "=== DATABASE BACKUP OPERATIONS ==="

# Create timestamped backup
BACKUP_DIR="backups/database"
mkdir -p "$BACKUP_DIR"

BACKUP_FILE="$BACKUP_DIR/lumen_backup_$(date +%Y%m%d_%H%M%S).sql"
echo "Creating database backup: $BACKUP_FILE"

# Backup command (adjust connection parameters as needed)
# pg_dump -h localhost -U lumen_user -d lumen_dev --no-password > "$BACKUP_FILE"

# Compressed backup for large databases
# pg_dump -h localhost -U lumen_user -d lumen_dev --no-password | gzip > "$BACKUP_FILE.gz"

echo "Backup created: $BACKUP_FILE"
echo "Backup size: $(du -h $BACKUP_FILE 2>/dev/null | cut -f1 || echo 'N/A')"

# Keep only last 7 days of backups
find "$BACKUP_DIR" -name "lumen_backup_*.sql*" -mtime +7 -delete 2>/dev/null
echo "Old backups cleaned up (keeping last 7 days)"
```

### Recovery Testing
```bash
echo "=== BACKUP RECOVERY TESTING ==="

# Test backup integrity (dry run)
echo "Testing backup integrity..."
LATEST_BACKUP=$(ls -t $BACKUP_DIR/lumen_backup_*.sql 2>/dev/null | head -1)

if [ -n "$LATEST_BACKUP" ]; then
    echo "Latest backup: $LATEST_BACKUP"
    
    # Test SQL file integrity
    if head -10 "$LATEST_BACKUP" | grep -q "PostgreSQL database dump"; then
        echo "✅ Backup file appears to be valid PostgreSQL dump"
    else
        echo "❌ Backup file may be corrupted"
    fi
    
    # Show backup contents summary
    echo ""
    echo "Backup contents:"
    grep -E "(CREATE TABLE|INSERT INTO)" "$LATEST_BACKUP" | wc -l | xargs echo "  SQL statements:"
else
    echo "No backup files found"
fi
```

## 6. Development Utilities

### Test Data Management
```bash
echo "=== TEST DATA MANAGEMENT ==="

# Generate test data for development
echo "Test data operations for: $ARGUMENTS"

case "$ARGUMENTS" in
    *user*|*profile*)
        echo "Generating test user profiles..."
        python -c "
import sys
sys.path.append('app')
# Add test user generation logic here
print('Test users would be created here')
"
        ;;
    *photo*)
        echo "Generating test photo records..."
        python -c "
import sys
sys.path.append('app')
# Add test photo generation logic here
print('Test photos would be created here')
"
        ;;
    *city*)
        echo "Loading city data..."
        python -c "
import sys
sys.path.append('app')
# Add city data loading logic here
print('City data would be loaded here')
"
        ;;
esac
```

### Database Reset (Development Only)
```bash
echo "=== DATABASE RESET (DEVELOPMENT ONLY) ==="

echo "⚠️  WARNING: This will destroy all data!"
echo "Only use in development environment"
echo ""
read -p "Are you sure you want to reset the database? Type 'RESET' to confirm: " confirm

if [ "$confirm" = "RESET" ]; then
    echo "Resetting database..."
    
    # Drop all tables
    alembic downgrade base
    
    # Re-apply all migrations
    alembic upgrade head
    
    # Load seed data
    echo "Loading seed data..."
    # python scripts/load_seed_data.py
    
    echo "✅ Database reset complete"
else
    echo "Database reset cancelled"
fi
```

## 7. Monitoring and Health

### Database Health Check
```bash
echo "=== DATABASE HEALTH CHECK ==="

# Connection and basic health
echo "Testing database connectivity..."
python -c "
import sys
sys.path.append('app')
from database.connection import get_db_session
from sqlalchemy import text

try:
    with get_db_session() as db:
        result = db.execute(text('SELECT version();'))
        version = result.fetchone()[0]
        print(f'✅ Database connected: {version[:50]}...')
        
        # Check database size
        result = db.execute(text('''
            SELECT pg_size_pretty(pg_database_size(current_database())) as db_size;
        '''))
        size = result.fetchone().db_size
        print(f'Database size: {size}')
        
        # Check connection count
        result = db.execute(text('''
            SELECT count(*) as connections 
            FROM pg_stat_activity 
            WHERE state = 'active';
        '''))
        connections = result.fetchone().connections
        print(f'Active connections: {connections}')
        
except Exception as e:
    print(f'❌ Database connection failed: {e}')
" 2>/dev/null || echo "Could not perform health check"
```

## Implementation Notes

- **Safety First**: Always backup before migrations
- **JSONB Usage**: Leverage PostgreSQL JSONB for flexible profile data
- **Performance**: Monitor query performance and optimize indexes
- **Security**: Validate all data inputs and use parameterized queries
- **Monitoring**: Track database metrics and performance

This command integrates with:
- `/check` for database validation
- `/deploy` for production database operations
- `/edis` for remote database health monitoring