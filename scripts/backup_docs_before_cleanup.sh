#!/bin/bash

# Lumen Documentation Backup Script
# Run this before executing MD_CLEANUP_EXECUTION_PLAN.md

set -e  # Exit on any error

echo "=== Lumen Documentation Backup ==="
echo "Creating backup before cleanup..."

# Create backup directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/cdc/Storage/projects/lumen/backups"
BACKUP_NAME="docs_backup_${TIMESTAMP}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Full backup directory
FULL_BACKUP_PATH="${BACKUP_DIR}/${BACKUP_NAME}"

echo "Backup directory: $FULL_BACKUP_PATH"

# Create the backup
mkdir -p "$FULL_BACKUP_PATH"

# Copy docs, archive, and agent-system/docs
echo "Copying documentation files..."
cp -r /home/cdc/Storage/projects/lumen/docs "$FULL_BACKUP_PATH/"
cp -r /home/cdc/Storage/projects/lumen/archive "$FULL_BACKUP_PATH/"
cp -r /home/cdc/Storage/projects/lumen/agent-system/docs "$FULL_BACKUP_PATH/"

# Create compressed archive
echo "Creating compressed archive..."
cd "$BACKUP_DIR"
tar -czf "${BACKUP_NAME}.tar.gz" "$BACKUP_NAME"

# Create md5 hash for integrity check
md5sum "${BACKUP_NAME}.tar.gz" > "${BACKUP_NAME}.md5"

# Create backup manifest
cat > "${BACKUP_NAME}_MANIFEST.txt" << EOF
Lumen Documentation Backup Manifest
Created: $(date)
Backup ID: ${TIMESTAMP}

Contents:
- docs/: All active documentation
- archive/: All archived documentation
- agent-system/docs/: Agent system documentation

File Count:
$(find "$FULL_BACKUP_PATH" -name "*.md" -type f | wc -l) MD files total

Backup Size:
$(du -sh "${BACKUP_NAME}.tar.gz" | cut -f1)

Commands to restore:
1. cd /home/cdc/Storage/projects/lumen
2. tar -xzf backups/${BACKUP_NAME}.tar.gz
3. cp -r ${BACKUP_NAME}/* ./
4. git status (to see changes)
EOF

echo "Backup complete!"
echo ""
echo "Backup details:"
echo "- Archive: ${BACKUP_DIR}/${BACKUP_NAME}.tar.gz"
echo "- Manifest: ${BACKUP_DIR}/${BACKUP_NAME}_MANIFEST.txt"
echo "- MD5: ${BACKUP_DIR}/${BACKUP_NAME}.md5"
echo ""
echo "To verify backup integrity:"
echo "md5sum -c ${BACKUP_DIR}/${BACKUP_NAME}.md5"
echo ""
echo "To restore if needed:"
echo "cd /home/cdc/Storage/projects/lumen"
echo "tar -xzf backups/${BACKUP_NAME}.tar.gz"
echo "cp -r ${BACKUP_NAME}/* ./"