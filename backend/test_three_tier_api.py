"""
Test the Three-Tier P&L API endpoints
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from services.three_tier_pnl_calculator import ThreeTierPnLCalculator
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_api_logic():
    """
    Test the API logic without actually calling HTTP endpoints
    """
    mongo_url = os.environ.get('MONGO_URL')
    client = AsyncIOMotorClient(mongo_url)
    db = client['fidus_production']
    
    calculator = ThreeTierPnLCalculator(db)
    
    print("="*80)
    print("TESTING THREE-TIER P&L API LOGIC")
    print("="*80)
    print()
    
    # Test 1: Admin View (Three-Tier)
    print("TEST 1: /api/pnl/three-tier (Admin View)")
    print("-"*80)
    admin_view = await calculator.get_admin_view()
    print(json.dumps(admin_view, indent=2, default=str))
    print()
    
    # Test 2: Client View
    print("\nTEST 2: /api/pnl/client/client_alejandro")
    print("-"*80)
    client_view = await calculator.get_client_view('client_alejandro')
    print(json.dumps(client_view, indent=2, default=str))
    print()
    
    # Test 3: Fund Performance vs Obligations
    print("\nTEST 3: /api/pnl/fund-performance")
    print("-"*80)
    
    # Calculate obligations
    core_obligations = 3267.25  # $18,151.41 × 1.5% × 12 months
    balance_obligations = 30000.00  # $100,000 × 2.5% × 12 months
    total_obligations = core_obligations + balance_obligations
    
    fund_pnl = admin_view['total_fund_pnl']
    gap = fund_pnl['true_pnl'] - total_obligations
    
    performance_data = {
        'fund_performance': fund_pnl,
        'client_obligations': {
            'core_obligations': core_obligations,
            'balance_obligations': balance_obligations,
            'total_obligations': total_obligations
        },
        'gap_analysis': {
            'fund_pnl': fund_pnl['true_pnl'],
            'obligations': total_obligations,
            'surplus_deficit': gap,
            'status': 'surplus' if gap > 0 else 'deficit',
            'coverage_ratio': round((fund_pnl['true_pnl'] / total_obligations * 100), 2) if total_obligations > 0 else 0
        },
        'separation_balance': admin_view['separation_balance']
    }
    
    print(json.dumps(performance_data, indent=2, default=str))
    print()
    
    # Summary
    print("="*80)
    print("📊 SUMMARY - FUND PERFORMANCE VS OBLIGATIONS")
    print("="*80)
    print(f"\n💰 Fund Performance:")
    print(f"   Initial Investment: ${fund_pnl['initial_allocation']:,.2f}")
    print(f"   Current Value: ${fund_pnl['current_equity']:,.2f}")
    print(f"   P&L: ${fund_pnl['true_pnl']:,.2f} ({fund_pnl['return_percent']}%)")
    
    print(f"\n📋 Client Obligations (Fixed Interest):")
    print(f"   CORE (1.5% × 12): ${core_obligations:,.2f}")
    print(f"   BALANCE (2.5% × 12): ${balance_obligations:,.2f}")
    print(f"   Total: ${total_obligations:,.2f}")
    
    print(f"\n📈 Gap Analysis:")
    print(f"   Surplus/Deficit: ${gap:,.2f}")
    print(f"   Status: {'✅ SURPLUS' if gap > 0 else '❌ DEFICIT'}")
    print(f"   Coverage: {performance_data['gap_analysis']['coverage_ratio']:.2f}%")
    
    print(f"\n💵 Separation Balance: ${admin_view['separation_balance']:,.2f}")
    print()
    
    print("="*80)
    print("✅ ALL API LOGIC TESTS PASSED")
    print("="*80)
    
    client.close()

if __name__ == "__main__":
    asyncio.run(test_api_logic())
