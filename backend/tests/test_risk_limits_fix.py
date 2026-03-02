"""
Test Risk Limits Fix - Hull Risk Engine deal data retrieval

This test verifies that the fix for retrieving demo account deals from 
mt5_deals_history collection is working correctly.

Issue: Risk Limits tab in Demo Analytics was showing 0 trades analyzed 
and 100% compliance for all strategies.

Fix: Updated get_deals_for_account() method in HullRiskEngine to query 
both mt5_deals and mt5_deals_history collections.
"""

import pytest
import requests
import os

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', '').rstrip('/')

class TestRiskLimitsFix:
    """Tests for the Risk Limits fix verifying demo account deal retrieval"""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup authentication token"""
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "username": "admin",
                "password": "Password123",
                "user_type": "admin"
            }
        )
        assert login_response.status_code == 200, f"Login failed: {login_response.text}"
        self.token = login_response.json().get("token")
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    def test_account_2217_uno14_trades_analyzed(self):
        """
        Account 2217 (UNO14) should show ~991 trades with Score 70 (Moderate)
        """
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2217?period_days=30",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify success
        assert data.get("success") == True, "API should return success"
        
        # Verify trades are being analyzed (not 0)
        total_trades = data.get("total_trades_analyzed", 0)
        assert total_trades > 900, f"Expected ~991 trades, got {total_trades}"
        
        # Verify risk score (expected 70 Moderate)
        risk_score = data.get("risk_control_score", {}).get("composite_score", 0)
        assert 65 <= risk_score <= 75, f"Expected score ~70, got {risk_score}"
        
        # Verify risk label
        risk_label = data.get("risk_control_score", {}).get("label", "")
        assert risk_label == "Moderate", f"Expected 'Moderate', got {risk_label}"
        
        print(f"✓ Account 2217 (UNO14): {total_trades} trades, Score {risk_score} ({risk_label})")
    
    def test_account_2210_gold_day_trading(self):
        """
        Account 2210 (GOLD DAY TRADING) should show ~623 trades with Score 40 (Weak)
        """
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2210?period_days=30",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify trades are being analyzed
        total_trades = data.get("total_trades_analyzed", 0)
        assert total_trades > 600, f"Expected ~623 trades, got {total_trades}"
        
        # Verify risk score (expected 40 Weak)
        risk_score = data.get("risk_control_score", {}).get("composite_score", 0)
        assert 35 <= risk_score <= 45, f"Expected score ~40, got {risk_score}"
        
        risk_label = data.get("risk_control_score", {}).get("label", "")
        assert risk_label == "Weak", f"Expected 'Weak', got {risk_label}"
        
        print(f"✓ Account 2210 (GOLD DAY TRADING): {total_trades} trades, Score {risk_score} ({risk_label})")
    
    def test_account_2215_joel_nasdaq_strong_score(self):
        """
        Account 2215 (JOEL ALVES NASDAQ) should show ~383 trades with Score 100 (Strong)
        """
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2215?period_days=30",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify trades are being analyzed
        total_trades = data.get("total_trades_analyzed", 0)
        assert total_trades > 350, f"Expected ~383 trades, got {total_trades}"
        
        # Verify risk score (expected 100 Strong)
        risk_score = data.get("risk_control_score", {}).get("composite_score", 0)
        assert risk_score >= 95, f"Expected score ~100, got {risk_score}"
        
        risk_label = data.get("risk_control_score", {}).get("label", "")
        assert risk_label == "Strong", f"Expected 'Strong', got {risk_label}"
        
        print(f"✓ Account 2215 (JOEL ALVES NASDAQ): {total_trades} trades, Score {risk_score} ({risk_label})")
    
    def test_compliance_data_present(self):
        """
        Verify compliance summary data is present and correct
        """
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2217?period_days=30",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        compliance = data.get("compliance_summary", {})
        
        # Verify lot size compliance
        lot_compliance = compliance.get("lot_size_compliance", {})
        assert lot_compliance.get("total_trades", 0) > 0, "Should have lot size compliance data"
        assert "compliance_rate" in lot_compliance, "Should have compliance rate"
        
        # Verify risk per trade compliance
        risk_compliance = compliance.get("risk_per_trade_compliance", {})
        assert risk_compliance.get("total_trades", 0) > 0, "Should have risk per trade data"
        
        # Verify daily loss compliance
        daily_compliance = compliance.get("daily_loss_compliance", {})
        assert "status" in daily_compliance, "Should have daily loss status"
        
        print(f"✓ Compliance data: Lot Size {lot_compliance.get('compliance_rate')}%, "
              f"Risk Per Trade {risk_compliance.get('compliance_rate')}%")
    
    def test_instruments_data_present(self):
        """
        Verify instruments breakdown is present
        """
        response = requests.get(
            f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/2217?period_days=30",
            headers=self.headers
        )
        
        assert response.status_code == 200
        data = response.json()
        
        instruments = data.get("instruments", [])
        assert len(instruments) > 0, "Should have instrument breakdown"
        
        for inst in instruments:
            assert "symbol" in inst, "Instrument should have symbol"
            assert "trades" in inst, "Instrument should have trade count"
            assert inst["trades"] > 0, "Instrument should have positive trades"
            
            print(f"  - {inst['symbol']}: {inst['trades']} trades")
        
        print(f"✓ Found {len(instruments)} instruments traded")
    
    def test_different_risk_scores_per_strategy(self):
        """
        Verify that different strategies have different risk scores (not all 100)
        """
        accounts = [2210, 2215, 2216, 2217, 20062]
        scores = []
        
        for account in accounts:
            response = requests.get(
                f"{BASE_URL}/api/admin/risk-engine/strategy-analysis/{account}?period_days=30",
                headers=self.headers
            )
            
            if response.status_code == 200:
                data = response.json()
                score = data.get("risk_control_score", {}).get("composite_score", 0)
                scores.append(score)
        
        # Verify scores are not all the same
        unique_scores = set(scores)
        assert len(unique_scores) > 1, f"All accounts have same score: {scores}"
        
        # Verify at least one score is not 100
        assert any(s < 100 for s in scores), "Should have at least one non-100 score"
        
        print(f"✓ Different risk scores across strategies: {scores}")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
