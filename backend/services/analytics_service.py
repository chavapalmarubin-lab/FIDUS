"""
Analytics Service
Handles all trading analytics calculations
ALL calculations done in backend - frontend only displays
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for trading analytics - Single source of truth"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_trading_metrics(
        self,
        account_number: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict:
        """
        Calculate COMPLETE trading metrics with ALL calculations done here.
        Returns display-ready strings - frontend does ZERO calculations.
        
        Returns:
            {
                "total_pnl": "36264.44",
                "win_rate": "65.50",
                "profit_factor": "2.15",
                "avg_trade": "36.26",
                ...
            }
        
        All numbers returned as strings with .2f format - NO .toFixed() needed in frontend
        """
        try:
            logger.info(f"📊 Calculating trading metrics for account: {account_number or 'ALL'}")
            
            # Build match filter
            match_filter = {}
            if account_number and account_number != 'all':
                match_filter["account_number"] = int(account_number)
            
            if start_date or end_date:
                match_filter["time"] = {}
                if start_date:
                    match_filter["time"]["$gte"] = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                if end_date:
                    match_filter["time"]["$lte"] = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            
            # Get all trades
            trades = await self.db.mt5_deals_history.find(match_filter).to_list(length=None)
            
            if not trades:
                logger.warning(f"No trades found for account: {account_number or 'ALL'}")
                return self._empty_metrics()
            
            # Filter only actual trades (not balance operations)
            actual_trades = [
                t for t in trades 
                if t.get("entry") in [0, 1]  # IN or OUT
            ]
            
            if not actual_trades:
                return self._empty_metrics()
            
            # Calculate ALL metrics in BACKEND
            total_pnl = sum(t.get("profit", 0) for t in actual_trades)
            total_commission = sum(t.get("commission", 0) for t in actual_trades)
            total_swap = sum(t.get("swap", 0) for t in actual_trades)
            
            # Classify trades
            winning_trades = [t for t in actual_trades if t.get("profit", 0) > 0]
            losing_trades = [t for t in actual_trades if t.get("profit", 0) < 0]
            
            win_count = len(winning_trades)
            loss_count = len(losing_trades)
            total_count = len(actual_trades)
            
            # Win rate calculation
            win_rate = (win_count / total_count * 100) if total_count > 0 else 0.0
            
            # Profit calculations
            gross_profit = sum(t.get("profit", 0) for t in winning_trades)
            gross_loss = abs(sum(t.get("profit", 0) for t in losing_trades))
            
            # Profit factor
            profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0.0
            
            # Average trade
            avg_trade = (total_pnl / total_count) if total_count > 0 else 0.0
            avg_win = (gross_profit / win_count) if win_count > 0 else 0.0
            avg_loss = (gross_loss / loss_count) if loss_count > 0 else 0.0
            
            # Calculate max drawdown
            equity_curve = []
            running_equity = 0.0
            for trade in sorted(actual_trades, key=lambda x: x.get("time", datetime.now(timezone.utc))):
                running_equity += trade.get("profit", 0)
                equity_curve.append(running_equity)
            
            peak = equity_curve[0] if equity_curve else 0.0
            max_drawdown = 0.0
            for equity in equity_curve:
                if equity > peak:
                    peak = equity
                drawdown = peak - equity
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
            
            # Recovery factor
            recovery_factor = (total_pnl / max_drawdown) if max_drawdown > 0 else 0.0
            
            # Sharpe ratio (simplified)
            if total_count > 1:
                returns = [t.get("profit", 0) for t in actual_trades]
                avg_return = sum(returns) / len(returns)
                variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
                std_dev = variance ** 0.5
                sharpe_ratio = (avg_return / std_dev) if std_dev > 0 else 0.0
            else:
                sharpe_ratio = 0.0
            
            # Volume calculations
            total_volume = sum(t.get("volume", 0) for t in actual_trades)
            
            # Format ALL numbers as strings with .2f - NO frontend .toFixed() needed
            metrics = {
                "total_pnl": f"{total_pnl:.2f}",
                "win_rate": f"{win_rate:.2f}",
                "profit_factor": f"{profit_factor:.2f}",
                "avg_trade": f"{avg_trade:.2f}",
                "avg_win": f"{avg_win:.2f}",
                "avg_loss": f"{avg_loss:.2f}",
                "max_drawdown": f"{max_drawdown:.2f}",
                "recovery_factor": f"{recovery_factor:.2f}",
                "sharpe_ratio": f"{sharpe_ratio:.2f}",
                "total_trades": total_count,
                "winning_trades": win_count,
                "losing_trades": loss_count,
                "gross_profit": f"{gross_profit:.2f}",
                "gross_loss": f"{gross_loss:.2f}",
                "total_volume": f"{total_volume:.2f}",
                "total_commission": f"{total_commission:.2f}",
                "total_swap": f"{total_swap:.2f}"
            }
            
            logger.info(f"✅ Trading metrics calculated: Total P&L = ${metrics['total_pnl']}, Win Rate = {metrics['win_rate']}%, Trades = {total_count}")
            
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Error calculating trading metrics: {str(e)}")
            raise
    
    def _empty_metrics(self) -> Dict:
        """Return empty metrics with proper string formatting"""
        return {
            "total_pnl": "0.00",
            "win_rate": "0.00",
            "profit_factor": "0.00",
            "avg_trade": "0.00",
            "avg_win": "0.00",
            "avg_loss": "0.00",
            "max_drawdown": "0.00",
            "recovery_factor": "0.00",
            "sharpe_ratio": "0.00",
            "total_trades": 0,
            "winning_trades": 0,
            "losing_trades": 0,
            "gross_profit": "0.00",
            "gross_loss": "0.00",
            "total_volume": "0.00",
            "total_commission": "0.00",
            "total_swap": "0.00"
        }
