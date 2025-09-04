#!/bin/bash
# FIDUS Database Backup Script
# Run this script daily for production backups

BACKUP_DIR="/app/backups"
DB_NAME="fidus_investment_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/fidus_backup_$TIMESTAMP.gz"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR

# Create MongoDB dump
echo "Creating database backup..."
mongodump --db $DB_NAME --archive=$BACKUP_FILE --gzip

if [ $? -eq 0 ]; then
    echo "✅ Backup created successfully: $BACKUP_FILE"
    
    # Keep only last 7 days of backups
    find $BACKUP_DIR -name "fidus_backup_*.gz" -mtime +7 -delete
    echo "✅ Old backups cleaned up"
else
    echo "❌ Backup failed!"
    exit 1
fi
