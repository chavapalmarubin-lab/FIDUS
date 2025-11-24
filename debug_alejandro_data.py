#!/usr/bin/env python3
"""
DEBUG ALEJANDRO DATA
Check what's actually in the database for Alejandro
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json

# MongoDB connection
mongo_url = "mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"
client = AsyncIOMotorClient(mongo_url)
db = client["fidus_production"]

async def check_alejandro_data():
    """Check what data exists for Alejandro in the database"""
    print("🔍 DEBUGGING ALEJANDRO DATA IN DATABASE")
    print("=" * 60)
    
    # Check users collection for Alejandro
    print("\n1. CHECKING USERS COLLECTION:")
    alejandro_users = await db.users.find({
        "$or": [
            {"username": {"$regex": "alejandro", "$options": "i"}},
            {"name": {"$regex": "alejandro", "$options": "i"}},
            {"id": {"$regex": "alejandro", "$options": "i"}}
        ]
    }).to_list(length=10)
    
    print(f"Found {len(alejandro_users)} Alejandro users:")
    for user in alejandro_users:
        print(f"  - ID: {user.get('id')}, Username: {user.get('username')}, Name: {user.get('name')}")
    
    # Check investments collection
    print("\n2. CHECKING INVESTMENTS COLLECTION:")
    
    # All investments
    all_investments = await db.investments.find({}).to_list(length=100)
    print(f"Total investments in database: {len(all_investments)}")
    
    # Alejandro-specific investments
    alejandro_investments = await db.investments.find({
        "client_id": {"$in": ["client_alejandro", "client_alejandro_mariscal"]}
    }).to_list(length=10)
    
    print(f"Alejandro investments: {len(alejandro_investments)}")
    for inv in alejandro_investments:
        print(f"  - Client ID: {inv.get('client_id')}, Fund: {inv.get('fund_code')}, Amount: ${inv.get('principal_amount', 0):,.2f}, Status: {inv.get('status')}")
    
    # Check for any other client_ids that might be Alejandro
    unique_client_ids = await db.investments.distinct("client_id")
    print(f"\nAll unique client_ids in investments: {unique_client_ids}")
    
    # Check active investments summary
    print("\n3. ACTIVE INVESTMENTS SUMMARY:")
    active_investments = await db.investments.find({
        "status": {"$in": ["active", "active_incubation"]}
    }).to_list(length=100)
    
    print(f"Total active investments: {len(active_investments)}")
    
    client_summary = {}
    for inv in active_investments:
        client_id = inv.get('client_id')
        amount = inv.get('principal_amount', 0)
        fund = inv.get('fund_code')
        
        if client_id not in client_summary:
            client_summary[client_id] = {'total': 0, 'funds': [], 'count': 0}
        
        client_summary[client_id]['total'] += amount
        client_summary[client_id]['funds'].append(f"{fund}: ${amount:,.2f}")
        client_summary[client_id]['count'] += 1
    
    print("Active investments by client:")
    total_aum = 0
    for client_id, data in client_summary.items():
        print(f"  - {client_id}: ${data['total']:,.2f} ({data['count']} investments)")
        for fund_info in data['funds']:
            print(f"    * {fund_info}")
        total_aum += data['total']
    
    print(f"\nTotal AUM across all clients: ${total_aum:,.2f}")
    print(f"Active clients count: {len(client_summary)}")
    
    # Check MT5 accounts
    print("\n4. CHECKING MT5 ACCOUNTS:")
    mt5_accounts = await db.mt5_accounts.find({}).to_list(length=20)
    print(f"Total MT5 accounts: {len(mt5_accounts)}")
    
    for account in mt5_accounts:
        print(f"  - Account: {account.get('account')}, Client: {account.get('client_id')}, Fund: {account.get('fund_type')}")

async def main():
    try:
        await check_alejandro_data()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(main())