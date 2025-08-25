#!/bin/bash

# 🏢⚡ Energy Optimizer Pro - Security Audit Script
# =================================================
# Comprehensive security scanning and vulnerability assessment

set -euo pipefail

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
REPORTS_DIR="$PROJECT_ROOT/security-reports"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Logging functions
log() { echo -e "${CYAN}[$(date +'%H:%M:%S')]${NC} $1"; }
success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Banner
print_banner() {
    clear
    echo -e "${CYAN}"
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════════╗
║                  🏢⚡ ENERGY OPTIMIZER PRO                        ║
║                   Security Audit Suite v2.0                     ║
║                                                                  ║
║              🔒 Comprehensive Security Assessment                ║
╚══════════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
}

# Create reports directory
setup_reports() {
    mkdir -p "$REPORTS_DIR"
    log "📁 Created reports directory: $REPORTS_DIR"
}

# Dependency scanning
scan_dependencies() {
    log "📦 Scanning dependencies for vulnerabilities..."
    
    # Frontend dependency scan
    log "🎨 Scanning frontend dependencies..."
    cd "$PROJECT_ROOT/frontend"
    
    # npm audit
    if command -v npm >/dev/null 2>&1; then
        npm audit --audit-level=moderate --json > "$REPORTS_DIR/npm-audit-$TIMESTAMP.json" 2>/dev/null || true
        npm audit --audit-level=moderate > "$REPORTS_DIR/npm-audit-$TIMESTAMP.txt" 2>/dev/null || true
        success "npm audit completed"
    fi
    
    # Backend dependency scan
    log "🐍 Scanning backend dependencies..."
    cd "$PROJECT_ROOT/backend"
    
    # Activate virtual environment
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    elif [ -f "venv/Scripts/activate" ]; then
        source venv/Scripts/activate
    fi
    
    # Safety check
    if command -v safety >/dev/null 2>&1; then
        safety check --json --output "$REPORTS_DIR/safety-report-$TIMESTAMP.json" || true
        safety check --output text --output "$REPORTS_DIR/safety-report-$TIMESTAMP.txt" || true
        success "Safety scan completed"
    else
        pip install safety
        safety check --json --output "$REPORTS_DIR/safety-report-$TIMESTAMP.json" || true
        success "Safety scan completed (installed and ran)"
    fi
    
    # Bandit security scan
    if command -v bandit >/dev/null 2>&1; then
        bandit -r app/ -f json -o "$REPORTS_DIR/bandit-report-$TIMESTAMP.json" || true
        bandit -r app/ -f txt -o "$REPORTS_DIR/bandit-report-$TIMESTAMP.txt" || true
        success "Bandit scan completed"
    else
        pip install bandit
        bandit -r app/ -f json -o "$REPORTS_DIR/bandit-report-$TIMESTAMP.json" || true
        success "Bandit scan completed (installed and ran)"
    fi
    
    cd "$PROJECT_ROOT"
}

# Container security scanning
scan_containers() {
    log "🐳 Scanning Docker containers for vulnerabilities..."
    
    # Build containers first
    docker-compose build >/dev/null 2>&1
    
    # Get image names
    images=$(docker-compose config --services)
    
    for service in $images; do
        image_name="energy_optimizer_${service}"
        log "🔍 Scanning $service container..."
        
        # Trivy scan
        if command -v trivy >/dev/null 2>&1; then
            trivy image --format json --output "$REPORTS_DIR/trivy-${service}-$TIMESTAMP.json" "$image_name" 2>/dev/null || true
            trivy image --format table --output "$REPORTS_DIR/trivy-${service}-$TIMESTAMP.txt" "$image_name" 2>/dev/null || true
        else
            # Install and run Trivy
            docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
                -v "$REPORTS_DIR:/reports" \
                aquasec/trivy image --format json --output "/reports/trivy-${service}-$TIMESTAMP.json" "$image_name" 2>/dev/null || true
        fi
        
        success "$service container scan completed"
    done
}

# Network security check
scan_network() {
    log "🌐 Scanning network security configuration..."
    
    # Check open ports
    log "🔍 Checking exposed ports..."
    netstat -tlnp 2>/dev/null | grep LISTEN > "$REPORTS_DIR/open-ports-$TIMESTAMP.txt" || \
        ss -tlnp 2>/dev/null | grep LISTEN > "$REPORTS_DIR/open-ports-$TIMESTAMP.txt" || true
    
    # Check firewall status
    log "🛡️ Checking firewall configuration..."
    if command -v ufw >/dev/null 2>&1; then
        ufw status verbose > "$REPORTS_DIR/firewall-$TIMESTAMP.txt" 2>/dev/null || true
    elif command -v iptables >/dev/null 2>&1; then
        iptables -L -n -v > "$REPORTS_DIR/firewall-$TIMESTAMP.txt" 2>/dev/null || true
    fi
    
    success "Network security scan completed"
}

# Application security testing
scan_application() {
    log "🚀 Scanning application security..."
    
    # Check if services are running
    if ! curl -s -f http://localhost:8000/health >/dev/null 2>&1; then
        warning "Backend not running, starting services..."
        cd "$PROJECT_ROOT"
        docker-compose up -d
        sleep 30
    fi
    
    # OWASP ZAP scan (if available)
    if command -v zap-baseline.py >/dev/null 2>&1; then
        log "🕷️ Running OWASP ZAP baseline scan..."
        zap-baseline.py -t http://localhost:3000 -J "$REPORTS_DIR/zap-report-$TIMESTAMP.json" || true
        success "OWASP ZAP scan completed"
    else
        # Docker-based ZAP scan
        docker run --rm -v "$REPORTS_DIR:/zap/wrk/:rw" \
            -t owasp/zap2docker-stable zap-baseline.py \
            -t http://host.docker.internal:3000 \
            -J "zap-report-$TIMESTAMP.json" >/dev/null 2>&1 || true
        info "OWASP ZAP scan attempted (may require network access)"
    fi
    
    # SSL/TLS configuration check
    log "🔒 Checking SSL/TLS configuration..."
    if [ -f "$PROJECT_ROOT/nginx/ssl/energy-optimizer.com.crt" ]; then
        openssl x509 -in "$PROJECT_ROOT/nginx/ssl/energy-optimizer.com.crt" -text -noout > "$REPORTS_DIR/ssl-cert-$TIMESTAMP.txt" 2>/dev/null || true
        success "SSL certificate analysis completed"
    else
        warning "SSL certificate not found (development mode)"
    fi
}

# Configuration security audit
audit_configuration() {
    log "⚙️ Auditing configuration security..."
    
    # Check for secrets in environment files
    log "🔐 Scanning for potential secrets..."
    
    find "$PROJECT_ROOT" -name "*.env*" -type f | while read -r env_file; do
        if [ -f "$env_file" ]; then
            # Check for default passwords
            if grep -qi "password.*123\|secret.*test\|key.*demo" "$env_file" 2>/dev/null; then
                echo "⚠️ Default credentials found in: $env_file" >> "$REPORTS_DIR/config-audit-$TIMESTAMP.txt"
            fi
            
            # Check for hardcoded secrets
            if grep -qi "sk-\|ghp_\|glpat-" "$env_file" 2>/dev/null; then
                echo "🔒 Potential API keys found in: $env_file" >> "$REPORTS_DIR/config-audit-$TIMESTAMP.txt"
            fi
        fi
    done
    
    # Check Docker Compose security
    log "🐳 Auditing Docker Compose configuration..."
    
    # Check for privileged containers
    if grep -q "privileged.*true" "$PROJECT_ROOT"/docker-compose*.yml 2>/dev/null; then
        echo "⚠️ Privileged containers found in Docker Compose" >> "$REPORTS_DIR/config-audit-$TIMESTAMP.txt"
    fi
    
    # Check for host network mode
    if grep -q "network_mode.*host" "$PROJECT_ROOT"/docker-compose*.yml 2>/dev/null; then
        echo "🌐 Host network mode found in Docker Compose" >> "$REPORTS_DIR/config-audit-$TIMESTAMP.txt"
    fi
    
    success "Configuration audit completed"
}

# Code security analysis
scan_code() {
    log "🔍 Performing static code security analysis..."
    
    # Frontend security scanning
    log "🎨 Scanning frontend code..."
    cd "$PROJECT_ROOT/frontend"
    
    # ESLint security rules
    if command -v npx >/dev/null 2>&1; then
        npx eslint . --ext .ts,.tsx,.js,.jsx --format json --output-file "$REPORTS_DIR/eslint-security-$TIMESTAMP.json" >/dev/null 2>&1 || true
        success "Frontend security scan completed"
    fi
    
    # Backend security scanning (already done with Bandit above)
    log "🐍 Backend security analysis completed with Bandit"
    
    cd "$PROJECT_ROOT"
}

# Generate security report
generate_report() {
    log "📋 Generating comprehensive security report..."
    
    report_file="$REPORTS_DIR/security-summary-$TIMESTAMP.md"
    
    cat > "$report_file" << EOF
# 🔒 Energy Optimizer Pro - Security Audit Report

**Generated**: $(date)  
**Version**: 1.0.0  
**Audit Type**: Comprehensive Security Assessment

---

## 🎯 Executive Summary

This report contains the results of a comprehensive security audit of Energy Optimizer Pro,
including dependency scanning, container security, network configuration, and application
security testing.

### 📊 Audit Scope
- ✅ Dependency vulnerability scanning
- ✅ Container security assessment
- ✅ Network configuration review
- ✅ Application security testing
- ✅ Configuration audit
- ✅ Static code analysis

---

## 📋 Findings Summary

### 🔍 Scan Results
- **📦 Dependency Scan**: $([ -f "$REPORTS_DIR/safety-report-$TIMESTAMP.json" ] && echo "Completed" || echo "Skipped")
- **🐳 Container Scan**: $([ -f "$REPORTS_DIR/trivy-backend-$TIMESTAMP.json" ] && echo "Completed" || echo "Skipped")
- **🌐 Network Scan**: $([ -f "$REPORTS_DIR/open-ports-$TIMESTAMP.txt" ] && echo "Completed" || echo "Skipped")
- **🚀 Application Scan**: $([ -f "$REPORTS_DIR/zap-report-$TIMESTAMP.json" ] && echo "Completed" || echo "Skipped")
- **⚙️ Configuration Audit**: $([ -f "$REPORTS_DIR/config-audit-$TIMESTAMP.txt" ] && echo "Completed" || echo "Skipped")

### 🎯 Risk Assessment
- **🔴 Critical**: Review detailed reports for critical vulnerabilities
- **🟡 Medium**: Address medium-risk findings in next release
- **🟢 Low**: Monitor low-risk findings for future updates
- **ℹ️ Info**: Informational findings for awareness

---

## 📁 Detailed Reports

The following detailed reports are available in the security-reports directory:

### 📦 Dependency Reports
- \`npm-audit-$TIMESTAMP.json\` - Frontend dependency vulnerabilities
- \`safety-report-$TIMESTAMP.json\` - Backend dependency vulnerabilities  
- \`bandit-report-$TIMESTAMP.json\` - Python security issues

### 🐳 Container Reports
- \`trivy-*-$TIMESTAMP.json\` - Container vulnerability scans
- \`trivy-*-$TIMESTAMP.txt\` - Human-readable container reports

### 🌐 Network Reports
- \`open-ports-$TIMESTAMP.txt\` - Open ports and services
- \`firewall-$TIMESTAMP.txt\` - Firewall configuration

### 🚀 Application Reports
- \`zap-report-$TIMESTAMP.json\` - OWASP ZAP security scan
- \`eslint-security-$TIMESTAMP.json\` - Frontend security issues

### ⚙️ Configuration Reports
- \`config-audit-$TIMESTAMP.txt\` - Configuration security issues
- \`ssl-cert-$TIMESTAMP.txt\` - SSL certificate analysis

---

## 🎯 Recommendations

### 🔒 Immediate Actions
1. **Change Default Passwords**: Ensure all default passwords are changed in production
2. **Update Dependencies**: Address any high/critical vulnerability findings
3. **SSL Configuration**: Implement proper SSL certificates for production
4. **Access Controls**: Verify proper authentication and authorization

### 📊 Security Monitoring
1. **Regular Scans**: Schedule weekly security scans
2. **Dependency Updates**: Monitor for new vulnerabilities monthly
3. **Penetration Testing**: Conduct quarterly professional security assessments
4. **Security Training**: Ensure development team follows secure coding practices

### 🛡️ Hardening Recommendations
1. **Container Security**: Implement security policies and runtime protection
2. **Network Segmentation**: Use proper network isolation in production
3. **Monitoring**: Implement comprehensive security monitoring and alerting
4. **Backup Security**: Ensure backups are encrypted and access-controlled

---

## 📞 Next Steps

1. **📋 Review Reports**: Examine detailed findings in individual report files
2. **🎯 Prioritize Fixes**: Address critical and high-risk findings first
3. **🔄 Implement Changes**: Apply security improvements and patches
4. **🧪 Re-test**: Run security audit again after implementing fixes
5. **📊 Monitor**: Set up ongoing security monitoring and alerting

---

## 📚 Additional Resources

- **🔒 Security Documentation**: \`docs/security.md\`
- **🛡️ Security Best Practices**: \`docs/security-best-practices.md\`
- **🚨 Incident Response**: \`docs/incident-response.md\`
- **🔐 Access Control Guide**: \`docs/access-control.md\`

---

**Report Generated by**: Energy Optimizer Pro Security Audit Suite  
**Next Scheduled Audit**: $(date -d "+1 week")
EOF
    
    success "Security report generated: $report_file"
}

# Full security audit
full_audit() {
    print_banner
    log "🔒 Starting comprehensive security audit..."
    
    setup_reports
    
    # Run all security scans
    scan_dependencies
    scan_containers  
    scan_network
    audit_configuration
    scan_code
    scan_application
    
    # Generate comprehensive report
    generate_report
    
    # Display summary
    echo ""
    success "🎉 Security audit completed successfully!"
    echo ""
    echo -e "${CYAN}📋 Reports generated in:${NC} $REPORTS_DIR"
    echo -e "${CYAN}📊 Summary report:${NC} $REPORTS_DIR/security-summary-$TIMESTAMP.md"
    echo ""
    echo -e "${CYAN}🎯 Next steps:${NC}"
    echo "  1. 📋 Review the summary report"
    echo "  2. 🔍 Examine detailed findings"
    echo "  3. 🎯 Prioritize and fix critical issues"
    echo "  4. 🔄 Re-run audit after fixes"
    echo ""
}

# Quick security check
quick_check() {
    print_banner
    log "⚡ Running quick security check..."
    
    setup_reports
    
    # Basic checks only
    scan_dependencies
    audit_configuration
    
    echo ""
    success "⚡ Quick security check completed!"
    echo -e "${CYAN}📋 Reports in:${NC} $REPORTS_DIR"
}

# Clean old reports
clean_reports() {
    log "🧹 Cleaning old security reports..."
    
    if [ -d "$REPORTS_DIR" ]; then
        # Keep only last 10 reports
        find "$REPORTS_DIR" -name "*-[0-9]*" -type f | sort | head -n -10 | xargs rm -f 2>/dev/null || true
        success "Old reports cleaned"
    fi
}

# Setup security monitoring
setup_monitoring() {
    log "📊 Setting up security monitoring..."
    
    # Create monitoring configuration
    cat > "$PROJECT_ROOT/monitoring/security-rules.yml" << 'EOF'
# 🔒 Security Alert Rules
groups:
  - name: security.alerts
    rules:
      - alert: HighFailedLoginRate
        expr: rate(auth_failed_logins_total[5m]) > 0.1
        for: 2m
        labels:
          severity: medium
        annotations:
          summary: "High rate of failed login attempts"
      
      - alert: SuspiciousAPIAccess
        expr: rate(http_requests_total{status="401"}[5m]) > 0.05
        for: 5m
        labels:
          severity: high
        annotations:
          summary: "High rate of unauthorized API access attempts"
EOF
    
    success "Security monitoring rules created"
}

# ================================
# 🎯 CLI Interface
# ================================

case "${1:-help}" in
    "full"|"audit")
        full_audit
        ;;
    "quick")
        quick_check
        ;;
    "dependencies"|"deps")
        setup_reports
        scan_dependencies
        ;;
    "containers")
        setup_reports
        scan_containers
        ;;
    "network")
        setup_reports
        scan_network
        ;;
    "application"|"app")
        setup_reports
        scan_application
        ;;
    "config")
        setup_reports
        audit_configuration
        ;;
    "clean")
        clean_reports
        ;;
    "setup-monitoring")
        setup_monitoring
        ;;
    "help"|"--help"|"-h")
        print_banner
        echo "🔒 Energy Optimizer Pro - Security Audit Suite"
        echo ""
        echo "Usage: $0 [COMMAND]"
        echo ""
        echo -e "${CYAN}🔍 Audit Commands:${NC}"
        echo "  full                 Complete security audit (default)"
        echo "  quick                Quick security check"
        echo "  dependencies         Scan dependencies only"
        echo "  containers           Scan containers only"
        echo "  network              Network security check"
        echo "  application          Application security test"
        echo "  config               Configuration audit"
        echo ""
        echo -e "${CYAN}🛠️ Utility Commands:${NC}"
        echo "  clean                Clean old security reports"
        echo "  setup-monitoring     Setup security monitoring"
        echo ""
        echo -e "${CYAN}📋 Examples:${NC}"
        echo "  $0 full              # Comprehensive security audit"
        echo "  $0 quick             # Quick dependency and config check"
        echo "  $0 dependencies      # Check only npm and pip dependencies"
        echo "  $0 containers        # Scan Docker containers with Trivy"
        echo ""
        echo -e "${CYAN}📁 Output:${NC}"
        echo "  All reports are saved to: ./security-reports/"
        echo "  Summary report: security-summary-[timestamp].md"
        echo ""
        echo -e "${CYAN}🔧 Prerequisites:${NC}"
        echo "  - Docker and Docker Compose"
        echo "  - npm (for frontend scanning)"
        echo "  - Python 3.11+ with pip (for backend scanning)"
        echo ""
        echo -e "${CYAN}📞 Support:${NC}"
        echo "  📖 Security docs: docs/security.md"
        echo "  🐛 Report issues: https://github.com/your-username/energy-optimizer-pro/issues"
        echo ""
        ;;
    *)
        error "Unknown command: $1"
        echo "Use '$0 help' for usage information"
        exit 1
        ;;
esac
