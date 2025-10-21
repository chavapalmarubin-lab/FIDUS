#!/usr/bin/env python3
"""
Direct SSH Deployment to New VPS
Sets up MT5 Bridge service via SSH
"""
import paramiko
import time
import sys

# VPS Credentials
VPS_HOST = "92.118.45.135"
VPS_PORT = 42014
VPS_USERNAME = "trader"
VPS_PASSWORD = "4p1We0OHh3LKgm6"

def execute_powershell(ssh, command, description=""):
    """Execute PowerShell command via SSH"""
    if description:
        print(f"\n📋 {description}")
    
    # Wrap in PowerShell command
    full_command = f'powershell -Command "{command}"'
    
    stdin, stdout, stderr = ssh.exec_command(full_command, timeout=300)
    
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    exit_code = stdout.channel.recv_exit_status()
    
    if output:
        print(output)
    if error and exit_code != 0:
        print(f"⚠️ Error: {error}")
    
    return exit_code == 0, output, error

def main():
    """Main deployment"""
    print("=" * 70)
    print("🚀 DEPLOYING MT5 BRIDGE TO NEW VPS")
    print("=" * 70)
    print(f"Host: {VPS_HOST}")
    print(f"Port: {VPS_PORT}")
    print(f"User: {VPS_USERNAME}")
    print("=" * 70)
    
    try:
        # Connect via SSH
        print("\n🔌 Connecting to VPS via SSH...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        
        ssh.connect(
            hostname=VPS_HOST,
            port=VPS_PORT,
            username=VPS_USERNAME,
            password=VPS_PASSWORD,
            timeout=30
        )
        
        print("✅ Connected successfully!")
        
        # Step 1: Create directory structure
        success, _, _ = execute_powershell(
            ssh,
            "New-Item -Path 'C:\\mt5_bridge_service' -ItemType Directory -Force; New-Item -Path 'C:\\mt5_bridge_service\\logs' -ItemType Directory -Force",
            "Creating directory structure"
        )
        
        if not success:
            print("❌ Failed to create directories")
            return False
        
        # Step 2: Create batch file
        batch_content = """@echo off
cd /d C:\\mt5_bridge_service
SET PYTHON_PATH=C:\\Users\\trader\\AppData\\Local\\Programs\\Python\\Python312
"%PYTHON_PATH%\\python.exe" mt5_bridge_api_service.py >> logs\\service_output.log 2>> logs\\service_error.log
exit /b %ERRORLEVEL%"""
        
        success, _, _ = execute_powershell(
            ssh,
            f"Set-Content -Path 'C:\\mt5_bridge_service\\start_service.bat' -Value @'\n{batch_content}\n'@",
            "Creating batch file"
        )
        
        if not success:
            print("❌ Failed to create batch file")
            return False
        
        print("✅ Batch file created")
        
        # Step 3: Check if Python exists
        success, output, _ = execute_powershell(
            ssh,
            "Test-Path 'C:\\Users\\trader\\AppData\\Local\\Programs\\Python\\Python312\\python.exe'",
            "Checking Python installation"
        )
        
        if "True" not in output:
            print("⚠️ Python not found at expected path")
            print("💡 You may need to install Python or update the path")
        else:
            print("✅ Python found")
        
        # Step 4: Create Task Scheduler task
        task_xml = """<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>MT5 Bridge API Service</Description>
  </RegistrationInfo>
  <Triggers>
    <BootTrigger>
      <Enabled>true</Enabled>
    </BootTrigger>
  </Triggers>
  <Principals>
    <Principal>
      <UserId>trader</UserId>
      <LogonType>Password</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT0S</ExecutionTimeLimit>
    <Priority>7</Priority>
    <RestartOnFailure>
      <Interval>PT5M</Interval>
      <Count>3</Count>
    </RestartOnFailure>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>C:\\mt5_bridge_service\\start_service.bat</Command>
      <WorkingDirectory>C:\\mt5_bridge_service</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
        
        success, _, _ = execute_powershell(
            ssh,
            f"Set-Content -Path 'C:\\mt5_bridge_service\\task.xml' -Value @'\n{task_xml}\n'@",
            "Creating Task Scheduler XML"
        )
        
        if not success:
            print("❌ Failed to create task XML")
            return False
        
        # Register the task
        success, output, error = execute_powershell(
            ssh,
            "schtasks /Create /TN 'MT5BridgeService' /XML 'C:\\mt5_bridge_service\\task.xml' /F",
            "Registering Task Scheduler task"
        )
        
        if not success:
            print("⚠️ Task registration may have failed")
            print(f"Output: {output}")
            print(f"Error: {error}")
        else:
            print("✅ Task registered successfully")
        
        # Step 5: Check if MT5 Bridge script exists
        success, output, _ = execute_powershell(
            ssh,
            "Test-Path 'C:\\mt5_bridge_service\\mt5_bridge_api_service.py'",
            "Checking for MT5 Bridge script"
        )
        
        if "True" not in output:
            print("⚠️ MT5 Bridge script not found!")
            print("💡 You need to deploy mt5_bridge_api_service.py to the VPS")
            print("💡 This can be done via GitHub Actions or manual file transfer")
        else:
            print("✅ MT5 Bridge script exists")
            
            # Try to start the task
            success, _, _ = execute_powershell(
                ssh,
                "schtasks /Run /TN 'MT5BridgeService'",
                "Starting MT5 Bridge service"
            )
            
            if success:
                print("✅ Service start command sent")
                print("\n⏳ Waiting 10 seconds for service to start...")
                time.sleep(10)
                
                # Test the service
                print("\n🧪 Testing MT5 Bridge service...")
                test_cmd = "Invoke-WebRequest -Uri 'http://localhost:8000/api/mt5/bridge/health' -UseBasicParsing -TimeoutSec 5"
                success, output, _ = execute_powershell(ssh, test_cmd, "")
                
                if success and "200" in output:
                    print("✅ Service is responding!")
                else:
                    print("⚠️ Service may not be running yet")
                    print("💡 Check logs: C:\\mt5_bridge_service\\logs\\")
        
        # Close SSH connection
        ssh.close()
        
        print("\n" + "=" * 70)
        print("🎉 DEPLOYMENT COMPLETE!")
        print("=" * 70)
        print("\n📋 Next Steps:")
        print("1. Verify service: curl http://92.118.45.135:8000/api/mt5/bridge/health")
        print("2. Check Task Scheduler on VPS")
        print("3. Review logs: C:\\mt5_bridge_service\\logs\\")
        print("\n💡 If service not responding:")
        print("   - Ensure mt5_bridge_api_service.py is deployed")
        print("   - Check Python path is correct")
        print("   - Review service error logs")
        
        return True
        
    except paramiko.AuthenticationException:
        print("❌ Authentication failed - check VPS credentials")
        return False
    except paramiko.SSHException as e:
        print(f"❌ SSH error: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ Deployment error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
