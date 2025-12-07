---
description: EDIS Swiss VPS health monitoring and status checks
---

# EDIS Server Health Monitor

Monitor Swiss VPS status for $ARGUMENTS:

## 1. System Health Overview

### Connection and Basic Status
```bash
echo "=== EDIS SERVER HEALTH CHECK ==="
echo "Server: 83.172.136.127 (Swiss VPS)"
echo "Timestamp: $(date)"
echo ""

# Test SSH connection
if ssh -o ConnectTimeout=10 root@83.172.136.127 "echo 'Connection successful'" 2>/dev/null; then
    echo "✅ SSH Connection: Available"
else
    echo "❌ SSH Connection: Failed"
    echo "Check network connectivity and server status"
    exit 1
fi
```

### System Resources
```bash
echo "=== SYSTEM RESOURCES ==="

# Get system information
ssh root@83.172.136.127 "
    echo 'Uptime:'
    uptime
    echo ''
    echo 'Memory Usage:'
    free -h
    echo ''
    echo 'Disk Usage:'
    df -h /
    echo ''
    echo 'CPU Load (1min, 5min, 15min):'
    cat /proc/loadavg
    echo ''
    echo 'Top 5 processes by CPU:'
    ps aux --sort=-%cpu | head -6
" 2>/dev/null || echo "❌ Failed to get system resources"
```

### Disk Space Analysis
```bash
echo "=== DISK SPACE ANALYSIS ==="

DISK_INFO=$(ssh root@83.172.136.127 "df -h / | tail -1" 2>/dev/null)
DISK_USAGE=$(echo "$DISK_INFO" | awk '{print $5}' | sed 's/%//')
DISK_AVAIL=$(echo "$DISK_INFO" | awk '{print $4}')

echo "Current usage: $DISK_USAGE%"
echo "Available space: $DISK_AVAIL"

if [ "$DISK_USAGE" -gt 90 ]; then
    echo "🚨 CRITICAL: Disk usage over 90%"
elif [ "$DISK_USAGE" -gt 80 ]; then
    echo "⚠️  WARNING: Disk usage over 80%"
else
    echo "✅ Disk usage: Normal ($DISK_USAGE%)"
fi

# Show largest directories
echo ""
echo "Largest directories:"
ssh root@83.172.136.127 "du -h /opt /var/log /tmp 2>/dev/null | sort -hr | head -10" || echo "Could not analyze directories"
```

## 2. Service Status Checks

### Application Services
```bash
echo "=== APPLICATION SERVICES ==="

# Check backend service
if ssh root@83.172.136.127 "systemctl is-active lumen-backend" >/dev/null 2>&1; then
    echo "✅ Backend Service: Running"
    
    # Get service details
    ssh root@83.172.136.127 "
        echo '   Status:' \$(systemctl is-active lumen-backend)
        echo '   Since:' \$(systemctl show lumen-backend --property=ActiveEnterTimestamp --value | cut -d' ' -f2-3)
        echo '   Memory:' \$(systemctl show lumen-backend --property=MemoryCurrent --value | numfmt --to=iec)
    " 2>/dev/null
else
    echo "❌ Backend Service: Not running"
    echo "   Check logs: ssh root@83.172.136.127 'journalctl -u lumen-backend --no-pager -n 20'"
fi

# Check nginx
if ssh root@83.172.136.127 "systemctl is-active nginx" >/dev/null 2>&1; then
    echo "✅ Nginx: Running"
else
    echo "❌ Nginx: Not running"
fi

# Check PostgreSQL
if ssh root@83.172.136.127 "systemctl is-active postgresql" >/dev/null 2>&1; then
    echo "✅ PostgreSQL: Running"
else
    echo "❌ PostgreSQL: Not running"
fi
```

### Network Services
```bash
echo "=== NETWORK SERVICES ==="

# Check listening ports
echo "Services listening on ports:"
ssh root@83.172.136.127 "
    netstat -tlnp 2>/dev/null | grep -E ':(80|443|8080|5432)' | while read line; do
        port=\$(echo \$line | awk '{print \$4}' | sed 's/.*://')
        service=\$(echo \$line | awk '{print \$7}' | cut -d'/' -f2)
        echo '  Port '\$port': '\$service
    done
" 2>/dev/null || echo "Could not check network services"
```

## 3. Database Health

### PostgreSQL Status
```bash
echo "=== DATABASE HEALTH ==="

# Test database connection
DB_STATUS=$(ssh root@83.172.136.127 "
    sudo -u postgres psql lumen_db -c 'SELECT version();' -t 2>/dev/null | head -1
" 2>/dev/null)

if [ -n "$DB_STATUS" ]; then
    echo "✅ Database Connection: OK"
    echo "   Version:$DB_STATUS"
    
    # Get database statistics
    ssh root@83.172.136.127 "
        sudo -u postgres psql lumen_db -c '
            SELECT 
                schemaname,
                tablename,
                n_tup_ins as inserts,
                n_tup_upd as updates,
                n_tup_del as deletes
            FROM pg_stat_user_tables 
            WHERE n_tup_ins > 0 OR n_tup_upd > 0 OR n_tup_del > 0
            ORDER BY (n_tup_ins + n_tup_upd + n_tup_del) DESC 
            LIMIT 5;
        ' -q 2>/dev/null
    " | head -10
else
    echo "❌ Database Connection: Failed"
    echo "   Check PostgreSQL service and credentials"
fi

# Database size and performance
echo ""
echo "Database Statistics:"
ssh root@83.172.136.127 "
    sudo -u postgres psql lumen_db -c '
        SELECT 
            pg_size_pretty(pg_database_size(current_database())) as db_size,
            (SELECT count(*) FROM pg_stat_activity WHERE state = '\''active'\'') as active_connections;
    ' -t 2>/dev/null
" 2>/dev/null || echo "Could not get database statistics"
```

## 4. Application Health Checks

### API Endpoints
```bash
echo "=== APPLICATION HEALTH ==="

# Test public endpoints
PUBLIC_ENDPOINTS=(
    "https://lumenphotos.com"
    "https://lumenphotos.com/api/v1/health"
    "https://lumenphotos.com/docs"
)

for endpoint in "${PUBLIC_ENDPOINTS[@]}"; do
    if curl -f -s "$endpoint" >/dev/null 2>&1; then
        echo "✅ $endpoint: Responding"
    else
        echo "❌ $endpoint: Not responding"
    fi
done

# Check response times
echo ""
echo "Response Times:"
for endpoint in "${PUBLIC_ENDPOINTS[@]}"; do
    response_time=$(curl -o /dev/null -s -w "%{time_total}" "$endpoint" 2>/dev/null || echo "timeout")
    echo "   $endpoint: ${response_time}s"
done
```

### SSL Certificate Status
```bash
echo "=== SSL CERTIFICATE ==="

# Check SSL certificate
CERT_INFO=$(echo | openssl s_client -connect lumenphotos.com:443 -servername lumenphotos.com 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)

if [ -n "$CERT_INFO" ]; then
    echo "✅ SSL Certificate: Valid"
    echo "$CERT_INFO" | while read line; do
        echo "   $line"
    done
    
    # Check expiration
    NOT_AFTER=$(echo "$CERT_INFO" | grep notAfter | cut -d= -f2)
    EXPIRY_TIMESTAMP=$(date -d "$NOT_AFTER" +%s 2>/dev/null || echo "0")
    CURRENT_TIMESTAMP=$(date +%s)
    DAYS_UNTIL_EXPIRY=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))
    
    if [ "$DAYS_UNTIL_EXPIRY" -lt 30 ]; then
        echo "⚠️  Certificate expires in $DAYS_UNTIL_EXPIRY days - renewal needed"
    else
        echo "   Expires in $DAYS_UNTIL_EXPIRY days"
    fi
else
    echo "❌ SSL Certificate: Cannot verify"
fi
```

## 5. Security Status

### Security Checks
```bash
echo "=== SECURITY STATUS ==="

# Check for security updates
echo "Security updates available:"
ssh root@83.172.136.127 "
    apt list --upgradable 2>/dev/null | grep -i security | wc -l
" 2>/dev/null | xargs echo "   Available:"

# Check SSH authentication attempts
echo ""
echo "Recent SSH login attempts:"
ssh root@83.172.136.127 "
    grep 'sshd.*Failed' /var/log/auth.log 2>/dev/null | tail -5 | while read line; do
        echo '   '\$line
    done
" 2>/dev/null || echo "   Could not check auth logs"

# Check firewall status
echo ""
echo "Firewall status:"
ssh root@83.172.136.127 "ufw status" 2>/dev/null || echo "   UFW not configured"
```

## 6. Log Analysis

### Recent Errors
```bash
echo "=== RECENT LOGS ==="

# Application logs
echo "Backend errors (last 5):"
ssh root@83.172.136.127 "
    journalctl -u lumen-backend --no-pager -p err -n 5 --since '24 hours ago' 2>/dev/null
" | head -10 || echo "   No recent backend errors"

# Nginx errors
echo ""
echo "Nginx errors (last 5):"
ssh root@83.172.136.127 "
    tail -n 20 /var/log/nginx/error.log 2>/dev/null | grep ERROR | tail -5
" | head -10 || echo "   No recent nginx errors"

# System errors
echo ""
echo "System errors (last 3):"
ssh root@83.172.136.127 "
    journalctl -p err --no-pager -n 3 --since '24 hours ago' 2>/dev/null
" | head -6 || echo "   No recent system errors"
```

## 7. Performance Metrics

### Current Performance
```bash
echo "=== PERFORMANCE METRICS ==="

# Network statistics
echo "Network interface stats:"
ssh root@83.172.136.127 "
    cat /proc/net/dev | grep -E '(eth|ens)' | head -1 | awk '{print \"   RX: \" \$2 \" bytes, TX: \" \$10 \" bytes\"}'
" 2>/dev/null

# Load averages over time
echo ""
echo "Load average trend:"
ssh root@83.172.136.127 "
    uptime | awk -F'load average:' '{print \"   \" \$2}'
" 2>/dev/null

# Memory usage breakdown
echo ""
echo "Memory details:"
ssh root@83.172.136.127 "
    free -h | grep -E '(Mem|Swap)' | while read line; do
        echo '   '\$line
    done
" 2>/dev/null
```

## 8. Health Summary

### Generate Health Report
```bash
echo "=== HEALTH SUMMARY ==="

# Create summary
HEALTH_REPORT="logs/edis-health-$(date +%Y%m%d-%H%M%S).log"
mkdir -p logs

{
    echo "EDIS Server Health Report - $(date)"
    echo "========================================"
    echo "Server: 83.172.136.127"
    echo "Disk Usage: $DISK_USAGE%"
    echo "Services Status:"
    echo "  - Backend: $(ssh root@83.172.136.127 'systemctl is-active lumen-backend' 2>/dev/null)"
    echo "  - Nginx: $(ssh root@83.172.136.127 'systemctl is-active nginx' 2>/dev/null)"
    echo "  - PostgreSQL: $(ssh root@83.172.136.127 'systemctl is-active postgresql' 2>/dev/null)"
    echo ""
    echo "SSL Certificate: $DAYS_UNTIL_EXPIRY days until expiry"
    echo "System Load: $(ssh root@83.172.136.127 'cat /proc/loadavg' 2>/dev/null)"
    echo ""
    echo "Overall Status: $([ $DISK_USAGE -lt 80 ] && echo 'HEALTHY' || echo 'ATTENTION NEEDED')"
} > "$HEALTH_REPORT" 2>/dev/null

echo "✅ Health report saved to: $HEALTH_REPORT"
echo ""
echo "Quick Status:"
echo "  🖥️  Server: Available"
echo "  💾 Disk: $DISK_USAGE% used"
echo "  🔒 SSL: $DAYS_UNTIL_EXPIRY days until renewal"
echo "  🌐 Website: $(curl -f -s https://lumenphotos.com >/dev/null 2>&1 && echo 'Online' || echo 'Offline')"
```

## Automated Alerts

This command can be scheduled to run periodically and alert on:
- Disk usage > 80%
- SSL certificate < 30 days
- Service failures
- High system load
- Database connection issues

## Emergency Contacts

If critical issues are found:
1. Check system logs for details
2. Restart services if needed
3. Contact EDIS support if hardware issues
4. Consider scaling resources if performance issues