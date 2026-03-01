"""
FIDUS Instrument Specifications Seeder
Populates the instrument_specs collection with Tier 1 instruments based on Lucrum contract specs.

Run with: python seed_instrument_specs.py
"""

import asyncio
import os
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Load environment
load_dotenv('.env')

# FIDUS Tier 1 Instrument Specifications
# Based on Lucrum broker contract specs - 200:1 leverage, USD base currency
FIDUS_TIER1_SPECS = [
    {
        "symbol": "XAUUSD",
        "name": "Gold",
        "asset_class": "Metals",
        "base_currency": "XAU",
        "quote_currency": "USD",
        "contract_size": 100,  # 100 oz per lot
        "tick_size": 0.01,
        "tick_value_per_lot": 1.0,  # $1 per 0.01 move per lot
        "value_per_1_usd_move_per_lot": 100,  # $100 per $1 move per lot
        "pip_size": 0.01,
        "pip_value_per_lot": 1.0,
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100,
        "default_stop_proxy_usd": 10,
        "default_stop_proxy_pips": None,
        "default_stop_proxy_points": None,
        "atr_multiplier": 0.60,  # Gold is volatile; tighter intraday management
        "margin_leverage": 200,
        "price_source": "broker_feed",
        "typical_spread": 0.30,
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "symbol": "EURUSD",
        "name": "Euro/US Dollar",
        "asset_class": "FX_MAJOR",
        "base_currency": "EUR",
        "quote_currency": "USD",
        "contract_size": 100000,  # Standard lot
        "tick_size": 0.00001,
        "tick_value_per_lot": 0.1,
        "value_per_1_usd_move_per_lot": 100000,
        "pip_size": 0.0001,
        "pip_value_per_lot_usd": 10.0,  # $10 per pip per lot
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100,
        "default_stop_proxy_usd": None,
        "default_stop_proxy_pips": 25,  # Conservative fallback
        "default_stop_proxy_points": None,
        "atr_multiplier": 0.75,  # FX majors
        "margin_leverage": 200,
        "price_source": "broker_feed",
        "typical_spread": 1.0,
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "symbol": "GBPUSD",
        "name": "British Pound/US Dollar",
        "asset_class": "FX_MAJOR",
        "base_currency": "GBP",
        "quote_currency": "USD",
        "contract_size": 100000,
        "tick_size": 0.00001,
        "tick_value_per_lot": 0.1,
        "value_per_1_usd_move_per_lot": 100000,
        "pip_size": 0.0001,
        "pip_value_per_lot_usd": 10.0,
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100,
        "default_stop_proxy_usd": None,
        "default_stop_proxy_pips": 30,
        "default_stop_proxy_points": None,
        "atr_multiplier": 0.75,
        "margin_leverage": 200,
        "price_source": "broker_feed",
        "typical_spread": 1.2,
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "symbol": "USDJPY",
        "name": "US Dollar/Japanese Yen",
        "asset_class": "FX_MAJOR",
        "base_currency": "USD",
        "quote_currency": "JPY",
        "contract_size": 100000,
        "tick_size": 0.001,
        "tick_value_per_lot": 0.01,
        "value_per_1_usd_move_per_lot": 667,  # Varies with rate
        "pip_size": 0.01,
        "pip_value_per_lot_usd": 9.1,  # Approx at 110 rate (need live conversion)
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100,
        "default_stop_proxy_usd": None,
        "default_stop_proxy_pips": 25,
        "default_stop_proxy_points": None,
        "atr_multiplier": 0.75,
        "margin_leverage": 200,
        "price_source": "broker_feed",
        "typical_spread": 1.0,
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "symbol": "AUDCAD",
        "name": "Australian Dollar/Canadian Dollar",
        "asset_class": "FX_CROSS",
        "base_currency": "AUD",
        "quote_currency": "CAD",
        "contract_size": 100000,
        "tick_size": 0.00001,
        "tick_value_per_lot": 0.1,
        "value_per_1_usd_move_per_lot": 100000,
        "pip_size": 0.0001,
        "pip_value_per_lot_usd_estimate": 7.5,  # Need live USD conversion
        "lot_step": 0.01,
        "min_lot": 0.01,
        "max_lot": 100,
        "default_stop_proxy_usd": None,
        "default_stop_proxy_pips": 30,
        "default_stop_proxy_points": None,
        "atr_multiplier": 1.00,  # FX crosses are more volatile
        "margin_leverage": 200,
        "price_source": "broker_feed",
        "typical_spread": 2.0,
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "symbol": "US30",
        "name": "Dow Jones Industrial Average",
        "asset_class": "INDEX_CFD",
        "base_currency": "USD",
        "quote_currency": "USD",
        "contract_size": 1,  # 1 lot = 1 contract
        "tick_size": 1,
        "tick_value_per_lot": 1.0,  # $1 per point per lot
        "tick_value_per_lot_usd": 1.0,
        "value_per_1_usd_move_per_lot": 1.0,
        "pip_size": 1.0,
        "pip_value_per_lot": 1.0,
        "lot_step": 0.10,
        "min_lot": 0.10,
        "max_lot": 100,
        "default_stop_proxy_usd": None,
        "default_stop_proxy_pips": None,
        "default_stop_proxy_points": 200,
        "atr_multiplier": 0.80,
        "margin_leverage": 200,
        "price_source": "broker_feed",
        "typical_spread": 3.0,
        "updated_at": datetime.now(timezone.utc)
    },
    {
        "symbol": "DE40",
        "name": "DAX 40 (Germany 40)",
        "asset_class": "INDEX_CFD",
        "base_currency": "EUR",
        "quote_currency": "EUR",
        "contract_size": 1,
        "tick_size": 1,
        "tick_value_per_lot": 1.0,
        "tick_value_per_lot_usd_estimate": 1.1,  # Need EUR/USD conversion
        "value_per_1_usd_move_per_lot": 1.0,
        "pip_size": 0.1,
        "pip_value_per_lot": 1.0,
        "lot_step": 0.10,
        "min_lot": 0.10,
        "max_lot": 100,
        "default_stop_proxy_usd": None,
        "default_stop_proxy_pips": None,
        "default_stop_proxy_points": 150,
        "atr_multiplier": 0.80,
        "margin_leverage": 200,
        "price_source": "broker_feed",
        "typical_spread": 2.0,
        "updated_at": datetime.now(timezone.utc)
    }
]


async def seed_instrument_specs():
    """Seed instrument specifications into MongoDB"""
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("❌ MONGO_URL not found in environment")
        return False
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'fidus_production')]
    
    print("=" * 60)
    print("FIDUS INSTRUMENT SPECS SEEDER")
    print("=" * 60)
    
    try:
        # Upsert each instrument
        for spec in FIDUS_TIER1_SPECS:
            result = await db.instrument_specs.update_one(
                {"symbol": spec["symbol"]},
                {"$set": spec},
                upsert=True
            )
            
            action = "Updated" if result.matched_count > 0 else "Created"
            print(f"✅ {action}: {spec['symbol']} ({spec['name']})")
        
        # Verify count
        count = await db.instrument_specs.count_documents({})
        print("-" * 60)
        print(f"📊 Total instruments in collection: {count}")
        
        # List all instruments
        print("\n📋 Current instrument_specs collection:")
        async for doc in db.instrument_specs.find({}, {"symbol": 1, "name": 1, "asset_class": 1, "_id": 0}):
            print(f"   - {doc['symbol']}: {doc['name']} ({doc.get('asset_class', 'N/A')})")
        
        print("=" * 60)
        print("✅ SEEDING COMPLETE")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error seeding specs: {e}")
        return False
    finally:
        client.close()


if __name__ == "__main__":
    asyncio.run(seed_instrument_specs())
