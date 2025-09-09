#!/usr/bin/env python3
"""
MT5 Monitor Service Starter
==========================

Starts and manages the MT5 real-time monitoring service as a background process.
"""

import asyncio
import logging
import signal
import sys
import os
from mt5_realtime_monitor import MT5RealtimeMonitor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('MT5Service')

class MT5MonitorService:
    def __init__(self):
        self.monitor = MT5RealtimeMonitor()
        self.running = True
        
    async def start(self):
        """Start the monitoring service"""
        logger.info("🚀 Starting MT5 Monitor Service")
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            await self.monitor.start_monitoring()
        except Exception as e:
            logger.error(f"❌ Service error: {str(e)}")
        finally:
            logger.info("🏁 MT5 Monitor Service stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"📡 Received signal {signum}")
        self.monitor.stop_monitoring()
        self.running = False

async def main():
    """Main service function"""
    service = MT5MonitorService()
    await service.start()

if __name__ == "__main__":
    # Create logs directory
    os.makedirs('/app/logs', exist_ok=True)
    
    # Run the service
    asyncio.run(main())