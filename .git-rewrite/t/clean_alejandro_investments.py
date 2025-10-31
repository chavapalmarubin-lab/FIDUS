#!/usr/bin/env python3
"""
PRODUCTION CLEANUP: Remove duplicate investments and create EXACTLY 4 correct ones
"""
import requests
import json

BASE_URL = "https://fidus-invest.emergent.host"

def get_admin_token():
    login_data = {"username": "admin", "password": "password123", "user_type": "admin"}
    response = requests.post(f"{BASE_URL}/api/auth/login", json=login_data)
    if response.status_code == 200:
        return response.json().get("token")
    return None

def delete_investment(token, investment_id):
    """Delete a specific investment"""
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.delete(f"{BASE_URL}/api/investments/{investment_id}", headers=headers)
        if response.status_code == 200:
            print(f"✅ Deleted investment: {investment_id}")
            return True
        else:
            print(f"❌ Failed to delete {investment_id}: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error deleting {investment_id}: {e}")
        return False

def clean_all_investments(token):
    """Delete ALL current investments for Alejandro"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("🧹 CLEANING ALL CURRENT INVESTMENTS...")
    
    # Get current investments
    response = requests.get(f"{BASE_URL}/api/investments/client/alejandrom", headers=headers)
    if response.status_code == 200:
        data = response.json()
        investments = data.get('investments', [])
        
        print(f"📋 Found {len(investments)} investments to delete")
        
        deleted_count = 0
        for investment in investments:
            investment_id = investment.get('investment_id')
            amount = investment.get('principal_amount')
            fund = investment.get('fund_code')
            
            print(f"🗑️ Deleting: ${amount} {fund} - {investment_id}")
            if delete_investment(token, investment_id):
                deleted_count += 1
        
        print(f"✅ Deleted {deleted_count}/{len(investments)} investments")
        return deleted_count == len(investments)
    else:
        print(f"❌ Could not get investments: {response.status_code}")
        return False

def create_correct_investments(token):
    """Create the EXACT 4 investments required"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🎯 CREATING CORRECT 4 INVESTMENTS...")
    
    # THE EXACT 4 INVESTMENTS REQUIRED
    correct_investments = [
        {
            "client_id": "client_11aed9e2",
            "fund_code": "BALANCE",
            "amount": 80000,
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
            "bank_reference": "ALEJANDRO-INV1-80K-BALANCE-MT5-886557",
            "mt5_login": "886557",
            "mt5_server": "MEXAtlantic-Real",
            "mt5_password": "Fidus13@"
        },
        {
            "client_id": "client_11aed9e2",
            "fund_code": "BALANCE", 
            "amount": 10000,
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
            "bank_reference": "ALEJANDRO-INV2-10K-BALANCE-MT5-886602",
            "mt5_login": "886602", 
            "mt5_server": "MEXAtlantic-Real",
            "mt5_password": "Fidus13@"
        },
        {
            "client_id": "client_11aed9e2",
            "fund_code": "BALANCE",
            "amount": 10000,
            "deposit_date": "2025-10-01", 
            "payment_method": "cryptocurrency",
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
            "bank_reference": "ALEJANDRO-INV3-10K-BALANCE-MT5-886066",
            "mt5_login": "886066",
            "mt5_server": "MEXAtlantic-Real", 
            "mt5_password": "Fidus13@"
        },
        {
            "client_id": "client_11aed9e2",
            "fund_code": "CORE",
            "amount": 18151.41,
            "deposit_date": "2025-10-01",
            "payment_method": "cryptocurrency", 
            "wire_confirmation": "5b6d2c28e60af70552418d040d6c5a18de1f1ee55ba71cf4397386fffd6f957c",
            "bank_reference": "ALEJANDRO-INV4-18151-CORE-MT5-885822",
            "mt5_login": "885822",
            "mt5_server": "MEXAtlantic-Real",
            "mt5_password": "Fidus13@"
        }
    ]
    
    created_count = 0
    
    for i, investment in enumerate(correct_investments, 1):
        print(f"\n--- Creating Investment {i}: ${investment['amount']} {investment['fund_code']} → MT5: {investment['mt5_login']} ---")
        
        try:
            response = requests.post(f"{BASE_URL}/api/investments/create", 
                                   json=investment, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS: {result.get('message', 'Investment created')}")
                created_count += 1
            else:
                print(f"❌ FAILED: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"❌ ERROR: {e}")
    
    print(f"\n📊 Created {created_count}/4 investments")
    return created_count == 4

def verify_final_state(token):
    """Verify final state is correct"""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 VERIFYING FINAL STATE...")
    
    response = requests.get(f"{BASE_URL}/api/investments/client/alejandrom", headers=headers)
    if response.status_code == 200:
        data = response.json()
        investments = data.get('investments', [])
        
        total_amount = sum(inv.get('principal_amount', 0) for inv in investments)
        
        print(f"📊 Final Investment Count: {len(investments)}")
        print(f"💰 Final Total Amount: ${total_amount:,.2f}")
        
        # Check each investment
        for i, inv in enumerate(investments, 1):
            amount = inv.get('principal_amount')
            fund = inv.get('fund_code')
            print(f"   {i}. ${amount:,.2f} → {fund} Fund")
        
        # Verify totals
        expected_total = 118151.41
        correct_count = len(investments) == 4
        correct_total = abs(total_amount - expected_total) < 0.01
        
        if correct_count and correct_total:
            print(f"\n🎉 SUCCESS: Alejandro has exactly 4 investments totaling ${expected_total:,.2f}")
            return True
        else:
            print(f"\n❌ ERROR: Expected 4 investments totaling ${expected_total:,.2f}")
            print(f"   Got: {len(investments)} investments totaling ${total_amount:,.2f}")
            return False
    else:
        print(f"❌ Could not verify final state: {response.status_code}")
        return False

def main():
    print("🔥 PRODUCTION EMERGENCY CLEANUP - ALEJANDRO INVESTMENTS")
    print("=" * 65)
    print("OBJECTIVE: Remove duplicates and ensure EXACTLY 4 investments")
    print("Expected total: $118,151.41")
    print("=" * 65)
    
    token = get_admin_token()
    if not token:
        print("❌ CRITICAL: Authentication failed")
        return
    
    print("✅ Authentication successful")
    
    # Step 1: Clean all existing investments
    if clean_all_investments(token):
        print("✅ All duplicate investments removed")
    else:
        print("⚠️ Some investments may remain - continuing anyway")
    
    # Step 2: Create the correct 4 investments
    if create_correct_investments(token):
        print("✅ All 4 correct investments created")
    else:
        print("❌ Failed to create all investments")
    
    # Step 3: Verify final state
    if verify_final_state(token):
        print("\n🏆 PRODUCTION FIX COMPLETE!")
        print("✅ Alejandro now has exactly 4 investments")
        print("✅ Total: $118,151.41 as required")
        print("✅ Ready for MT5 mapping and system verification")
    else:
        print("\n🚨 PRODUCTION FIX INCOMPLETE!")
        print("❌ Manual intervention may be required")

if __name__ == "__main__":
    main()