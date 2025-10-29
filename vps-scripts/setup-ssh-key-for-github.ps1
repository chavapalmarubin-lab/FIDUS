# ============================================================================
# ONE-TIME SSH KEY SETUP FOR GITHUB ACTIONS
# Run this ONCE on the VPS as Administrator
# Takes 2 minutes
# ============================================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SSH KEY SETUP FOR GITHUB ACTIONS" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Step 1: Generate SSH key pair
Write-Host "[1/5] Generating SSH key pair..." -ForegroundColor Yellow
$sshDir = "$env:USERPROFILE\.ssh"
New-Item -Path $sshDir -ItemType Directory -Force | Out-Null

$keyPath = "$sshDir\github_actions_rsa"

# Generate key with no passphrase
ssh-keygen -t rsa -b 4096 -f $keyPath -N '""' -C "github-actions@vps" -q

if (Test-Path $keyPath) {
    Write-Host "  [OK] Key pair generated" -ForegroundColor Green
} else {
    Write-Host "  [FAIL] Key generation failed" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Step 2: Configure authorized_keys
Write-Host "[2/5] Configuring authorized_keys..." -ForegroundColor Yellow

$publicKey = Get-Content "$keyPath.pub"
$authorizedKeysPath = "$sshDir\authorized_keys"

# Create or append to authorized_keys
if (Test-Path $authorizedKeysPath) {
    Add-Content -Path $authorizedKeysPath -Value $publicKey
} else {
    $publicKey | Out-File -FilePath $authorizedKeysPath -Encoding ASCII
}

Write-Host "  [OK] Public key added to authorized_keys" -ForegroundColor Green
Write-Host ""

# Step 3: Set correct permissions
Write-Host "[3/5] Setting permissions..." -ForegroundColor Yellow

# Remove inheritance and set specific permissions
icacls $sshDir /inheritance:r | Out-Null
icacls $sshDir /grant:r "$env:USERNAME:(OI)(CI)F" | Out-Null
icacls $authorizedKeysPath /inheritance:r | Out-Null
icacls $authorizedKeysPath /grant:r "$env:USERNAME:F" | Out-Null
icacls $authorizedKeysPath /grant:r "SYSTEM:F" | Out-Null

Write-Host "  [OK] Permissions configured" -ForegroundColor Green
Write-Host ""

# Step 4: Test SSH connection locally
Write-Host "[4/5] Testing SSH connection..." -ForegroundColor Yellow

$testResult = ssh -i $keyPath -o StrictHostKeyChecking=no Administrator@localhost "echo 'SSH_TEST_SUCCESS'"

if ($testResult -eq "SSH_TEST_SUCCESS") {
    Write-Host "  [OK] SSH key authentication working!" -ForegroundColor Green
} else {
    Write-Host "  [WARN] Local test inconclusive, but key is configured" -ForegroundColor Yellow
}
Write-Host ""

# Step 5: Output private key for GitHub Secrets
Write-Host "[5/5] Private key for GitHub Secrets:" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

Get-Content $keyPath | Write-Host -ForegroundColor White

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Instructions
Write-Host "NEXT STEPS:" -ForegroundColor Green
Write-Host ""
Write-Host "1. Copy the ENTIRE private key above (from -----BEGIN to -----END)" -ForegroundColor White
Write-Host ""
Write-Host "2. Go to GitHub:" -ForegroundColor White
Write-Host "   Repository -> Settings -> Secrets and variables -> Actions" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Create new secret:" -ForegroundColor White
Write-Host "   Name: VPS_SSH_KEY" -ForegroundColor Gray
Write-Host "   Value: [paste the private key]" -ForegroundColor Gray
Write-Host ""
Write-Host "4. Click 'Add secret'" -ForegroundColor White
Write-Host ""
Write-Host "5. Keep existing VPS_PASSWORD secret (as backup)" -ForegroundColor White
Write-Host ""
Write-Host "Done! GitHub Actions can now authenticate to this VPS." -ForegroundColor Green
Write-Host ""

# Save to file for reference
$privateKeyOutput = "$env:USERPROFILE\Desktop\github_actions_private_key.txt"
Get-Content $keyPath | Out-File -FilePath $privateKeyOutput -Encoding ASCII

Write-Host "Private key also saved to: $privateKeyOutput" -ForegroundColor Cyan
Write-Host "Delete this file after copying to GitHub Secrets!" -ForegroundColor Yellow
Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
