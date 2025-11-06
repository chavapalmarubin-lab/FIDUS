import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv

load_dotenv()

async def check():
    client = AsyncIOMotorClient(os.environ.get('MONGO_URL'))
    db = client['fidus_production']
    
    print("="*80)
    print("CHECKING WHICH MANAGERS HAVE TRADES")
    print("="*80)
    print()
    
    accounts_to_check = [
        (885822, "CP Strategy Provider", "CORE"),
        (886557, "TradingHub Gold Provider", "BALANCE"),
        (886602, "UNO14 Manager", "BALANCE"),
        (886066, "GoldenTrade Manager", "BALANCE - Inactive"),
        (891215, "TradingHub Gold Provider", "BALANCE_FIDUS"),
        (897589, "Provider1-Assev", "BALANCE_REINVESTED"),
        (897590, "CP Strategy Provider", "CORE_REINVESTED"),
        (897591, "alefloreztrader", "SEPARATION"),
        (897599, "alefloreztrader", "SEPARATION"),
    ]
    
    for acc_num, manager, fund in accounts_to_check:
        count = await db.mt5_deals_history.count_documents({
            "account_number": acc_num,
            "entry": {"$in": [0, 1]}  # Only actual trades
        })
        
        status = "✅ HAS TRADES" if count > 0 else "❌ NO TRADES"
        print(f"{status} | Account {acc_num} ({fund}) - {manager}: {count} trades")
    
    client.close()

asyncio.run(check())
