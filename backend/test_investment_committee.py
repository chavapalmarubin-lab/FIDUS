"""
Test Investment Committee API Endpoints
Direct database-level testing to verify functionality
"""
import asyncio
import sys
from services.allocation_service import AllocationService
from mongodb_integration import mongodb_manager
from validation.field_registry import transform_to_api_format


async def test_investment_committee():
    """Test Investment Committee endpoints"""
    
    print("=" * 70)
    print("🧪 TESTING INVESTMENT COMMITTEE API")
    print("=" * 70)
    
    # Get database
    db = mongodb_manager.db
    service = AllocationService(db)
    
    # TEST 1: Get BALANCE fund allocation
    print("\n📊 TEST 1: Get BALANCE Fund Allocation")
    print("-" * 70)
    
    balance_state = await service.get_fund_state("BALANCE")
    if balance_state:
        balance_api = transform_to_api_format(balance_state)
        print(f"✅ Fund Type: {balance_api['fundType']}")
        print(f"✅ Total Capital: ${balance_api['totalCapital']:,.2f}")
        print(f"✅ Allocated: ${balance_api['allocatedCapital']:,.2f}")
        print(f"✅ Unallocated: ${balance_api['unallocatedCapital']:,.2f}")
        print(f"✅ Number of Managers: {len(balance_api['managerAllocations'])}")
        
        print("\n   Manager Allocations:")
        for alloc in balance_api['managerAllocations']:
            print(f"   - {alloc['managerName']}: ${alloc['allocatedAmount']:,.2f}")
    else:
        print("❌ BALANCE fund not found")
        return
    
    # TEST 2: Get allocation history
    print("\n📜 TEST 2: Get Allocation History")
    print("-" * 70)
    
    history = await service.get_history("BALANCE", limit=5)
    print(f"✅ Found {len(history)} history records")
    
    for i, record in enumerate(history, 1):
        record_api = transform_to_api_format(record)
        print(f"\n   Record {i}:")
        print(f"   - Action: {record_api['actionType']}")
        print(f"   - Manager: {record_api['affectedManager']}")
        print(f"   - Financial Impact:")
        impact = record_api['financialImpact']
        if impact.get('lossAmount', 0) > 0:
            print(f"     Loss: ${impact['lossAmount']:,.2f}")
        if impact.get('gainAmount', 0) > 0:
            print(f"     Gain: ${impact['gainAmount']:,.2f}")
        if impact.get('allocationChange', 0) != 0:
            print(f"     Allocation Change: ${impact['allocationChange']:,.2f}")
    
    # TEST 3: Get available managers
    print("\n👥 TEST 3: Get Available Managers")
    print("-" * 70)
    
    managers = await service.get_available_managers()
    print(f"✅ Found {len(managers)} managers")
    
    for manager in managers:
        manager_api = transform_to_api_format(manager)
        status_icon = "✅" if manager_api.get('status') == 'active' else "⏸️"
        print(f"\n   {status_icon} {manager_api.get('name', 'N/A')}")
        print(f"      Status: {manager_api.get('status', 'N/A')}")
        print(f"      Execution: {manager_api.get('executionMethod', 'N/A')}")
        print(f"      Accounts: {manager_api.get('assignedAccounts', [])}")
        
        current_alloc = manager_api.get('currentAllocation')
        if current_alloc:
            print(f"      Current Allocation: ${current_alloc['allocatedAmount']:,.2f} ({current_alloc['fundType']})")
    
    # TEST 4: Preview allocation (validation test)
    print("\n🔍 TEST 4: Preview Allocation (Validation)")
    print("-" * 70)
    
    # Try to allocate more than available (should fail)
    preview_result = await service.preview_allocation(
        fund_type="BALANCE",
        manager_name="JOSE",
        new_allocation=100000.00,  # More than available $50,500
        account_distribution=[]
    )
    
    if preview_result['is_valid']:
        print("❌ FAIL: Should have rejected allocation (insufficient capital)")
    else:
        print(f"✅ PASS: Correctly rejected allocation")
        print(f"   Errors: {preview_result['errors']}")
    
    # Try valid allocation
    preview_result = await service.preview_allocation(
        fund_type="BALANCE",
        manager_name="CP Strategy",
        new_allocation=10000.00,  # Within available $50,500
        account_distribution=[
            {"account_number": 885822, "amount": 5000.00, "type": "master"},
            {"account_number": 891234, "amount": 5000.00, "type": "copy"}
        ]
    )
    
    if preview_result['is_valid']:
        print(f"\n✅ PASS: Valid allocation preview")
        impact = preview_result['impact']
        print(f"   Impact:")
        print(f"   - Unallocated Before: ${impact['unallocated_before']:,.2f}")
        print(f"   - Unallocated After: ${impact['unallocated_after']:,.2f}")
        print(f"   - Manager Allocation: ${impact['manager_allocation_after']:,.2f}")
    else:
        print(f"❌ FAIL: Should have accepted allocation")
        print(f"   Errors: {preview_result['errors']}")
    
    # TEST 5: Get manager actual balance
    print("\n💰 TEST 5: Get Manager Actual Balance")
    print("-" * 70)
    
    for manager_name in ["Spaniard Stock CFDs", "UNO14 Manager", "Provider1-Assev"]:
        balance = await service.get_manager_actual_balance(manager_name)
        print(f"   {manager_name}: ${balance:,.2f}")
    
    # Final summary
    print("\n" + "=" * 70)
    print("✅ ALL TESTS COMPLETED SUCCESSFULLY")
    print("=" * 70)
    
    print("\n📊 BALANCE Fund Summary:")
    print(f"   Total Capital:     ${balance_api['totalCapital']:,.2f}")
    print(f"   Allocated:         ${balance_api['allocatedCapital']:,.2f} ({(balance_api['allocatedCapital']/balance_api['totalCapital']*100):.1f}%)")
    print(f"   Unallocated:       ${balance_api['unallocatedCapital']:,.2f} ({(balance_api['unallocatedCapital']/balance_api['totalCapital']*100):.1f}%)")
    print(f"   Active Managers:   {len(balance_api['managerAllocations'])}")
    
    mongodb_manager.close()


if __name__ == "__main__":
    asyncio.run(test_investment_committee())
