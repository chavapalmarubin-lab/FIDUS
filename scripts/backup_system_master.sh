#!/bin/bash
#
# SYSTEM_MASTER.md Backup Script
# Automatically backs up SYSTEM_MASTER.md every time it's modified
# Keeps last 50 backups
#

BACKUP_DIR="/tmp/system_master_backups"
SOURCE_FILE="/app/SYSTEM_MASTER.md"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "═══════════════════════════════════════════════════════"
echo "SYSTEM_MASTER.md Backup Script"
echo "Time: $(date)"
echo "═══════════════════════════════════════════════════════"

# Check if source file exists
if [ -f "$SOURCE_FILE" ]; then
    # Create backup
    BACKUP_FILE="$BACKUP_DIR/SYSTEM_MASTER_$TIMESTAMP.md"
    cp "$SOURCE_FILE" "$BACKUP_FILE"
    
    # Calculate file hash for verification
    FILE_HASH=$(md5sum "$SOURCE_FILE" | awk '{print $1}')
    
    echo "✅ Backup created: SYSTEM_MASTER_$TIMESTAMP.md"
    echo "   Size: $(stat -f%z "$SOURCE_FILE" 2>/dev/null || stat -c%s "$SOURCE_FILE") bytes"
    echo "   Hash: $FILE_HASH"
    
    # Store metadata
    echo "$TIMESTAMP|$FILE_HASH|$(stat -f%z "$SOURCE_FILE" 2>/dev/null || stat -c%s "$SOURCE_FILE")" >> "$BACKUP_DIR/backup_log.txt"
    
    # Keep only last 50 backups
    BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/SYSTEM_MASTER_*.md 2>/dev/null | wc -l)
    if [ "$BACKUP_COUNT" -gt 50 ]; then
        echo "🗑️  Cleaning old backups (keeping last 50)..."
        ls -t "$BACKUP_DIR"/SYSTEM_MASTER_*.md | tail -n +51 | xargs rm -f 2>/dev/null
        echo "   Removed $((BACKUP_COUNT - 50)) old backups"
    fi
    
    echo "📊 Total backups: $(ls -1 "$BACKUP_DIR"/SYSTEM_MASTER_*.md 2>/dev/null | wc -l)"
    
else
    echo "❌ SYSTEM_MASTER.md not found at $SOURCE_FILE!"
    echo ""
    echo "🔍 Searching for file..."
    find /app -name "SYSTEM_MASTER.md" -type f 2>/dev/null
    
    # Try to restore from latest backup
    LATEST_BACKUP=$(ls -t "$BACKUP_DIR"/SYSTEM_MASTER_*.md 2>/dev/null | head -1)
    
    if [ -n "$LATEST_BACKUP" ]; then
        echo ""
        echo "💾 Found backup: $LATEST_BACKUP"
        echo "🔄 Attempting to restore..."
        
        cp "$LATEST_BACKUP" "$SOURCE_FILE"
        
        if [ -f "$SOURCE_FILE" ]; then
            echo "✅ Successfully restored from backup!"
            echo "   Restored from: $(basename "$LATEST_BACKUP")"
            
            # Send alert
            echo "🚨 ALERT: SYSTEM_MASTER.md was missing and restored from backup" >> /tmp/system_master_alerts.log
            echo "   Time: $(date)" >> /tmp/system_master_alerts.log
            echo "   Backup used: $LATEST_BACKUP" >> /tmp/system_master_alerts.log
            echo "" >> /tmp/system_master_alerts.log
        else
            echo "❌ Restoration failed!"
        fi
    else
        echo ""
        echo "❌ No backups found in $BACKUP_DIR"
        echo "⚠️  SYSTEM_MASTER.md is MISSING and cannot be restored!"
        
        # Create emergency alert
        echo "🚨🚨🚨 CRITICAL ALERT 🚨🚨🚨" > /tmp/system_master_critical_alert.txt
        echo "SYSTEM_MASTER.md is MISSING" >> /tmp/system_master_critical_alert.txt
        echo "No backups available" >> /tmp/system_master_critical_alert.txt
        echo "Time: $(date)" >> /tmp/system_master_critical_alert.txt
        echo "IMMEDIATE ACTION REQUIRED" >> /tmp/system_master_critical_alert.txt
        
        exit 1
    fi
fi

echo "═══════════════════════════════════════════════════════"
echo "Backup complete"
echo "═══════════════════════════════════════════════════════"
