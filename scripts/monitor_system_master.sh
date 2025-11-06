#!/bin/bash
#
# SYSTEM_MASTER.md Monitoring Script
# Continuously monitors for file deletion or unauthorized changes
# Runs as a background service
#

WATCH_FILE="/app/SYSTEM_MASTER.md"
CHECK_INTERVAL=60  # Check every 60 seconds
ALERT_LOG="/tmp/system_master_alerts.log"
BACKUP_SCRIPT="/app/scripts/backup_system_master.sh"

echo "═══════════════════════════════════════════════════════"
echo "SYSTEM_MASTER.md Monitoring Service Started"
echo "Time: $(date)"
echo "Watching: $WATCH_FILE"
echo "Check Interval: ${CHECK_INTERVAL}s"
echo "═══════════════════════════════════════════════════════"

# Initialize alert log
touch "$ALERT_LOG"

# Store initial state
if [ -f "$WATCH_FILE" ]; then
    LAST_HASH=$(md5sum "$WATCH_FILE" | awk '{print $1}')
    LAST_MODIFIED=$(stat -f%m "$WATCH_FILE" 2>/dev/null || stat -c%Y "$WATCH_FILE")
    echo "✅ Initial state captured"
    echo "   Hash: $LAST_HASH"
    echo "   Last Modified: $(date -d @$LAST_MODIFIED 2>/dev/null || date -r $LAST_MODIFIED)"
else
    LAST_HASH=""
    LAST_MODIFIED=0
    echo "⚠️  File does not exist initially"
fi

echo "🔍 Monitoring started..."
echo ""

# Monitoring loop
while true; do
    sleep $CHECK_INTERVAL
    
    if [ ! -f "$WATCH_FILE" ]; then
        # File is missing!
        echo "🚨 ALERT: SYSTEM_MASTER.md DELETED at $(date)" | tee -a "$ALERT_LOG"
        echo "Attempting restore..." | tee -a "$ALERT_LOG"
        
        # Run backup/restore script
        if [ -x "$BACKUP_SCRIPT" ]; then
            $BACKUP_SCRIPT
            
            if [ -f "$WATCH_FILE" ]; then
                echo "✅ File restored successfully" | tee -a "$ALERT_LOG"
                LAST_HASH=$(md5sum "$WATCH_FILE" | awk '{print $1}')
                LAST_MODIFIED=$(stat -f%m "$WATCH_FILE" 2>/dev/null || stat -c%Y "$WATCH_FILE")
            else
                echo "❌ Restoration FAILED" | tee -a "$ALERT_LOG"
                
                # Send critical alert (implement your notification method)
                # Example: send email, Slack notification, etc.
                echo "CRITICAL: SYSTEM_MASTER.md deleted and could not be restored" | tee -a "$ALERT_LOG"
            fi
        else
            echo "❌ Backup script not found or not executable" | tee -a "$ALERT_LOG"
        fi
        
        echo "" | tee -a "$ALERT_LOG"
        
    else
        # File exists - check for modifications
        CURRENT_HASH=$(md5sum "$WATCH_FILE" | awk '{print $1}')
        CURRENT_MODIFIED=$(stat -f%m "$WATCH_FILE" 2>/dev/null || stat -c%Y "$WATCH_FILE")
        
        if [ "$CURRENT_HASH" != "$LAST_HASH" ]; then
            echo "📝 File modified at $(date)"
            echo "   Old hash: $LAST_HASH"
            echo "   New hash: $CURRENT_HASH"
            
            # Create backup on modification
            if [ -x "$BACKUP_SCRIPT" ]; then
                echo "💾 Creating backup..."
                $BACKUP_SCRIPT
            fi
            
            # Update stored state
            LAST_HASH="$CURRENT_HASH"
            LAST_MODIFIED="$CURRENT_MODIFIED"
            
            # Log modification
            echo "$(date)|MODIFIED|$CURRENT_HASH" >> "$ALERT_LOG"
            echo ""
        fi
    fi
    
done
