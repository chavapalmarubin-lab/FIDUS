#!/usr/bin/env python3
"""
DETAILED CRM PROSPECTS ANALYSIS TEST
===================================

This test provides detailed analysis of the CRM prospects system to understand:
1. Actual data structure and schema
2. Google Drive folder implementation
3. MongoDB schema validation status
4. Calendar API issues
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://invest-manager-9.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

class CRMDetailedAnalysisTest:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        
    def authenticate_admin(self):
        """Authenticate as admin user"""
        try:
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
                    print("✅ Admin authentication successful")
                    return True
            print("❌ Admin authentication failed")
            return False
        except Exception as e:
            print(f"❌ Authentication error: {str(e)}")
            return False
    
    def analyze_prospects_structure(self):
        """Analyze the actual structure of prospects data"""
        print("\n🔍 ANALYZING PROSPECTS DATA STRUCTURE")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/prospects")
            if response.status_code == 200:
                prospects_data = response.json()
                print(f"✅ Prospects endpoint accessible")
                print(f"Response type: {type(prospects_data).__name__}")
                
                if isinstance(prospects_data, dict):
                    print(f"Response keys: {list(prospects_data.keys())}")
                    if 'prospects' in prospects_data:
                        prospects = prospects_data['prospects']
                        print(f"Total prospects: {len(prospects)}")
                        
                        if len(prospects) > 0:
                            print("\n📋 SAMPLE PROSPECT STRUCTURE:")
                            sample = prospects[0]
                            for key, value in sample.items():
                                if isinstance(value, dict):
                                    print(f"  {key}: {type(value).__name__} with keys {list(value.keys())}")
                                else:
                                    print(f"  {key}: {type(value).__name__} = {value}")
                            
                            # Look for Alejandro specifically
                            alejandro = None
                            for prospect in prospects:
                                if 'Alejandro' in prospect.get('name', ''):
                                    alejandro = prospect
                                    break
                            
                            if alejandro:
                                print(f"\n👤 ALEJANDRO MARISCAL ROMERO FOUND:")
                                print(f"  prospect_id: {alejandro.get('prospect_id')}")
                                print(f"  name: {alejandro.get('name')}")
                                print(f"  email: {alejandro.get('email')}")
                                print(f"  phone: {alejandro.get('phone')}")
                                print(f"  stage: {alejandro.get('stage')}")
                                
                                # Analyze Google Drive folder structure
                                folder_data = alejandro.get('google_drive_folder')
                                if folder_data:
                                    print(f"  google_drive_folder type: {type(folder_data).__name__}")
                                    if isinstance(folder_data, dict):
                                        print(f"    folder_id: {folder_data.get('folder_id')}")
                                        print(f"    folder_name: {folder_data.get('folder_name')}")
                                        print(f"    web_view_link: {folder_data.get('web_view_link')}")
                                        print(f"    created_at: {folder_data.get('created_at')}")
                                    else:
                                        print(f"    value: {folder_data}")
                                else:
                                    print(f"  google_drive_folder: None/Missing")
                            else:
                                print("\n❌ Alejandro Mariscal Romero not found")
                
            else:
                print(f"❌ Failed to get prospects: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error analyzing prospects: {str(e)}")
    
    def test_prospect_creation_detailed(self):
        """Test prospect creation with detailed response analysis"""
        print("\n🔍 TESTING PROSPECT CREATION (DETAILED)")
        print("-" * 50)
        
        try:
            test_data = {
                "name": "Test Prospect Analysis",
                "email": "test.analysis@example.com",
                "phone": "+1234567890",
                "notes": "Detailed analysis test prospect"
            }
            
            response = self.session.post(f"{BACKEND_URL}/crm/prospects", json=test_data)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code in [200, 201]:
                result = response.json()
                print("✅ Prospect creation successful")
                print(f"Response type: {type(result).__name__}")
                print(f"Response keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
                
                # Analyze the created prospect structure
                if 'prospect' in result:
                    prospect = result['prospect']
                    print(f"\n📋 CREATED PROSPECT STRUCTURE:")
                    for key, value in prospect.items():
                        if isinstance(value, dict):
                            print(f"  {key}: {type(value).__name__} with keys {list(value.keys())}")
                        else:
                            print(f"  {key}: {type(value).__name__} = {value}")
                
            else:
                print(f"❌ Prospect creation failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing prospect creation: {str(e)}")
    
    def test_calendar_api_detailed(self):
        """Test Calendar API endpoints with detailed analysis"""
        print("\n🔍 TESTING CALENDAR API (DETAILED)")
        print("-" * 50)
        
        endpoints = [
            "/google/calendar/events",
            "/google/calendar/real-events", 
            "/admin/google/profile"
        ]
        
        for endpoint in endpoints:
            try:
                print(f"\nTesting: {endpoint}")
                response = self.session.get(f"{BACKEND_URL}{endpoint}")
                print(f"  Status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  ✅ Success - Response type: {type(data).__name__}")
                    if isinstance(data, dict):
                        print(f"  Keys: {list(data.keys())}")
                elif response.status_code == 401:
                    print(f"  🔐 Requires authentication (expected)")
                elif response.status_code == 500:
                    print(f"  ❌ Server error")
                    error_text = response.text[:200]
                    print(f"  Error: {error_text}")
                else:
                    print(f"  ⚠️ Unexpected status")
                    
            except Exception as e:
                print(f"  ❌ Exception: {str(e)}")
    
    def test_pipeline_stats_detailed(self):
        """Test pipeline stats with detailed analysis"""
        print("\n🔍 TESTING PIPELINE STATS (DETAILED)")
        print("-" * 50)
        
        try:
            response = self.session.get(f"{BACKEND_URL}/crm/pipeline-stats")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ Pipeline stats accessible")
                print(f"Response type: {type(data).__name__}")
                
                if isinstance(data, dict):
                    print(f"Top-level keys: {list(data.keys())}")
                    
                    if 'stats' in data:
                        stats = data['stats']
                        print(f"\nStats structure:")
                        for key, value in stats.items():
                            print(f"  {key}: {type(value).__name__} = {value}")
                    
                    # Check what the frontend might expect
                    print(f"\nFrontend compatibility check:")
                    print(f"  Has 'stages': {'stages' in data}")
                    print(f"  Has 'total_prospects': {'total_prospects' in data}")
                    print(f"  Has 'conversion_rate': {'conversion_rate' in data}")
                    
                    # Check nested stats
                    if 'stats' in data:
                        nested_stats = data['stats']
                        print(f"  Nested 'total_prospects': {'total_prospects' in nested_stats}")
                        print(f"  Nested 'conversion_rate': {'conversion_rate' in nested_stats}")
                
            else:
                print(f"❌ Pipeline stats failed: HTTP {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error testing pipeline stats: {str(e)}")
    
    def run_analysis(self):
        """Run complete detailed analysis"""
        print("🎯 DETAILED CRM PROSPECTS ANALYSIS")
        print("=" * 50)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Analysis Time: {datetime.now().isoformat()}")
        
        if not self.authenticate_admin():
            return False
        
        self.analyze_prospects_structure()
        self.test_prospect_creation_detailed()
        self.test_calendar_api_detailed()
        self.test_pipeline_stats_detailed()
        
        print("\n" + "=" * 50)
        print("🎯 ANALYSIS COMPLETE")
        print("=" * 50)
        
        return True

def main():
    """Main analysis execution"""
    analyzer = CRMDetailedAnalysisTest()
    analyzer.run_analysis()

if __name__ == "__main__":
    main()