"""
MT5 Deals Service
Handles deal history queries, analytics, rebate calculations, and manager performance

Phase 4A: Deal History Collection
"""

from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class MT5DealsService:
    def __init__(self, db):
        self.db = db
    
    async def get_deals(
        self,
        account_number: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        symbol: Optional[str] = None,
        deal_type: Optional[int] = None,
        limit: int = 1000
    ) -> List[Dict]:
        """
        Get deal history with optional filters
        
        Args:
            account_number: Filter by MT5 account
            start_date: Filter deals from this date
            end_date: Filter deals until this date
            symbol: Filter by trading symbol (e.g., 'EURUSD')
            deal_type: Filter by type (0=buy, 1=sell, 2=balance operation)
            limit: Maximum number of deals to return
        
        Returns:
            List of deal documents
        """
        try:
            # Build query filter
            query = {}
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            if symbol:
                query["symbol"] = symbol
            
            if deal_type is not None:
                query["type"] = deal_type
            
            # Query deals
            cursor = self.db.mt5_deals_history.find(query).sort("time", -1).limit(limit)
            deals = await cursor.to_list(length=limit)
            
            # Convert ObjectId to string for JSON serialization
            for deal in deals:
                if "_id" in deal:
                    deal["_id"] = str(deal["_id"])
                # Convert datetime to ISO string
                if "time" in deal:
                    deal["time"] = deal["time"].isoformat()
                if "synced_at" in deal:
                    deal["synced_at"] = deal["synced_at"].isoformat()
            
            logger.info(f"Retrieved {len(deals)} deals (filters: account={account_number}, symbol={symbol}, type={deal_type})")
            return deals
            
        except Exception as e:
            logger.error(f"Error retrieving deals: {e}")
            raise
    
    async def get_deals_summary(
        self,
        account_number: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict:
        """
        Get aggregated deal statistics
        
        Returns:
            {
                "total_deals": 1234,
                "total_volume": 156.5,  # Total lots traded
                "total_profit": 5432.10,
                "total_commission": -234.50,
                "buy_deals": 567,
                "sell_deals": 645,
                "balance_operations": 22,
                "symbols_traded": ["EURUSD", "GBPUSD", ...],
                "date_range": {"start": "2024-10-15", "end": "2025-01-15"}
            }
        """
        try:
            # Build query filter
            query = {}
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            # Aggregation pipeline
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "total_deals": {"$sum": 1},
                        "total_volume": {"$sum": "$volume"},
                        "total_profit": {"$sum": "$profit"},
                        "total_commission": {"$sum": "$commission"},
                        "total_swap": {"$sum": "$swap"},
                        "buy_deals": {
                            "$sum": {"$cond": [{"$eq": ["$type", 0]}, 1, 0]}
                        },
                        "sell_deals": {
                            "$sum": {"$cond": [{"$eq": ["$type", 1]}, 1, 0]}
                        },
                        "balance_operations": {
                            "$sum": {"$cond": [{"$eq": ["$type", 2]}, 1, 0]}
                        },
                        "symbols_traded": {"$addToSet": "$symbol"},
                        "earliest_deal": {"$min": "$time"},
                        "latest_deal": {"$max": "$time"}
                    }
                }
            ]
            
            result = await self.db.mt5_deals_history.aggregate(pipeline).to_list(length=1)
            
            if not result:
                return {
                    "total_deals": 0,
                    "total_volume": 0,
                    "total_profit": 0,
                    "total_commission": 0,
                    "total_swap": 0,
                    "buy_deals": 0,
                    "sell_deals": 0,
                    "balance_operations": 0,
                    "symbols_traded": [],
                    "date_range": None
                }
            
            summary = result[0]
            summary.pop("_id", None)
            
            # Convert datetime to ISO string
            if "earliest_deal" in summary and summary["earliest_deal"]:
                summary["earliest_deal"] = summary["earliest_deal"].isoformat()
            if "latest_deal" in summary and summary["latest_deal"]:
                summary["latest_deal"] = summary["latest_deal"].isoformat()
            
            # Add date range info
            summary["date_range"] = {
                "start": summary.get("earliest_deal"),
                "end": summary.get("latest_deal")
            }
            
            logger.info(f"Generated deals summary: {summary['total_deals']} deals, {summary['total_volume']:.2f} lots")
            return summary
            
        except Exception as e:
            logger.error(f"Error generating deals summary: {e}")
            raise
    
    async def calculate_rebates(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        account_number: Optional[int] = None,
        rebate_per_lot: float = 5.05
    ) -> Dict:
        """
        Calculate broker rebates based on trading volume
        
        Formula: total_volume (lots) × rebate_per_lot ($5.05)
        
        Returns:
            {
                "total_volume": 156.5,
                "rebate_per_lot": 5.05,
                "total_rebates": 790.825,
                "by_account": [
                    {"account": 886557, "volume": 50.5, "rebates": 255.025},
                    ...
                ],
                "by_symbol": [
                    {"symbol": "EURUSD", "volume": 80.0, "rebates": 404.00},
                    ...
                ],
                "date_range": {"start": "2024-10-15", "end": "2025-01-15"}
            }
        """
        try:
            # Build query filter (only trading deals, not balance operations)
            query = {"type": {"$in": [0, 1]}}  # 0=buy, 1=sell (exclude 2=balance)
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            # Total volume and rebates
            total_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": None,
                        "total_volume": {"$sum": "$volume"},
                        "total_commission": {"$sum": "$commission"}
                    }
                }
            ]
            
            total_result = await self.db.mt5_deals_history.aggregate(total_pipeline).to_list(length=1)
            total_volume = total_result[0]["total_volume"] if total_result else 0
            total_commission = total_result[0]["total_commission"] if total_result else 0
            total_rebates = total_volume * rebate_per_lot
            
            # Rebates by account
            by_account_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$account_number",
                        "account_name": {"$first": "$account_name"},
                        "fund_type": {"$first": "$fund_type"},
                        "volume": {"$sum": "$volume"},
                        "commission": {"$sum": "$commission"}
                    }
                },
                {"$sort": {"volume": -1}}
            ]
            
            by_account = await self.db.mt5_deals_history.aggregate(by_account_pipeline).to_list(length=None)
            
            for item in by_account:
                item["account"] = item.pop("_id")
                item["rebates"] = item["volume"] * rebate_per_lot
            
            # Rebates by symbol
            by_symbol_pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$symbol",
                        "volume": {"$sum": "$volume"},
                        "deals": {"$sum": 1}
                    }
                },
                {"$sort": {"volume": -1}}
            ]
            
            by_symbol = await self.db.mt5_deals_history.aggregate(by_symbol_pipeline).to_list(length=None)
            
            for item in by_symbol:
                item["symbol"] = item.pop("_id")
                item["rebates"] = item["volume"] * rebate_per_lot
            
            result = {
                "total_volume": round(total_volume, 2),
                "total_commission": round(total_commission, 2),
                "rebate_per_lot": rebate_per_lot,
                "total_rebates": round(total_rebates, 2),
                "by_account": by_account,
                "by_symbol": by_symbol[:10],  # Top 10 symbols
                "date_range": {
                    "start": start_date.isoformat() if start_date else None,
                    "end": end_date.isoformat() if end_date else None
                }
            }
            
            logger.info(f"Calculated rebates: {total_volume:.2f} lots = ${total_rebates:.2f}")
            return result
            
        except Exception as e:
            logger.error(f"Error calculating rebates: {e}")
            raise
    
    async def get_manager_performance(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get performance attribution by money manager (using magic number)
        
        Returns:
            [
                {
                    "magic": 100234,
                    "manager_name": "TradingHub Gold",
                    "total_deals": 234,
                    "total_volume": 45.5,
                    "total_profit": 2345.67,
                    "win_deals": 156,
                    "loss_deals": 78,
                    "win_rate": 66.67,
                    "avg_profit_per_deal": 10.02
                },
                ...
            ]
        """
        try:
            # Build query filter (only trading deals)
            query = {"type": {"$in": [0, 1]}}  # 0=buy, 1=sell
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            # Aggregation by magic number
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": "$magic",
                        "total_deals": {"$sum": 1},
                        "total_volume": {"$sum": "$volume"},
                        "total_profit": {"$sum": "$profit"},
                        "total_commission": {"$sum": "$commission"},
                        "win_deals": {
                            "$sum": {"$cond": [{"$gt": ["$profit", 0]}, 1, 0]}
                        },
                        "loss_deals": {
                            "$sum": {"$cond": [{"$lt": ["$profit", 0]}, 1, 0]}
                        },
                        "accounts_used": {"$addToSet": "$account_number"}
                    }
                },
                {"$sort": {"total_profit": -1}}
            ]
            
            results = await self.db.mt5_deals_history.aggregate(pipeline).to_list(length=None)
            
            # Calculate derived metrics and add manager names
            manager_map = {
                0: "Manual Trading",
                100234: "TradingHub Gold",
                100235: "GoldenTrade",
                100236: "UNO14 MAM",
                100237: "CP Strategy"
            }
            
            for item in results:
                magic = item.pop("_id")
                item["magic"] = magic
                item["manager_name"] = manager_map.get(magic, f"Manager {magic}")
                
                # Calculate win rate
                total_trades = item["win_deals"] + item["loss_deals"]
                item["win_rate"] = round((item["win_deals"] / total_trades * 100) if total_trades > 0 else 0, 2)
                
                # Average profit per deal
                item["avg_profit_per_deal"] = round(item["total_profit"] / item["total_deals"], 2) if item["total_deals"] > 0 else 0
                
                # Round values
                item["total_volume"] = round(item["total_volume"], 2)
                item["total_profit"] = round(item["total_profit"], 2)
                item["total_commission"] = round(item["total_commission"], 2)
            
            logger.info(f"Generated manager performance for {len(results)} managers")
            return results
            
        except Exception as e:
            logger.error(f"Error getting manager performance: {e}")
            raise
    
    async def get_balance_operations(
        self,
        account_number: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Get balance operations (type=2) for cash flow tracking
        
        Enhanced with detailed transfer classification
        
        Identifies:
        - Profit withdrawals
        - Deposits (bank wire, card, crypto, etc.)
        - Inter-account transfers
        - Interest payments
        
        Returns:
            [
                {
                    "ticket": 12345678,
                    "time": "2025-01-15T14:30:00Z",
                    "account_number": 886557,
                    "profit": 5000.00,
                    "comment": "Profit withdrawal",
                    "operation_type": "withdrawal",
                    "transfer_detail": "profit_withdrawal"  // NEW: Detailed classification
                },
                ...
            ]
        """
        try:
            # Query for balance operations only
            query = {"type": 2}  # 2 = balance operation
            
            if account_number:
                query["account_number"] = account_number
            
            if start_date:
                query.setdefault("time", {})["$gte"] = start_date
            
            if end_date:
                query.setdefault("time", {})["$lte"] = end_date
            
            cursor = self.db.mt5_deals_history.find(query).sort("time", -1)
            operations = await cursor.to_list(length=None)
            
            # Classify operations based on comment (ENHANCED)
            for op in operations:
                if "_id" in op:
                    op["_id"] = str(op["_id"])
                if "time" in op:
                    op["time"] = op["time"].isoformat()
                if "synced_at" in op:
                    op["synced_at"] = op["synced_at"].isoformat()
                
                # Classify operation type
                comment = op.get("comment", "").lower()
                profit = op.get("profit", 0)
                
                # Enhanced classification with transfer detail
                if "withdrawal" in comment or "profit" in comment:
                    op["operation_type"] = "withdrawal"
                    op["transfer_detail"] = "profit_withdrawal"
                elif "deposit" in comment:
                    op["operation_type"] = "deposit"
                    # Detailed deposit classification
                    if "bank" in comment or "wire" in comment:
                        op["transfer_detail"] = "bank_wire"
                    elif "card" in comment or "credit" in comment or "debit" in comment:
                        op["transfer_detail"] = "card_deposit"
                    elif "crypto" in comment or "bitcoin" in comment or "btc" in comment:
                        op["transfer_detail"] = "crypto_deposit"
                    elif "e-wallet" in comment or "paypal" in comment or "skrill" in comment:
                        op["transfer_detail"] = "ewallet_deposit"
                    else:
                        op["transfer_detail"] = "other_deposit"
                elif "transfer" in comment:
                    op["operation_type"] = "transfer"
                    # Detailed transfer classification
                    if "internal" in comment or "inter" in comment:
                        op["transfer_detail"] = "internal_transfer"
                    elif "between" in comment:
                        op["transfer_detail"] = "inter_account_transfer"
                    else:
                        op["transfer_detail"] = "other_transfer"
                elif "interest" in comment or "separation" in comment:
                    op["operation_type"] = "interest"
                    op["transfer_detail"] = "interest_payment"
                elif "bonus" in comment or "rebate" in comment:
                    op["operation_type"] = "credit"
                    op["transfer_detail"] = "bonus_rebate"
                elif profit > 0:
                    op["operation_type"] = "credit"
                    op["transfer_detail"] = "other_credit"
                elif profit < 0:
                    op["operation_type"] = "debit"
                    op["transfer_detail"] = "other_debit"
                else:
                    op["operation_type"] = "other"
                    op["transfer_detail"] = "unclassified"
            
            logger.info(f"Retrieved {len(operations)} balance operations with enhanced classification")
            return operations
            
        except Exception as e:
            logger.error(f"Error retrieving balance operations: {e}")
            raise
    
    async def get_daily_pnl(
        self,
        account_number: Optional[int] = None,
        days: int = 30
    ) -> List[Dict]:
        """
        Get daily P&L for equity curve charting
        
        Returns:
            [
                {"date": "2025-01-15", "pnl": 234.56, "volume": 5.5, "deals": 12},
                {"date": "2025-01-14", "pnl": -45.32, "volume": 3.2, "deals": 8},
                ...
            ]
        """
        try:
            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Build query
            query = {
                "type": {"$in": [0, 1]},  # Trading deals only
                "time": {"$gte": start_date, "$lte": end_date}
            }
            
            if account_number:
                query["account_number"] = account_number
            
            # Aggregation by date
            pipeline = [
                {"$match": query},
                {
                    "$group": {
                        "_id": {
                            "$dateToString": {"format": "%Y-%m-%d", "date": "$time"}
                        },
                        "pnl": {"$sum": "$profit"},
                        "volume": {"$sum": "$volume"},
                        "deals": {"$sum": 1},
                        "commission": {"$sum": "$commission"},
                        "swap": {"$sum": "$swap"}
                    }
                },
                {"$sort": {"_id": 1}}
            ]
            
            results = await self.db.mt5_deals_history.aggregate(pipeline).to_list(length=None)
            
            # Format results
            daily_pnl = []
            for item in results:
                daily_pnl.append({
                    "date": item["_id"],
                    "pnl": round(item["pnl"], 2),
                    "volume": round(item["volume"], 2),
                    "deals": item["deals"],
                    "commission": round(item["commission"], 2),
                    "swap": round(item["swap"], 2)
                })
            
            logger.info(f"Generated daily P&L for {len(daily_pnl)} days")
            return daily_pnl
            
        except Exception as e:
            logger.error(f"Error calculating daily P&L: {e}")
            raise
    
    async def calculate_account_growth_metrics(
        self,
        account_number: int,
        days: int = 30
    ) -> Dict:
        """
        Calculate comprehensive growth metrics for an account
        
        Returns:
            {
                "roi": 12.5,  # Return on investment %
                "max_drawdown": -5.2,  # Maximum drawdown %
                "max_drawdown_amount": -1250.50,
                "sharpe_ratio": 1.85,  # Risk-adjusted return
                "win_rate": 65.5,  # Win rate %
                "profit_factor": 2.15,  # Gross profit / Gross loss
                "avg_win": 250.50,
                "avg_loss": -150.25,
                "total_trades": 145,
                "winning_trades": 95,
                "losing_trades": 50,
                "period_days\": 30
            }
        """
        try:\n            # Calculate date range
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=days)
            
            # Get equity snapshots for drawdown and ROI calculation
            equity_cursor = self.db.mt5_equity_snapshots.find({
                \"account_number\": account_number,
                \"timestamp\": {\"$gte\": start_date, \"$lte\": end_date}
            }).sort(\"timestamp\", 1)
            
            equity_snapshots = await equity_cursor.to_list(length=None)
            
            # Get deals for trading metrics
            deals_cursor = self.db.mt5_deals_history.find({
                \"account_number\": account_number,
                \"type\": {\"$in\": [0, 1]},  # Trading deals only
                \"time\": {\"$gte\": start_date, \"$lte\": end_date}
            }).sort(\"time\", 1)
            
            deals = await deals_cursor.to_list(length=None)
            
            # Initialize metrics
            metrics = {
                \"roi\": 0,
                \"max_drawdown\": 0,
                \"max_drawdown_amount\": 0,
                \"sharpe_ratio\": 0,
                \"win_rate\": 0,
                \"profit_factor\": 0,
                \"avg_win\": 0,
                \"avg_loss\": 0,
                \"total_trades\": 0,
                \"winning_trades\": 0,
                \"losing_trades\": 0,
                \"period_days\": days,
                \"starting_equity\": 0,
                \"ending_equity\": 0
            }
            
            # Calculate equity-based metrics
            if equity_snapshots and len(equity_snapshots) > 0:
                equities = [s[\"equity\"] for s in equity_snapshots]
                starting_equity = equities[0]
                ending_equity = equities[-1]
                
                metrics[\"starting_equity\"] = round(starting_equity, 2)
                metrics[\"ending_equity\"] = round(ending_equity, 2)
                
                # ROI
                if starting_equity > 0:
                    roi = ((ending_equity - starting_equity) / starting_equity) * 100
                    metrics[\"roi\"] = round(roi, 2)
                
                # Max Drawdown
                peak_equity = equities[0]
                max_drawdown = 0
                max_drawdown_pct = 0
                
                for equity in equities:
                    if equity > peak_equity:
                        peak_equity = equity
                    
                    drawdown = equity - peak_equity
                    if drawdown < max_drawdown:
                        max_drawdown = drawdown
                        max_drawdown_pct = (drawdown / peak_equity * 100) if peak_equity > 0 else 0
                
                metrics[\"max_drawdown\"] = round(max_drawdown_pct, 2)
                metrics[\"max_drawdown_amount\"] = round(max_drawdown, 2)
                
                # Sharpe Ratio (simplified: assumes risk-free rate = 0)
                if len(equities) > 1:
                    daily_returns = []
                    for i in range(1, len(equities)):
                        daily_return = (equities[i] - equities[i-1]) / equities[i-1]
                        daily_returns.append(daily_return)
                    
                    if daily_returns:
                        avg_return = sum(daily_returns) / len(daily_returns)
                        
                        # Calculate standard deviation
                        variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
                        std_dev = variance ** 0.5
                        
                        # Sharpe ratio (annualized)
                        if std_dev > 0:
                            sharpe = (avg_return / std_dev) * (252 ** 0.5)  # Annualized
                            metrics[\"sharpe_ratio\"] = round(sharpe, 2)
            
            # Calculate trading metrics
            if deals:
                total_trades = len(deals)
                winning_trades = [d for d in deals if d[\"profit\"] > 0]
                losing_trades = [d for d in deals if d[\"profit\"] < 0]
                
                metrics[\"total_trades\"] = total_trades
                metrics[\"winning_trades\"] = len(winning_trades)
                metrics[\"losing_trades\"] = len(losing_trades)
                
                # Win Rate
                if total_trades > 0:
                    win_rate = (len(winning_trades) / total_trades) * 100
                    metrics[\"win_rate\"] = round(win_rate, 2)
                
                # Average Win/Loss
                if winning_trades:
                    avg_win = sum(d[\"profit\"] for d in winning_trades) / len(winning_trades)
                    metrics[\"avg_win\"] = round(avg_win, 2)
                
                if losing_trades:
                    avg_loss = sum(d[\"profit\"] for d in losing_trades) / len(losing_trades)
                    metrics[\"avg_loss\"] = round(avg_loss, 2)
                
                # Profit Factor
                gross_profit = sum(d[\"profit\"] for d in winning_trades)
                gross_loss = abs(sum(d[\"profit\"] for d in losing_trades))
                
                if gross_loss > 0:
                    profit_factor = gross_profit / gross_loss
                    metrics[\"profit_factor\"] = round(profit_factor, 2)
            
            logger.info(f\"Calculated growth metrics for account {account_number}: ROI={metrics['roi']}%, Sharpe={metrics['sharpe_ratio']}\")
            return metrics
            
        except Exception as e:
            logger.error(f\"Error calculating growth metrics: {e}\")
            raise
