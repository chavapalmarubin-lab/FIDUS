#!/usr/bin/env python3
"""
MT5 Real-Time Data Collector Service Manager
==========================================

This script manages the MT5 data collection service for FIDUS production portal.
It ensures continuous data collection with automatic restart on failures.
"""

import subprocess
import time
import logging
import os
import signal
import sys
from datetime import datetime
import threading

class MT5CollectorService:
    def __init__(self):
        self.setup_logging()
        self.process = None
        self.running = False
        self.restart_count = 0
        self.max_restarts = 10
        self.restart_window = 3600  # 1 hour
        self.restart_times = []
        
    def setup_logging(self):
        """Setup service logging"""
        os.makedirs('/app/logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('/app/logs/mt5_service.log', mode='a'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('MT5Service')
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"🛑 Received signal {signum}, shutting down...")
        self.stop_service()
        sys.exit(0)
    
    def start_collector(self):
        """Start the MT5 data collector process"""
        try:
            self.logger.info("🚀 Starting MT5 Real-Time Data Collector...")
            
            # Start the collector as a subprocess
            self.process = subprocess.Popen(
                [sys.executable, '/app/mt5_realtime_collector.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1
            )
            
            self.logger.info(f"✅ MT5 Collector started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to start MT5 collector: {str(e)}")
            return False
    
    def stop_collector(self):
        """Stop the MT5 data collector process"""
        if self.process:
            try:
                self.logger.info("🛑 Stopping MT5 collector...")
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    self.process.wait(timeout=10)
                    self.logger.info("✅ MT5 collector stopped gracefully")
                except subprocess.TimeoutExpired:
                    self.logger.warning("⚠️ Force killing MT5 collector...")
                    self.process.kill()
                    self.process.wait()
                    
            except Exception as e:
                self.logger.error(f"❌ Error stopping collector: {str(e)}")
            
            self.process = None
    
    def is_collector_running(self):
        """Check if the collector process is running"""
        if self.process is None:
            return False
        
        poll = self.process.poll()
        return poll is None
    
    def should_restart(self):
        """Determine if we should restart the collector"""
        current_time = time.time()
        
        # Remove restart times older than the window
        self.restart_times = [t for t in self.restart_times if current_time - t < self.restart_window]
        
        # Check if we've exceeded max restarts in the window
        if len(self.restart_times) >= self.max_restarts:
            self.logger.error(f"❌ Too many restarts ({len(self.restart_times)}) in the last hour. Stopping service.")
            return False
        
        return True
    
    def restart_collector(self):
        """Restart the MT5 collector"""
        if not self.should_restart():
            return False
        
        self.logger.info("🔄 Restarting MT5 collector...")
        
        # Stop current process
        self.stop_collector()
        
        # Wait a moment
        time.sleep(2)
        
        # Start new process
        if self.start_collector():
            self.restart_times.append(time.time())
            self.restart_count += 1
            self.logger.info(f"✅ MT5 collector restarted (restart #{self.restart_count})")
            return True
        else:
            self.logger.error("❌ Failed to restart MT5 collector")
            return False
    
    def monitor_collector(self):
        """Monitor the collector process and restart if needed"""
        while self.running:
            try:
                if not self.is_collector_running():
                    self.logger.warning("⚠️ MT5 collector is not running")
                    
                    if self.running:  # Only restart if service is supposed to be running
                        if not self.restart_collector():
                            self.logger.error("❌ Failed to restart collector, stopping service")
                            break
                
                # Check every 30 seconds
                time.sleep(30)
                
            except Exception as e:
                self.logger.error(f"❌ Error in monitor loop: {str(e)}")
                time.sleep(5)
    
    def start_service(self):
        """Start the service with monitoring"""
        self.running = True
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Start the collector
        if not self.start_collector():
            self.logger.error("❌ Failed to start initial collector process")
            return False
        
        # Start monitoring in a separate thread
        monitor_thread = threading.Thread(target=self.monitor_collector, daemon=True)
        monitor_thread.start()
        
        self.logger.info("🟢 MT5 Collector Service is running")
        self.logger.info("   - Real-time data collection every 30 seconds")
        self.logger.info("   - Automatic restart on failures")
        self.logger.info("   - Health checks every 5 minutes")
        self.logger.info("   - Data retention: 30 days")
        self.logger.info("   - Logs: /app/logs/mt5_collector.log")
        
        try:
            # Keep the main thread alive
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        
        return True
    
    def stop_service(self):
        """Stop the service"""
        self.running = False
        self.stop_collector()
        self.logger.info("🏁 MT5 Collector Service stopped")
    
    def status(self):
        """Get service status"""
        if self.is_collector_running():
            return {
                'status': 'running',
                'pid': self.process.pid if self.process else None,
                'restart_count': self.restart_count,
                'uptime': 'running'
            }
        else:
            return {
                'status': 'stopped',
                'pid': None,
                'restart_count': self.restart_count,
                'uptime': 'stopped'
            }

def main():
    """Main service execution"""
    print("🚀 FIDUS MT5 Real-Time Data Collection Service")
    print("=" * 50)
    print("This service ensures continuous MT5 data collection")
    print("for the FIDUS investment management production portal.")
    print()
    
    service = MT5CollectorService()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'status':
            status = service.status()
            print(f"Service Status: {status['status']}")
            print(f"PID: {status['pid']}")
            print(f"Restart Count: {status['restart_count']}")
            return
        
        elif command == 'start':
            print("Starting MT5 Collector Service...")
            service.start_service()
            return
        
        elif command == 'stop':
            print("Stopping MT5 Collector Service...")
            service.stop_service()
            return
        
        else:
            print(f"Unknown command: {command}")
            print("Usage: python mt5_collector_service.py [start|stop|status]")
            return
    
    # Default: start the service
    try:
        service.start_service()
    except Exception as e:
        print(f"❌ Service failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)