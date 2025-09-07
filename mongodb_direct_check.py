#!/usr/bin/env python3
"""
Direct MongoDB Check - Query the database directly to see what's stored
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, timezone

async def check_mongodb_data():
    # Connect to MongoDB
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    client = AsyncIOMotorClient(mongo_url)
    db = client['test_database']
    
    print("🔍 DIRECT MONGODB DATA CHECK")
    print("=" * 50)
    
    # Check investments collection
    print("\n💰 INVESTMENTS COLLECTION:")
    try:
        investments = await db.investments.find({}).to_list(length=None)
        print(f"   Total investment documents: {len(investments)}")
        
        for inv in investments:
            print(f"   - ID: {inv.get('_id')}")
            print(f"     Client: {inv.get('client_id')}")
            print(f"     Fund: {inv.get('fund_code')}")
            print(f"     Amount: ${inv.get('principal_amount', 0):,.2f}")
            print(f"     Deposit Date: {inv.get('deposit_date')}")
            print(f"     Status: {inv.get('status', 'N/A')}")
            print()
    except Exception as e:
        print(f"   ❌ Error querying investments: {e}")
    
    # Check MT5 accounts collection
    print("\n🔗 MT5 ACCOUNTS COLLECTION:")
    try:
        mt5_accounts = await db.mt5_accounts.find({}).to_list(length=None)
        print(f"   Total MT5 account documents: {len(mt5_accounts)}")
        
        for acc in mt5_accounts:
            print(f"   - ID: {acc.get('_id')}")
            print(f"     Client: {acc.get('client_id')}")
            print(f"     Login: {acc.get('mt5_login')}")
            print(f"     Broker: {acc.get('broker_name')}")
            print(f"     Investment ID: {acc.get('investment_id', 'N/A')}")
            print()
    except Exception as e:
        print(f"   ❌ Error querying MT5 accounts: {e}")
    
    # Check clients collection
    print("\n👥 CLIENTS COLLECTION:")
    try:
        clients = await db.clients.find({}).to_list(length=None)
        print(f"   Total client documents: {len(clients)}")
        
        for client in clients:
            print(f"   - ID: {client.get('_id')}")
            print(f"     Client ID: {client.get('client_id')}")
            print(f"     Name: {client.get('name')}")
            print(f"     Email: {client.get('email')}")
            print()
    except Exception as e:
        print(f"   ❌ Error querying clients: {e}")
    
    # Check fund configurations
    print("\n📊 FUND CONFIGURATIONS:")
    try:
        funds = await db.fund_configurations.find({}).to_list(length=None)
        print(f"   Total fund configuration documents: {len(funds)}")
        
        for fund in funds:
            print(f"   - Fund: {fund.get('fund_code')}")
            print(f"     Name: {fund.get('name')}")
            print(f"     Rate: {fund.get('monthly_interest_rate', 0)}%")
            print(f"     Min Investment: ${fund.get('minimum_investment', 0):,.2f}")
            print()
    except Exception as e:
        print(f"   ❌ Error querying fund configurations: {e}")
    
    # Check all collections
    print("\n📋 ALL COLLECTIONS:")
    try:
        collections = await db.list_collection_names()
        print(f"   Available collections: {collections}")
    except Exception as e:
        print(f"   ❌ Error listing collections: {e}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(check_mongodb_data())