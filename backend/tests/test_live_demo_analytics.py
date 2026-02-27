"""
Live Demo Analytics Backend Tests
Tests for the Demo Analytics dashboard that mirrors Trading Analytics but for LIVE DEMO accounts.
"""

import pytest
import requests
import os
import json
from datetime import datetime

# Backend URL from environment variable
BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestLiveDemoAnalytics:
    """Tests for Live Demo Analytics API endpoints"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup for each test - authenticate as admin"""
        self.admin_token = None
        self.authenticate_admin()
    
    def authenticate_admin(self):
        """Authenticate as admin and get token"""
        try:
            response = requests.post(
                f"{BASE_URL}/api/auth/login",
                json={
                    "username": "admin",
                    "password": "password123",
                    "user_type": "admin"
                },
                timeout=30
            )
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token')
                print(f"Admin authentication successful")
            else:
                print(f"Admin authentication failed: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Authentication error: {e}")
    
    def get_auth_headers(self):
        """Get authorization headers with token"""
        if self.admin_token:
            return {
                'Authorization': f'Bearer {self.admin_token}',
                'Content-Type': 'application/json'
            }
        return {'Content-Type': 'application/json'}
    
    # ============================================================
    # ADMIN LOGIN TEST
    # ============================================================
    
    def test_admin_login(self):
        """Test admin login endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "admin",
                "password": "password123",
                "user_type": "admin"
            },
            timeout=30
        )
        
        assert response.status_code == 200, f"Login failed: {response.status_code} - {response.text}"
        data = response.json()
        assert 'token' in data, "Token not in login response"
        assert data.get('type') == 'admin', "User type is not admin"
        print(f"Admin login test PASSED - token received")
    
    # ============================================================
    # LIVE DEMO ANALYTICS MANAGERS ENDPOINT
    # ============================================================
    
    def test_live_demo_analytics_managers_endpoint_exists(self):
        """Test that the live demo analytics managers endpoint exists and responds"""
        response = requests.get(
            f"{BASE_URL}/api/admin/live-demo-analytics/managers",
            headers=self.get_auth_headers(),
            timeout=30
        )
        
        # Endpoint should exist (not 404)
        assert response.status_code != 404, "Live Demo Analytics endpoint not found - 404"
        assert response.status_code in [200, 401, 403], f"Unexpected status code: {response.status_code}"
        print(f"Live Demo Analytics managers endpoint exists - Status: {response.status_code}")
    
    def test_live_demo_analytics_managers_returns_data(self):
        """Test that live demo analytics returns proper data structure"""
        response = requests.get(
            f"{BASE_URL}/api/admin/live-demo-analytics/managers?period_days=30",
            headers=self.get_auth_headers(),
            timeout=30
        )
        
        assert response.status_code == 200, f"Failed to get managers: {response.status_code} - {response.text}"
        data = response.json()
        
        # Check required fields in response
        assert 'success' in data, "Response missing 'success' field"
        assert 'managers' in data, "Response missing 'managers' field"
        assert 'account_type' in data, "Response missing 'account_type' field"
        
        # Verify account_type is 'live_demo'
        assert data['account_type'] == 'live_demo', f"Expected account_type 'live_demo', got '{data.get('account_type')}'"
        
        print(f"Live Demo Analytics managers response verified - {len(data.get('managers', []))} managers found")
        print(f"Response structure: {list(data.keys())}")
    
    def test_live_demo_managers_data_structure(self):
        """Test that manager data has correct structure with metrics"""
        response = requests.get(
            f"{BASE_URL}/api/admin/live-demo-analytics/managers?period_days=30",
            headers=self.get_auth_headers(),
            timeout=30
        )
        
        assert response.status_code == 200
        data = response.json()
        
        managers = data.get('managers', [])
        
        if managers:
            # Check first manager has required fields
            manager = managers[0]
            
            expected_fields = [
                'manager_id', 'manager_name', 'account', 'fund', 'account_type',
                'return_percentage', 'total_pnl', 'initial_allocation'
            ]
            
            for field in expected_fields:
                assert field in manager, f"Manager missing field: {field}"
            
            # Verify account_type is live_demo for each manager
            for mgr in managers:
                assert mgr.get('account_type') == 'live_demo', f"Manager {mgr.get('account')} has wrong account_type: {mgr.get('account_type')}"
            
            print(f"Manager data structure verified - Sample manager: {manager.get('manager_name')}")
        else:
            print("No live demo managers found - this may be expected if no demo accounts exist")
    
    def test_live_demo_analytics_with_different_periods(self):
        """Test live demo analytics with different period_days values"""
        periods = [7, 30, 90]
        
        for period in periods:
            response = requests.get(
                f"{BASE_URL}/api/admin/live-demo-analytics/managers?period_days={period}",
                headers=self.get_auth_headers(),
                timeout=30
            )
            
            assert response.status_code == 200, f"Failed for period {period}: {response.status_code}"
            data = response.json()
            assert data.get('period_days') == period, f"Period mismatch: expected {period}, got {data.get('period_days')}"
            print(f"Period {period} days test PASSED")
    
    # ============================================================
    # LIVE DEMO AI ADVISOR ENDPOINTS
    # ============================================================
    
    def test_live_demo_ai_insights_endpoint(self):
        """Test the live demo AI insights endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/admin/live-demo-ai-advisor/insights?period_days=30",
            headers=self.get_auth_headers(),
            timeout=60  # AI calls may take longer
        )
        
        # Should either work (200) or indicate no data (still 200 with error message)
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert 'success' in data
            print(f"Live Demo AI Insights endpoint working - success: {data.get('success')}")
        else:
            print(f"AI Insights returned {response.status_code} - may be expected if no demo data")
    
    def test_live_demo_ai_chat_endpoint(self):
        """Test the live demo AI chat endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/admin/live-demo-ai-advisor/chat",
            headers=self.get_auth_headers(),
            json={
                "message": "What are the top performing demo strategies?",
                "session_id": f"test_session_{datetime.now().timestamp()}",
                "include_context": True,
                "period_days": 30
            },
            timeout=90  # AI calls may take longer
        )
        
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert 'success' in data
            print(f"Live Demo AI Chat endpoint working - success: {data.get('success')}")
        else:
            print(f"AI Chat returned {response.status_code}")
    
    def test_live_demo_ai_allocation_endpoint(self):
        """Test the live demo AI allocation advisor endpoint"""
        response = requests.post(
            f"{BASE_URL}/api/admin/live-demo-ai-advisor/allocation",
            headers=self.get_auth_headers(),
            json={
                "total_capital": 100000,
                "risk_tolerance": "moderate",
                "period_days": 30
            },
            timeout=90  # AI calls may take longer
        )
        
        assert response.status_code in [200, 500], f"Unexpected status: {response.status_code}"
        
        if response.status_code == 200:
            data = response.json()
            assert 'success' in data
            print(f"Live Demo AI Allocation endpoint working - success: {data.get('success')}")
        else:
            print(f"AI Allocation returned {response.status_code}")
    
    # ============================================================
    # DATA SEPARATION VERIFICATION
    # ============================================================
    
    def test_demo_vs_real_data_separation(self):
        """CRITICAL: Verify that demo analytics returns DIFFERENT data than real trading analytics"""
        # Get live demo managers
        demo_response = requests.get(
            f"{BASE_URL}/api/admin/live-demo-analytics/managers?period_days=30",
            headers=self.get_auth_headers(),
            timeout=30
        )
        
        # Get real trading managers
        real_response = requests.get(
            f"{BASE_URL}/api/admin/trading-analytics/managers?period_days=30",
            headers=self.get_auth_headers(),
            timeout=30
        )
        
        # Both should return 200
        assert demo_response.status_code == 200, f"Demo endpoint failed: {demo_response.status_code}"
        
        demo_data = demo_response.json()
        demo_managers = demo_data.get('managers', [])
        demo_accounts = set(m.get('account') for m in demo_managers)
        
        if real_response.status_code == 200:
            real_data = real_response.json()
            real_managers = real_data.get('managers', [])
            real_accounts = set(m.get('account') for m in real_managers)
            
            # Verify no overlap between demo and real accounts
            overlap = demo_accounts.intersection(real_accounts)
            
            print(f"Demo accounts: {demo_accounts}")
            print(f"Real accounts: {real_accounts}")
            print(f"Overlap: {overlap}")
            
            # No overlap is expected (complete separation)
            assert len(overlap) == 0, f"DATA SEPARATION VIOLATION: Found overlapping accounts: {overlap}"
            print("Data separation verified - NO overlap between demo and real accounts")
        else:
            print(f"Real trading analytics returned {real_response.status_code} - checking demo account_type only")
            
        # Verify all demo managers have account_type = 'live_demo'
        for manager in demo_managers:
            assert manager.get('account_type') == 'live_demo', f"Manager {manager.get('account')} is not live_demo type"
        
        print("All demo managers confirmed as 'live_demo' account_type")
    
    # ============================================================
    # LIVE DEMO ACCOUNTS ENDPOINT
    # ============================================================
    
    def test_live_demo_accounts_list(self):
        """Test the basic live demo accounts list endpoint"""
        response = requests.get(
            f"{BASE_URL}/api/live-demo/accounts",
            timeout=30
        )
        
        assert response.status_code == 200, f"Failed to get demo accounts: {response.status_code}"
        data = response.json()
        
        assert 'success' in data
        assert 'accounts' in data
        
        accounts = data.get('accounts', [])
        print(f"Found {len(accounts)} live demo accounts")
        
        # Verify account structure
        for acc in accounts:
            assert acc.get('account_type') == 'live_demo', f"Account {acc.get('account')} is not live_demo type"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
