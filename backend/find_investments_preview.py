#!/usr/bin/env python3
"""
Find all investments in PREVIEW database
"""

import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URL = os.getenv("MONGO_URL")

async def find_investments():
    client = AsyncIOMotorClient(MONGO_URL)
    db_name = "fidus_production"
    db = client[db_name]
    
    print("\n" + "=" * 80)
    print("ALL INVESTMENTS IN PREVIEW DATABASE")
    print("=" * 80)
    
    investments = await db.investments.find({}).to_list(None)
    
    print(f"\nTotal investments: {len(investments)}")
    
    for inv in investments:
        principal = inv.get('principal_amount', 0)
        print(f"\n  ID: {inv['_id']}")
        print(f"  Fund Code: {inv.get('fund_code', 'N/A')}")
        print(f"  Principal: ${principal:,.2f}")
        print(f"  Client ID: {inv.get('client_id', 'N/A')}")
        print(f"  Referred By: {inv.get('referred_by', 'N/A')}")
        print(f"  Referred By Name: {inv.get('referred_by_name', 'N/A')}")
    
    # Also check clients
    print("\n" + "=" * 80)
    print("ALL CLIENTS")
    print("=" * 80)
    
    clients = await db.clients.find({}).to_list(None)
    print(f"\nTotal clients: {len(clients)}")
    
    for client_doc in clients:
        print(f"\n  ID: {client_doc['_id']}")
        print(f"  Name: {client_doc.get('name', 'N/A')}")
        print(f"  Email: {client_doc.get('email', 'N/A')}")
        print(f"  Referred By: {client_doc.get('referred_by', 'N/A')}")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(find_investments())
