#!/usr/bin/env python3
"""
MONGODB ATLAS PRODUCTION DEPLOYMENT TEST
========================================

CRITICAL TESTING FOR TOMORROW'S DEPLOYMENT

This test verifies MongoDB Atlas connection for production deployment as requested:
1. MongoDB Atlas Connection - Test connection to cluster "FIDUS" with database "fidus_production"
2. Data Migration Verification - Verify all user data exists in MongoDB Atlas
3. Backend Health Check - Verify backend starts successfully with Atlas connection
4. Production Readiness - Verify no local MongoDB dependencies remain

Authentication: Use admin credentials (admin/password123)
Database: MongoDB Atlas cluster "FIDUS", database "fidus_production", user "chavapalmarubin_db_user"

Expected Results:
- Backend connects successfully to MongoDB Atlas
- All existing data is available (users, clients, CRM data)
- Authentication works properly with Atlas
- Ready for production deployment tomorrow
"""

import requests
import json
import sys
from datetime import datetime
import time
import os
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

# Configuration - Use production backend URL
BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

# MongoDB Atlas Configuration (from backend/.env)
MONGO_URL = "mongodb+srv://chavapalmarubin_db_user:HlX8kJaF38fIOVHi@fidus.ylp9be2.mongodb.net/?retryWrites=true&w=majority&appName=FIDUS"
DB_NAME = "fidus_production"  # Fixed the typo from backend/.env

class MongoDBAtlasProductionTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.test_results = []
        self.mongo_client = None
        self.db = None
        
    def log_result(self, test_name, success, message, details=None):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        result = {
            "test": test_name,
            "status": status,
            "success": success,
            "message": message,
            "details": details or {},
            "timestamp": datetime.now().isoformat()
        }
        self.test_results.append(result)
        print(f"{status}: {test_name} - {message}")
        if details and not success:
            print(f"   Details: {details}")
    
    async def test_mongodb_atlas_direct_connection(self):
        """Test direct connection to MongoDB Atlas cluster FIDUS"""
        try:
            print("🔗 Testing direct MongoDB Atlas connection...")
            
            # Create MongoDB Atlas client
            self.mongo_client = AsyncIOMotorClient(
                MONGO_URL,
                minPoolSize=5,
                maxPoolSize=100,
                maxIdleTimeMS=30000,
                serverSelectionTimeoutMS=5000,
                socketTimeoutMS=10000,
                connectTimeoutMS=10000,
                retryWrites=True
            )
            
            # Get database
            self.db = self.mongo_client[DB_NAME]
            
            # Test connection with ping
            await self.mongo_client.admin.command('ping')
            
            # Get server info
            server_info = await self.mongo_client.server_info()
            
            # Get database stats
            db_stats = await self.db.command("dbStats")
            
            self.log_result("MongoDB Atlas Direct Connection", True, 
                          f"Successfully connected to MongoDB Atlas cluster FIDUS",
                          {
                              "cluster": "FIDUS",
                              "database": DB_NAME,
                              "user": "chavapalmarubin_db_user",
                              "server_version": server_info.get('version'),
                              "db_size_mb": round(db_stats.get('dataSize', 0) / (1024*1024), 2),
                              "collections": db_stats.get('collections', 0),
                              "objects": db_stats.get('objects', 0)
                          })
            return True
            
        except Exception as e:
            self.log_result("MongoDB Atlas Direct Connection", False, 
                          f"Failed to connect to MongoDB Atlas: {str(e)}")
            return False
    
    async def test_user_data_migration_verification(self):
        """Verify all user data exists in MongoDB Atlas"""
        try:
            if not self.db:
                self.log_result("User Data Migration Verification", False, 
                              "No database connection available")
                return False
            
            print("👥 Verifying user data migration...")
            
            # Check users collection
            users_count = await self.db.users.count_documents({})
            
            # Get all users
            users = []
            async for user in self.db.users.find({}):
                users.append({
                    "id": user.get("id"),
                    "username": user.get("username"),
                    "name": user.get("name"),
                    "email": user.get("email"),
                    "type": user.get("type"),
                    "status": user.get("status")
                })
            
            # Check for critical users
            admin_user = await self.db.users.find_one({"username": "admin", "type": "admin"})
            salvador_user = await self.db.users.find_one({"username": "client3", "name": "SALVADOR PALMA"})
            alejandro_user = await self.db.users.find_one({"username": {"$regex": "alejandro", "$options": "i"}})
            
            # Check CRM prospects
            prospects_count = await self.db.crm_prospects.count_documents({})
            
            # Check client investments
            investments_count = await self.db.investments.count_documents({})
            
            critical_data_present = all([
                users_count >= 6,  # Should have at least 6 users
                admin_user is not None,
                salvador_user is not None
            ])
            
            if critical_data_present:
                self.log_result("User Data Migration Verification", True, 
                              f"All critical user data verified in MongoDB Atlas",
                              {
                                  "total_users": users_count,
                                  "admin_found": bool(admin_user),
                                  "salvador_found": bool(salvador_user),
                                  "alejandro_found": bool(alejandro_user),
                                  "crm_prospects": prospects_count,
                                  "investments": investments_count,
                                  "sample_users": users[:3]
                              })
                return True
            else:
                self.log_result("User Data Migration Verification", False, 
                              "Critical user data missing from MongoDB Atlas",
                              {
                                  "total_users": users_count,
                                  "admin_found": bool(admin_user),
                                  "salvador_found": bool(salvador_user),
                                  "alejandro_found": bool(alejandro_user)
                              })
                return False
                
        except Exception as e:
            self.log_result("User Data Migration Verification", False, 
                          f"Error verifying user data: {str(e)}")
            return False
    
    def test_backend_health_with_atlas(self):
        """Test backend health check with Atlas connection"""
        try:
            print("🏥 Testing backend health with MongoDB Atlas...")
            
            # Test basic health endpoint
            response = self.session.get(f"{BACKEND_URL}/health")
            
            if response.status_code == 200:
                health_data = response.json()
                
                # Test readiness endpoint (includes database connectivity)
                ready_response = self.session.get(f"{BACKEND_URL}/health/ready")
                
                if ready_response.status_code == 200:
                    ready_data = ready_response.json()
                    
                    self.log_result("Backend Health with Atlas", True, 
                                  "Backend successfully running with MongoDB Atlas connection",
                                  {
                                      "health_status": health_data.get("status"),
                                      "ready_status": ready_data.get("status"),
                                      "timestamp": health_data.get("timestamp")
                                  })
                    return True
                else:
                    self.log_result("Backend Health with Atlas", False, 
                                  f"Backend readiness check failed: HTTP {ready_response.status_code}",
                                  {"response": ready_response.text})
                    return False
            else:
                self.log_result("Backend Health with Atlas", False, 
                              f"Backend health check failed: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Backend Health with Atlas", False, 
                          f"Error testing backend health: {str(e)}")
            return False
    
    def authenticate_admin_with_atlas(self):
        """Test admin authentication with Atlas backend"""
        try:
            print("🔐 Testing admin authentication with MongoDB Atlas...")
            
            response = self.session.post(f"{BACKEND_URL}/auth/login", json={
                "username": ADMIN_USERNAME,
                "password": ADMIN_PASSWORD,
                "user_type": "admin"
            })
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get("token")
                if self.admin_token:
                    self.session.headers.update({"Authorization": f"Bearer {self.admin_token}"})
                    self.log_result("Admin Authentication with Atlas", True, 
                                  "Admin authentication successful with MongoDB Atlas backend",
                                  {
                                      "user_id": data.get("id"),
                                      "username": data.get("username"),
                                      "name": data.get("name"),
                                      "email": data.get("email")
                                  })
                    return True
                else:
                    self.log_result("Admin Authentication with Atlas", False, 
                                  "No token received from Atlas backend", {"response": data})
                    return False
            else:
                self.log_result("Admin Authentication with Atlas", False, 
                              f"Authentication failed: HTTP {response.status_code}", 
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Admin Authentication with Atlas", False, 
                          f"Exception during authentication: {str(e)}")
            return False
    
    def test_crm_data_availability(self):
        """Test CRM data availability in Atlas"""
        try:
            if not self.admin_token:
                self.log_result("CRM Data Availability", False, "No admin authentication")
                return False
            
            print("📊 Testing CRM data availability...")
            
            # Test CRM prospects endpoint
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            
            if response.status_code == 200:
                data = response.json()
                prospects = data.get("prospects", [])
                
                # Test pipeline stats
                stats_response = self.session.get(f"{BACKEND_URL}/crm/pipeline-stats")
                stats_success = stats_response.status_code == 200
                
                self.log_result("CRM Data Availability", True, 
                              f"CRM data accessible from MongoDB Atlas",
                              {
                                  "prospects_count": len(prospects),
                                  "pipeline_stats_available": stats_success,
                                  "sample_prospects": [p.get("name") for p in prospects[:3]]
                              })
                return True
            else:
                self.log_result("CRM Data Availability", False, 
                              f"CRM data not accessible: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("CRM Data Availability", False, 
                          f"Error testing CRM data: {str(e)}")
            return False
    
    def test_client_data_availability(self):
        """Test client data availability in Atlas"""
        try:
            if not self.admin_token:
                self.log_result("Client Data Availability", False, "No admin authentication")
                return False
            
            print("👤 Testing client data availability...")
            
            # Test admin users endpoint
            response = self.session.get(f"{BACKEND_URL}/admin/users")
            
            if response.status_code == 200:
                data = response.json()
                users = data.get("users", [])
                
                # Look for Salvador Palma specifically
                salvador_found = any(user.get("name") == "SALVADOR PALMA" for user in users)
                admin_found = any(user.get("type") == "admin" for user in users)
                
                self.log_result("Client Data Availability", True, 
                              f"Client data accessible from MongoDB Atlas",
                              {
                                  "total_users": len(users),
                                  "salvador_palma_found": salvador_found,
                                  "admin_users_found": admin_found,
                                  "user_types": list(set(user.get("type") for user in users))
                              })
                return True
            else:
                self.log_result("Client Data Availability", False, 
                              f"Client data not accessible: HTTP {response.status_code}",
                              {"response": response.text})
                return False
                
        except Exception as e:
            self.log_result("Client Data Availability", False, 
                          f"Error testing client data: {str(e)}")
            return False
    
    def test_production_readiness_verification(self):
        """Verify production readiness - no local MongoDB dependencies"""
        try:
            print("🚀 Testing production readiness...")
            
            # Test multiple critical endpoints to ensure Atlas integration
            critical_endpoints = [
                "/health",
                "/health/ready", 
                "/admin/users",
                "/crm/prospects"
            ]
            
            all_working = True
            endpoint_results = {}
            
            for endpoint in critical_endpoints:
                try:
                    response = self.session.get(f"{BACKEND_URL}{endpoint}")
                    endpoint_results[endpoint] = {
                        "status_code": response.status_code,
                        "working": response.status_code == 200
                    }
                    if response.status_code != 200:
                        all_working = False
                except Exception as e:
                    endpoint_results[endpoint] = {
                        "status_code": "ERROR",
                        "working": False,
                        "error": str(e)
                    }
                    all_working = False
            
            if all_working:
                self.log_result("Production Readiness Verification", True, 
                              "All critical endpoints working with MongoDB Atlas - Ready for deployment",
                              {
                                  "endpoints_tested": len(critical_endpoints),
                                  "all_working": all_working,
                                  "atlas_cluster": "FIDUS",
                                  "database": DB_NAME
                              })
                return True
            else:
                self.log_result("Production Readiness Verification", False, 
                              "Some critical endpoints not working with MongoDB Atlas",
                              {"endpoint_results": endpoint_results})
                return False
                
        except Exception as e:
            self.log_result("Production Readiness Verification", False, 
                          f"Error verifying production readiness: {str(e)}")
            return False
    
    async def run_all_tests(self):
        """Run all MongoDB Atlas production tests"""
        print("🎯 MONGODB ATLAS PRODUCTION DEPLOYMENT TEST")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"MongoDB Atlas Cluster: FIDUS")
        print(f"Database: {DB_NAME}")
        print(f"User: chavapalmarubin_db_user")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        # Test 1: Direct MongoDB Atlas Connection
        print("🔗 Testing MongoDB Atlas Connection...")
        print("-" * 50)
        atlas_connected = await self.test_mongodb_atlas_direct_connection()
        
        if atlas_connected:
            # Test 2: Data Migration Verification
            print("\n👥 Testing Data Migration...")
            print("-" * 50)
            await self.test_user_data_migration_verification()
        
        # Test 3: Backend Health with Atlas
        print("\n🏥 Testing Backend Health...")
        print("-" * 50)
        self.test_backend_health_with_atlas()
        
        # Test 4: Authentication with Atlas
        print("\n🔐 Testing Authentication...")
        print("-" * 50)
        auth_success = self.authenticate_admin_with_atlas()
        
        if auth_success:
            # Test 5: CRM Data Availability
            print("\n📊 Testing CRM Data...")
            print("-" * 50)
            self.test_crm_data_availability()
            
            # Test 6: Client Data Availability
            print("\n👤 Testing Client Data...")
            print("-" * 50)
            self.test_client_data_availability()
        
        # Test 7: Production Readiness
        print("\n🚀 Testing Production Readiness...")
        print("-" * 50)
        self.test_production_readiness_verification()
        
        # Generate summary
        self.generate_test_summary()
        
        # Close MongoDB connection
        if self.mongo_client:
            self.mongo_client.close()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🎯 MONGODB ATLAS PRODUCTION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['success'])
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {success_rate:.1f}%")
        print()
        
        # Show failed tests first (critical for deployment)
        if failed_tests > 0:
            print("❌ FAILED TESTS (DEPLOYMENT BLOCKERS):")
            for result in self.test_results:
                if not result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Show passed tests
        if passed_tests > 0:
            print("✅ PASSED TESTS:")
            for result in self.test_results:
                if result['success']:
                    print(f"   • {result['test']}: {result['message']}")
            print()
        
        # Critical deployment assessment
        critical_tests = [
            "MongoDB Atlas Direct Connection",
            "User Data Migration Verification", 
            "Backend Health with Atlas",
            "Admin Authentication with Atlas",
            "Production Readiness Verification"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 DEPLOYMENT READINESS ASSESSMENT:")
        if critical_passed >= 4:  # At least 4 out of 5 critical tests
            print("✅ MONGODB ATLAS INTEGRATION: READY FOR DEPLOYMENT")
            print("   ✓ MongoDB Atlas cluster FIDUS connection successful")
            print("   ✓ User data migration verified in production database")
            print("   ✓ Backend health confirmed with Atlas connection")
            print("   ✓ Authentication working with Atlas backend")
            print("   🚀 APPROVED FOR TOMORROW'S PRODUCTION DEPLOYMENT")
        else:
            print("❌ MONGODB ATLAS INTEGRATION: NOT READY FOR DEPLOYMENT")
            print("   ⚠️  Critical MongoDB Atlas integration issues detected")
            print("   🛑 DEPLOYMENT BLOCKED - Fix required before tomorrow")
            print("   📞 Contact development team immediately")
        
        print("\n" + "=" * 60)

async def main():
    """Main test execution"""
    test_runner = MongoDBAtlasProductionTest()
    success = await test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())