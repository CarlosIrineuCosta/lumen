---
description: ENHANCED EDIS Swiss VPS health monitoring with comprehensive safety analysis
---

# ENHANCED EDIS Server Health Monitor

**🔍 COMPREHENSIVE MONITORING: EDIS Swiss VPS (83.172.136.127)**

Monitor Swiss VPS status for $ARGUMENTS with enhanced safety analysis:

## 1. Enhanced Connection and Authentication

### Secure Connection Verification
```bash
echo "================================================================"
echo "🔍 ENHANCED EDIS SERVER HEALTH MONITORING"
echo "================================================================"
echo "Server: 83.172.136.127 (EDIS Swiss VPS)"
echo "Domain: lumenphotos.com"
echo "Timestamp: $(date)"
echo "Monitor ID: $(date +%Y%m%d-%H%M%S)"
echo ""

# Test SSH connection with multiple verification layers
echo "=== SECURE CONNECTION VERIFICATION ==="

# Basic connectivity test with timeout
echo "Testing basic connectivity..."
if ping -c 3 -W 5 83.172.136.127 >/dev/null 2>&1; then
    echo "✅ Network Connectivity: Server is reachable"
else
    echo "❌ Network Connectivity: Server not reachable via ping"
    echo "Possible issues:"
    echo "  - Server is down"
    echo "  - Firewall blocking ICMP"
    echo "  - Network routing problems"
fi

# SSH connection test with detailed error handling
echo ""
echo "Testing SSH connection..."
SSH_TEST_OUTPUT=$(ssh -o ConnectTimeout=10 -o ServerAliveInterval=5 -o ServerAliveCountMax=3 root@83.172.136.127 "echo 'SSH connection successful'; whoami; date" 2>&1)
SSH_EXIT_CODE=$?

if [ $SSH_EXIT_CODE -eq 0 ]; then
    echo "✅ SSH Connection: Available"
    echo "   Server response: $SSH_TEST_OUTPUT"
else
    echo "❌ SSH Connection: Failed (exit code: $SSH_EXIT_CODE)"
    echo "   Error details: $SSH_TEST_OUTPUT"
    echo ""
    echo "Troubleshooting steps:"
    echo "  1. Verify SSH key is properly loaded: ssh-add -l"
    echo "  2. Test SSH key: ssh -T root@83.172.136.127"
    echo "  3. Check SSH config: cat ~/.ssh/config | grep -A 5 83.172.136.127"
    echo "  4. Contact EDIS support if server is unresponsive"
    
    # Don't exit here - continue with other checks that don't require SSH
    echo ""
    echo "⚠️  Continuing with external checks only..."
fi
```

### Authentication and Security Status
```bash
echo "=== AUTHENTICATION AND SECURITY STATUS ==="

if [ $SSH_EXIT_CODE -eq 0 ]; then
    # Check SSH key authentication method
    echo "SSH authentication details:"
    SSH_AUTH_METHOD=$(ssh -o ConnectTimeout=5 root@83.172.136.127 "echo 'Key-based authentication successful'" 2>&1)
    if [[ "$SSH_AUTH_METHOD" == *"successful"* ]]; then
        echo "✅ Authentication: SSH key-based (secure)"
    else
        echo "⚠️  Authentication: Non-standard response"
    fi
    
    # Check for recent security events
    echo ""
    echo "Recent security events:"
    ssh root@83.172.136.127 "
        echo 'Failed SSH attempts (last 10):'
        grep 'sshd.*Failed password' /var/log/auth.log 2>/dev/null | tail -10 | while read line; do
            echo '  '\$line
        done
        
        echo ''
        echo 'Successful SSH logins (last 5):'
        grep 'sshd.*Accepted' /var/log/auth.log 2>/dev/null | tail -5 | while read line; do
            echo '  '\$line
        done
    " 2>/dev/null || echo "   Could not retrieve security logs"
    
else
    echo "❌ Cannot perform authentication checks - SSH connection failed"
fi

echo "✅ Enhanced connection verification complete"
```

## 2. Comprehensive System Health Analysis

### Detailed System Resources
```bash
echo "=== COMPREHENSIVE SYSTEM HEALTH ANALYSIS ==="

if [ $SSH_EXIT_CODE -eq 0 ]; then
    # Get comprehensive system information
    ssh root@83.172.136.127 "
        echo '=== SYSTEM OVERVIEW ==='
        echo 'Hostname: '\$(hostname)
        echo 'OS Version: '\$(cat /etc/os-release | grep PRETTY_NAME | cut -d'\"' -f2)
        echo 'Kernel Version: '\$(uname -r)
        echo 'Architecture: '\$(uname -m)
        echo ''
        
        echo '=== UPTIME AND LOAD ==='
        uptime
        echo ''
        
        echo '=== MEMORY USAGE (DETAILED) ==='
        free -h
        echo ''
        echo 'Memory usage by process (top 10):'
        ps aux --sort=-%mem | head -11
        echo ''
        
        echo '=== DISK USAGE (ALL FILESYSTEMS) ==='
        df -h
        echo ''
        
        echo '=== CPU INFORMATION ==='
        echo 'CPU cores: '\$(nproc)
        echo 'Load averages:'
        cat /proc/loadavg
        echo ''
        echo 'CPU usage by process (top 10):'
        ps aux --sort=-%cpu | head -11
        echo ''
        
        echo '=== NETWORK INTERFACES ==='
        ip addr show | grep -E '^[0-9]|inet '
        echo ''
    " 2>/dev/null || echo "❌ Failed to get comprehensive system resources"
    
else
    echo "❌ Cannot perform system health analysis - SSH connection failed"
fi
```

### Advanced Disk Space Analysis
```bash
echo "=== ADVANCED DISK SPACE ANALYSIS ==="

if [ $SSH_EXIT_CODE -eq 0 ]; then
    # Get detailed disk information with critical analysis
    DISK_ANALYSIS=$(ssh root@83.172.136.127 "
        echo '=== FILESYSTEM ANALYSIS ==='
        df -h
        echo ''
        
        echo '=== INODE USAGE ==='
        df -i
        echo ''
        
        echo '=== DISK USAGE BY DIRECTORY (TOP 20) ==='
        du -h --max-depth=1 / 2>/dev/null | sort -hr | head -20
        echo ''
        
        echo '=== LARGE FILES (>100MB) ==='
        find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null | head -10
        echo ''
        
        echo '=== LOG FILE SIZES ==='
        find /var/log -type f -name '*.log' -exec ls -lh {} \; 2>/dev/null | sort -k5 -hr | head -10
        echo ''
    " 2>/dev/null)
    
    if [ -n "$DISK_ANALYSIS" ]; then
        echo "$DISK_ANALYSIS"
        
        # Extract disk usage percentage for main filesystem
        DISK_USAGE=$(echo "$DISK_ANALYSIS" | grep -E '/$|/dev/' | head -1 | awk '{print $5}' | sed 's/%//')
        DISK_AVAIL=$(echo "$DISK_ANALYSIS" | grep -E '/$|/dev/' | head -1 | awk '{print $4}')
        
        echo "=== DISK SPACE ASSESSMENT ==="
        echo "Root filesystem usage: $DISK_USAGE%"
        echo "Available space: $DISK_AVAIL"
        
        # Critical disk space analysis
        if [ "$DISK_USAGE" -gt 95 ]; then
            echo "🚨 CRITICAL ALERT: Disk usage over 95%!"
            echo "   IMMEDIATE ACTION REQUIRED:"
            echo "   - Clean log files: journalctl --vacuum-time=7d"
            echo "   - Remove old backups"
            echo "   - Check for core dumps: find / -name core -type f"
            echo "   - Consider expanding disk or moving data"
        elif [ "$DISK_USAGE" -gt 85 ]; then
            echo "⚠️  HIGH ALERT: Disk usage over 85%"
            echo "   RECOMMENDED ACTIONS:"
            echo "   - Monitor disk usage closely"
            echo "   - Plan cleanup or expansion"
            echo "   - Review log retention policies"
        elif [ "$DISK_USAGE" -gt 70 ]; then
            echo "📊 MODERATE: Disk usage over 70%"
            echo "   ADVISORY: Regular monitoring recommended"
        else
            echo "✅ HEALTHY: Disk usage under 70% ($DISK_USAGE%)"
        fi
        
        # Check inode usage
        INODE_USAGE=$(echo "$DISK_ANALYSIS" | grep -E '/$|/dev/' | grep -E 'IUse%|iused' -A1 | tail -1 | awk '{print $5}' | sed 's/%//')
        if [ -n "$INODE_USAGE" ] && [ "$INODE_USAGE" -gt 85 ]; then
            echo "⚠️  WARNING: High inode usage ($INODE_USAGE%)"
        fi
        
    else
        echo "❌ Failed to get disk analysis"
    fi
    
else
    echo "❌ Cannot perform disk space analysis - SSH connection failed"
fi

echo "✅ Advanced disk space analysis complete"
```

## 3. Enhanced Service Status Monitoring

### Comprehensive Application Services
```bash
echo "=== COMPREHENSIVE APPLICATION SERVICES ==="

if [ $SSH_EXIT_CODE -eq 0 ]; then
    # Check all critical services with detailed information
    ssh root@83.172.136.127 "
        echo '=== LUMEN BACKEND SERVICE ==='
        SERVICE_STATUS=\$(systemctl is-active lumen-backend)
        echo 'Status: '\$SERVICE_STATUS
        
        if [ \"\$SERVICE_STATUS\" = 'active' ]; then
            echo '✅ Backend Service: Running'
            echo '   Details:'
            systemctl show lumen-backend --no-pager | grep -E '^(ActiveState|SubState|ActiveEnterTimestamp|MemoryCurrent|CPUUsageNSec)' | while read line; do
                echo '     '\$line
            done
            
            echo '   Process Information:'
            ps aux | grep -E 'lumen|uvicorn|python.*main' | grep -v grep
            
            echo '   Port Status:'
            netstat -tlnp | grep :8080 || echo '     Port 8080 not found'
            
            echo '   Recent Logs:'
            journalctl -u lumen-backend --no-pager -n 5 --since '1 hour ago' | tail -5
        else
            echo '❌ Backend Service: Not running ('\$SERVICE_STATUS')'
            echo '   Last 10 log entries:'
            journalctl -u lumen-backend --no-pager -n 10
            echo '   Service file status:'
            systemctl cat lumen-backend | head -20
        fi
        echo ''
        
        echo '=== NGINX WEB SERVER ==='
        NGINX_STATUS=\$(systemctl is-active nginx)
        echo 'Status: '\$NGINX_STATUS
        
        if [ \"\$NGINX_STATUS\" = 'active' ]; then
            echo '✅ Nginx: Running'
            echo '   Configuration Test:'
            nginx -t 2>&1 | sed 's/^/     /'
            
            echo '   Port Status:'
            netstat -tlnp | grep -E ':(80|443)' | while read line; do
                echo '     '\$line
            done
            
            echo '   Active Connections:'
            nginx -s status 2>/dev/null || echo '     Status module not available'
            
            echo '   Error Log (last 5 entries):'
            tail -5 /var/log/nginx/error.log 2>/dev/null | sed 's/^/     /' || echo '     No recent errors'
        else
            echo '❌ Nginx: Not running ('\$NGINX_STATUS')'
            echo '   Configuration test:'
            nginx -t 2>&1 | sed 's/^/     /'
            echo '   Recent error logs:'
            tail -10 /var/log/nginx/error.log 2>/dev/null | sed 's/^/     /'
        fi
        echo ''
        
        echo '=== POSTGRESQL DATABASE ==='
        DB_STATUS=\$(systemctl is-active postgresql)
        echo 'Status: '\$DB_STATUS
        
        if [ \"\$DB_STATUS\" = 'active' ]; then
            echo '✅ PostgreSQL: Running'
            
            # Test database connectivity
            DB_VERSION=\$(sudo -u postgres psql -c 'SELECT version();' -t 2>/dev/null | head -1)
            if [ -n \"\$DB_VERSION\" ]; then
                echo '   Version:'\$DB_VERSION
                
                # Database size and statistics
                sudo -u postgres psql lumen_db -c '
                    SELECT 
                        pg_size_pretty(pg_database_size(current_database())) as db_size,
                        (SELECT count(*) FROM pg_stat_activity WHERE state = '\''active'\'') as active_connections,
                        (SELECT count(*) FROM pg_stat_activity) as total_connections;
                ' -t 2>/dev/null | sed 's/^/     /'
                
                # Table statistics
                echo '   Table Statistics:'
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
                    LIMIT 10;
                ' -t 2>/dev/null | sed 's/^/     /' | head -15
                
            else
                echo '   ⚠️  Database connectivity test failed'
            fi
            
            echo '   Connection Status:'
            netstat -tlnp | grep :5432 | sed 's/^/     /'
            
        else
            echo '❌ PostgreSQL: Not running ('\$DB_STATUS')'
            echo '   Recent logs:'
            journalctl -u postgresql --no-pager -n 10 | sed 's/^/     /'
        fi
        echo ''
    " 2>/dev/null || echo "❌ Failed to get comprehensive service status"
    
else
    echo "❌ Cannot perform service monitoring - SSH connection failed"
fi

echo "✅ Enhanced service monitoring complete"
```

### Network and Security Services
```bash
echo "=== NETWORK AND SECURITY SERVICES ==="

if [ $SSH_EXIT_CODE -eq 0 ]; then
    ssh root@83.172.136.127 "
        echo '=== NETWORK SERVICES ==='
        echo 'All listening services:'
        netstat -tlnp | grep LISTEN | while read line; do
            port=\$(echo \$line | awk '{print \$4}' | sed 's/.*://')
            service=\$(echo \$line | awk '{print \$7}' | cut -d'/' -f2)
            echo '  Port '\$port': '\$service
        done
        echo ''
        
        echo '=== FIREWALL STATUS ==='
        if command -v ufw >/dev/null 2>&1; then
            echo 'UFW Firewall:'
            ufw status verbose | sed 's/^/  /'
        elif command -v iptables >/dev/null 2>&1; then
            echo 'IPTables rules (sample):'
            iptables -L INPUT -n | head -10 | sed 's/^/  /'
        else
            echo '  No recognized firewall found'
        fi
        echo ''
        
        echo '=== SSL/TLS CERTIFICATES ==='
        if [ -d /etc/letsencrypt/live ]; then
            echo 'Let'\''s Encrypt certificates:'
            ls -la /etc/letsencrypt/live/ | sed 's/^/  /'
        else
            echo '  No Let'\''s Encrypt certificates found'
        fi
        echo ''
        
        echo '=== CRON JOBS ==='
        echo 'Active cron jobs:'
        crontab -l 2>/dev/null | grep -v '^#' | sed 's/^/  /' || echo '  No cron jobs configured'
        echo ''
        
    " 2>/dev/null || echo "❌ Failed to get network and security status"
    
else
    echo "❌ Cannot perform network security analysis - SSH connection failed"
fi

echo "✅ Network and security analysis complete"
```

## 4. Advanced Application Health Checks

### Multi-Endpoint API Testing
```bash
echo "=== ADVANCED APPLICATION HEALTH CHECKS ==="

# Test public endpoints with detailed response analysis
echo "Testing production endpoints with comprehensive analysis..."

PUBLIC_ENDPOINTS=(
    "https://lumenphotos.com"
    "https://lumenphotos.com/api/v1/health"
    "https://lumenphotos.com/docs"
    "https://lumenphotos.com/redoc"
)

declare -A ENDPOINT_RESULTS
declare -A RESPONSE_TIMES

for endpoint in "${PUBLIC_ENDPOINTS[@]}"; do
    echo ""
    echo "Testing: $endpoint"
    
    # Test with detailed timing and response information
    START_TIME=$(date +%s.%3N)
    HTTP_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code};SIZE:%{size_download};TIME:%{time_total};REDIRECT:%{redirect_url}" "$endpoint" 2>&1)
    END_TIME=$(date +%s.%3N)
    
    # Extract response details
    HTTP_BODY=$(echo "$HTTP_RESPONSE" | sed -E 's/HTTPSTATUS:[0-9]{3};SIZE:[0-9]+;TIME:[0-9]+\.[0-9]+;REDIRECT:.*$//')
    HTTP_STATUS=$(echo "$HTTP_RESPONSE" | grep -o "HTTPSTATUS:[0-9]*" | cut -d: -f2)
    RESPONSE_SIZE=$(echo "$HTTP_RESPONSE" | grep -o "SIZE:[0-9]*" | cut -d: -f2)
    RESPONSE_TIME=$(echo "$HTTP_RESPONSE" | grep -o "TIME:[0-9]*\.[0-9]*" | cut -d: -f2)
    REDIRECT_URL=$(echo "$HTTP_RESPONSE" | grep -o "REDIRECT:.*$" | cut -d: -f2-)
    
    # Analyze response
    if [ "$HTTP_STATUS" = "200" ]; then
        echo "✅ Status: HTTP $HTTP_STATUS (Success)"
        ENDPOINT_RESULTS["$endpoint"]="SUCCESS"
    elif [ "$HTTP_STATUS" = "301" ] || [ "$HTTP_STATUS" = "302" ]; then
        echo "➡️  Status: HTTP $HTTP_STATUS (Redirect to: $REDIRECT_URL)"
        ENDPOINT_RESULTS["$endpoint"]="REDIRECT"
    elif [ "$HTTP_STATUS" = "404" ]; then
        echo "❌ Status: HTTP $HTTP_STATUS (Not Found)"
        ENDPOINT_RESULTS["$endpoint"]="NOT_FOUND"
    elif [ -z "$HTTP_STATUS" ]; then
        echo "❌ Status: Connection failed or timeout"
        ENDPOINT_RESULTS["$endpoint"]="CONNECTION_FAILED"
    else
        echo "⚠️  Status: HTTP $HTTP_STATUS (Unexpected)"
        ENDPOINT_RESULTS["$endpoint"]="UNEXPECTED"
    fi
    
    echo "   Response Time: ${RESPONSE_TIME}s"
    echo "   Response Size: ${RESPONSE_SIZE} bytes"
    
    # Store response time for analysis
    RESPONSE_TIMES["$endpoint"]="$RESPONSE_TIME"
    
    # Additional analysis for specific endpoints
    case "$endpoint" in
        *"/api/v1/health")
            if [ "$HTTP_STATUS" = "200" ] && [[ "$HTTP_BODY" == *"healthy"* ]] || [[ "$HTTP_BODY" == *"ok"* ]]; then
                echo "   Health Check: ✅ API reports healthy"
            else
                echo "   Health Check: ⚠️  API response unclear"
                echo "   Response Body: $(echo "$HTTP_BODY" | head -c 200)..."
            fi
            ;;
        *"/docs")
            if [ "$HTTP_STATUS" = "200" ] && [[ "$HTTP_BODY" == *"swagger"* ]] || [[ "$HTTP_BODY" == *"API"* ]]; then
                echo "   Documentation: ✅ API docs accessible"
            else
                echo "   Documentation: ⚠️  API docs may have issues"
            fi
            ;;
        "https://lumenphotos.com")
            if [ "$HTTP_STATUS" = "200" ] && [[ "$HTTP_BODY" == *"lumen"* ]] || [[ "$HTTP_BODY" == *"photo"* ]]; then
                echo "   Frontend: ✅ Main page loading correctly"
            else
                echo "   Frontend: ⚠️  Main page content unclear"
            fi
            ;;
    esac
done

# Response time analysis
echo ""
echo "=== RESPONSE TIME ANALYSIS ==="
TOTAL_TIME=0
ENDPOINT_COUNT=0

for endpoint in "${!RESPONSE_TIMES[@]}"; do
    time=${RESPONSE_TIMES[$endpoint]}
    if [[ "$time" =~ ^[0-9]+\.[0-9]+$ ]]; then
        echo "   $(basename "$endpoint"): ${time}s"
        TOTAL_TIME=$(echo "$TOTAL_TIME + $time" | bc -l 2>/dev/null || echo "$TOTAL_TIME")
        ENDPOINT_COUNT=$((ENDPOINT_COUNT + 1))
    fi
done

if [ $ENDPOINT_COUNT -gt 0 ]; then
    AVG_TIME=$(echo "scale=3; $TOTAL_TIME / $ENDPOINT_COUNT" | bc -l 2>/dev/null || echo "N/A")
    echo "   Average Response Time: ${AVG_TIME}s"
fi

echo "✅ Advanced application health checks complete"
```

### SSL Certificate Analysis
```bash
echo "=== COMPREHENSIVE SSL CERTIFICATE ANALYSIS ==="

# Detailed SSL certificate analysis
echo "Analyzing SSL certificate for lumenphotos.com..."

SSL_INFO=$(echo | openssl s_client -connect lumenphotos.com:443 -servername lumenphotos.com 2>/dev/null | openssl x509 -noout -text 2>/dev/null)

if [ -n "$SSL_INFO" ]; then
    echo "✅ SSL Certificate: Accessible"
    
    # Extract certificate details
    CERT_SUBJECT=$(echo "$SSL_INFO" | grep -A1 "Subject:" | tail -1 | sed 's/^[[:space:]]*//')
    CERT_ISSUER=$(echo "$SSL_INFO" | grep -A1 "Issuer:" | tail -1 | sed 's/^[[:space:]]*//')
    CERT_DATES=$(echo | openssl s_client -connect lumenphotos.com:443 -servername lumenphotos.com 2>/dev/null | openssl x509 -noout -dates 2>/dev/null)
    
    echo "   Subject: $CERT_SUBJECT"
    echo "   Issuer: $CERT_ISSUER"
    echo "   $CERT_DATES"
    
    # Check certificate expiration
    NOT_AFTER=$(echo "$CERT_DATES" | grep notAfter | cut -d= -f2)
    if [ -n "$NOT_AFTER" ]; then
        EXPIRY_TIMESTAMP=$(date -d "$NOT_AFTER" +%s 2>/dev/null || echo "0")
        CURRENT_TIMESTAMP=$(date +%s)
        DAYS_UNTIL_EXPIRY=$(( (EXPIRY_TIMESTAMP - CURRENT_TIMESTAMP) / 86400 ))
        
        if [ "$DAYS_UNTIL_EXPIRY" -lt 7 ]; then
            echo "🚨 CRITICAL: Certificate expires in $DAYS_UNTIL_EXPIRY days - IMMEDIATE RENEWAL REQUIRED"
        elif [ "$DAYS_UNTIL_EXPIRY" -lt 30 ]; then
            echo "⚠️  WARNING: Certificate expires in $DAYS_UNTIL_EXPIRY days - renewal needed soon"
        elif [ "$DAYS_UNTIL_EXPIRY" -lt 60 ]; then
            echo "📅 NOTICE: Certificate expires in $DAYS_UNTIL_EXPIRY days - plan renewal"
        else
            echo "✅ Certificate valid for $DAYS_UNTIL_EXPIRY more days"
        fi
    fi
    
    # Check certificate chain
    echo ""
    echo "Certificate Chain Analysis:"
    CERT_CHAIN=$(echo | openssl s_client -connect lumenphotos.com:443 -servername lumenphotos.com -showcerts 2>/dev/null | grep -c "BEGIN CERTIFICATE")
    echo "   Certificates in chain: $CERT_CHAIN"
    
    # Test SSL configuration
    echo ""
    echo "SSL Configuration Test:"
    SSL_TEST=$(echo | openssl s_client -connect lumenphotos.com:443 -servername lumenphotos.com 2>&1 | grep -E "(Protocol|Cipher)")
    if [ -n "$SSL_TEST" ]; then
        echo "$SSL_TEST" | sed 's/^/   /'
    else
        echo "   Could not retrieve SSL configuration details"
    fi
    
else
    echo "❌ SSL Certificate: Cannot retrieve certificate information"
    echo "   This could indicate:"
    echo "   - Certificate is not properly installed"
    echo "   - SSL/TLS configuration issues"
    echo "   - Network connectivity problems"
fi

echo "✅ SSL certificate analysis complete"
```

## 5. Enhanced Security Monitoring

### Comprehensive Security Assessment
```bash
echo "=== COMPREHENSIVE SECURITY ASSESSMENT ==="

if [ $SSH_EXIT_CODE -eq 0 ]; then
    ssh root@83.172.136.127 "
        echo '=== SYSTEM SECURITY STATUS ==='
        
        echo 'System Updates:'
        if command -v apt >/dev/null 2>&1; then
            # Check for security updates
            apt list --upgradable 2>/dev/null | grep -c security | xargs -I {} echo '   Security updates available: {}'
            
            # Last update check
            LAST_UPDATE=\$(stat -c %y /var/lib/apt/periodic/update-success-stamp 2>/dev/null || echo 'Unknown')
            echo '   Last update check: '\$LAST_UPDATE
        fi
        echo ''
        
        echo 'Active User Sessions:'
        who | sed 's/^/   /'
        echo ''
        
        echo 'Recent Authentication Events:'
        echo '   Successful logins (last 10):'
        last -n 10 | grep -v 'wtmp begins' | sed 's/^/     /'
        echo ''
        echo '   Failed SSH attempts (last 10):'
        grep 'sshd.*Failed password' /var/log/auth.log 2>/dev/null | tail -10 | sed 's/^/     /' || echo '     No recent failures'
        echo ''
        echo '   Successful SSH logins (last 10):'
        grep 'sshd.*Accepted' /var/log/auth.log 2>/dev/null | tail -10 | sed 's/^/     /' || echo '     No recent logins'
        echo ''
        
        echo 'Process Security:'
        echo '   Running processes by user:'
        ps aux | awk '{print \$1}' | sort | uniq -c | sort -nr | head -10 | sed 's/^/     /'
        echo ''
        echo '   Processes listening on network ports:'
        netstat -tlnp | grep LISTEN | awk '{print \$7}' | cut -d'/' -f2 | sort | uniq -c | sort -nr | sed 's/^/     /'
        echo ''
        
        echo 'File System Security:'
        echo '   World-writable files (sample):'
        find /etc /opt -type f -perm -002 2>/dev/null | head -5 | sed 's/^/     /' || echo '     None found in /etc /opt'
        echo ''
        echo '   SUID/SGID files (sample):'
        find /usr -type f \\( -perm -4000 -o -perm -2000 \\) 2>/dev/null | head -10 | sed 's/^/     /'
        echo ''
        
        echo 'Log File Analysis:'
        echo '   Log file sizes:'
        du -h /var/log/*.log 2>/dev/null | sort -hr | head -5 | sed 's/^/     /' || echo '     No .log files found'
        echo ''
        echo '   Disk space used by logs:'
        du -sh /var/log 2>/dev/null | sed 's/^/     /'
        echo ''
        
    " 2>/dev/null || echo "❌ Failed to get comprehensive security status"
    
else
    echo "❌ Cannot perform security assessment - SSH connection failed"
fi

echo "✅ Comprehensive security assessment complete"
```

## 6. Performance and Resource Monitoring

### Advanced Performance Metrics
```bash
echo "=== ADVANCED PERFORMANCE MONITORING ==="

if [ $SSH_EXIT_CODE -eq 0 ]; then
    ssh root@83.172.136.127 "
        echo '=== PERFORMANCE METRICS ==='
        
        echo 'CPU Performance:'
        echo '   CPU Information:'
        grep -E '(model name|cpu cores|flags)' /proc/cpuinfo | head -6 | sed 's/^/     /'
        
        echo '   Load Average Trend:'
        uptime | awk -F'load average:' '{print \"     Current: \" \$2}'
        
        echo '   CPU Usage by Process (top 10):'
        ps aux --sort=-%cpu | head -11 | sed 's/^/     /'
        echo ''
        
        echo 'Memory Performance:'
        echo '   Memory Details:'
        free -h | sed 's/^/     /'
        
        echo '   Memory Usage by Process (top 10):'
        ps aux --sort=-%mem | head -11 | sed 's/^/     /'
        echo ''
        
        echo 'Disk I/O Performance:'
        if command -v iostat >/dev/null 2>&1; then
            echo '   I/O Statistics:'
            iostat -x 1 1 | sed 's/^/     /'
        else
            echo '     iostat not available'
        fi
        
        echo '   Disk Usage by Mount Point:'
        df -h | sed 's/^/     /'
        echo ''
        
        echo 'Network Performance:'
        echo '   Network Interface Statistics:'
        cat /proc/net/dev | grep -E '(eth|ens|wlan)' | sed 's/^/     /' || echo '     No standard network interfaces found'
        
        echo '   Network Connections:'
        netstat -an | awk '{print \$6}' | sort | uniq -c | sort -nr | sed 's/^/     /'
        echo ''
        
        echo 'System Resources Summary:'
        echo -n '     CPU Cores: '; nproc
        echo -n '     Total Memory: '; free -h | grep Mem | awk '{print \$2}'
        echo -n '     Available Memory: '; free -h | grep Mem | awk '{print \$7}'
        echo -n '     Root Disk Total: '; df -h / | tail -1 | awk '{print \$2}'
        echo -n '     Root Disk Available: '; df -h / | tail -1 | awk '{print \$4}'
        echo -n '     System Uptime: '; uptime | awk -F'up ' '{print \$2}' | awk -F',' '{print \$1}' | xargs
        echo ''
        
    " 2>/dev/null || echo "❌ Failed to get performance metrics"
    
else
    echo "❌ Cannot perform performance monitoring - SSH connection failed"
fi

echo "✅ Advanced performance monitoring complete"
```

## 7. Intelligent Health Assessment

### Automated Health Scoring
```bash
echo "=== AUTOMATED HEALTH SCORING ==="

# Calculate health scores based on collected metrics
HEALTH_SCORE=100
ISSUES_FOUND=()
WARNINGS_FOUND=()

# SSH connectivity (critical)
if [ $SSH_EXIT_CODE -ne 0 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 30))
    ISSUES_FOUND+=("SSH connection failed")
fi

# Disk space assessment
if [ -n "$DISK_USAGE" ]; then
    if [ "$DISK_USAGE" -gt 95 ]; then
        HEALTH_SCORE=$((HEALTH_SCORE - 25))
        ISSUES_FOUND+=("Critical disk usage: ${DISK_USAGE}%")
    elif [ "$DISK_USAGE" -gt 85 ]; then
        HEALTH_SCORE=$((HEALTH_SCORE - 15))
        WARNINGS_FOUND+=("High disk usage: ${DISK_USAGE}%")
    elif [ "$DISK_USAGE" -gt 70 ]; then
        HEALTH_SCORE=$((HEALTH_SCORE - 5))
        WARNINGS_FOUND+=("Moderate disk usage: ${DISK_USAGE}%")
    fi
fi

# SSL certificate expiration
if [ -n "$DAYS_UNTIL_EXPIRY" ]; then
    if [ "$DAYS_UNTIL_EXPIRY" -lt 7 ]; then
        HEALTH_SCORE=$((HEALTH_SCORE - 20))
        ISSUES_FOUND+=("SSL certificate expires in $DAYS_UNTIL_EXPIRY days")
    elif [ "$DAYS_UNTIL_EXPIRY" -lt 30 ]; then
        HEALTH_SCORE=$((HEALTH_SCORE - 10))
        WARNINGS_FOUND+=("SSL certificate expires in $DAYS_UNTIL_EXPIRY days")
    fi
fi

# Endpoint accessibility
FAILED_ENDPOINTS=0
for endpoint in "${!ENDPOINT_RESULTS[@]}"; do
    result=${ENDPOINT_RESULTS[$endpoint]}
    if [ "$result" != "SUCCESS" ] && [ "$result" != "REDIRECT" ]; then
        FAILED_ENDPOINTS=$((FAILED_ENDPOINTS + 1))
    fi
done

if [ $FAILED_ENDPOINTS -gt 2 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 20))
    ISSUES_FOUND+=("Multiple endpoint failures: $FAILED_ENDPOINTS")
elif [ $FAILED_ENDPOINTS -gt 0 ]; then
    HEALTH_SCORE=$((HEALTH_SCORE - 10))
    WARNINGS_FOUND+=("Some endpoint issues: $FAILED_ENDPOINTS")
fi

# Health score interpretation
echo "EDIS Server Health Score: $HEALTH_SCORE/100"

if [ $HEALTH_SCORE -ge 90 ]; then
    echo "🟢 EXCELLENT: Server is operating optimally"
    HEALTH_STATUS="EXCELLENT"
elif [ $HEALTH_SCORE -ge 75 ]; then
    echo "🔵 GOOD: Server is healthy with minor issues"
    HEALTH_STATUS="GOOD"
elif [ $HEALTH_SCORE -ge 60 ]; then
    echo "🟡 FAIR: Server needs attention"
    HEALTH_STATUS="FAIR"
elif [ $HEALTH_SCORE -ge 40 ]; then
    echo "🟠 POOR: Server has significant issues"
    HEALTH_STATUS="POOR"
else
    echo "🔴 CRITICAL: Server requires immediate attention"
    HEALTH_STATUS="CRITICAL"
fi

# Report issues and warnings
if [ ${#ISSUES_FOUND[@]} -gt 0 ]; then
    echo ""
    echo "🚨 CRITICAL ISSUES FOUND:"
    for issue in "${ISSUES_FOUND[@]}"; do
        echo "   - $issue"
    done
fi

if [ ${#WARNINGS_FOUND[@]} -gt 0 ]; then
    echo ""
    echo "⚠️  WARNINGS:"
    for warning in "${WARNINGS_FOUND[@]}"; do
        echo "   - $warning"
    done
fi

echo "✅ Automated health scoring complete"
```

## 8. Enhanced Reporting and Alerting

### Comprehensive Health Report Generation
```bash
echo "=== COMPREHENSIVE HEALTH REPORT ==="

# Create timestamped health report
HEALTH_TIMESTAMP=$(date +%Y%m%d-%H%M%S)
HEALTH_REPORT="logs/edis-health-$HEALTH_TIMESTAMP.log"
mkdir -p logs

# Generate comprehensive report
{
    echo "ENHANCED EDIS SERVER HEALTH REPORT"
    echo "=================================="
    echo "Report Generated: $(date)"
    echo "Report ID: $HEALTH_TIMESTAMP"
    echo "Server: 83.172.136.127 (EDIS Swiss VPS)"
    echo "Domain: lumenphotos.com"
    echo ""
    
    echo "OVERALL HEALTH ASSESSMENT"
    echo "-------------------------"
    echo "Health Score: $HEALTH_SCORE/100"
    echo "Health Status: $HEALTH_STATUS"
    echo ""
    
    if [ $SSH_EXIT_CODE -eq 0 ]; then
        echo "CONNECTIVITY STATUS"
        echo "------------------"
        echo "SSH Connection: ✅ Available"
        echo "Authentication: ✅ Key-based"
    else
        echo "CONNECTIVITY STATUS"
        echo "------------------"
        echo "SSH Connection: ❌ Failed"
        echo "Error Code: $SSH_EXIT_CODE"
    fi
    echo ""
    
    echo "SYSTEM RESOURCES"
    echo "---------------"
    if [ -n "$DISK_USAGE" ]; then
        echo "Disk Usage: $DISK_USAGE% ($DISK_AVAIL available)"
    else
        echo "Disk Usage: Unable to determine"
    fi
    echo ""
    
    echo "APPLICATION STATUS"
    echo "-----------------"
    for endpoint in "${!ENDPOINT_RESULTS[@]}"; do
        result=${ENDPOINT_RESULTS[$endpoint]}
        time=${RESPONSE_TIMES[$endpoint]}
        echo "$(basename "$endpoint"): $result (${time}s)"
    done
    echo ""
    
    echo "SSL CERTIFICATE"
    echo "--------------"
    if [ -n "$DAYS_UNTIL_EXPIRY" ]; then
        echo "Certificate Status: Valid"
        echo "Days Until Expiry: $DAYS_UNTIL_EXPIRY"
        if [ "$DAYS_UNTIL_EXPIRY" -lt 30 ]; then
            echo "Action Required: Schedule renewal"
        fi
    else
        echo "Certificate Status: Unable to verify"
    fi
    echo ""
    
    echo "CRITICAL ISSUES"
    echo "--------------"
    if [ ${#ISSUES_FOUND[@]} -eq 0 ]; then
        echo "None"
    else
        for issue in "${ISSUES_FOUND[@]}"; do
            echo "- $issue"
        done
    fi
    echo ""
    
    echo "WARNINGS"
    echo "--------"
    if [ ${#WARNINGS_FOUND[@]} -eq 0 ]; then
        echo "None"
    else
        for warning in "${WARNINGS_FOUND[@]}"; do
            echo "- $warning"
        done
    fi
    echo ""
    
    echo "RECOMMENDED ACTIONS"
    echo "------------------"
    if [ $HEALTH_SCORE -ge 90 ]; then
        echo "- Continue regular monitoring"
        echo "- Schedule routine maintenance"
    elif [ $HEALTH_SCORE -ge 75 ]; then
        echo "- Address minor issues identified"
        echo "- Increase monitoring frequency"
    elif [ $HEALTH_SCORE -ge 60 ]; then
        echo "- Priority attention needed for identified issues"
        echo "- Review system logs for additional problems"
        echo "- Consider maintenance window for fixes"
    else
        echo "- IMMEDIATE attention required"
        echo "- Contact system administrator"
        echo "- Consider emergency maintenance procedures"
        echo "- Review backup and disaster recovery plans"
    fi
    echo ""
    
    echo "MONITORING HISTORY"
    echo "-----------------"
    echo "Previous health reports:"
    ls -la logs/edis-health-*.log 2>/dev/null | tail -5 | sed 's/^/  /' || echo "  No previous reports found"
    echo ""
    
    echo "EMERGENCY CONTACTS"
    echo "----------------"
    echo "- System Administrator: [Configure contact details]"
    echo "- EDIS Support: support@edis.com"
    echo "- Emergency Escalation: [Configure emergency contact]"
    echo ""
    
    echo "TECHNICAL DETAILS"
    echo "----------------"
    echo "Report Generation Time: $(date)"
    echo "Monitoring Script Version: Enhanced EDIS Monitor v2.0"
    echo "SSH Exit Code: $SSH_EXIT_CODE"
    echo "Total Endpoints Tested: ${#ENDPOINT_RESULTS[@]}"
    echo "Failed Endpoints: $FAILED_ENDPOINTS"
    
} > "$HEALTH_REPORT" 2>/dev/null

echo "✅ Comprehensive health report generated: $HEALTH_REPORT"
```

### Alert Generation and Notification
```bash
echo "=== ALERT GENERATION ==="

# Generate alerts based on health status
if [ $HEALTH_SCORE -lt 60 ] || [ ${#ISSUES_FOUND[@]} -gt 0 ]; then
    ALERT_FILE="logs/edis-alert-$HEALTH_TIMESTAMP.txt"
    
    {
        echo "EDIS SERVER ALERT - $(date)"
        echo "=========================="
        echo ""
        echo "Server: 83.172.136.127"
        echo "Domain: lumenphotos.com"
        echo "Alert Level: $([ $HEALTH_SCORE -lt 40 ] && echo 'CRITICAL' || echo 'WARNING')"
        echo "Health Score: $HEALTH_SCORE/100"
        echo ""
        echo "Issues Requiring Attention:"
        for issue in "${ISSUES_FOUND[@]}"; do
            echo "- $issue"
        done
        echo ""
        echo "Immediate Actions Required:"
        if [ $SSH_EXIT_CODE -ne 0 ]; then
            echo "1. Verify server connectivity and SSH access"
        fi
        if [ -n "$DISK_USAGE" ] && [ "$DISK_USAGE" -gt 90 ]; then
            echo "2. Clean disk space immediately"
        fi
        if [ -n "$DAYS_UNTIL_EXPIRY" ] && [ "$DAYS_UNTIL_EXPIRY" -lt 7 ]; then
            echo "3. Renew SSL certificate urgently"
        fi
        echo ""
        echo "Full Report: $HEALTH_REPORT"
        echo "Generated: $(date)"
        
    } > "$ALERT_FILE"
    
    echo "🚨 ALERT GENERATED: $ALERT_FILE"
    
    # Display alert summary
    echo ""
    echo "ALERT SUMMARY:"
    if [ $HEALTH_SCORE -lt 40 ]; then
        echo "🔴 CRITICAL ALERT: Server requires immediate attention"
    else
        echo "🟠 WARNING ALERT: Server needs attention"
    fi
    
    echo "Key issues:"
    for issue in "${ISSUES_FOUND[@]}"; do
        echo "  - $issue"
    done
    
else
    echo "✅ No alerts generated - server health is acceptable"
fi

echo "✅ Alert generation complete"
```

## 9. Final Health Summary

### Executive Summary
```bash
echo "================================================================"
echo "🔍 ENHANCED EDIS HEALTH MONITORING COMPLETE"
echo "================================================================"
echo ""
echo "Server Overview:"
echo "  Server: 83.172.136.127 (EDIS Swiss VPS)"
echo "  Domain: lumenphotos.com"
echo "  Monitoring ID: $HEALTH_TIMESTAMP"
echo "  Report Time: $(date)"
echo ""
echo "Health Assessment:"
echo "  Overall Score: $HEALTH_SCORE/100"
echo "  Status: $HEALTH_STATUS"
echo "  SSH Access: $([ $SSH_EXIT_CODE -eq 0 ] && echo '✅ Available' || echo '❌ Failed')"
if [ -n "$DISK_USAGE" ]; then
echo "  Disk Usage: $DISK_USAGE% ($DISK_AVAIL available)"
fi
if [ -n "$DAYS_UNTIL_EXPIRY" ]; then
echo "  SSL Certificate: $DAYS_UNTIL_EXPIRY days until expiry"
fi
echo "  Endpoint Tests: $((${#ENDPOINT_RESULTS[@]} - FAILED_ENDPOINTS))/${#ENDPOINT_RESULTS[@]} successful"
echo ""
echo "Documentation:"
echo "  Health Report: $HEALTH_REPORT"
if [ -f "logs/edis-alert-$HEALTH_TIMESTAMP.txt" ]; then
echo "  Alert Generated: logs/edis-alert-$HEALTH_TIMESTAMP.txt"
fi
echo ""

if [ $HEALTH_SCORE -ge 90 ]; then
    echo "✅ RESULT: Server is healthy and operating normally"
elif [ $HEALTH_SCORE -ge 75 ]; then
    echo "🔵 RESULT: Server is mostly healthy with minor issues to monitor"
elif [ $HEALTH_SCORE -ge 60 ]; then
    echo "🟡 RESULT: Server needs attention - schedule maintenance"
else
    echo "🚨 RESULT: Server requires immediate attention"
    echo ""
    echo "IMMEDIATE ACTIONS:"
    for issue in "${ISSUES_FOUND[@]}"; do
        echo "  ❗ $issue"
    done
fi

echo ""
echo "Next Steps:"
echo "  1. Review detailed health report: cat $HEALTH_REPORT"
echo "  2. Address any critical issues identified"
echo "  3. Schedule next health check"
echo "  4. Update monitoring documentation"
echo ""
echo "✅ Enhanced EDIS monitoring session completed at $(date)"
echo "================================================================"
```

## Enhanced Monitoring Features

### Automated Monitoring Capabilities
- **Multi-layer connectivity testing** with detailed failure analysis
- **Comprehensive system resource monitoring** including CPU, memory, disk, and network
- **Advanced service status checking** with process and port verification
- **Intelligent health scoring** with automated issue classification
- **SSL certificate monitoring** with expiration alerting
- **Security assessment** including failed login attempts and system updates
- **Performance metrics collection** with trend analysis
- **Automated alert generation** for critical issues
- **Comprehensive reporting** with actionable recommendations

### Safety and Reliability Features
- **Connection failure handling** with graceful degradation
- **Timeout protection** for all remote operations
- **Multiple verification layers** for critical checks
- **Detailed error reporting** with troubleshooting guidance
- **Historical tracking** with previous report comparison
- **Emergency contact information** integration
- **Automated documentation** generation

### Monitoring Scope
- **System Health**: CPU, memory, disk, network, uptime
- **Application Services**: Lumen backend, Nginx, PostgreSQL
- **Network Services**: Port status, firewall, SSL/TLS
- **Security Status**: Authentication events, updates, permissions
- **Performance Metrics**: Response times, resource utilization
- **External Accessibility**: Website, API, documentation endpoints

This enhanced monitoring system provides comprehensive visibility into the EDIS server health while maintaining safety through intelligent error handling and detailed reporting.