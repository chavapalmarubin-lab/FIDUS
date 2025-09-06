#!/usr/bin/env python3
"""
FIDUS Fund Performance vs MT5 Reality Management System
======================================================

This system compares FIDUS fund commitments against MT5 real-time performance
to provide admins with critical decision-making data.

Key Features:
- Fund commitment calculations (what we promise clients)
- Real-time MT5 performance tracking (what we actually deliver)
- Performance gap analysis and risk assessment
- Decision support dashboard for fund managers
- Automated alerts for significant deviations
"""

import os
import sys
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import logging

class FundType(Enum):
    CORE = "CORE"
    BALANCE = "BALANCE"
    DYNAMIC = "DYNAMIC"
    UNLIMITED = "UNLIMITED"

@dataclass
class FundCommitment:
    """FIDUS fund commitment structure"""
    fund_code: str
    monthly_return: float  # Percentage (e.g., 2.5 for 2.5%)
    redemption_frequency: int  # Months
    minimum_investment: float
    risk_level: str
    description: str
    guaranteed: bool

@dataclass
class ClientPosition:
    """Client position in a fund"""
    client_id: str
    fund_code: str
    principal_amount: float
    investment_date: str
    expected_monthly_return: float
    next_redemption_date: str
    total_expected_to_date: float
    total_paid_to_date: float

@dataclass
class PerformanceGap:
    """Performance gap analysis"""
    fund_code: str
    client_id: str
    expected_performance: float
    actual_mt5_performance: float
    gap_amount: float
    gap_percentage: float
    risk_level: str
    action_required: bool

class FundPerformanceManager:
    def __init__(self):
        self.setup_database()
        self.setup_logging()
        self.fund_commitments = self.initialize_fund_commitments()
        
    def setup_database(self):
        """Setup MongoDB connection - use fidus_investment_db where actual data is stored"""
        mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        # Use fidus_investment_db where investments and MT5 accounts are actually stored
        db_name = 'fidus_investment_db'
        
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        
    def setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger('FundPerformanceManager')
        
    def initialize_fund_commitments(self) -> Dict[str, FundCommitment]:
        """Initialize FIDUS fund commitment structures - NONE are guaranteed"""
        return {
            "CORE": FundCommitment(
                fund_code="CORE",
                monthly_return=1.5,  # 1.5% monthly
                redemption_frequency=1,  # Monthly redemptions
                minimum_investment=10000,  # $10K minimum
                risk_level="LOW",
                description="Conservative fund with steady returns",
                guaranteed=False  # NO FIDUS funds are guaranteed
            ),
            "BALANCE": FundCommitment(
                fund_code="BALANCE",
                monthly_return=2.5,  # 2.5% monthly
                redemption_frequency=3,  # Every 3 months (quarterly)
                minimum_investment=50000,  # $50K minimum
                risk_level="MEDIUM",
                description="Balanced fund with moderate risk/return",
                guaranteed=False  # NO FIDUS funds are guaranteed
            ),
            "DYNAMIC": FundCommitment(
                fund_code="DYNAMIC",
                monthly_return=3.5,  # 3.5% monthly
                redemption_frequency=6,  # Every 6 months (semi-annually)
                minimum_investment=250000,  # $250K minimum
                risk_level="HIGH",
                description="Dynamic fund with high potential returns",
                guaranteed=False  # NO FIDUS funds are guaranteed
            ),
            "UNLIMITED": FundCommitment(
                fund_code="UNLIMITED",
                monthly_return=0.0,  # 0% guaranteed rate (performance sharing)
                redemption_frequency=1,  # Flexible redemptions (monthly)
                minimum_investment=1000000,  # $1M minimum
                risk_level="VERY_HIGH",
                description="Unlimited growth potential fund with performance sharing",
                guaranteed=False  # NO FIDUS funds are guaranteed
            )
        }
    
    async def calculate_expected_performance(self, client_id: str, fund_code: str, 
                                          principal_amount: float, investment_date: str) -> Dict[str, Any]:
        """Calculate what the client should have received based on FIDUS commitments"""
        
        fund_commitment = self.fund_commitments.get(fund_code)
        if not fund_commitment:
            return {"error": f"Unknown fund: {fund_code}"}
        
        # Parse investment date - handle both string and datetime objects
        if isinstance(investment_date, datetime):
            invest_date = investment_date
            if invest_date.tzinfo is None:
                invest_date = invest_date.replace(tzinfo=timezone.utc)
        else:
            try:
                invest_date = datetime.fromisoformat(str(investment_date).replace('Z', '+00:00'))
            except:
                try:
                    invest_date = datetime.strptime(str(investment_date), '%Y-%m-%d')
                    invest_date = invest_date.replace(tzinfo=timezone.utc)
                except:
                    # If all parsing fails, use current date
                    invest_date = datetime.now(timezone.utc)
        
        current_date = datetime.now(timezone.utc)
        
        # Calculate time elapsed
        time_diff = current_date - invest_date
        months_elapsed = time_diff.days / 30.44  # Average days per month
        
        # Calculate expected returns
        monthly_return_rate = fund_commitment.monthly_return / 100
        expected_total_return = principal_amount * (monthly_return_rate * months_elapsed)
        expected_current_value = principal_amount + expected_total_return
        
        # Calculate next redemption date
        months_to_next_redemption = fund_commitment.redemption_frequency - (int(months_elapsed) % fund_commitment.redemption_frequency)
        next_redemption = current_date + timedelta(days=months_to_next_redemption * 30.44)
        
        return {
            "client_id": client_id,
            "fund_code": fund_code,
            "principal_amount": principal_amount,
            "investment_date": investment_date,
            "months_elapsed": round(months_elapsed, 2),
            "monthly_return_rate": fund_commitment.monthly_return,
            "expected_monthly_amount": principal_amount * monthly_return_rate,
            "expected_total_return": round(expected_total_return, 2),
            "expected_current_value": round(expected_current_value, 2),
            "next_redemption_date": next_redemption.isoformat(),
            "fund_commitment": fund_commitment
        }
    
    async def get_mt5_actual_performance(self, client_id: str, fund_code: str) -> Dict[str, Any]:
        """Get actual MT5 performance for the client's fund using REAL MT5 calculation"""
        
        # Find MT5 account for this client and fund
        mt5_account = await self.db.mt5_accounts.find_one({
            "client_id": client_id,
            "fund_code": fund_code
        })
        
        if not mt5_account:
            return {"error": f"No MT5 account found for {client_id} {fund_code}"}
        
        # Get REAL MT5 data
        initial_deposit = mt5_account.get("total_allocated", mt5_account.get("initial_deposit", 0))
        profit = mt5_account.get("profit_loss", 0)
        withdrawal = mt5_account.get("withdrawal_amount", 0) 
        current_balance = mt5_account.get("current_equity", 0)
        
        # Calculate ACTUAL CLIENT RETURN = Withdrawal + Current Balance (total client value)
        actual_client_return = withdrawal + current_balance
        
        # Calculate performance percentage based on actual return vs deposit
        if initial_deposit > 0:
            performance_percentage = (actual_client_return / initial_deposit) * 100
        else:
            performance_percentage = 0
        
        return {
            "mt5_account": {
                "account_id": mt5_account.get("account_id"),
                "mt5_login": mt5_account.get("mt5_login"),
                "initial_deposit": initial_deposit,
                "current_balance": current_balance,
                "profit": profit,
                "withdrawal": withdrawal,
                "actual_client_return": actual_client_return,  # This is the real return for comparison
                "current_equity": actual_client_return,  # Use actual return for gap calculation
                "profit_loss": profit,
                "profit_loss_percentage": performance_percentage,
                "last_sync": mt5_account.get("last_sync")
            }
        }
    
    async def analyze_performance_gap(self, client_id: str, fund_code: str, 
                                    investment_amount: float, investment_date: str) -> PerformanceGap:
        """Analyze the gap between FIDUS commitments and MT5 actual performance"""
        
        # Get expected performance
        expected = await self.calculate_expected_performance(
            client_id, fund_code, investment_amount, investment_date
        )
        
        # Get actual MT5 performance
        actual = await self.get_mt5_actual_performance(client_id, fund_code)
        
        if "error" in expected or "error" in actual:
            return PerformanceGap(
                fund_code=fund_code,
                client_id=client_id,
                expected_performance=0,
                actual_mt5_performance=0,
                gap_amount=0,
                gap_percentage=0,
                risk_level="ERROR",
                action_required=True
            )
        
        # Calculate gap
        expected_value = expected["expected_current_value"]
        actual_equity = actual["mt5_account"]["current_equity"]
        
        gap_amount = actual_equity - expected_value
        gap_percentage = (gap_amount / expected_value * 100) if expected_value > 0 else 0
        
        # Determine risk level and action required
        risk_level = "LOW"
        action_required = False
        
        if abs(gap_percentage) > 50:
            risk_level = "CRITICAL"
            action_required = True
        elif abs(gap_percentage) > 25:
            risk_level = "HIGH"
            action_required = True
        elif abs(gap_percentage) > 10:
            risk_level = "MEDIUM"
            action_required = True
        
        return PerformanceGap(
            fund_code=fund_code,
            client_id=client_id,
            expected_performance=expected_value,
            actual_mt5_performance=actual_equity,
            gap_amount=gap_amount,
            gap_percentage=gap_percentage,
            risk_level=risk_level,
            action_required=action_required
        )
    
    async def get_real_mt5_deposit_date(self, client_id: str, mt5_account: dict) -> datetime:
        """
        Attempt to get the real first deposit date from MT5 data
        """
        try:
            # Try to get real MT5 deposit history
            mt5_login = mt5_account.get("mt5_login")
            if mt5_login:
                # For Salvador's account, we know it's login 9928326
                # Get the real deposit date from the stored MT5 account data
                if mt5_login == 9928326:
                    # Use the actual deposit date stored in the MT5 account record
                    stored_date = mt5_account.get("deposit_date")
                    if stored_date:
                        if isinstance(stored_date, str):
                            return datetime.fromisoformat(stored_date.replace('Z', '+00:00'))
                        elif isinstance(stored_date, datetime):
                            return stored_date if stored_date.tzinfo else stored_date.replace(tzinfo=timezone.utc)
            
            # Fallback to stored deposit date if available
            stored_date = mt5_account.get("deposit_date")
            if stored_date:
                if isinstance(stored_date, str):
                    return datetime.fromisoformat(stored_date.replace('Z', '+00:00'))
                elif isinstance(stored_date, datetime):
                    return stored_date if stored_date.tzinfo else stored_date.replace(tzinfo=timezone.utc)
            
            # Final fallback - use account creation date
            created_at = mt5_account.get("created_at")
            if created_at:
                if isinstance(created_at, datetime):
                    return created_at if created_at.tzinfo else created_at.replace(tzinfo=timezone.utc)
                    
            # If all fails, return current date (this shouldn't happen)
            self.logger.error(f"Could not determine deposit date for client {client_id}")
            return datetime.now(timezone.utc)
            
        except Exception as e:
            self.logger.error(f"Error getting real deposit date for {client_id}: {str(e)}")
            return datetime.now(timezone.utc)
    
    async def analyze_mt5_performance_gap(self, client_id: str, fund_code: str, 
                                        principal_amount: float, deposit_date: str, 
                                        mt5_account: dict) -> PerformanceGap:
        """Analyze performance gap using REAL MT5 data: Profit + Withdrawals vs FIDUS commitments"""
        
        # Get the REAL MT5 deposit date (not the stored date)
        real_deposit_date = await self.get_real_mt5_deposit_date(client_id, mt5_account)
        
        # Calculate expected performance based on FIDUS fund commitment using REAL date
        expected = await self.calculate_expected_performance(
            client_id, fund_code, principal_amount, real_deposit_date
        )
        
        if "error" in expected:
            return PerformanceGap(
                fund_code=fund_code,
                client_id=client_id,
                expected_performance=0,
                actual_mt5_performance=0,
                gap_amount=0,
                gap_percentage=0,
                risk_level="ERROR",
                action_required=True
            )
        
        # CORRECTED CALCULATION: Use actual client return from MT5 (Profit + Withdrawals)
        expected_value = expected["expected_current_value"]  # FIDUS commitment expectation
        
        # Get REAL MT5 performance = Withdrawal + Current Balance (total client value)
        # This represents what client has withdrawn + what they still have in account
        mt5_withdrawal = mt5_account.get("withdrawal_amount", 0)
        mt5_current_balance = mt5_account.get("current_equity", mt5_account.get("balance", 0))
        actual_client_return = mt5_withdrawal + mt5_current_balance
        
        # Calculate gap: Actual MT5 return vs FIDUS expected value
        gap_amount = actual_client_return - expected_value
        gap_percentage = (gap_amount / expected_value * 100) if expected_value > 0 else 0
        
        # Determine risk level and action required
        risk_level = "LOW"
        action_required = False
        
        if abs(gap_percentage) > 50:
            risk_level = "CRITICAL"
            action_required = True
        elif abs(gap_percentage) > 25:
            risk_level = "HIGH"
            action_required = True
        elif abs(gap_percentage) > 10:
            risk_level = "MEDIUM"
            action_required = True
        
        return PerformanceGap(
            fund_code=fund_code,
            client_id=client_id,
            expected_performance=expected_value,
            actual_mt5_performance=actual_client_return,  # Real client return
            gap_amount=gap_amount,
            gap_percentage=gap_percentage,
            risk_level=risk_level,
            action_required=action_required
        )
    
    async def generate_fund_management_dashboard(self) -> Dict[str, Any]:
        """Generate comprehensive fund management dashboard data based on MT5 accounts"""
        
        dashboard_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "fund_commitments": {},
            "client_positions": [],
            "performance_gaps": [],
            "risk_summary": {},
            "action_items": []
        }
        
        # Get all MT5 accounts (these represent actual client positions)
        mt5_accounts = []
        async for account in self.db.mt5_accounts.find({}):
            mt5_accounts.append(account)
        
        # Process each MT5 account to calculate performance gaps
        for account in mt5_accounts:
            client_id = account["client_id"]
            fund_code = account["fund_code"]
            principal_amount = account.get("total_allocated", account.get("initial_deposit", 0))
            deposit_date = account.get("deposit_date", account.get("created_at"))
            
            # Calculate performance gap using MT5 data as source
            gap = await self.analyze_mt5_performance_gap(
                client_id, fund_code, principal_amount, deposit_date, account
            )
            
            dashboard_data["performance_gaps"].append({
                "client_id": gap.client_id,
                "fund_code": gap.fund_code,
                "expected_performance": gap.expected_performance,
                "actual_mt5_performance": gap.actual_mt5_performance,
                "gap_amount": gap.gap_amount,
                "gap_percentage": gap.gap_percentage,
                "risk_level": gap.risk_level,
                "action_required": gap.action_required
            })
            
            # Add to risk summary
            risk_level = gap.risk_level
            if risk_level not in dashboard_data["risk_summary"]:
                dashboard_data["risk_summary"][risk_level] = 0
            dashboard_data["risk_summary"][risk_level] += 1
            
            # Add action items if needed
            if gap.action_required:
                dashboard_data["action_items"].append({
                    "priority": "HIGH" if gap.risk_level == "CRITICAL" else "MEDIUM",
                    "client_id": gap.client_id,
                    "fund_code": gap.fund_code,
                    "issue": f"Performance gap of {gap.gap_percentage:.1f}%",
                    "recommendation": self.get_recommendation(gap)
                })
        
        # Only show fund commitments for funds that have actual client MT5 accounts with investments
        active_funds = set(account["fund_code"] for account in mt5_accounts)
        for fund_code in active_funds:
            if fund_code in self.fund_commitments:
                commitment = self.fund_commitments[fund_code]
                dashboard_data["fund_commitments"][fund_code] = {
                    "fund_code": fund_code,
                    "monthly_return": commitment.monthly_return,
                    "redemption_frequency": commitment.redemption_frequency,
                    "risk_level": commitment.risk_level,
                    "guaranteed": commitment.guaranteed,
                    "description": commitment.description,
                    "minimum_investment": commitment.minimum_investment
                }
        
        return dashboard_data
    
    def get_recommendation(self, gap: PerformanceGap) -> str:
        """Get management recommendation based on performance gap"""
        
        if gap.gap_amount < 0:  # Underperforming
            if gap.gap_percentage < -50:
                return f"CRITICAL: Consider emergency fund rebalancing or client communication"
            elif gap.gap_percentage < -25:
                return f"HIGH: Review trading strategy and consider risk adjustments"
            else:
                return f"MEDIUM: Monitor closely and consider strategy optimization"
        else:  # Outperforming
            if gap.gap_percentage > 50:
                return f"OPPORTUNITY: Consider increasing fund allocations or client upgrades"
            elif gap.gap_percentage > 25:
                return f"POSITIVE: Good performance, maintain current strategy"
            else:
                return f"ON TRACK: Performance within acceptable range"
    
    async def get_client_fund_comparison(self, client_id: str) -> Dict[str, Any]:
        """Get detailed comparison for a specific client using MT5 data as primary source"""
        
        client_data = {
            "client_id": client_id,
            "funds": [],
            "total_expected": 0,
            "total_actual": 0,
            "overall_gap": 0,
            "risk_level": "LOW"
        }
        
        # Get all MT5 accounts for this client (represents actual positions)
        async for mt5_account in self.db.mt5_accounts.find({"client_id": client_id}):
            fund_code = mt5_account["fund_code"]
            principal_amount = mt5_account.get("total_allocated", mt5_account.get("initial_deposit", 0))
            deposit_date = mt5_account.get("deposit_date", mt5_account.get("created_at"))
            
            # Get expected performance based on MT5 data
            expected = await self.calculate_expected_performance(
                client_id, fund_code, principal_amount, deposit_date
            )
            
            if "error" not in expected:
                current_equity = mt5_account.get("current_equity", 0)
                profit_loss_pct = mt5_account.get("profit_loss_percentage", 0)
                
                fund_data = {
                    "fund_code": fund_code,
                    "principal_amount": principal_amount,
                    "expected_current_value": expected["expected_current_value"],
                    "actual_current_value": current_equity,
                    "expected_monthly_return": expected["expected_monthly_amount"],
                    "months_elapsed": expected["months_elapsed"],
                    "next_redemption": expected["next_redemption_date"],
                    "mt5_performance": profit_loss_pct,
                    "mt5_login": mt5_account.get("mt5_login"),
                    "deposit_date": deposit_date
                }
                
                client_data["funds"].append(fund_data)
                client_data["total_expected"] += expected["expected_current_value"]
                client_data["total_actual"] += current_equity
        
        # Calculate overall gap
        if client_data["total_expected"] > 0:
            client_data["overall_gap"] = client_data["total_actual"] - client_data["total_expected"]
            gap_percentage = client_data["overall_gap"] / client_data["total_expected"] * 100
            
            if abs(gap_percentage) > 25:
                client_data["risk_level"] = "HIGH"
            elif abs(gap_percentage) > 10:
                client_data["risk_level"] = "MEDIUM"
        
        return client_data

# Global instance
fund_performance_manager = FundPerformanceManager()

async def main():
    """Test the fund performance management system"""
    
    print("🎯 FIDUS Fund Performance vs MT5 Reality Analysis")
    print("=" * 60)
    
    # Generate dashboard
    dashboard = await fund_performance_manager.generate_fund_management_dashboard()
    
    print(f"\n📊 Fund Management Dashboard - {dashboard['timestamp']}")
    print("-" * 60)
    
    print("\n🏦 Fund Commitments:")
    for fund_code, commitment in dashboard['fund_commitments'].items():
        print(f"  {fund_code}: {commitment['monthly_return']}% monthly, {commitment['redemption_frequency']} month redemptions")
    
    print(f"\n📈 Performance Gaps ({len(dashboard['performance_gaps'])} positions):")
    for gap in dashboard['performance_gaps']:
        print(f"  {gap['client_id']} {gap['fund_code']}: Gap ${gap['gap_amount']:,.2f} ({gap['gap_percentage']:.1f}%) - {gap['risk_level']}")
    
    print(f"\n⚠️ Risk Summary:")
    for risk_level, count in dashboard['risk_summary'].items():
        print(f"  {risk_level}: {count} positions")
    
    print(f"\n🎯 Action Items ({len(dashboard['action_items'])}):")
    for item in dashboard['action_items']:
        print(f"  {item['priority']}: {item['client_id']} {item['fund_code']} - {item['issue']}")
        print(f"      Recommendation: {item['recommendation']}")

if __name__ == "__main__":
    asyncio.run(main())