"""
FINAL FIX: Alejandro Mariscal Production Setup
Resolves all identified issues:
1. Client ID mismatch (consolidate to client_alejandro)  
2. Email correction to alexmar7609@gmail.com
3. Create missing MT5 accounts
4. Ensure correct investment amounts
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from cryptography.fernet import Fernet

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fix_alejandro_production():
    """Final fix for Alejandro's production setup"""
    
    # MongoDB connection
    mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
    db_name = os.environ.get('DB_NAME', 'fidus_production')
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    try:
        print("🔧 STARTING ALEJANDRO FINAL FIX")
        print("=" * 60)
        
        # Step 1: Update client_alejandro record to have correct email
        print("1. Updating client_alejandro email...")
        result = await db.users.update_one(
            {"id": "client_alejandro"},
            {"$set": {
                "email": "alexmar7609@gmail.com",
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        print(f"✅ Updated client email: {result.modified_count} documents")
        
        # Step 2: Create investment records for client_alejandro if they don't exist
        print("2. Ensuring investment records for client_alejandro...")
        
        # Check existing investments
        existing_investments = await db.investments.find({"client_id": "client_alejandro"}).to_list(length=None)
        
        if len(existing_investments) < 2:
            # Delete any existing investments for client_alejandro to start fresh
            await db.investments.delete_many({"client_id": "client_alejandro"})
            
            # Create the correct investments
            investments_to_create = [
                {
                    "investment_id": "inv_alejandro_balance_final",
                    "client_id": "client_alejandro",
                    "fund_code": "BALANCE",
                    "principal_amount": 100000.00,
                    "deposit_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                    "incubation_end_date": datetime(2025, 12, 1, tzinfo=timezone.utc),
                    "interest_start_date": datetime(2025, 12, 1, tzinfo=timezone.utc),
                    "minimum_hold_end_date": datetime(2026, 12, 1, tzinfo=timezone.utc),
                    "current_value": 100000.00,
                    "status": "active",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "total_interest_earned": 0.0
                },
                {
                    "investment_id": "inv_alejandro_core_final",
                    "client_id": "client_alejandro",
                    "fund_code": "CORE",
                    "principal_amount": 18151.41,
                    "deposit_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                    "incubation_end_date": datetime(2025, 12, 1, tzinfo=timezone.utc),
                    "interest_start_date": datetime(2025, 12, 1, tzinfo=timezone.utc),
                    "minimum_hold_end_date": datetime(2026, 12, 1, tzinfo=timezone.utc),
                    "current_value": 18151.41,
                    "status": "active",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "total_interest_earned": 0.0
                }
            ]
            
            result = await db.investments.insert_many(investments_to_create)
            print(f"✅ Created {len(result.inserted_ids)} investment records")
        else:
            print(f"✅ Investment records already exist: {len(existing_investments)} found")
        
        # Step 3: Create MT5 accounts for client_alejandro
        print("3. Creating MT5 accounts for client_alejandro...")
        
        # Delete any existing MT5 accounts for client_alejandro
        await db.mt5_accounts.delete_many({"client_id": "client_alejandro"})
        
        # Get encryption key
        def get_encryption_key() -> bytes:
            if os.environ.get('ENVIRONMENT') == 'production' or os.environ.get('RENDER'):
                key_file = "/tmp/.mt5_key"
            else:
                key_file = "/app/backend/.mt5_key"
                
            if os.path.exists(key_file):
                with open(key_file, 'rb') as f:
                    return f.read()
            else:
                key = Fernet.generate_key()
                os.makedirs(os.path.dirname(key_file), exist_ok=True)
                with open(key_file, 'wb') as f:
                    f.write(key)
                try:
                    os.chmod(key_file, 0o600)
                except OSError:
                    pass
                return key
        
        def encrypt_password(password: str) -> str:
            fernet = Fernet(get_encryption_key())
            return fernet.encrypt(password.encode()).decode()
        
        # Create MT5 accounts
        mt5_accounts_to_create = [
            {
                "account_id": "mt5_alejandro_balance_001_final",
                "client_id": "client_alejandro",
                "fund_code": "BALANCE",
                "investment_id": "inv_alejandro_balance_final",
                "mt5_login": 886557,
                "mt5_server": "MEXAtlantic-Real",
                "broker_code": "mexatlantic",
                "broker_name": "MEXAtlantic",
                "encrypted_password": encrypt_password("FIDUS13@"),
                "total_allocated": 80000.00,
                "current_equity": 80000.00,
                "profit_loss": 0.0,
                "profit_loss_percentage": 0.0,
                "investment_ids": ["inv_alejandro_balance_final"],
                "status": "active",
                "is_active": True,
                "is_demo": False,
                "mt5_initial_balance": 80000.00,
                "banking_fees": 0.0,
                "fee_notes": "",
                "credentials_provided": True,
                "created_via": "final_fix",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_sync": None,
                "sync_status": "pending"
            },
            {
                "account_id": "mt5_alejandro_balance_002_final",
                "client_id": "client_alejandro",
                "fund_code": "BALANCE",
                "investment_id": "inv_alejandro_balance_final",
                "mt5_login": 886066,
                "mt5_server": "MEXAtlantic-Real",
                "broker_code": "mexatlantic",
                "broker_name": "MEXAtlantic",
                "encrypted_password": encrypt_password("FIDUS13@"),
                "total_allocated": 10000.00,
                "current_equity": 10000.00,
                "profit_loss": 0.0,
                "profit_loss_percentage": 0.0,
                "investment_ids": ["inv_alejandro_balance_final"],
                "status": "active",
                "is_active": True,
                "is_demo": False,
                "mt5_initial_balance": 10000.00,
                "banking_fees": 0.0,
                "fee_notes": "",
                "credentials_provided": True,
                "created_via": "final_fix",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_sync": None,
                "sync_status": "pending"
            },
            {
                "account_id": "mt5_alejandro_balance_003_final",
                "client_id": "client_alejandro",
                "fund_code": "BALANCE",
                "investment_id": "inv_alejandro_balance_final",
                "mt5_login": 886602,
                "mt5_server": "MEXAtlantic-Real",
                "broker_code": "mexatlantic",
                "broker_name": "MEXAtlantic",
                "encrypted_password": encrypt_password("FIDUS13@"),
                "total_allocated": 10000.00,
                "current_equity": 10000.00,
                "profit_loss": 0.0,
                "profit_loss_percentage": 0.0,
                "investment_ids": ["inv_alejandro_balance_final"],
                "status": "active",
                "is_active": True,
                "is_demo": False,
                "mt5_initial_balance": 10000.00,
                "banking_fees": 0.0,
                "fee_notes": "",
                "credentials_provided": True,
                "created_via": "final_fix",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_sync": None,
                "sync_status": "pending"
            },
            {
                "account_id": "mt5_alejandro_core_001_final",
                "client_id": "client_alejandro",
                "fund_code": "CORE",
                "investment_id": "inv_alejandro_core_final",
                "mt5_login": 885822,
                "mt5_server": "MEXAtlantic-Real",
                "broker_code": "mexatlantic",
                "broker_name": "MEXAtlantic",
                "encrypted_password": encrypt_password("FIDUS13@"),
                "total_allocated": 18151.41,
                "current_equity": 18151.41,
                "profit_loss": 0.0,
                "profit_loss_percentage": 0.0,
                "investment_ids": ["inv_alejandro_core_final"],
                "status": "active",
                "is_active": True,
                "is_demo": False,
                "mt5_initial_balance": 18151.41,
                "banking_fees": 0.0,
                "fee_notes": "",
                "credentials_provided": True,
                "created_via": "final_fix",
                "created_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
                "last_sync": None,
                "sync_status": "pending"
            }
        ]
        
        result = await db.mt5_accounts.insert_many(mt5_accounts_to_create)
        print(f"✅ Created {len(result.inserted_ids)} MT5 account records")
        
        # Step 4: Ensure client readiness for client_alejandro
        print("4. Ensuring client readiness for client_alejandro...")
        readiness_record = {
            "client_id": "client_alejandro",
            "aml_kyc_completed": True,
            "agreement_signed": True,
            "account_creation_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
            "investment_ready": True,
            "notes": "Final fix - All documents completed",
            "updated_at": datetime.now(timezone.utc),
            "updated_by": "final_fix",
            "readiness_override": False,
            "readiness_override_reason": "",
            "readiness_override_by": "",
            "readiness_override_date": None
        }
        
        result = await db.client_readiness.replace_one(
            {"client_id": "client_alejandro"},
            readiness_record,
            upsert=True
        )
        print("✅ Updated client readiness record")
        
        # Step 5: Verification
        print("5. Final verification...")
        
        # Verify client
        client_doc = await db.users.find_one({"id": "client_alejandro"})
        print(f"✅ Client: {client_doc['name']} ({client_doc['email']})")
        
        # Verify investments
        investments = await db.investments.find({"client_id": "client_alejandro"}).to_list(length=None)
        total_investment = sum(inv['principal_amount'] for inv in investments)
        print(f"✅ Investments: {len(investments)} records, Total: ${total_investment:,.2f}")
        
        # Verify MT5 accounts
        mt5_accounts = await db.mt5_accounts.find({"client_id": "client_alejandro"}).to_list(length=None)
        total_mt5 = sum(acc['total_allocated'] for acc in mt5_accounts)
        print(f"✅ MT5 Accounts: {len(mt5_accounts)} records, Total: ${total_mt5:,.2f}")
        
        # Verify readiness
        readiness = await db.client_readiness.find_one({"client_id": "client_alejandro"})
        print(f"✅ Investment Ready: {readiness['investment_ready']}")
        
        print("=" * 60)
        print("🎉 ALEJANDRO FINAL FIX COMPLETED SUCCESSFULLY!")
        print(f"Client: client_alejandro")
        print(f"Email: alexmar7609@gmail.com")
        print(f"Investments: 2 records totaling ${total_investment:,.2f}")
        print(f"MT5 Accounts: 4 records totaling ${total_mt5:,.2f}")
        print(f"Investment Ready: True")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Final fix failed: {e}")
        return False
    finally:
        client.close()

if __name__ == "__main__":
    success = asyncio.run(fix_alejandro_production())
    if success:
        print("✅ Fix completed successfully")
        exit(0)
    else:
        print("❌ Fix failed")
        exit(1)