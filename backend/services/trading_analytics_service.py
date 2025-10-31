#!/usr/bin/env python3
"""
Trading Analytics Service for FIDUS Platform

This service provides comprehensive trading analytics across 3 levels:
1. Portfolio Level - Overall performance across all funds
2. Fund Level - Individual fund performance (BALANCE, CORE)
3. Manager Level - Manager-specific performance with risk-adjusted metrics

Key Features:
- Manager performance ranking
- Risk-adjusted returns (Sharpe, Sortino, Calmar ratios)
- Fund-level aggregation
- Portfolio-wide analytics
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TradingAnalyticsService:
    """
    Service for comprehensive trading analytics across portfolio, funds, and managers
    """
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        
        # Fund structure mapping
        self.FUND_STRUCTURE = {
            "BALANCE": {
                "aum": 100000,
                "accounts": [886557, 886066, 886602],
                "managers": [
                    {"id": "manager_tradinghub_gold", "account": 886557},
                    {"id": "manager_goldentrade", "account": 886066},
                    {"id": "manager_uno14", "account": 886602}
                ]
            },
            "CORE": {
                "aum": 18151.41,
                "accounts": [885822, 891234],
                "managers": [
                    {"id": "manager_cp_strategy", "account": 885822}
                    # 891234 is unassigned
                ]
            }
        }
    
    async def get_portfolio_analytics(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get portfolio-level analytics - highest level view
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            Portfolio-wide performance metrics
        """
        try:
            logger.info(f"📊 Calculating portfolio analytics for {period_days} days")
            
            # Get all funds performance
            balance_fund = await self.get_fund_analytics("BALANCE", period_days)
            core_fund = await self.get_fund_analytics("CORE", period_days)
            
            # Calculate portfolio totals
            total_aum = balance_fund["aum"] + core_fund["aum"]
            total_pnl = balance_fund["total_pnl"] + core_fund["total_pnl"]
            total_equity = balance_fund["total_equity"] + core_fund["total_equity"]
            
            # Calculate blended return
            balance_weight = balance_fund["aum"] / total_aum
            core_weight = core_fund["aum"] / total_aum
            blended_return = (balance_fund["weighted_return"] * balance_weight +
                            core_fund["weighted_return"] * core_weight)
            
            # Get all managers for portfolio stats
            all_managers = balance_fund["managers"] + core_fund["managers"]
            total_managers = len(all_managers)
            active_managers = len([m for m in all_managers if m["total_pnl"] != 0])
            
            return {
                "total_aum": round(total_aum, 2),
                "total_equity": round(total_equity, 2),
                "total_pnl": round(total_pnl, 2),
                "blended_return": round(blended_return, 2),
                "total_managers": total_managers,
                "active_managers": active_managers,
                "funds": {
                    "BALANCE": {
                        "aum": balance_fund["aum"],
                        "pnl": balance_fund["total_pnl"],
                        "return_pct": balance_fund["weighted_return"],
                        "managers_count": len(balance_fund["managers"])
                    },
                    "CORE": {
                        "aum": core_fund["aum"],
                        "pnl": core_fund["total_pnl"],
                        "return_pct": core_fund["weighted_return"],
                        "managers_count": len(core_fund["managers"])
                    }
                },
                "period_days": period_days,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate portfolio analytics: {str(e)}")
            raise
    
    async def get_fund_analytics(self, fund_name: str, period_days: int = 30) -> Dict[str, Any]:
        """
        Get fund-level analytics for BALANCE or CORE fund
        
        Args:
            fund_name: "BALANCE" or "CORE"
            period_days: Number of days to analyze
            
        Returns:
            Fund performance with manager breakdown
        """
        try:
            logger.info(f"📊 Calculating {fund_name} fund analytics")
            
            fund_config = self.FUND_STRUCTURE.get(fund_name)
            if not fund_config:
                raise ValueError(f"Unknown fund: {fund_name}")
            
            # Get managers performance
            managers_performance = []
            total_pnl = 0
            total_equity = 0
            
            for manager_config in fund_config["managers"]:
                manager_perf = await self.get_manager_analytics(
                    manager_config["id"],
                    manager_config["account"],
                    period_days
                )
                managers_performance.append(manager_perf)
                total_pnl += manager_perf["total_pnl"]
                total_equity += manager_perf["current_equity"]
            
            # Handle unassigned accounts (like 891234 in CORE)
            for account in fund_config["accounts"]:
                if account not in [m["account"] for m in fund_config["managers"]]:
                    # Get account data for unassigned account
                    account_data = await self.db.mt5_accounts.find_one({"account": account})
                    if account_data:
                        total_equity += account_data.get("equity", 0)
                        total_pnl += account_data.get("true_pnl", 0)
            
            # Calculate fund-level metrics
            aum = fund_config["aum"]
            weighted_return = (total_pnl / aum * 100) if aum > 0 else 0
            
            # Find best/worst performers
            if managers_performance:
                best_performer = max(managers_performance, key=lambda x: x["return_percentage"])
                worst_performer = min(managers_performance, key=lambda x: x["return_percentage"])
            else:
                best_performer = worst_performer = None
            
            return {
                "fund_name": fund_name,
                "aum": aum,
                "total_equity": round(total_equity, 2),
                "total_pnl": round(total_pnl, 2),
                "weighted_return": round(weighted_return, 2),
                "managers": managers_performance,
                "managers_count": len(managers_performance),
                "best_performer": best_performer["manager_name"] if best_performer else None,
                "worst_performer": worst_performer["manager_name"] if worst_performer else None,
                "period_days": period_days
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate fund analytics for {fund_name}: {str(e)}")
            raise
    
    async def get_manager_analytics(
        self,
        manager_id: str,
        account_num: int,
        period_days: int = 30
    ) -> Dict[str, Any]:
        """
        Get comprehensive manager-level analytics with risk-adjusted metrics
        
        Args:
            manager_id: Manager identifier
            account_num: Primary account number
            period_days: Number of days to analyze
            
        Returns:
            Complete manager performance with all risk metrics
        """
        try:
            logger.info(f"📊 Calculating manager analytics for {manager_id}")
            
            # Get manager document
            manager = await self.db.money_managers.find_one({"manager_id": manager_id})
            if not manager:
                raise ValueError(f"Manager not found: {manager_id}")
            
            # Get account data
            account_data = await self.db.mt5_accounts.find_one({"account": account_num})
            if not account_data:
                logger.warning(f"Account {account_num} not found, using zeros")
                account_data = {}
            
            # FIXED: Get correct allocation and P&L values
            balance = account_data.get("balance", 0)
            equity = account_data.get("equity", 0)
            target_amount = account_data.get("target_amount", 0)
            profit_withdrawals = account_data.get("profit_withdrawals", 0)
            
            # CORRECT CALCULATIONS:
            # Initial allocation = target_amount (what was originally allocated)
            initial_allocation = target_amount if target_amount > 0 else balance
            
            # TRUE P&L = Current Balance - Initial Allocation
            true_pnl = balance - initial_allocation
            
            # Current equity (for display)
            current_equity = equity
            
            # Calculate return percentage correctly
            return_percentage = (true_pnl / initial_allocation * 100) if initial_allocation > 0 else 0
            
            # Calculate drawdown percentage (how much was lost from initial)
            if initial_allocation > 0 and balance < initial_allocation:
                drawdown_pct = ((initial_allocation - balance) / initial_allocation * 100)
            else:
                drawdown_pct = 0
            
            # Get trades for this account (last N days)
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=period_days)
            
            trades_cursor = self.db.mt5_trades.find({
                "account": account_num,
                "close_time": {"$gte": start_date, "$lte": end_date}
            })
            trades = await trades_cursor.to_list(length=None)
            
            # Calculate trading statistics
            total_trades = len(trades)
            winning_trades = [t for t in trades if t["profit"] > 0]
            losing_trades = [t for t in trades if t["profit"] < 0]
            
            win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
            
            # Calculate profit factor
            gross_profit = sum(t["profit"] for t in winning_trades) if winning_trades else 0
            gross_loss = abs(sum(t["profit"] for t in losing_trades)) if losing_trades else 0
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 999.99
            
            # Calculate risk-adjusted returns
            sharpe_ratio = await self.calculate_sharpe_ratio(trades, initial_allocation)
            sortino_ratio = await self.calculate_sortino_ratio(trades, initial_allocation)
            # Use calculated drawdown from balance, not from trades
            max_drawdown = drawdown_pct
            calmar_ratio = await self.calculate_calmar_ratio(return_percentage, max_drawdown, period_days)
            
            # Calculate contribution to fund
            fund_name = account_data.get("fund_code", "Unknown")
            fund_aum = self.FUND_STRUCTURE.get(fund_name, {}).get("aum", initial_allocation)
            contribution_to_fund = (true_pnl / fund_aum * 100) if fund_aum > 0 else 0
            
            return {
                "manager_id": manager_id,
                "manager_name": manager.get("display_name", manager.get("name", "Unknown")),
                "strategy": manager.get("strategy_name", "Unknown"),
                "execution_type": manager.get("execution_type", "Unknown"),
                "risk_level": manager.get("risk_profile", "Unknown"),
                "account": account_num,
                "fund": fund_name,
                
                # Financial metrics
                "initial_allocation": round(initial_allocation, 2),
                "current_equity": round(current_equity, 2),
                "profit_withdrawals": round(profit_withdrawals, 2),
                "total_pnl": round(true_pnl, 2),
                "return_percentage": round(return_percentage, 2),
                "contribution_to_fund": round(contribution_to_fund, 2),
                
                # Trading statistics
                "total_trades": total_trades,
                "winning_trades": len(winning_trades),
                "losing_trades": len(losing_trades),
                "win_rate": round(win_rate, 2),
                "profit_factor": round(profit_factor, 2),
                
                # Risk-adjusted returns
                "sharpe_ratio": round(sharpe_ratio, 3),
                "sortino_ratio": round(sortino_ratio, 3),
                "max_drawdown_pct": round(max_drawdown, 2),
                "calmar_ratio": round(calmar_ratio, 3),
                
                # Status
                "status": "active" if true_pnl != 0 or total_trades > 0 else "inactive",
                "period_days": period_days
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate manager analytics for {manager_id}: {str(e)}")
            raise
    
    async def get_managers_ranking(self, period_days: int = 30) -> Dict[str, Any]:
        """
        Get all managers ranked by performance
        
        Args:
            period_days: Number of days to analyze
            
        Returns:
            Ranked list of all managers with complete metrics
        """
        try:
            logger.info(f"📊 Calculating managers ranking for {period_days} days")
            
            # Get all managers from both funds
            all_managers = []
            
            for fund_name, fund_config in self.FUND_STRUCTURE.items():
                for manager_config in fund_config["managers"]:
                    manager_perf = await self.get_manager_analytics(
                        manager_config["id"],
                        manager_config["account"],
                        period_days
                    )
                    all_managers.append(manager_perf)
            
            # Sort by return percentage (highest first)
            all_managers.sort(key=lambda x: x["return_percentage"], reverse=True)
            
            # Add ranking
            for idx, manager in enumerate(all_managers, 1):
                manager["rank"] = idx
            
            # Calculate portfolio-wide stats
            total_pnl = sum(m["total_pnl"] for m in all_managers)
            avg_return = sum(m["return_percentage"] for m in all_managers) / len(all_managers) if all_managers else 0
            avg_sharpe = sum(m["sharpe_ratio"] for m in all_managers) / len(all_managers) if all_managers else 0
            
            return {
                "managers": all_managers,
                "total_managers": len(all_managers),
                "total_pnl": round(total_pnl, 2),
                "average_return": round(avg_return, 2),
                "average_sharpe": round(avg_sharpe, 3),
                "best_performer": all_managers[0] if all_managers else None,
                "worst_performer": all_managers[-1] if all_managers else None,
                "period_days": period_days,
                "generated_at": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to calculate managers ranking: {str(e)}")
            raise
    
    async def calculate_sharpe_ratio(self, trades: List[Dict], allocation: float) -> float:
        """
        Calculate Sharpe Ratio for a series of trades
        
        Sharpe Ratio = (Average Return - Risk-Free Rate) / Standard Deviation of Returns
        
        Args:
            trades: List of trade documents
            allocation: Initial allocation
            
        Returns:
            Sharpe ratio
        """
        if not trades or allocation == 0:
            return 0.0
        
        # Calculate daily returns
        returns = [t["profit"] / allocation for t in trades]
        
        if len(returns) < 2:
            return 0.0
        
        # Calculate mean return
        mean_return = sum(returns) / len(returns)
        
        # Calculate standard deviation
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance) if variance > 0 else 0
        
        if std_dev == 0:
            return 0.0
        
        # Risk-free rate (assume 0 for simplicity)
        risk_free_rate = 0.0
        
        sharpe = (mean_return - risk_free_rate) / std_dev
        
        return sharpe
    
    async def calculate_sortino_ratio(self, trades: List[Dict], allocation: float) -> float:
        """
        Calculate Sortino Ratio (only considers downside deviation)
        
        Args:
            trades: List of trade documents
            allocation: Initial allocation
            
        Returns:
            Sortino ratio
        """
        if not trades or allocation == 0:
            return 0.0
        
        # Calculate returns
        returns = [t["profit"] / allocation for t in trades]
        
        if len(returns) < 2:
            return 0.0
        
        # Calculate mean return
        mean_return = sum(returns) / len(returns)
        
        # Calculate downside deviation (only negative returns)
        negative_returns = [r for r in returns if r < 0]
        
        if not negative_returns:
            return 999.99  # No downside, extremely high Sortino
        
        downside_variance = sum(r ** 2 for r in negative_returns) / len(negative_returns)
        downside_dev = math.sqrt(downside_variance)
        
        if downside_dev == 0:
            return 0.0
        
        sortino = mean_return / downside_dev
        
        return sortino
    
    async def calculate_max_drawdown(self, trades: List[Dict], allocation: float) -> float:
        """
        Calculate maximum drawdown percentage
        
        Args:
            trades: List of trade documents
            allocation: Initial allocation
            
        Returns:
            Max drawdown percentage
        """
        if not trades or allocation == 0:
            return 0.0
        
        # Build equity curve
        equity = allocation
        peak = allocation
        max_dd = 0.0
        
        for trade in sorted(trades, key=lambda x: x.get("close_time", datetime.now())):
            equity += trade["profit"]
            
            if equity > peak:
                peak = equity
            
            drawdown = ((peak - equity) / peak * 100) if peak > 0 else 0
            
            if drawdown > max_dd:
                max_dd = drawdown
        
        return max_dd
    
    async def calculate_calmar_ratio(
        self,
        return_percentage: float,
        max_drawdown: float,
        period_days: int
    ) -> float:
        """
        Calculate Calmar Ratio (Annualized Return / Max Drawdown)
        
        Args:
            return_percentage: Return percentage
            max_drawdown: Maximum drawdown percentage
            period_days: Period in days
            
        Returns:
            Calmar ratio
        """
        if max_drawdown == 0:
            return 999.99 if return_percentage > 0 else 0.0
        
        # Annualize the return
        annualized_return = (return_percentage / period_days) * 365
        
        calmar = abs(annualized_return / max_drawdown)
        
        return calmar
