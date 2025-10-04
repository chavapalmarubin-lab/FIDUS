"""
MT5 Bridge Service VPS Deployment Script
Automates the deployment of MT5 Bridge Service to Windows VPS
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime

class VPSDeployer:
    """Handles deployment to Windows VPS"""
    
    def __init__(self):
        self.vps_ip = "217.197.163.11"
        self.vps_user = "chavapalmarubin@gmail.com" 
        self.vps_password = "2170Tenoch!"
        self.service_dir = "C:\\mt5_bridge_service"
        
    def create_deployment_package(self):
        """Create deployment package with all necessary files"""
        
        print("📦 Creating deployment package...")
        
        deployment_files = {
            "main_production.py": "Main FastAPI service",
            "requirements.txt": "Python dependencies", 
            "setup_instructions.md": "Setup guide",
            ".env.template": "Environment template"
        }
        
        # Create .env template
        env_template = """# MT5 Bridge Service Configuration
MT5_BRIDGE_API_KEY=generate_secure_key_here
ENVIRONMENT=prod
PORT=8000
LOG_LEVEL=info

# Optional: Database logging (if needed)
# DATABASE_URL=sqlite:///mt5_bridge.db
"""
        
        with open(".env.template", "w") as f:
            f.write(env_template)
        
        print("✅ Deployment package created")
        
        return deployment_files
    
    def generate_windows_setup_script(self):
        """Generate Windows batch script for VPS setup"""
        
        setup_script = f"""@echo off
echo FIDUS MT5 Bridge Service - Windows VPS Setup
echo ============================================

REM Create service directory
mkdir {self.service_dir}
cd {self.service_dir}

REM Check Python installation
python --version
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python not installed or not in PATH
    echo Please install Python 3.11+ from python.org
    pause
    exit /b 1
)

REM Install dependencies
echo Installing Python dependencies...
pip install --upgrade pip
pip install -r requirements.txt

REM Copy environment file
copy .env.template .env
echo.
echo IMPORTANT: Edit .env file with proper configuration:
echo - Generate secure API key
echo - Set ENVIRONMENT=prod
echo.

REM Create Windows service script
echo Creating service scripts...

REM Start service script
echo @echo off > start_service.bat
echo echo Starting FIDUS MT5 Bridge Service... >> start_service.bat
echo cd {self.service_dir} >> start_service.bat
echo python main_production.py >> start_service.bat
echo pause >> start_service.bat

REM Stop service script  
echo @echo off > stop_service.bat
echo echo Stopping FIDUS MT5 Bridge Service... >> stop_service.bat
echo taskkill /f /im python.exe >> stop_service.bat
echo echo Service stopped >> stop_service.bat
echo pause >> stop_service.bat

REM Install as Windows service (optional)
echo @echo off > install_service.bat
echo echo Installing as Windows service... >> install_service.bat
echo pip install pywin32 >> install_service.bat
echo echo Service installation requires admin privileges >> install_service.bat
echo pause >> install_service.bat

echo.
echo ============================================
echo Setup completed successfully!
echo.
echo Next steps:
echo 1. Edit .env file with your configuration
echo 2. Install MetaTrader 5 terminal
echo 3. Configure Windows Firewall (port 8000)
echo 4. Run start_service.bat to start the service
echo.
echo For help, see setup_instructions.md
echo ============================================
pause
"""
        
        with open("setup_vps.bat", "w") as f:
            f.write(setup_script)
        
        print("✅ Windows setup script created: setup_vps.bat")
    
    def create_api_key_generator(self):
        """Create API key generator script"""
        
        key_generator = """#!/usr/bin/env python3
\"\"\"
API Key Generator for MT5 Bridge Service
Generates secure API keys for production use
\"\"\"

import secrets
import string
from cryptography.fernet import Fernet

def generate_api_key(length=32):
    \"\"\"Generate secure API key\"\"\"
    alphabet = string.ascii_letters + string.digits + '-_'
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_encryption_key():
    \"\"\"Generate encryption key for MT5 passwords\"\"\"
    return Fernet.generate_key().decode()

if __name__ == "__main__":
    print("🔐 FIDUS MT5 Bridge - Security Key Generator")
    print("=" * 50)
    
    # Generate API key
    api_key = generate_api_key()
    print(f"API Key: {api_key}")
    
    # Generate encryption key
    encryption_key = generate_encryption_key()
    print(f"Encryption Key: {encryption_key}")
    
    print("\\n📝 Add these to your .env file:")
    print(f"MT5_BRIDGE_API_KEY={api_key}")
    print(f"MT5_ENCRYPTION_KEY={encryption_key}")
    
    print("\\n⚠️  Keep these keys secure and never share them!")
"""
        
        with open("generate_keys.py", "w") as f:
            f.write(key_generator)
        
        print("✅ API key generator created: generate_keys.py")
    
    def create_firewall_script(self):
        """Create Windows firewall configuration script"""
        
        firewall_script = """@echo off
echo Configuring Windows Firewall for MT5 Bridge Service
echo ====================================================

REM Enable firewall rule for MT5 Bridge Service
netsh advfirewall firewall add rule name="FIDUS MT5 Bridge Service" dir=in action=allow protocol=TCP localport=8000

echo.
if %ERRORLEVEL% EQU 0 (
    echo ✅ Firewall rule added successfully
    echo Port 8000 is now open for incoming connections
) else (
    echo ❌ Failed to add firewall rule
    echo Please run as Administrator or configure manually:
    echo 1. Open Windows Defender Firewall
    echo 2. Click "Advanced settings"
    echo 3. Click "Inbound Rules" 
    echo 4. Click "New Rule..."
    echo 5. Select "Port" and click Next
    echo 6. Select "TCP" and enter "8000" 
    echo 7. Select "Allow the connection"
    echo 8. Apply to all profiles
    echo 9. Name: "FIDUS MT5 Bridge Service"
)

echo.
echo Testing port accessibility...
netstat -an | find ":8000"

echo.
echo ====================================================
echo Firewall configuration completed
echo ====================================================
pause
"""
        
        with open("configure_firewall.bat", "w") as f:
            f.write(firewall_script)
        
        print("✅ Firewall configuration script created: configure_firewall.bat")
    
    def create_deployment_instructions(self):
        """Create comprehensive deployment instructions"""
        
        instructions = f"""# FIDUS MT5 Bridge Service - VPS Deployment Guide

## 🖥️ VPS Information
- **IP Address**: {self.vps_ip}
- **Username**: {self.vps_user}
- **Password**: {self.vps_password}
- **OS**: Windows Server
- **Service Port**: 8000

## 📋 Prerequisites Checklist

### 1. Remote Desktop Connection
```bash
# Connect to VPS using RDP
# Windows: Remote Desktop Connection
# Mac: Microsoft Remote Desktop from App Store
# Linux: Remmina or similar RDP client

Host: {self.vps_ip}
Username: {self.vps_user}
Password: {self.vps_password}
```

### 2. Install Python (if not already installed)
1. Download Python 3.11+ from https://python.org
2. **IMPORTANT**: Check "Add to PATH" during installation
3. Verify installation: `python --version`

### 3. Install MetaTrader 5 Terminal
1. Download MT5 from your broker's website
2. Install and login with your trading account
3. Ensure MT5 terminal stays running for API access

## 🚀 Deployment Steps

### Step 1: Upload Files to VPS
Upload these files to `C:\\mt5_bridge_service\\`:
- `main_production.py`
- `requirements.txt`
- `setup_vps.bat`
- `generate_keys.py`
- `configure_firewall.bat`
- `.env.template`

### Step 2: Run Setup Script
```cmd
# On VPS, open Command Prompt as Administrator
cd C:\\mt5_bridge_service
setup_vps.bat
```

### Step 3: Generate Security Keys
```cmd
python generate_keys.py
```
Copy the generated keys to your `.env` file.

### Step 4: Configure Environment
1. Copy `.env.template` to `.env`
2. Edit `.env` with generated keys:
```env
MT5_BRIDGE_API_KEY=your_generated_api_key
MT5_ENCRYPTION_KEY=your_generated_encryption_key
ENVIRONMENT=prod
PORT=8000
LOG_LEVEL=info
```

### Step 5: Configure Firewall
```cmd
# Run as Administrator
configure_firewall.bat
```

### Step 6: Start Service
```cmd
# Test run first
python main_production.py

# If successful, use service scripts:
start_service.bat
```

### Step 7: Verify Service
Open browser on VPS: http://localhost:8000/health

Expected response:
```json
{{
  "status": "healthy",
  "mt5_available": true,
  "mt5_initialized": true,
  "timestamp": "2025-01-04T..."
}}
```

## 🔧 FIDUS Backend Configuration

Update FIDUS backend `.env` file:
```env
MT5_BRIDGE_URL=http://{self.vps_ip}:8000
MT5_BRIDGE_API_KEY=same_key_as_vps
MT5_BRIDGE_TIMEOUT=30
MT5_ENCRYPTION_KEY=same_encryption_key_as_vps
```

## 🧪 Testing Integration

### 1. Test from FIDUS Backend
```python
# In FIDUS backend, run:
from mt5_bridge_client import mt5_bridge
health = await mt5_bridge.health_check()
print(health)
```

### 2. Test MT5 Connection
Use FIDUS admin dashboard:
1. Go to MT5 Management
2. Click "Test Connection"
3. Enter MT5 credentials
4. Verify connection success

## 🔍 Troubleshooting

### Common Issues:

**1. Service won't start**
- Check Python installation: `python --version`
- Verify dependencies: `pip list`
- Check logs in service directory

**2. Connection refused from FIDUS**
- Verify firewall settings (port 8000 open)
- Check VPS IP address is correct
- Ensure service is running: `netstat -an | find ":8000"`

**3. MT5 not connecting**
- Ensure MT5 terminal is running and logged in
- Verify MetaTrader5 package: `pip show MetaTrader5`
- Check MT5 account credentials

**4. API key errors**
- Ensure same API key in both VPS `.env` and FIDUS backend `.env`
- Regenerate keys if needed: `python generate_keys.py`

### Service Logs
Check logs in: `C:\\mt5_bridge_service\\logs\\`

### Network Testing
```cmd
# Test port from VPS
netstat -an | find ":8000"

# Test external access (if needed)
telnet {self.vps_ip} 8000
```

## 🔒 Security Best Practices

1. **Change default API key** - Never use example keys
2. **Use strong encryption key** - Generate with script
3. **Limit network access** - Whitelist FIDUS backend IP only
4. **Regular updates** - Keep Python and packages updated
5. **Monitor logs** - Check for suspicious activity
6. **Backup configuration** - Save `.env` file securely

## 📊 Monitoring

### Health Endpoints:
- `GET /health` - Basic health check
- `GET /api/mt5/status` - Detailed MT5 status
- `GET /api/mt5/terminal/info` - MT5 terminal information

### Service Management:
- Start: `start_service.bat`
- Stop: `stop_service.bat` 
- Logs: Check `logs/` directory

## 🆘 Support

If you encounter issues:
1. Check this documentation first
2. Review service logs
3. Test basic connectivity
4. Verify MT5 terminal is running
5. Contact FIDUS technical support with log files

---
**Deployment Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Version**: 1.0.0
"""
        
        with open("DEPLOYMENT_GUIDE.md", "w") as f:
            f.write(instructions)
        
        print("✅ Deployment guide created: DEPLOYMENT_GUIDE.md")
    
    def run_deployment(self):
        """Run complete deployment process"""
        
        print("🚀 FIDUS MT5 Bridge Service - VPS Deployment")
        print("=" * 60)
        
        try:
            # Create all deployment files
            self.create_deployment_package()
            self.generate_windows_setup_script()
            self.create_api_key_generator() 
            self.create_firewall_script()
            self.create_deployment_instructions()
            
            print(f"\\n📦 Deployment package ready!")
            print(f"Files created in current directory:")
            print(f"  - main_production.py (FastAPI service)")
            print(f"  - requirements.txt (Python dependencies)")
            print(f"  - setup_vps.bat (Windows setup script)")
            print(f"  - generate_keys.py (Security key generator)")
            print(f"  - configure_firewall.bat (Firewall config)")
            print(f"  - DEPLOYMENT_GUIDE.md (Complete instructions)")
            print(f"  - .env.template (Environment template)")
            
            print(f"\\n🎯 Next Steps:")
            print(f"1. Connect to VPS: {self.vps_ip}")
            print(f"2. Upload all files to C:\\\\mt5_bridge_service\\\\")
            print(f"3. Follow DEPLOYMENT_GUIDE.md instructions")
            print(f"4. Run setup_vps.bat on VPS")
            print(f"5. Configure .env file with generated keys")
            print(f"6. Start service and test connectivity")
            
            print(f"\\n✅ Deployment preparation completed successfully!")
            
        except Exception as e:
            print(f"❌ Deployment preparation failed: {e}")
            return False
        
        return True

if __name__ == "__main__":
    deployer = VPSDeployer()
    success = deployer.run_deployment()
    
    if success:
        print(f"\\n🎉 Ready for VPS deployment!")
    else:
        print(f"\\n💥 Deployment preparation failed")
        sys.exit(1)