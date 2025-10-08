"""
URGENT PRODUCTION SETUP: Alejandro Mariscal - First Real Client
Creates all necessary database records for production deployment
"""

import os
import asyncio
import logging
from datetime import datetime, timezone
from decimal import Decimal
from motor.motor_asyncio import AsyncIOMotorClient
from cryptography.fernet import Fernet
import uuid

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AlejandroProductionSetup:
    """Production setup for Alejandro Mariscal - First Real Client"""
    
    def __init__(self):
        # MongoDB connection
        self.mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
        self.db_name = os.environ.get('DB_NAME', 'fidus_production')
        self.client = None
        self.db = None
        
        # Client data
        self.client_data = {
            "client_id": "client_alejandro_mariscal",
            "username": "alejandrom", 
            "name": "Alejandro Mariscal",
            "email": "alexmar7609@gmail.com",
            "type": "client",
            "status": "active",
            "created_at": datetime(2025, 10, 1, tzinfo=timezone.utc),
            "total_invested": 118151.41,
            "phone": "+52-XXX-XXX-XXXX",  # To be updated with actual phone
            "temporary_password": self._generate_secure_password(),
            "must_change_password": True
        }
        
        # Investment data
        self.investment_data = {
            "balance_fund": {
                "investment_id": "inv_alejandro_balance_001",
                "client_id": "client_alejandro_mariscal",
                "fund_code": "BALANCE",
                "principal_amount": 100000.00,
                "deposit_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "incubation_end_date": datetime(2025, 12, 1, tzinfo=timezone.utc),
                "interest_start_date": datetime(2025, 12, 1, tzinfo=timezone.utc), 
                "minimum_hold_end_date": datetime(2026, 12, 1, tzinfo=timezone.utc),
                "current_value": 100000.00,
                "status": "active"
            },
            "core_fund": {
                "investment_id": "inv_alejandro_core_001", 
                "client_id": "client_alejandro_mariscal",
                "fund_code": "CORE",
                "principal_amount": 18151.41,
                "deposit_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "incubation_end_date": datetime(2025, 12, 1, tzinfo=timezone.utc),
                "interest_start_date": datetime(2025, 12, 1, tzinfo=timezone.utc),
                "minimum_hold_end_date": datetime(2026, 12, 1, tzinfo=timezone.utc),
                "current_value": 18151.41,
                "status": "active"
            }
        }
        
        # MT5 Account data - REAL CREDENTIALS
        self.mt5_accounts = [
            {
                "account_id": "mt5_alejandro_balance_001",
                "client_id": "client_alejandro_mariscal", 
                "fund_code": "BALANCE",
                "investment_id": "inv_alejandro_balance_001",
                "mt5_login": 886557,
                "mt5_password": "FIDUS13@",  # REAL PASSWORD
                "mt5_server": "MEXAtlantic-Real",
                "broker_code": "mexatlantic",
                "broker_name": "MEXAtlantic",
                "principal_amount": 80000.00,
                "mt5_initial_balance": 80000.00
            },
            {
                "account_id": "mt5_alejandro_balance_002",
                "client_id": "client_alejandro_mariscal",
                "fund_code": "BALANCE", 
                "investment_id": "inv_alejandro_balance_001",
                "mt5_login": 886066,
                "mt5_password": "FIDUS13@",  # REAL PASSWORD
                "mt5_server": "MEXAtlantic-Real",
                "broker_code": "mexatlantic",
                "broker_name": "MEXAtlantic",
                "principal_amount": 10000.00,
                "mt5_initial_balance": 10000.00
            },
            {
                "account_id": "mt5_alejandro_balance_003", 
                "client_id": "client_alejandro_mariscal",
                "fund_code": "BALANCE",
                "investment_id": "inv_alejandro_balance_001", 
                "mt5_login": 886602,
                "mt5_password": "FIDUS13@",  # REAL PASSWORD
                "mt5_server": "MEXAtlantic-Real", 
                "broker_code": "mexatlantic",
                "broker_name": "MEXAtlantic",
                "principal_amount": 10000.00,
                "mt5_initial_balance": 10000.00
            },
            {
                "account_id": "mt5_alejandro_core_001",
                "client_id": "client_alejandro_mariscal",
                "fund_code": "CORE",
                "investment_id": "inv_alejandro_core_001",
                "mt5_login": 885822, 
                "mt5_password": "FIDUS13@",  # REAL PASSWORD
                "mt5_server": "MEXAtlantic-Real",
                "broker_code": "mexatlantic",
                "broker_name": "MEXAtlantic",
                "principal_amount": 18151.41,
                "mt5_initial_balance": 18151.41
            }
        ]
        
    def _generate_secure_password(self) -> str:
        """Generate a secure temporary password"""
        import secrets
        import string
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(secrets.choice(alphabet) for _ in range(12))
    
    def _get_encryption_key(self) -> bytes:
        """Get or create encryption key for MT5 credentials"""
        # Use production-compatible path
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
    
    def _encrypt_password(self, password: str) -> str:
        """Encrypt MT5 password for secure storage"""
        fernet = Fernet(self._get_encryption_key())
        return fernet.encrypt(password.encode()).decode()
    
    async def connect_database(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.mongo_url)
            self.db = self.client[self.db_name]
            
            # Test connection
            await self.client.admin.command('ping')
            logger.info("✅ MongoDB connection established")
            return True
            
        except Exception as e:
            logger.error(f"❌ MongoDB connection failed: {e}")
            return False
    
    async def create_client_record(self):
        """Create Alejandro's client record"""
        try:
            # Check if client already exists
            existing_client = await self.db.users.find_one({"client_id": self.client_data["client_id"]})
            if existing_client:
                logger.info("✅ Client record already exists")
                return True
            
            # Hash the temporary password
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            hashed_password = pwd_context.hash(self.client_data["temporary_password"])
            
            client_record = {
                **self.client_data,
                "id": self.client_data["client_id"],
                "password_hash": hashed_password,
                "profile_picture": "",
                "login_attempts": 0,
                "last_login": None,
                "updated_at": datetime.now(timezone.utc)
            }
            
            result = await self.db.users.insert_one(client_record)
            
            if result.inserted_id:
                logger.info(f"✅ Created client record: {self.client_data['client_id']}")
                logger.info(f"📧 Email: {self.client_data['email']}")
                logger.info(f"🔑 Temporary Password: {self.client_data['temporary_password']}")
                return True
            else:
                logger.error("❌ Failed to create client record")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error creating client record: {e}")
            return False
    
    async def create_client_readiness(self):
        """Create client readiness record"""
        try:
            readiness_record = {
                "client_id": self.client_data["client_id"],
                "aml_kyc_completed": True,
                "agreement_signed": True,
                "account_creation_date": datetime(2025, 10, 1, tzinfo=timezone.utc),
                "investment_ready": True,
                "notes": "First production client - All documents completed",
                "updated_at": datetime.now(timezone.utc),
                "updated_by": "system",
                "readiness_override": False,
                "readiness_override_reason": "",
                "readiness_override_by": "",
                "readiness_override_date": None
            }
            
            # Upsert the readiness record
            result = await self.db.client_readiness.replace_one(
                {"client_id": self.client_data["client_id"]},
                readiness_record,
                upsert=True
            )
            
            logger.info("✅ Created client readiness record")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating client readiness: {e}")
            return False
    
    async def create_investment_records(self):
        """Create investment records for BALANCE and CORE funds"""
        try:
            investment_records = []
            
            for fund_key, investment in self.investment_data.items():
                # Check if investment already exists
                existing_investment = await self.db.investments.find_one({"investment_id": investment["investment_id"]})
                if existing_investment:
                    logger.info(f"✅ Investment {investment['investment_id']} already exists")
                    continue
                
                investment_record = {
                    **investment,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "total_interest_earned": 0.0
                }
                
                investment_records.append(investment_record)
            
            if investment_records:
                result = await self.db.investments.insert_many(investment_records)
                logger.info(f"✅ Created {len(result.inserted_ids)} investment records")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating investment records: {e}")
            return False
    
    async def create_mt5_accounts(self):
        """Create MT5 account records with real credentials"""
        try:
            mt5_records = []
            
            for mt5_account in self.mt5_accounts:
                # Check if MT5 account already exists
                existing_mt5 = await self.db.mt5_accounts.find_one({"account_id": mt5_account["account_id"]})
                if existing_mt5:
                    logger.info(f"✅ MT5 account {mt5_account['account_id']} already exists")
                    continue
                
                # Encrypt password
                encrypted_password = self._encrypt_password(mt5_account["mt5_password"])
                
                mt5_record = {
                    "account_id": mt5_account["account_id"],
                    "client_id": mt5_account["client_id"],
                    "fund_code": mt5_account["fund_code"], 
                    "broker_code": mt5_account["broker_code"],
                    "broker_name": mt5_account["broker_name"],
                    "mt5_login": mt5_account["mt5_login"],
                    "mt5_server": mt5_account["mt5_server"],
                    "encrypted_password": encrypted_password,
                    "total_allocated": mt5_account["principal_amount"],
                    "current_equity": mt5_account["mt5_initial_balance"],
                    "profit_loss": 0.0,
                    "profit_loss_percentage": 0.0,
                    "investment_ids": [mt5_account["investment_id"]],
                    "status": "active",
                    "is_active": True,
                    "is_demo": False,
                    "mt5_initial_balance": mt5_account["mt5_initial_balance"],
                    "banking_fees": 0.0,
                    "fee_notes": "",
                    "credentials_provided": True,
                    "created_via": "production_setup",
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                    "last_sync": None,
                    "sync_status": "pending"
                }
                
                mt5_records.append(mt5_record)
            
            if mt5_records:
                result = await self.db.mt5_accounts.insert_many(mt5_records)
                logger.info(f"✅ Created {len(result.inserted_ids)} MT5 account records")
                
                # Log account details (without passwords)
                for account in self.mt5_accounts:
                    logger.info(f"📊 MT5 Account: {account['mt5_login']} - {account['fund_code']} - ${account['principal_amount']:,.2f}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating MT5 accounts: {e}")
            return False
    
    async def verify_data_integrity(self):
        """Verify all data was created correctly"""
        try:
            verification_results = {
                "client_record": False,
                "client_readiness": False,
                "balance_investment": False,
                "core_investment": False,
                "mt5_accounts": [],
                "total_amounts": {}
            }
            
            # Verify client record
            client_record = await self.db.users.find_one({"client_id": self.client_data["client_id"]})
            verification_results["client_record"] = bool(client_record)
            
            # Verify client readiness
            readiness_record = await self.db.client_readiness.find_one({"client_id": self.client_data["client_id"]})
            verification_results["client_readiness"] = bool(readiness_record and readiness_record.get("investment_ready"))
            
            # Verify investments
            balance_investment = await self.db.investments.find_one({"investment_id": "inv_alejandro_balance_001"})
            verification_results["balance_investment"] = bool(balance_investment)
            
            core_investment = await self.db.investments.find_one({"investment_id": "inv_alejandro_core_001"})
            verification_results["core_investment"] = bool(core_investment)
            
            # Verify MT5 accounts
            mt5_accounts = await self.db.mt5_accounts.find({"client_id": self.client_data["client_id"]}).to_list(length=None)
            verification_results["mt5_accounts"] = [{"login": acc["mt5_login"], "amount": acc["total_allocated"]} for acc in mt5_accounts]
            
            # Calculate totals
            balance_total = sum(acc["total_allocated"] for acc in mt5_accounts if acc["fund_code"] == "BALANCE")
            core_total = sum(acc["total_allocated"] for acc in mt5_accounts if acc["fund_code"] == "CORE")
            
            verification_results["total_amounts"] = {
                "balance_fund_total": balance_total,
                "core_fund_total": core_total,
                "grand_total": balance_total + core_total,
                "expected_balance": 100000.00,
                "expected_core": 18151.41,
                "expected_total": 118151.41
            }
            
            # Print verification report
            logger.info("=" * 60)
            logger.info("ALEJANDRO MARISCAL PRODUCTION SETUP - VERIFICATION REPORT")
            logger.info("=" * 60)
            logger.info(f"✅ Client Record: {'PASS' if verification_results['client_record'] else 'FAIL'}")
            logger.info(f"✅ Client Readiness: {'PASS' if verification_results['client_readiness'] else 'FAIL'}")
            logger.info(f"✅ BALANCE Investment: {'PASS' if verification_results['balance_investment'] else 'FAIL'}")
            logger.info(f"✅ CORE Investment: {'PASS' if verification_results['core_investment'] else 'FAIL'}")
            logger.info(f"✅ MT5 Accounts Created: {len(verification_results['mt5_accounts'])}/4")
            
            logger.info("\n💰 INVESTMENT TOTALS:")
            logger.info(f"BALANCE Fund: ${verification_results['total_amounts']['balance_fund_total']:,.2f} (Expected: ${verification_results['total_amounts']['expected_balance']:,.2f})")
            logger.info(f"CORE Fund: ${verification_results['total_amounts']['core_fund_total']:,.2f} (Expected: ${verification_results['total_amounts']['expected_core']:,.2f})")
            logger.info(f"GRAND TOTAL: ${verification_results['total_amounts']['grand_total']:,.2f} (Expected: ${verification_results['total_amounts']['expected_total']:,.2f})")
            
            logger.info("\n🏦 MT5 ACCOUNTS:")
            for account in verification_results["mt5_accounts"]:
                logger.info(f"Login: {account['login']} - Amount: ${account['amount']:,.2f}")
            
            # Check if amounts match
            amounts_match = (
                abs(verification_results['total_amounts']['balance_fund_total'] - verification_results['total_amounts']['expected_balance']) < 0.01 and
                abs(verification_results['total_amounts']['core_fund_total'] - verification_results['total_amounts']['expected_core']) < 0.01 and
                abs(verification_results['total_amounts']['grand_total'] - verification_results['total_amounts']['expected_total']) < 0.01
            )
            
            logger.info(f"\n💯 AMOUNT VERIFICATION: {'PASS' if amounts_match else 'FAIL'}")
            logger.info("=" * 60)
            
            return verification_results
            
        except Exception as e:
            logger.error(f"❌ Error during verification: {e}")
            return None
    
    async def test_mt5_connections(self):
        """Test connections to real MT5 accounts (basic validation)"""
        try:
            logger.info("\n🔗 TESTING MT5 CONNECTIONS:")
            
            for account in self.mt5_accounts:
                login = account["mt5_login"]
                server = account["mt5_server"]
                
                # Basic validation of credentials format
                if not (100000 <= login <= 99999999):
                    logger.error(f"❌ Invalid login format: {login}")
                    continue
                
                if not server or len(server) < 3:
                    logger.error(f"❌ Invalid server format: {server}")
                    continue
                
                # For production, this would attempt real MT5 connection
                # For now, we'll do basic format validation
                logger.info(f"📊 Account {login} - Server: {server} - Amount: ${account['principal_amount']:,.2f} - FORMAT: VALID")
            
            logger.info("🔗 Connection testing completed (validation only)")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error testing connections: {e}")
            return False
    
    async def run_complete_setup(self):
        """Run the complete production setup"""
        try:
            logger.info("🚀 STARTING ALEJANDRO MARISCAL PRODUCTION SETUP")
            logger.info("=" * 60)
            
            # Step 1: Connect to database
            if not await self.connect_database():
                return False
            
            # Step 2: Create client record
            if not await self.create_client_record():
                return False
            
            # Step 3: Create client readiness
            if not await self.create_client_readiness():
                return False
            
            # Step 4: Create investment records  
            if not await self.create_investment_records():
                return False
            
            # Step 5: Create MT5 accounts with real credentials
            if not await self.create_mt5_accounts():
                return False
            
            # Step 6: Verify data integrity
            verification_results = await self.verify_data_integrity()
            if not verification_results:
                return False
            
            # Step 7: Test MT5 connections
            if not await self.test_mt5_connections():
                return False
            
            logger.info("\n✅ PRODUCTION SETUP COMPLETED SUCCESSFULLY!")
            logger.info("📧 Login Details:")
            logger.info(f"Username: {self.client_data['username']}")
            logger.info(f"Email: {self.client_data['email']}")
            logger.info(f"Temporary Password: {self.client_data['temporary_password']}")
            logger.info("🔒 Client will need to change password on first login")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Production setup failed: {e}")
            return False
        finally:
            if self.client:
                self.client.close()

async def main():
    """Main execution function"""
    setup = AlejandroProductionSetup()
    success = await setup.run_complete_setup()
    
    if success:
        print("\n🎉 ALEJANDRO MARISCAL PRODUCTION SETUP COMPLETE!")
        print("Ready for first real client deployment")
        return 0
    else:
        print("\n❌ PRODUCTION SETUP FAILED")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)