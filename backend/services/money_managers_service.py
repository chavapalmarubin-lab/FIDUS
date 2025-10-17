"""
Money Managers Service
Handles all money manager performance calculations
ALL calculations done in backend - frontend only displays
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class MoneyManagersService:
    """Service for money manager performance - Single source of truth"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_manager_performance(
        self,
        client_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Calculate COMPLETE money manager performance with ALL calculations done here.
        Groups by strategy provider and calculates all metrics.
        Returns display-ready data - frontend does ZERO calculations.
        
        Returns:
            {
                "managers": [
                    {
                        "manager_name": "GoldenTrade Provider",
                        "total_pnl": 692.22,
                        "trade_count": 45,
                        "win_rate": 60.00,
                        "winning_trades": 27,
                        "losing_trades": 18,
                        "account_count": 3,
                        "accounts": ["886066", "891234", "891215"]
                    },
                    ...
                ],
                "total_managers": 3
            }
        """
        try:
            logger.info(f"📊 Calculating money manager performance for client: {client_id or 'ALL'}")
            
            # Get accounts with their providers FOR ALEJANDRO ONLY
            match_filter = {
                "is_active": True,
                "client_id": {"$in": ["client_alejandro", "client_alejandro_mariscal"]}
            }
            if client_id:
                match_filter["client_id"] = {"$in": [client_id, "client_alejandro", "client_alejandro_mariscal"]}
            
            accounts = await self.db.mt5_account_config.find(match_filter).to_list(length=None)
            
            if not accounts:
                logger.warning("No active MT5 accounts found")
                return {
                    "managers": [],
                    "total_managers": 0
                }
            
            # Build time filter for deals
            time_filter = {}
            if start_date or end_date:
                time_filter["time"] = {}
                if start_date:
                    time_filter["time"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if end_date:
                    time_filter["time"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Group by provider and calculate metrics
            manager_stats = {}
            
            for account in accounts:
                provider = account.get("name", "Unknown Provider")  # Using 'name' as provider identifier
                account_number = account["account"]
                
                # Get trades for this account
                deal_filter = {
                    "account_number": account_number,
                    "entry": {"$in": [0, 1]},  # Only actual trades
                    **time_filter
                }
                
                trades = await self.db.mt5_deals_history.find(deal_filter).to_list(length=None)
                
                if provider not in manager_stats:
                    manager_stats[provider] = {
                        "manager_name": provider,
                        "total_pnl": 0.0,
                        "trade_count": 0,
                        "winning_trades": 0,
                        "losing_trades": 0,
                        "total_volume": 0.0,
                        "accounts": []
                    }
                
                # Calculate for this account in BACKEND
                account_pnl = sum(t.get("profit", 0) for t in trades)
                account_volume = sum(t.get("volume", 0) for t in trades)
                winning = len([t for t in trades if t.get("profit", 0) > 0])
                losing = len([t for t in trades if t.get("profit", 0) < 0])
                
                manager_stats[provider]["total_pnl"] += account_pnl
                manager_stats[provider]["total_volume"] += account_volume
                manager_stats[provider]["trade_count"] += len(trades)
                manager_stats[provider]["winning_trades"] += winning
                manager_stats[provider]["losing_trades"] += losing
                manager_stats[provider]["accounts"].append(str(account_number))
            
            # Calculate win rates and format data in BACKEND
            managers = []
            for provider, stats in manager_stats.items():
                total_trades = stats["trade_count"]
                win_rate = (stats["winning_trades"] / total_trades * 100) if total_trades > 0 else 0.0
                
                managers.append({
                    "manager_name": provider,
                    "total_pnl": round(stats["total_pnl"], 2),
                    "total_volume": round(stats["total_volume"], 2),
                    "trade_count": total_trades,
                    "win_rate": round(win_rate, 2),
                    "winning_trades": stats["winning_trades"],
                    "losing_trades": stats["losing_trades"],
                    "account_count": len(stats["accounts"]),
                    "accounts": stats["accounts"]
                })
            
            # Sort by total P&L (highest first)
            managers.sort(key=lambda x: x["total_pnl"], reverse=True)
            
            result = {
                "managers": managers,
                "total_managers": len(managers)
            }
            
            logger.info(f"✅ Manager performance calculated: {len(managers)} managers found")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Error calculating manager performance: {str(e)}")
            raise
    
    async def get_manager_details(self, manager_name: str) -> Dict:
        """
        Get detailed performance for a specific manager with ALL calculations.
        """
        try:
            logger.info(f"📊 Getting details for manager: {manager_name}")
            
            # Get accounts for this manager
            accounts = await self.db.mt5_account_config.find({
                "name": manager_name,
                "is_active": True
            }).to_list(length=None)
            
            if not accounts:
                return {
                    "manager_name": manager_name,
                    "total_pnl": 0.0,
                    "account_count": 0,
                    "accounts": []
                }
            
            # Calculate metrics for each account
            account_details = []
            total_pnl = 0.0
            
            for account in accounts:
                account_number = account["account"]
                
                trades = await self.db.mt5_deals_history.find({
                    "account_number": account_number,
                    "entry": {"$in": [0, 1]}
                }).to_list(length=None)
                
                account_pnl = sum(t.get("profit", 0) for t in trades)
                total_pnl += account_pnl
                
                account_details.append({
                    "account_number": str(account_number),
                    "fund_code": account.get("fund_type", ""),  # ✅ PHASE 2: Translate fund_type → fund_code
                    "pnl": round(account_pnl, 2),
                    "trade_count": len(trades)
                })
            
            return {
                "manager_name": manager_name,
                "total_pnl": round(total_pnl, 2),
                "account_count": len(accounts),
                "accounts": account_details
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting manager details for {manager_name}: {str(e)}")
            raise
