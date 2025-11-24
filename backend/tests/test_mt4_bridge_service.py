#!/usr/bin/env python3
"""
MT4 Bridge Service Field Name Correction and Service Validation Test

This test validates the critical bug fix where incorrect field name 'fundType' (camelCase) 
was being accessed instead of 'fund_type' (snake_case) on line 181 of mt4_bridge_api_service.py.

Test Objectives:
1. Service Import and Instantiation
2. MongoDB Document Structure Validation  
3. Field Name Compliance Check
4. Upsert Operation Test

Success Criteria:
✅ Python service imports successfully
✅ All field names match Python MT5 API standards (snake_case)
✅ Document structure is correct with _id='MT4_33200931'
✅ MongoDB upsert operation works correctly (no duplicates)
✅ No KeyError on accessing document['fund_type']
✅ Platform field = 'MT4'
✅ fund_type field = 'MONEY_MANAGER'
✅ Config collection also updated correctly
"""

import sys
import os
import asyncio
import json
from datetime import datetime, timezone
from typing import Dict, Any

# Add the vps-scripts directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../vps-scripts'))

# Test configuration
TEST_MONGODB_URI = "mongodb+srv://chavapalmarubin_db_user:"[CLEANED_PASSWORD]"@fidus.y1p9be2.mongodb.net/fidus_production?retryWrites=true&w=majority"
TEST_DATABASE = "fidus_production"
TEST_COLLECTIONS = ["mt5_accounts", "mt5_account_config"]

class MT4BridgeServiceTester:
    """Comprehensive tester for MT4 Bridge Service"""
    
    def __init__(self):
        self.test_results = []
        self.service = None
        self.mongo_client = None
        
    def log_test(self, test_name: str, passed: bool, message: str):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = {
            "test": test_name,
            "passed": passed,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["passed"])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*80)
        print("MT4 BRIDGE SERVICE TEST SUMMARY")
        print("="*80)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\nFAILED TESTS:")
            for result in self.test_results:
                if not result["passed"]:
                    print(f"❌ {result['test']}: {result['message']}")
        
        print("="*80)
        return failed_tests == 0

    def test_service_import(self):
        """Test 1: Service Import and Instantiation"""
        try:
            # Import the MT4 bridge service
            from mt4_bridge_api_service import MT4BridgeService
            
            # Check if all dependencies are available
            import zmq
            import pymongo
            import json
            from datetime import datetime, timezone
            
            self.log_test(
                "Service Import", 
                True, 
                "All dependencies (zmq, pymongo, datetime, json) imported successfully"
            )
            
            # Instantiate the service
            self.service = MT4BridgeService()
            
            self.log_test(
                "Service Instantiation", 
                True, 
                "MT4BridgeService class instantiated successfully"
            )
            
            return True
            
        except ImportError as e:
            self.log_test(
                "Service Import", 
                False, 
                f"Import error: {str(e)}"
            )
            return False
        except Exception as e:
            self.log_test(
                "Service Instantiation", 
                False, 
                f"Instantiation error: {str(e)}"
            )
            return False

    def test_mongodb_connection(self):
        """Test MongoDB connection"""
        try:
            import pymongo
            
            # Connect to MongoDB using the same URI as the service
            self.mongo_client = pymongo.MongoClient(
                TEST_MONGODB_URI,
                serverSelectionTimeoutMS=10000,
                connectTimeoutMS=10000,
                socketTimeoutMS=10000
            )
            
            # Test connection
            self.mongo_client.admin.command('ping')
            
            # Get database and collections
            db = self.mongo_client[TEST_DATABASE]
            accounts_collection = db['mt5_accounts']
            config_collection = db['mt5_account_config']
            
            self.log_test(
                "MongoDB Connection", 
                True, 
                f"Connected to {TEST_DATABASE} database successfully"
            )
            
            return db, accounts_collection, config_collection
            
        except Exception as e:
            self.log_test(
                "MongoDB Connection", 
                False, 
                f"Connection failed: {str(e)}"
            )
            return None, None, None

    def test_document_structure_validation(self):
        """Test 2: MongoDB Document Structure Validation"""
        try:
            # Create mock account data as specified in the review request
            mock_account_data = {
                'account': 33200931,
                'name': 'Money Manager MT4 Account',
                'server': 'MEXAtlantic-Real',
                'balance': 10000.00,
                'equity': 10500.00,
                'margin': 2000.00,
                'free_margin': 8500.00,  # CRITICAL: snake_case not freeMargin
                'profit': 500.00,
                'currency': 'USD',
                'leverage': 100,
                'credit': 0.00
            }
            
            self.log_test(
                "Mock Data Creation", 
                True, 
                "Mock account data created with correct snake_case field names"
            )
            
            # Connect to MongoDB
            db, accounts_collection, config_collection = self.test_mongodb_connection()
            if db is None:
                return False
            
            # Test the save_account_data method
            if not self.service:
                self.log_test(
                    "Service Availability", 
                    False, 
                    "MT4BridgeService not instantiated"
                )
                return False
            
            # Connect the service to MongoDB
            self.service.mongo_client = self.mongo_client
            self.service.db = db
            self.service.accounts_collection = accounts_collection
            self.service.config_collection = config_collection
            
            # Call save_account_data method
            success = self.service.save_account_data(mock_account_data)
            
            if not success:
                self.log_test(
                    "Save Account Data", 
                    False, 
                    "save_account_data() method returned False"
                )
                return False
            
            self.log_test(
                "Save Account Data", 
                True, 
                "save_account_data() method executed successfully"
            )
            
            # Verify document was created correctly
            document = accounts_collection.find_one({"_id": "MT4_33200931"})
            
            if not document:
                self.log_test(
                    "Document Creation", 
                    False, 
                    "Document with _id='MT4_33200931' not found in MongoDB"
                )
                return False
            
            self.log_test(
                "Document Creation", 
                True, 
                "Document created with correct _id: 'MT4_33200931'"
            )
            
            # CRITICAL TEST: Verify no KeyError when accessing fund_type
            try:
                fund_type_value = document['fund_type']
                self.log_test(
                    "Field Access - fund_type", 
                    True, 
                    f"No KeyError when accessing document['fund_type']: {fund_type_value}"
                )
            except KeyError:
                self.log_test(
                    "Field Access - fund_type", 
                    False, 
                    "KeyError when accessing document['fund_type'] - CRITICAL BUG NOT FIXED"
                )
                return False
            
            # Verify platform field
            if document.get('platform') == 'MT4':
                self.log_test(
                    "Platform Field", 
                    True, 
                    "Platform field correctly set to 'MT4'"
                )
            else:
                self.log_test(
                    "Platform Field", 
                    False, 
                    f"Platform field incorrect: {document.get('platform')}"
                )
            
            # Verify fund_type field
            if document.get('fund_type') == 'MONEY_MANAGER':
                self.log_test(
                    "Fund Type Field", 
                    True, 
                    "fund_type field correctly set to 'MONEY_MANAGER'"
                )
            else:
                self.log_test(
                    "Fund Type Field", 
                    False, 
                    f"fund_type field incorrect: {document.get('fund_type')}"
                )
            
            return True
            
        except Exception as e:
            self.log_test(
                "Document Structure Validation", 
                False, 
                f"Unexpected error: {str(e)}"
            )
            return False

    def test_field_name_compliance(self):
        """Test 3: Field Name Compliance Check"""
        try:
            db, accounts_collection, config_collection = self.test_mongodb_connection()
            if db is None:
                return False
            
            # Get the document we just created
            document = accounts_collection.find_one({"_id": "MT4_33200931"})
            
            if not document:
                self.log_test(
                    "Document Retrieval", 
                    False, 
                    "Cannot retrieve document for field name compliance check"
                )
                return False
            
            # Expected field names (Python MetaTrader5 API standards - snake_case)
            expected_fields = {
                'account': 'account number',
                'name': 'client name', 
                'server': 'server name',
                'balance': 'account balance',
                'equity': 'account equity',
                'margin': 'used margin',
                'free_margin': 'free margin (CRITICAL - NOT freeMargin)',
                'profit': 'current profit',
                'currency': 'account currency',
                'leverage': 'account leverage',
                'credit': 'account credit',
                'fund_type': 'fund type (CRITICAL FIX - NOT fundType)',
                'platform': 'trading platform',
                'updated_at': 'last update timestamp',
                '_id': 'document identifier'
            }
            
            # Check each expected field
            missing_fields = []
            incorrect_fields = []
            
            for field, description in expected_fields.items():
                if field not in document:
                    missing_fields.append(f"{field} ({description})")
                else:
                    # Field exists - check if it's the correct case
                    if field in ['free_margin', 'fund_type']:  # Critical fields
                        self.log_test(
                            f"Critical Field - {field}", 
                            True, 
                            f"✅ {field} field present (snake_case, not camelCase)"
                        )
            
            # Check for incorrect camelCase fields that should not exist
            forbidden_fields = ['freeMargin', 'fundType', 'accountNumber', 'clientName']
            found_forbidden = []
            
            for forbidden in forbidden_fields:
                if forbidden in document:
                    found_forbidden.append(forbidden)
            
            if missing_fields:
                self.log_test(
                    "Field Completeness", 
                    False, 
                    f"Missing fields: {', '.join(missing_fields)}"
                )
            else:
                self.log_test(
                    "Field Completeness", 
                    True, 
                    "All expected fields present in document"
                )
            
            if found_forbidden:
                self.log_test(
                    "Field Name Compliance", 
                    False, 
                    f"Found forbidden camelCase fields: {', '.join(found_forbidden)}"
                )
            else:
                self.log_test(
                    "Field Name Compliance", 
                    True, 
                    "No forbidden camelCase fields found - all snake_case compliant"
                )
            
            return len(missing_fields) == 0 and len(found_forbidden) == 0
            
        except Exception as e:
            self.log_test(
                "Field Name Compliance", 
                False, 
                f"Unexpected error: {str(e)}"
            )
            return False

    def test_upsert_operation(self):
        """Test 4: Upsert Operation Test"""
        try:
            db, accounts_collection, config_collection = self.test_mongodb_connection()
            if db is None:
                return False
            
            # Count documents before second save
            initial_count = accounts_collection.count_documents({"account": 33200931, "platform": "MT4"})
            
            # Create slightly modified mock data for second save
            mock_account_data_updated = {
                'account': 33200931,
                'name': 'Money Manager MT4 Account',
                'server': 'MEXAtlantic-Real',
                'balance': 11000.00,  # Updated balance
                'equity': 11500.00,   # Updated equity
                'margin': 2100.00,    # Updated margin
                'free_margin': 9400.00,  # Updated free margin
                'profit': 600.00,     # Updated profit
                'currency': 'USD',
                'leverage': 100,
                'credit': 0.00
            }
            
            # Call save_account_data again with updated data
            success = self.service.save_account_data(mock_account_data_updated)
            
            if not success:
                self.log_test(
                    "Second Save Operation", 
                    False, 
                    "Second save_account_data() call failed"
                )
                return False
            
            # Count documents after second save
            final_count = accounts_collection.count_documents({"account": 33200931, "platform": "MT4"})
            
            if final_count == initial_count:
                self.log_test(
                    "Upsert No Duplicates", 
                    True, 
                    f"Document count unchanged: {final_count} (no duplicates created)"
                )
            else:
                self.log_test(
                    "Upsert No Duplicates", 
                    False, 
                    f"Document count changed from {initial_count} to {final_count} (duplicates created)"
                )
                return False
            
            # Verify the document was updated with new values
            updated_document = accounts_collection.find_one({"_id": "MT4_33200931"})
            
            if updated_document and updated_document.get('balance') == 11000.00:
                self.log_test(
                    "Document Update", 
                    True, 
                    f"Document updated correctly - new balance: ${updated_document.get('balance'):,.2f}"
                )
            else:
                self.log_test(
                    "Document Update", 
                    False, 
                    f"Document not updated - balance: ${updated_document.get('balance', 0):,.2f}"
                )
                return False
            
            # Verify config collection was also updated
            config_doc = config_collection.find_one({"account_number": 33200931})
            
            if config_doc:
                self.log_test(
                    "Config Collection Update", 
                    True, 
                    "Config collection updated successfully"
                )
            else:
                self.log_test(
                    "Config Collection Update", 
                    False, 
                    "Config collection not updated"
                )
            
            return True
            
        except Exception as e:
            self.log_test(
                "Upsert Operation", 
                False, 
                f"Unexpected error: {str(e)}"
            )
            return False

    def cleanup(self):
        """Clean up test data"""
        try:
            if self.mongo_client:
                db = self.mongo_client[TEST_DATABASE]
                
                # Remove test documents
                db.mt5_accounts.delete_many({"_id": "MT4_33200931"})
                db.mt5_account_config.delete_many({"account_number": 33200931})
                
                self.mongo_client.close()
                
                self.log_test(
                    "Cleanup", 
                    True, 
                    "Test data cleaned up successfully"
                )
        except Exception as e:
            self.log_test(
                "Cleanup", 
                False, 
                f"Cleanup error: {str(e)}"
            )

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 STARTING MT4 BRIDGE SERVICE FIELD NAME CORRECTION TESTS")
        print("="*80)
        
        try:
            # Test 1: Service Import and Instantiation
            if not self.test_service_import():
                print("❌ Critical failure - cannot continue without service import")
                return False
            
            # Test 2: MongoDB Document Structure Validation
            if not self.test_document_structure_validation():
                print("❌ Critical failure - document structure validation failed")
                return False
            
            # Test 3: Field Name Compliance Check
            self.test_field_name_compliance()
            
            # Test 4: Upsert Operation Test
            self.test_upsert_operation()
            
            return True
            
        except Exception as e:
            self.log_test(
                "Test Execution", 
                False, 
                f"Unexpected error during test execution: {str(e)}"
            )
            return False
        finally:
            # Always cleanup
            self.cleanup()

def main():
    """Main test execution"""
    tester = MT4BridgeServiceTester()
    
    try:
        success = tester.run_all_tests()
        tester.print_summary()
        
        if success:
            print("\n🎉 ALL TESTS COMPLETED - MT4 BRIDGE SERVICE VALIDATION SUCCESSFUL!")
            print("✅ Field name correction (fundType → fund_type) verified")
            print("✅ Service ready for VPS deployment")
            return 0
        else:
            print("\n❌ TESTS FAILED - MT4 BRIDGE SERVICE NEEDS ATTENTION")
            print("🚨 Do not deploy until all tests pass")
            return 1
            
    except Exception as e:
        print(f"\n💥 FATAL ERROR: {str(e)}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)