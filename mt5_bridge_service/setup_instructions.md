# MT5 Bridge Service Setup Instructions

## Windows VPS Setup (ForexVPS.net)

### VPS Access Details:
- **Hostname:** VMI0594978015651953-1.forexvps.net
- **IP:** 217.197.163.11
- **Username:** chavapalmarubin@gmail.com
- **Password:** 2170Tenoch!

### Setup Steps:

#### 1. Connect to Windows VPS
```bash
# Use Windows Remote Desktop Connection
# Or from Linux/Mac:
rdesktop -u chavapalmarubin@gmail.com -p 2170Tenoch! 217.197.163.11
```

#### 2. Install Python on Windows VPS
1. Download Python 3.11+ from python.org
2. Install with "Add to PATH" option checked
3. Verify: Open Command Prompt, run `python --version`

#### 3. Install MetaTrader5 Terminal
1. Download MT5 from your broker's website
2. Install and configure with your trading account
3. Ensure MT5 is running and logged in

#### 4. Setup MT5 Bridge Service
```cmd
# Create directory
mkdir C:\mt5_bridge_service
cd C:\mt5_bridge_service

# Copy files from FIDUS server (upload via RDP or download from GitHub)
# Files needed:
# - main.py
# - requirements.txt
# - setup_instructions.md (this file)

# Install Python dependencies
pip install -r requirements.txt

# Set environment variables
set MT5_BRIDGE_API_KEY=your-secure-api-key-here
set MT5_BRIDGE_PORT=8000

# Run the service
python main.py
```

#### 5. Configure Windows Firewall
1. Open Windows Defender Firewall
2. Click "Advanced settings"
3. Create new Inbound Rule:
   - Type: Port
   - Protocol: TCP
   - Port: 8000
   - Action: Allow the connection
   - Profile: All profiles
   - Name: "MT5 Bridge Service"

#### 6. Test the Service
```cmd
# Test locally on VPS
curl http://localhost:8000/health

# Test from external (should work after firewall config)
curl http://217.197.163.11:8000/health
```

#### 7. Setup as Windows Service (Optional)
Use `nssm` (Non-Sucking Service Manager) to run as a Windows service:

```cmd
# Download nssm from nssm.cc
# Install as service
nssm install MT5BridgeService "C:\Python\python.exe" "C:\mt5_bridge_service\main.py"
nssm set MT5BridgeService AppDirectory "C:\mt5_bridge_service"
nssm start MT5BridgeService
```

### Security Notes:
1. Change the default API key in production
2. Use HTTPS with proper SSL certificates
3. Implement IP whitelisting for FIDUS backend only
4. Regular Windows updates and antivirus

### Troubleshooting:
1. **MT5 not connecting:** Ensure MT5 terminal is running and logged in
2. **Port not accessible:** Check Windows Firewall settings
3. **API errors:** Verify API key matches between FIDUS and bridge
4. **Performance issues:** Monitor VPS resources (CPU, RAM, Network)

### Monitoring:
- Service logs: Check console output or Windows Event Viewer
- MT5 status: Verify MT5 terminal stays connected
- Network: Monitor latency between VPS and FIDUS backend

### Configuration Files:

#### Environment Variables (.env):
```env
MT5_BRIDGE_API_KEY=your-secure-key-here
MT5_BRIDGE_PORT=8000
MT5_BRIDGE_HOST=0.0.0.0
DEBUG=false
```

#### MT5 Account Settings:
Configure in FIDUS backend `.env`:
```env
MT5_BRIDGE_URL=http://217.197.163.11:8000
MT5_BRIDGE_API_KEY=same-key-as-above
MT5_BRIDGE_TIMEOUT=30
```