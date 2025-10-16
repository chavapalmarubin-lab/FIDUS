"""
Investment Management Service
Handles all investment-related calculations
ALL calculations done in backend - frontend only displays
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Dict, List

logger = logging.getLogger(__name__)


class InvestmentService:
    """Service for investment calculations - Single source of truth"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def get_investments_summary(self) -> Dict:
        """
        Get complete investment summary with ALL calculations done here.
        Returns display-ready data - frontend does ZERO calculations.
        
        Returns:
            {
                "total_aum": 118151.41,
                "total_investments": 2,
                "active_clients": 1,
                "avg_investment": 59075.71,
                "by_fund": [...]
            }
        """
        try:
            logger.info("📊 Calculating investments summary")
            
            # Aggregate all active investments FOR ALEJANDRO ONLY
            pipeline = [
                {
                    "$match": {
                        "client_id": {"$in": ["client_alejandro", "client_alejandro_mariscal"]},
                        "status": {"$in": ["active", "active_incubation"]}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_aum": {"$sum": "$principal_amount"},
                        "investment_count": {"$sum": 1},
                        "unique_clients": {"$addToSet": "$client_id"}
                    }
                }
            ]
            
            result = await self.db.investments.aggregate(pipeline).to_list(length=1)
            
            if not result:
                logger.warning("No active investments found")
                return {
                    "total_aum": 0.0,
                    "total_investments": 0,
                    "active_clients": 0,
                    "avg_investment": 0.0,
                    "by_fund": []
                }
            
            data = result[0]
            total_aum = data["total_aum"]
            investment_count = data["investment_count"]
            client_count = len(data["unique_clients"])
            
            # Calculate average in BACKEND
            avg_investment = (total_aum / client_count) if client_count > 0 else 0.0
            
            # Get breakdown by fund FOR ALEJANDRO ONLY
            fund_pipeline = [
                {
                    "$match": {
                        "client_id": {"$in": ["client_alejandro", "client_alejandro_mariscal"]},
                        "status": {"$in": ["active", "active_incubation"]}
                    }
                },
                {
                    "$group": {
                        "_id": "$fund_code",
                        "principal_amount": {"$sum": "$principal_amount"},
                        "unique_clients": {"$addToSet": "$client_id"}
                    }
                }
            ]
            
            fund_results = await self.db.investments.aggregate(fund_pipeline).to_list(length=None)
            
            by_fund = [
                {
                    "fund_code": fund["_id"],
                    "principal_amount": round(fund["principal_amount"], 2),
                    "client_count": len(fund["unique_clients"])
                }
                for fund in fund_results
            ]
            
            # Sort by principal amount (largest first)
            by_fund.sort(key=lambda x: x["principal_amount"], reverse=True)
            
            summary = {
                "total_aum": round(total_aum, 2),
                "total_investments": investment_count,
                "active_clients": client_count,
                "avg_investment": round(avg_investment, 2),
                "by_fund": by_fund
            }
            
            logger.info(f"✅ Investments summary: Total AUM = ${summary['total_aum']:,.2f}, Clients = {client_count}, Investments = {investment_count}")
            
            return summary
            
        except Exception as e:
            logger.error(f"❌ Error calculating investments summary: {str(e)}")
            raise
    
    async def get_client_investments(self, client_id: str) -> Dict:
        """
        Get complete investment data for a specific client with ALL calculations.
        """
        try:
            logger.info(f"📊 Getting investments for client: {client_id}")
            
            # Get all investments for this client
            investments = await self.db.investments.find({
                "client_id": client_id,
                "status": {"$in": ["active", "active_incubation"]}
            }).to_list(length=None)
            
            if not investments:
                return {
                    "client_id": client_id,
                    "total_invested": 0.0,
                    "investment_count": 0,
                    "investments": []
                }
            
            # Calculate total in BACKEND
            total_invested = sum(inv.get("principal_amount", 0) for inv in investments)
            
            # Enrich investment data
            enriched_investments = []
            for inv in investments:
                enriched_investments.append({
                    "investment_id": inv.get("investment_id"),
                    "fund_code": inv.get("fund_code"),
                    "principal_amount": round(inv.get("principal_amount", 0), 2),
                    "current_value": round(inv.get("current_value", 0), 2),
                    "total_interest_earned": round(inv.get("total_interest_earned", 0), 2),
                    "deposit_date": inv.get("deposit_date"),
                    "status": inv.get("status")
                })
            
            return {
                "client_id": client_id,
                "total_invested": round(total_invested, 2),
                "investment_count": len(investments),
                "investments": enriched_investments
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting client investments for {client_id}: {str(e)}")
            raise
