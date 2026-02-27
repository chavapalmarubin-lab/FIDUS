#!/usr/bin/env python3
"""
Live Demo Analytics Service for FIDUS Platform

This service provides comprehensive trading analytics for LIVE DEMO accounts.
These are MT5 accounts used to evaluate potential money managers before 
allocating real capital to them.

Key Features:
- Manager performance ranking for demo accounts
- Risk-adjusted returns (Sharpe, Sortino, Calmar ratios)
- Evaluation metrics for manager candidates
- Completely separate from REAL trading accounts
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LiveDemoAnalyticsService:
    """
    Service for comprehensive trading analytics for LIVE DEMO accounts only.
    Completely separate from real trading accounts.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Live Demo account structure - accounts being evaluated
        self.DEMO_FUND_STRUCTURE = {
            "DEMO": {
                "aum": 0,  # Demo accounts don't have real AUM
                "accounts": [],  # Will be populated dynamically
                "managers": []
            }
        }
    
    async def get_demo_accounts_config(self) -> List[Dict]:
        """Get all live demo accounts from the database"""
        try:
            # Query for accounts marked as live_demo type
            demo_accounts = await self.db.mt5_accounts.find({
                "account_type": "live_demo"
            }).to_list(length=100)
            
            # Also check mt5_account_config for live_demo accounts
            config_accounts = await self.db.mt5_account_config.find({
                "account_type": "live_demo"
            }).to_list(length=100)
            
            # Merge account numbers
            account_numbers = set()
            for acc in demo_accounts:
                account_numbers.add(acc.get("account"))
            for acc in config_accounts:
                account_numbers.add(acc.get("account"))
            
            return list(account_numbers)
        except Exception as e:
            logger.error(f"Error getting demo accounts config: {e}")
            return []
    
    async def get_managers_ranking(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get all LIVE DEMO managers ranked by performance.
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            Complete manager rankings with risk-adjusted metrics for demo accounts only
        """
        try:
            logger.info(f"📊 Calculating LIVE DEMO manager rankings for {period_days} days")
            
            # Get all demo accounts
            demo_accounts = await self.db.mt5_accounts.find({
                "account_type": "live_demo"
            }).to_list(length=100)
            
            if not demo_accounts:
                logger.warning("No live demo accounts found")
                return {
                    "managers": [],
                    "total_pnl": 0,
                    "average_return": 0,
                    "best_performer": None,
                    "worst_performer": None,
                    "period_days": period_days,
                    "account_type": "live_demo"
                }
            
            managers_data = []
            
            for account in demo_accounts:
                account_num = account.get("account")
                if not account_num:
                    continue
                
                # Calculate performance metrics
                performance = await self._calculate_manager_performance(account, period_days)
                
                managers_data.append({
                    "manager_id": f"demo_{account_num}",
                    "manager_name": account.get("manager_name", f"Demo Manager {account_num}"),
                    "account": account_num,
                    "fund": "DEMO",
                    "account_type": "live_demo",
                    "status": account.get("status", "evaluating"),
                    "evaluation_notes": account.get("evaluation_notes", ""),
                    **performance
                })
            
            # Sort by return percentage
            managers_data.sort(key=lambda x: x.get("return_percentage", 0), reverse=True)
            
            # Calculate aggregates
            total_pnl = sum(m.get("total_pnl", 0) for m in managers_data)
            avg_return = sum(m.get("return_percentage", 0) for m in managers_data) / len(managers_data) if managers_data else 0
            
            best = managers_data[0]["manager_name"] if managers_data else None
            worst = managers_data[-1]["manager_name"] if managers_data else None
            
            return {
                "managers": managers_data,
                "total_pnl": round(total_pnl, 2),
                "average_return": round(avg_return, 2),
                "best_performer": best,
                "worst_performer": worst,
                "period_days": period_days,
                "account_type": "live_demo",
                "total_accounts": len(managers_data)
            }
            
        except Exception as e:
            logger.error(f"Error getting demo managers ranking: {e}")
            return {
                "managers": [],
                "total_pnl": 0,
                "average_return": 0,
                "best_performer": None,
                "worst_performer": None,
                "period_days": period_days,
                "account_type": "live_demo",
                "error": str(e)
            }
    
    async def _calculate_manager_performance(self, account: Dict, period_days: int) -> Dict[str, Any]:
        """Calculate performance metrics for a single demo manager"""
        try:
            account_num = account.get("account")
            initial_allocation = account.get("initial_allocation", 0)
            current_equity = account.get("equity", 0)
            current_balance = account.get("balance", 0)
            
            # Calculate P&L
            total_pnl = current_equity - initial_allocation if initial_allocation > 0 else account.get("profit", 0)
            
            # Calculate return percentage
            return_pct = (total_pnl / initial_allocation * 100) if initial_allocation > 0 else 0
            
            # Get deal history for risk metrics
            deals = await self.db.mt5_deals.find({
                "account": account_num
            }).sort("time", -1).limit(500).to_list(length=500)
            
            # Calculate trading statistics
            total_trades = len(deals)
            winning_trades = len([d for d in deals if d.get("profit", 0) > 0])
            losing_trades = len([d for d in deals if d.get("profit", 0) < 0])
            win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate profit factor
            gross_profit = sum(d.get("profit", 0) for d in deals if d.get("profit", 0) > 0)
            gross_loss = abs(sum(d.get("profit", 0) for d in deals if d.get("profit", 0) < 0))
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else (999.99 if gross_profit > 0 else 0)
            
            # Calculate drawdown (simplified)
            max_drawdown_pct = account.get("max_drawdown_pct", 0)
            if not max_drawdown_pct and initial_allocation > 0:
                # Calculate from equity vs peak
                peak_equity = max(initial_allocation, current_equity)
                drawdown = peak_equity - current_equity
                max_drawdown_pct = (drawdown / peak_equity * 100) if peak_equity > 0 else 0
            
            # Calculate risk-adjusted metrics (simplified)
            # These would normally require daily returns data
            sharpe_ratio = self._estimate_sharpe_ratio(return_pct, max_drawdown_pct, period_days)
            sortino_ratio = self._estimate_sortino_ratio(return_pct, max_drawdown_pct, period_days)
            calmar_ratio = (return_pct / max_drawdown_pct) if max_drawdown_pct > 0 else 0
            
            return {
                "initial_allocation": round(initial_allocation, 2),
                "current_equity": round(current_equity, 2),
                "current_balance": round(current_balance, 2),
                "total_pnl": round(total_pnl, 2),
                "return_percentage": round(return_pct, 2),
                "profit_withdrawals": account.get("profit_withdrawals", 0),
                "total_trades": total_trades,
                "winning_trades": winning_trades,
                "losing_trades": losing_trades,
                "win_rate": round(win_rate, 2),
                "profit_factor": round(min(profit_factor, 999.99), 2),
                "max_drawdown_pct": round(max_drawdown_pct, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "sortino_ratio": round(sortino_ratio, 2),
                "calmar_ratio": round(calmar_ratio, 2),
                "last_sync": account.get("last_sync", account.get("updated_at"))
            }
            
        except Exception as e:
            logger.error(f"Error calculating demo performance: {e}")
            return {
                "initial_allocation": 0,
                "current_equity": 0,
                "current_balance": 0,
                "total_pnl": 0,
                "return_percentage": 0,
                "profit_withdrawals": 0,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "profit_factor": 0,
                "max_drawdown_pct": 0,
                "sharpe_ratio": 0,
                "sortino_ratio": 0,
                "calmar_ratio": 0,
                "error": str(e)
            }
    
    def _estimate_sharpe_ratio(self, return_pct: float, drawdown_pct: float, period_days: int) -> float:
        """Estimate Sharpe ratio from return and drawdown"""
        # Simplified estimation: Sharpe ≈ (Annual Return - Risk Free) / Volatility
        # Using drawdown as proxy for volatility
        annual_return = return_pct * (365 / period_days) if period_days > 0 else 0
        risk_free = 5.0  # Assume 5% risk-free rate
        volatility_proxy = max(drawdown_pct * 2, 10)  # Use 2x drawdown as vol proxy
        
        sharpe = (annual_return - risk_free) / volatility_proxy if volatility_proxy > 0 else 0
        return max(min(sharpe, 5), -5)  # Cap between -5 and 5
    
    def _estimate_sortino_ratio(self, return_pct: float, drawdown_pct: float, period_days: int) -> float:
        """Estimate Sortino ratio from return and drawdown"""
        # Similar to Sharpe but only considers downside deviation
        annual_return = return_pct * (365 / period_days) if period_days > 0 else 0
        risk_free = 5.0
        downside_vol = max(drawdown_pct * 1.5, 8)  # Use 1.5x drawdown as downside vol
        
        sortino = (annual_return - risk_free) / downside_vol if downside_vol > 0 else 0
        return max(min(sortino, 5), -5)
    
    async def get_manager_details(self, account_num: int, period_days: int = 30) -> Dict[str, Any]:
        """Get detailed analytics for a specific demo manager"""
        try:
            account = await self.db.mt5_accounts.find_one({
                "account": account_num,
                "account_type": "live_demo"
            })
            
            if not account:
                return {
                    "success": False,
                    "error": f"Demo account {account_num} not found",
                    "manager": None
                }
            
            performance = await self._calculate_manager_performance(account, period_days)
            
            return {
                "success": True,
                "manager": {
                    "manager_id": f"demo_{account_num}",
                    "manager_name": account.get("manager_name", f"Demo Manager {account_num}"),
                    "account": account_num,
                    "fund": "DEMO",
                    "account_type": "live_demo",
                    "status": account.get("status", "evaluating"),
                    "evaluation_notes": account.get("evaluation_notes", ""),
                    **performance
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting demo manager details: {e}")
            return {
                "success": False,
                "error": str(e),
                "manager": None
            }
