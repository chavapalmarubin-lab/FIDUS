"""
Portfolio Service
Handles all portfolio-related calculations including fund allocations
ALL calculations done in backend - frontend only displays
"""

import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from typing import Dict, List

logger = logging.getLogger(__name__)


class PortfolioService:
    """Service for portfolio calculations - Single source of truth"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def calculate_fund_allocations(self, client_id: str) -> Dict:
        """
        Calculate complete fund allocation with ALL calculations done here.
        Returns display-ready data - frontend does ZERO calculations.
        
        Returns:
            {
                "total_aum": 118151.41,
                "funds": [
                    {
                        "fund_code": "CORE",
                        "amount": 18151.41,
                        "percentage": 15.37,
                        "accounts": ["885822", "891234"],
                        "account_count": 2
                    },
                    ...
                ]
            }
        """
        try:
            logger.info(f"📊 Calculating fund allocations for client: {client_id}")
            
            # MongoDB aggregation - ALL calculations in database
            # CRITICAL: Filter by Alejandro's client_id variations
            pipeline = [
                # Match active investments for this client
                {
                    "$match": {
                        "client_id": {"$in": [client_id, "client_alejandro", "client_alejandro_mariscal"]},
                        "status": {"$in": ["active", "active_incubation"]}
                    }
                },
                # Group by fund code and calculate totals
                {
                    "$group": {
                        "_id": "$fund_code",
                        "total_amount": {"$sum": "$principal_amount"},
                        "investment_count": {"$sum": 1}
                    }
                },
                # Calculate grand total for percentage calculations
                {
                    "$group": {
                        "_id": None,
                        "grand_total": {"$sum": "$total_amount"},
                        "funds": {
                            "$push": {
                                "fund_code": "$_id",
                                "amount": "$total_amount",
                                "investment_count": "$investment_count"
                            }
                        }
                    }
                }
            ]
            
            result = await self.db.investments.aggregate(pipeline).to_list(length=1)
            
            if not result or not result[0].get("funds"):
                logger.warning(f"No investments found for client: {client_id}")
                return {
                    "total_aum": 0.0,
                    "funds": []
                }
            
            data = result[0]
            grand_total = data["grand_total"]
            funds = data["funds"]
            
            # Get MT5 accounts for each fund to include account numbers
            enriched_funds = []
            for fund in funds:
                fund_code = fund["fund_code"]
                
                # Get accounts for this fund
                mt5_accounts = await self.db.mt5_account_config.find({
                    "client_id": client_id,
                    "fund_type": fund_code,
                    "is_active": True
                }).to_list(length=None)
                
                account_numbers = [str(acc["account"]) for acc in mt5_accounts]
                
                # Calculate percentage in BACKEND
                amount = fund["amount"]
                percentage = round((amount / grand_total * 100), 2) if grand_total > 0 else 0.0
                
                enriched_funds.append({
                    "fund_code": fund_code,
                    "amount": round(amount, 2),
                    "percentage": percentage,
                    "accounts": account_numbers,
                    "account_count": len(account_numbers)
                })
            
            # Sort by amount (largest first)
            enriched_funds.sort(key=lambda x: x["amount"], reverse=True)
            
            result_data = {
                "total_aum": round(grand_total, 2),
                "funds": enriched_funds
            }
            
            logger.info(f"✅ Fund allocations calculated: Total AUM = ${result_data['total_aum']:,.2f}, Funds = {len(enriched_funds)}")
            
            return result_data
            
        except Exception as e:
            logger.error(f"❌ Error calculating fund allocations: {str(e)}")
            raise
    
    async def get_fund_summary(self, fund_code: str) -> Dict:
        """
        Get complete summary for a specific fund with ALL calculations.
        """
        try:
            pipeline = [
                {
                    "$match": {
                        "fund_code": fund_code,
                        "status": {"$in": ["active", "active_incubation"]}
                    }
                },
                {
                    "$group": {
                        "_id": None,
                        "total_principal": {"$sum": "$principal_amount"},
                        "investment_count": {"$sum": 1},
                        "unique_clients": {"$addToSet": "$client_id"}
                    }
                }
            ]
            
            result = await self.db.investments.aggregate(pipeline).to_list(length=1)
            
            if not result:
                return {
                    "fund_code": fund_code,
                    "total_principal": 0.0,
                    "investment_count": 0,
                    "client_count": 0
                }
            
            data = result[0]
            
            return {
                "fund_code": fund_code,
                "total_principal": round(data["total_principal"], 2),
                "investment_count": data["investment_count"],
                "client_count": len(data["unique_clients"])
            }
            
        except Exception as e:
            logger.error(f"❌ Error getting fund summary for {fund_code}: {str(e)}")
            raise
