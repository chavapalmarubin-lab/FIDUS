#!/usr/bin/env python3
"""
FIDUS MT5 Bridge Service Monitoring Dashboard
Comprehensive monitoring and health checking for MT5 bridge service on Windows VPS
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime, timezone
from typing import Dict, Any, Optional
import logging

class MT5BridgeMonitor:
    """MT5 Bridge Service Monitoring System"""
    
    def __init__(self):
        self.bridge_url = "http://217.197.163.11:8000"
        self.api_key = "fidus-mt5-bridge-key-2025-secure"
        self.session = None
        self.monitoring_data = {
            "last_check": None,
            "connectivity_status": "unknown",
            "service_health": {},
            "mt5_status": {},
            "performance_metrics": {},
            "alerts": []
        }
    
    async def initialize(self):
        """Initialize monitoring session"""
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=30),
            headers={"X-API-Key": self.api_key}
        )
    
    async def cleanup(self):
        """Cleanup monitoring session"""
        if self.session:
            await self.session.close()
    
    async def check_connectivity(self) -> Dict[str, Any]:
        """Check basic connectivity to MT5 bridge service"""
        try:
            start_time = time.time()
            async with self.session.get(f"{self.bridge_url}/") as response:
                response_time = (time.time() - start_time) * 1000
                
                if response.status == 200:
                    data = await response.json()
                    return {
                        "status": "connected",
                        "response_time_ms": round(response_time, 2),
                        "service_info": data,
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                else:
                    return {
                        "status": "error", 
                        "error": f"HTTP {response.status}",
                        "response_time_ms": round(response_time, 2),
                        "timestamp": datetime.now(timezone.utc).isoformat()
                    }
                    
        except asyncio.TimeoutError:
            return {
                "status": "timeout",
                "error": "Connection timeout after 30 seconds",
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
        except Exception as e:
            return {
                "status": "unreachable",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
    
    async def check_health(self) -> Dict[str, Any]:
        """Check MT5 bridge service health"""
        try:
            async with self.session.get(f"{self.bridge_url}/health") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "status": "unhealthy",
                        "error": f"Health check failed with HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "status": "unreachable", 
                "error": str(e)
            }
    
    async def check_mt5_status(self) -> Dict[str, Any]:
        """Check MT5 terminal and connection status"""
        try:
            async with self.session.get(f"{self.bridge_url}/api/mt5/status") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "mt5_available": False,
                        "error": f"MT5 status check failed with HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "mt5_available": False,
                "error": str(e)
            }
    
    async def check_mt5_terminal_info(self) -> Dict[str, Any]:
        """Get MT5 terminal information"""
        try:
            async with self.session.get(f"{self.bridge_url}/api/mt5/terminal/info") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    return {
                        "error": f"Terminal info failed with HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    async def run_comprehensive_check(self) -> Dict[str, Any]:
        """Run comprehensive monitoring check"""
        print("🔍 Running comprehensive MT5 Bridge monitoring...")
        
        # 1. Connectivity Check
        print("  📡 Checking connectivity...")
        connectivity = await self.check_connectivity()
        
        # 2. Health Check
        print("  🏥 Checking service health...")
        health = await self.check_health()
        
        # 3. MT5 Status Check
        print("  💹 Checking MT5 status...")
        mt5_status = await self.check_mt5_status()
        
        # 4. Terminal Info (if MT5 is available)
        terminal_info = {}
        if mt5_status.get("mt5_available"):
            print("  🖥️  Checking MT5 terminal info...")
            terminal_info = await self.check_mt5_terminal_info()
        
        # 5. Generate alerts
        alerts = self.generate_alerts(connectivity, health, mt5_status)
        
        # Compile monitoring report
        report = {
            "monitoring_timestamp": datetime.now(timezone.utc).isoformat(),
            "connectivity": connectivity,
            "service_health": health,
            "mt5_status": mt5_status,
            "mt5_terminal": terminal_info,
            "alerts": alerts,
            "summary": self.generate_summary(connectivity, health, mt5_status)
        }
        
        # Update internal state
        self.monitoring_data = report
        
        return report
    
    def generate_alerts(self, connectivity: Dict, health: Dict, mt5_status: Dict) -> list:
        """Generate monitoring alerts"""
        alerts = []
        
        # Connectivity alerts
        if connectivity["status"] != "connected":
            alerts.append({
                "level": "critical",
                "type": "connectivity",
                "message": f"MT5 Bridge service unreachable: {connectivity.get('error', 'Unknown error')}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        elif connectivity.get("response_time_ms", 0) > 5000:
            alerts.append({
                "level": "warning", 
                "type": "performance",
                "message": f"Slow response time: {connectivity['response_time_ms']}ms",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # MT5 alerts
        if not mt5_status.get("mt5_available", False):
            alerts.append({
                "level": "warning",
                "type": "mt5_connection", 
                "message": "MT5 terminal not available or not connected",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        # Health alerts
        if health.get("status") == "unhealthy":
            alerts.append({
                "level": "critical",
                "type": "service_health",
                "message": f"Service health check failed: {health.get('error', 'Unknown error')}",
                "timestamp": datetime.now(timezone.utc).isoformat()
            })
        
        return alerts
    
    def generate_summary(self, connectivity: Dict, health: Dict, mt5_status: Dict) -> Dict[str, Any]:
        """Generate monitoring summary"""
        return {
            "overall_status": "healthy" if connectivity["status"] == "connected" and not any(alert["level"] == "critical" for alert in self.generate_alerts(connectivity, health, mt5_status)) else "degraded",
            "connectivity_status": connectivity["status"],
            "mt5_available": mt5_status.get("mt5_available", False),
            "service_responsive": connectivity["status"] == "connected",
            "alerts_count": len(self.generate_alerts(connectivity, health, mt5_status)),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    
    def print_monitoring_report(self, report: Dict[str, Any]):
        """Print formatted monitoring report"""
        print("\n" + "="*80)
        print("🚀 FIDUS MT5 Bridge Service Monitoring Report")
        print("="*80)
        
        # Summary
        summary = report["summary"]
        status_emoji = "🟢" if summary["overall_status"] == "healthy" else "🟡" if summary["overall_status"] == "degraded" else "🔴"
        print(f"\n📊 OVERALL STATUS: {status_emoji} {summary['overall_status'].upper()}")
        print(f"📡 Connectivity: {summary['connectivity_status']}")
        print(f"💹 MT5 Available: {'✅' if summary['mt5_available'] else '❌'}")
        print(f"⚠️  Active Alerts: {summary['alerts_count']}")
        
        # Connectivity Details
        print(f"\n🔍 CONNECTIVITY DETAILS:")
        conn = report["connectivity"]
        print(f"  Status: {conn['status']}")
        if conn.get("response_time_ms"):
            print(f"  Response Time: {conn['response_time_ms']}ms")
        if conn.get("service_info"):
            service_info = conn["service_info"]
            print(f"  Service: {service_info.get('service', 'Unknown')}")
            print(f"  Version: {service_info.get('version', 'Unknown')}")
        
        # MT5 Details  
        print(f"\n💹 MT5 STATUS:")
        mt5 = report["mt5_status"]
        print(f"  MT5 Available: {'✅' if mt5.get('mt5_available') else '❌'}")
        print(f"  MT5 Initialized: {'✅' if mt5.get('mt5_initialized') else '❌'}")
        if mt5.get("error"):
            print(f"  Error: {mt5['error']}")
        
        # Terminal Info
        if report["mt5_terminal"] and not report["mt5_terminal"].get("error"):
            print(f"\n🖥️  MT5 TERMINAL:")
            terminal = report["mt5_terminal"]
            if terminal.get("name"):
                print(f"  Name: {terminal['name']}")
            if terminal.get("connected") is not None:
                print(f"  Connected: {'✅' if terminal['connected'] else '❌'}")
        
        # Alerts
        if report["alerts"]:
            print(f"\n⚠️  ALERTS:")
            for alert in report["alerts"]:
                level_emoji = "🔴" if alert["level"] == "critical" else "🟡" if alert["level"] == "warning" else "🔵"
                print(f"  {level_emoji} [{alert['level'].upper()}] {alert['message']}")
        else:
            print(f"\n✅ NO ALERTS")
        
        print(f"\n🕐 Last Updated: {summary['last_updated']}")
        print("="*80)

# Monitoring CLI interface
async def main():
    """Main monitoring function"""
    monitor = MT5BridgeMonitor()
    
    try:
        await monitor.initialize()
        
        # Run monitoring check
        report = await monitor.run_comprehensive_check()
        
        # Print report
        monitor.print_monitoring_report(report)
        
        # Save report to file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = f"/app/mt5_monitoring_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Report saved to: {report_file}")
        
        return report
        
    except Exception as e:
        print(f"❌ Monitoring failed: {e}")
        return None
    
    finally:
        await monitor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())