#!/usr/bin/env python3
"""
FINAL: Salvador Palma Data Verification and Restoration Test
===========================================================

This script provides a comprehensive assessment of Salvador Palma's data status
across both preview and production environments.
"""

import requests
import sys
import json
from datetime import datetime

class FinalSalvadorTest:
    def __init__(self):
        self.environments = {
            "Preview": "https://fidus-workspace.preview.emergentagent.com",
            "Production": "https://fidus-invest.emergent.host"
        }
        self.results = {}
        
        # Expected Salvador data
        self.salvador_expected = {
            "client_id": "client_003",
            "name": "SALVADOR PALMA",
            "email": "chava@alyarglobal.com",
            "balance_investment": 1263485.40,
            "mt5_login": "9928326",
            "mt5_server": "DooTechnology-Live",
            "mt5_balance": 1837934.05,
            "mt5_profits": 860448.65
        }

    def authenticate(self, base_url):
        """Authenticate with environment"""
        try:
            response = requests.post(f"{base_url}/api/auth/login", json={
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            }, timeout=10)
            
            if response.status_code == 200:
                return response.json().get("token")
            return None
        except:
            return None

    def get_headers(self, token):
        """Get headers with auth token"""
        headers = {'Content-Type': 'application/json'}
        if token:
            headers['Authorization'] = f"Bearer {token}"
        return headers

    def test_environment(self, env_name, base_url):
        """Test a specific environment"""
        print(f"\n{'='*60}")
        print(f"🔍 TESTING {env_name.upper()} ENVIRONMENT")
        print(f"{'='*60}")
        print(f"URL: {base_url}")
        
        results = {
            "environment": env_name,
            "url": base_url,
            "auth_success": False,
            "client_exists": False,
            "client_count": 0,
            "investment_exists": False,
            "investment_count": 0,
            "balance_investment_amount": 0,
            "endpoints_working": [],
            "endpoints_failing": [],
            "critical_issues": [],
            "recommendations": []
        }
        
        # Step 1: Authentication
        token = self.authenticate(base_url)
        if token:
            results["auth_success"] = True
            print("✅ Authentication successful")
        else:
            results["critical_issues"].append("Authentication failed")
            print("❌ Authentication failed")
            return results
        
        headers = self.get_headers(token)
        
        # Step 2: Check clients
        try:
            response = requests.get(f"{base_url}/api/clients/all", headers=headers, timeout=10)
            if response.status_code == 200:
                results["endpoints_working"].append("/api/clients/all")
                clients = response.json().get("clients", [])
                results["client_count"] = len(clients)
                print(f"✅ Clients endpoint working: {len(clients)} clients found")
                
                # Look for Salvador
                for client in clients:
                    if (client.get("id") == self.salvador_expected["client_id"] or
                        "SALVADOR" in client.get("name", "").upper() or
                        self.salvador_expected["email"] in client.get("email", "")):
                        results["client_exists"] = True
                        print(f"   ✅ Salvador found: {client.get('name')} ({client.get('email')})")
                        break
                
                if not results["client_exists"]:
                    results["critical_issues"].append("Salvador Palma client profile missing")
                    print("   ❌ Salvador Palma NOT found")
            else:
                results["endpoints_failing"].append("/api/clients/all")
                results["critical_issues"].append(f"Clients endpoint failed: {response.status_code}")
                print(f"❌ Clients endpoint failed: {response.status_code}")
        except Exception as e:
            results["endpoints_failing"].append("/api/clients/all")
            results["critical_issues"].append(f"Clients endpoint error: {str(e)}")
            print(f"❌ Clients endpoint error: {str(e)}")
        
        # Step 3: Check investments
        try:
            response = requests.get(f"{base_url}/api/investments/client/{self.salvador_expected['client_id']}", 
                                  headers=headers, timeout=10)
            if response.status_code == 200:
                results["endpoints_working"].append("/api/investments/client/{client_id}")
                data = response.json()
                investments = data.get("investments", [])
                results["investment_count"] = len(investments)
                print(f"✅ Investments endpoint working: {len(investments)} investments found")
                
                # Look for BALANCE investment
                for inv in investments:
                    if inv.get("fund_code") == "BALANCE":
                        results["investment_exists"] = True
                        results["balance_investment_amount"] = inv.get("principal_amount", 0)
                        print(f"   ✅ BALANCE investment found: ${inv.get('principal_amount', 0):,.2f}")
                        break
                
                if not results["investment_exists"]:
                    results["critical_issues"].append("Salvador's BALANCE fund investment missing")
                    print("   ❌ BALANCE investment NOT found")
            else:
                results["endpoints_failing"].append("/api/investments/client/{client_id}")
                results["critical_issues"].append(f"Investments endpoint failed: {response.status_code}")
                print(f"❌ Investments endpoint failed: {response.status_code}")
        except Exception as e:
            results["endpoints_failing"].append("/api/investments/client/{client_id}")
            results["critical_issues"].append(f"Investments endpoint error: {str(e)}")
            print(f"❌ Investments endpoint error: {str(e)}")
        
        # Step 4: Test investment creation endpoint
        try:
            test_data = {
                "client_id": "test_client_validation",
                "fund_code": "CORE",
                "amount": 10000.0
            }
            response = requests.post(f"{base_url}/api/investments/create", 
                                   json=test_data, headers=headers, timeout=10)
            
            if response.status_code in [200, 400, 403]:  # 400/403 are expected for validation
                results["endpoints_working"].append("/api/investments/create")
                print("✅ Investment creation endpoint accessible")
            else:
                results["endpoints_failing"].append("/api/investments/create")
                results["critical_issues"].append(f"Investment creation endpoint failed: {response.status_code}")
                print(f"❌ Investment creation endpoint failed: {response.status_code}")
        except Exception as e:
            results["endpoints_failing"].append("/api/investments/create")
            results["critical_issues"].append(f"Investment creation endpoint error: {str(e)}")
            print(f"❌ Investment creation endpoint error: {str(e)}")
        
        # Step 5: Generate recommendations
        if env_name == "Production":
            if not results["client_exists"]:
                results["recommendations"].append("Restore Salvador Palma client profile (client_003)")
            if not results["investment_exists"]:
                results["recommendations"].append("Create BALANCE fund investment: $1,263,485.40")
                results["recommendations"].append("Create MT5 account mapping: Login 9928326")
            if "/api/investments/create" in results["endpoints_failing"]:
                results["recommendations"].append("Fix investment creation endpoint - missing route decorator")
        
        return results

    def run_comprehensive_test(self):
        """Run comprehensive test across all environments"""
        print("=" * 80)
        print("🚨 SALVADOR PALMA COMPREHENSIVE DATA VERIFICATION")
        print("=" * 80)
        print(f"Target: {self.salvador_expected['name']} ({self.salvador_expected['email']})")
        print(f"Expected BALANCE Investment: ${self.salvador_expected['balance_investment']:,.2f}")
        print(f"Expected MT5 Account: {self.salvador_expected['mt5_login']}")
        print("=" * 80)
        
        # Test all environments
        for env_name, base_url in self.environments.items():
            self.results[env_name] = self.test_environment(env_name, base_url)
        
        # Generate final report
        self.generate_final_report()
        
        # Return True if production is ready
        prod_results = self.results.get("Production", {})
        return (prod_results.get("client_exists", False) and 
                prod_results.get("investment_exists", False))

    def generate_final_report(self):
        """Generate final comprehensive report"""
        print("\n" + "=" * 80)
        print("📋 COMPREHENSIVE ASSESSMENT REPORT")
        print("=" * 80)
        
        for env_name, results in self.results.items():
            print(f"\n🔍 {env_name.upper()} ENVIRONMENT:")
            print(f"   URL: {results['url']}")
            print(f"   Authentication: {'✅' if results['auth_success'] else '❌'}")
            print(f"   Total Clients: {results['client_count']}")
            print(f"   Salvador Client: {'✅' if results['client_exists'] else '❌'}")
            print(f"   Total Investments: {results['investment_count']}")
            print(f"   BALANCE Investment: {'✅' if results['investment_exists'] else '❌'}")
            
            if results['investment_exists']:
                print(f"   Investment Amount: ${results['balance_investment_amount']:,.2f}")
            
            print(f"   Working Endpoints: {len(results['endpoints_working'])}")
            print(f"   Failing Endpoints: {len(results['endpoints_failing'])}")
            
            if results['critical_issues']:
                print(f"   🚨 Critical Issues:")
                for issue in results['critical_issues']:
                    print(f"      - {issue}")
            
            if results['recommendations']:
                print(f"   💡 Recommendations:")
                for rec in results['recommendations']:
                    print(f"      - {rec}")
        
        # Overall assessment
        preview_ok = self.results.get("Preview", {}).get("client_exists", False) and self.results.get("Preview", {}).get("investment_exists", False)
        production_ok = self.results.get("Production", {}).get("client_exists", False) and self.results.get("Production", {}).get("investment_exists", False)
        
        print("\n" + "=" * 80)
        print("🎯 FINAL DEPLOYMENT ASSESSMENT")
        print("=" * 80)
        print(f"Preview Environment: {'✅ READY' if preview_ok else '❌ ISSUES'}")
        print(f"Production Environment: {'✅ READY' if production_ok else '❌ BLOCKED'}")
        
        if production_ok:
            print("\n🚀 PRODUCTION DEPLOYMENT: APPROVED")
            print("   Salvador Palma's data is complete and ready for production use.")
        else:
            print("\n🚨 PRODUCTION DEPLOYMENT: BLOCKED")
            print("   Salvador Palma's data restoration required before deployment.")
            
            # Specific actions needed
            prod_results = self.results.get("Production", {})
            print("\n📋 REQUIRED ACTIONS:")
            
            if not prod_results.get("auth_success", False):
                print("   1. Fix production authentication system")
            
            if "/api/investments/create" in prod_results.get("endpoints_failing", []):
                print("   2. Deploy fixed investment creation endpoint to production")
            
            if not prod_results.get("client_exists", False):
                print("   3. Restore Salvador Palma client profile (client_003)")
            
            if not prod_results.get("investment_exists", False):
                print("   4. Create Salvador's BALANCE fund investment ($1,263,485.40)")
                print("   5. Create MT5 account mapping (Login: 9928326)")
                print("   6. Confirm deposit payment")
            
            print("\n⚠️  RECOMMENDATION: Deploy preview environment code to production")
            print("   The preview environment has Salvador's complete data and working endpoints.")

def main():
    """Main function"""
    try:
        tester = FinalSalvadorTest()
        success = tester.run_comprehensive_test()
        return success
    except Exception as e:
        print(f"\n💥 CRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)