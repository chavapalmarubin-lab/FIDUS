#!/bin/bash
# Sanitize MongoDB credentials from documentation files

# List of files with exposed credentials
FILES=(
  "./INFRASTRUCTURE_AUDIT_REPORT.md"
  "./FINAL_EMERGENT_REQUEST.md"
  "./CTO_Technical_Summary.md"
  "./MAKE_REPO_PRIVATE_GUIDE.md"
  "./mt5_bridge_service/VPS_DEPLOYMENT_CHECKLIST.md"
  "./SECURITY_INCIDENT_RESOLUTION.md"
  "./test_result.md"
  "./MULTI_TERMINAL_SOLUTION.md"
  "./MIGRATION_COMPLETE_REPORT.md"
  "./PHASE4A_VPS_DEPLOYMENT_GUIDE.md"
  "./MT4_INTEGRATION_GUIDE.md"
  "./ONE_COMMAND_DEPLOY.txt"
  "./SYSTEM_MASTER.md"
  "./VPS_DEPLOYMENT_PACKAGE.md"
  "./GITHUB_WORKFLOWS_GUIDE.md"
  "./BRIDGE_UPDATE_DEPLOYMENT.md"
  "./QUICK_ACTION_GUIDE.md"
  "./MT4_BRIDGE_DEPLOYMENT_GUIDE.md"
  "./DEPLOYMENT.md"
  "./SECURITY_AUDIT_COMPLETE.md"
  "./MONGODB_FIX_COMMAND.txt"
  "./VPS_MONGODB_PASSWORD_UPDATE.md"
  "./docs/COMPLETE_DATA_FLOW_VERIFICATION.md"
  "./docs/ACCOUNT_MANAGEMENT_FIXED.md"
  "./docs/TECH_DOCUMENTATION.md"
  "./docs/COMPLETE_DEPLOYMENT_GUIDE.md"
)

# Patterns to sanitize
# 2170Tenoch variations
sed -i 's/2170Tenoch[!@#$%^&*()_+=-]*[A-Za-z0-9!@#$%^&*()_+=-]*/\*\*\*SANITIZED\*\*\*/g' "${FILES[@]}" 2>/dev/null

# Old password patterns
sed -i 's/HLX8kJaF38fi0VHi/\*\*\*SANITIZED\*\*\*/g' "${FILES[@]}" 2>/dev/null
sed -i 's/BpzaxqxDCjz1yWY4/\*\*\*SANITIZED\*\*\*/g' "${FILES[@]}" 2>/dev/null
sed -i 's/FIDUS2024secureDB!/\*\*\*SANITIZED\*\*\*/g' "${FILES[@]}" 2>/dev/null

# Fidus13! password
sed -i 's/Fidus13!/\*\*\*SANITIZED\*\*\*/g' "${FILES[@]}" 2>/dev/null

echo "✅ Sanitized MongoDB credentials in documentation files"
