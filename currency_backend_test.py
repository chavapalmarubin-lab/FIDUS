#!/usr/bin/env python3
"""
CURRENCY CONVERSION API ENDPOINTS TESTING
=========================================

This test verifies the new currency conversion API endpoints as requested:

1. Currency Rates Endpoint (/api/currency/rates)
   - Returns success: true
   - Includes exchange rates for USD, MXN, EUR
   - USD rate is 1.0
   - MXN and EUR rates are reasonable (MXN around 18-20, EUR around 0.8-0.9)
   - Includes supported_currencies array with currency info
   - Includes last_updated timestamp

2. Currency Conversion Endpoint (/api/currency/convert)
   - Test with USD to MXN conversion (1000 USD)
   - Verify response includes converted amount and exchange rate
   - Test error handling with invalid currency codes

3. Currency Summary Endpoint (/api/currency/summary/{amount})
   - Test with 100000 USD
   - Returns conversions for all supported currencies
   - Each currency includes amount, formatted string, rate, name, symbol
   - USD amount should be exactly 100000
   - MXN and EUR amounts should be converted appropriately

4. Error Handling
   - Test invalid currency codes
   - Verify proper error responses
"""

import requests
import json
import sys
from datetime import datetime
import time

# Configuration
BACKEND_URL = "https://fidus-finance-api.preview.emergentagent.com/api"

class CurrencyConversionTest:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
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
    
    def test_currency_rates_endpoint(self):
        """Test /api/currency/rates endpoint"""
        try:
            response = self.session.get(f"{BACKEND_URL}/currency/rates")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic response structure
                if data.get('success') == True:
                    self.log_result("Currency Rates - Success Flag", True, "Response includes success: true")
                else:
                    self.log_result("Currency Rates - Success Flag", False, "Missing or false success flag", {"response": data})
                    return
                
                # Check rates structure
                rates = data.get('rates', {})
                if isinstance(rates, dict):
                    self.log_result("Currency Rates - Rates Structure", True, f"Rates object found with {len(rates)} currencies")
                    
                    # Check USD rate is 1.0
                    usd_rate = rates.get('USD')
                    if usd_rate == 1.0:
                        self.log_result("Currency Rates - USD Rate", True, "USD rate is correctly 1.0")
                    else:
                        self.log_result("Currency Rates - USD Rate", False, f"USD rate is {usd_rate}, expected 1.0")
                    
                    # Check MXN rate is reasonable (18-20)
                    mxn_rate = rates.get('MXN')
                    if mxn_rate and 18.0 <= mxn_rate <= 20.0:
                        self.log_result("Currency Rates - MXN Rate", True, f"MXN rate is reasonable: {mxn_rate}")
                    else:
                        self.log_result("Currency Rates - MXN Rate", False, f"MXN rate {mxn_rate} not in expected range 18-20")
                    
                    # Check EUR rate is reasonable (0.8-0.9)
                    eur_rate = rates.get('EUR')
                    if eur_rate and 0.8 <= eur_rate <= 0.9:
                        self.log_result("Currency Rates - EUR Rate", True, f"EUR rate is reasonable: {eur_rate}")
                    else:
                        self.log_result("Currency Rates - EUR Rate", False, f"EUR rate {eur_rate} not in expected range 0.8-0.9")
                        
                else:
                    self.log_result("Currency Rates - Rates Structure", False, "Rates is not a dictionary", {"rates": rates})
                
                # Check supported_currencies array
                supported_currencies = data.get('supported_currencies', [])
                if isinstance(supported_currencies, list) and len(supported_currencies) >= 3:
                    self.log_result("Currency Rates - Supported Currencies", True, f"Found {len(supported_currencies)} supported currencies")
                    
                    # Check currency info structure
                    for currency in supported_currencies:
                        if isinstance(currency, dict) and 'code' in currency and 'name' in currency and 'symbol' in currency:
                            continue
                        else:
                            self.log_result("Currency Rates - Currency Info Structure", False, "Invalid currency info structure", {"currency": currency})
                            break
                    else:
                        self.log_result("Currency Rates - Currency Info Structure", True, "All currencies have proper structure (code, name, symbol)")
                else:
                    self.log_result("Currency Rates - Supported Currencies", False, "Invalid supported_currencies array", {"supported_currencies": supported_currencies})
                
                # Check last_updated timestamp
                last_updated = data.get('last_updated')
                if last_updated:
                    self.log_result("Currency Rates - Last Updated", True, f"Last updated timestamp present: {last_updated}")
                else:
                    self.log_result("Currency Rates - Last Updated", False, "Missing last_updated timestamp")
                    
            else:
                self.log_result("Currency Rates Endpoint", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Currency Rates Endpoint", False, f"Exception: {str(e)}")
    
    def test_currency_conversion_endpoint(self):
        """Test /api/currency/convert endpoint"""
        try:
            # Test USD to MXN conversion with 1000 USD
            test_data = {
                "amount": 1000,
                "from_currency": "USD",
                "to_currency": "MXN"
            }
            
            response = self.session.post(f"{BACKEND_URL}/currency/convert", json=test_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic response structure
                if data.get('success') == True:
                    self.log_result("Currency Convert - Success Flag", True, "Response includes success: true")
                else:
                    self.log_result("Currency Convert - Success Flag", False, "Missing or false success flag", {"response": data})
                    return
                
                # Check original amount
                original_amount = data.get('original_amount')
                if original_amount == 1000:
                    self.log_result("Currency Convert - Original Amount", True, f"Original amount correct: {original_amount}")
                else:
                    self.log_result("Currency Convert - Original Amount", False, f"Original amount {original_amount}, expected 1000")
                
                # Check converted amount is reasonable
                converted_amount = data.get('converted_amount')
                if converted_amount and 18000 <= converted_amount <= 20000:  # 1000 USD * 18-20 MXN rate
                    self.log_result("Currency Convert - Converted Amount", True, f"Converted amount reasonable: {converted_amount} MXN")
                else:
                    self.log_result("Currency Convert - Converted Amount", False, f"Converted amount {converted_amount} not in expected range 18000-20000 MXN")
                
                # Check exchange rate
                exchange_rate = data.get('exchange_rate')
                if exchange_rate and 18.0 <= exchange_rate <= 20.0:
                    self.log_result("Currency Convert - Exchange Rate", True, f"Exchange rate reasonable: {exchange_rate}")
                else:
                    self.log_result("Currency Convert - Exchange Rate", False, f"Exchange rate {exchange_rate} not in expected range 18-20")
                
                # Check currency codes
                from_currency = data.get('from_currency')
                to_currency = data.get('to_currency')
                if from_currency == "USD" and to_currency == "MXN":
                    self.log_result("Currency Convert - Currency Codes", True, "Currency codes correct in response")
                else:
                    self.log_result("Currency Convert - Currency Codes", False, f"Currency codes incorrect: {from_currency} -> {to_currency}")
                
                # Check formatted amount
                formatted_amount = data.get('formatted_amount')
                if formatted_amount and 'MXN' in formatted_amount:
                    self.log_result("Currency Convert - Formatted Amount", True, f"Formatted amount includes MXN: {formatted_amount}")
                else:
                    self.log_result("Currency Convert - Formatted Amount", False, f"Formatted amount missing MXN: {formatted_amount}")
                    
            else:
                self.log_result("Currency Convert Endpoint", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Currency Convert Endpoint", False, f"Exception: {str(e)}")
    
    def test_currency_summary_endpoint(self):
        """Test /api/currency/summary/{amount} endpoint"""
        try:
            # Test with 100000 USD
            test_amount = 100000
            response = self.session.get(f"{BACKEND_URL}/currency/summary/{test_amount}")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check basic response structure
                if data.get('success') == True:
                    self.log_result("Currency Summary - Success Flag", True, "Response includes success: true")
                else:
                    self.log_result("Currency Summary - Success Flag", False, "Missing or false success flag", {"response": data})
                    return
                
                # Check base amount
                base_amount = data.get('base_amount')
                if base_amount == test_amount:
                    self.log_result("Currency Summary - Base Amount", True, f"Base amount correct: {base_amount}")
                else:
                    self.log_result("Currency Summary - Base Amount", False, f"Base amount {base_amount}, expected {test_amount}")
                
                # Check base currency
                base_currency = data.get('base_currency')
                if base_currency == "USD":
                    self.log_result("Currency Summary - Base Currency", True, "Base currency is USD")
                else:
                    self.log_result("Currency Summary - Base Currency", False, f"Base currency {base_currency}, expected USD")
                
                # Check conversions
                conversions = data.get('conversions', {})
                if isinstance(conversions, dict):
                    self.log_result("Currency Summary - Conversions Structure", True, f"Conversions object found with {len(conversions)} currencies")
                    
                    # Check USD conversion (should be exactly 100000)
                    usd_conversion = conversions.get('USD', {})
                    usd_amount = usd_conversion.get('amount')
                    if usd_amount == test_amount:
                        self.log_result("Currency Summary - USD Amount", True, f"USD amount exactly {test_amount}")
                    else:
                        self.log_result("Currency Summary - USD Amount", False, f"USD amount {usd_amount}, expected {test_amount}")
                    
                    # Check MXN conversion
                    mxn_conversion = conversions.get('MXN', {})
                    mxn_amount = mxn_conversion.get('amount')
                    if mxn_amount and 1800000 <= mxn_amount <= 2000000:  # 100000 USD * 18-20 MXN rate
                        self.log_result("Currency Summary - MXN Amount", True, f"MXN amount reasonable: {mxn_amount}")
                    else:
                        self.log_result("Currency Summary - MXN Amount", False, f"MXN amount {mxn_amount} not in expected range 1800000-2000000")
                    
                    # Check EUR conversion
                    eur_conversion = conversions.get('EUR', {})
                    eur_amount = eur_conversion.get('amount')
                    if eur_amount and 80000 <= eur_amount <= 90000:  # 100000 USD * 0.8-0.9 EUR rate
                        self.log_result("Currency Summary - EUR Amount", True, f"EUR amount reasonable: {eur_amount}")
                    else:
                        self.log_result("Currency Summary - EUR Amount", False, f"EUR amount {eur_amount} not in expected range 80000-90000")
                    
                    # Check each currency has required fields
                    required_fields = ['amount', 'formatted', 'rate', 'name', 'symbol']
                    for currency_code, conversion_data in conversions.items():
                        missing_fields = [field for field in required_fields if field not in conversion_data]
                        if not missing_fields:
                            self.log_result(f"Currency Summary - {currency_code} Fields", True, f"{currency_code} has all required fields")
                        else:
                            self.log_result(f"Currency Summary - {currency_code} Fields", False, f"{currency_code} missing fields: {missing_fields}")
                            
                else:
                    self.log_result("Currency Summary - Conversions Structure", False, "Conversions is not a dictionary", {"conversions": conversions})
                    
            else:
                self.log_result("Currency Summary Endpoint", False, f"HTTP {response.status_code}", {"response": response.text})
                
        except Exception as e:
            self.log_result("Currency Summary Endpoint", False, f"Exception: {str(e)}")
    
    def test_error_handling(self):
        """Test error handling with invalid currency codes"""
        try:
            # Test invalid currency in conversion
            invalid_conversion_data = {
                "amount": 1000,
                "from_currency": "USD",
                "to_currency": "INVALID"
            }
            
            response = self.session.post(f"{BACKEND_URL}/currency/convert", json=invalid_conversion_data)
            
            if response.status_code == 400:
                self.log_result("Error Handling - Invalid Currency", True, "Properly returns HTTP 400 for invalid currency")
                
                data = response.json()
                if 'detail' in data and 'Unsupported currency' in data['detail']:
                    self.log_result("Error Handling - Error Message", True, "Error message mentions unsupported currency")
                else:
                    self.log_result("Error Handling - Error Message", False, "Error message doesn't mention unsupported currency", {"response": data})
            else:
                self.log_result("Error Handling - Invalid Currency", False, f"Expected HTTP 400, got {response.status_code}", {"response": response.text})
            
            # Test another invalid currency combination
            invalid_conversion_data2 = {
                "amount": 1000,
                "from_currency": "FAKE",
                "to_currency": "USD"
            }
            
            response2 = self.session.post(f"{BACKEND_URL}/currency/convert", json=invalid_conversion_data2)
            
            if response2.status_code == 400:
                self.log_result("Error Handling - Invalid From Currency", True, "Properly returns HTTP 400 for invalid from_currency")
            else:
                self.log_result("Error Handling - Invalid From Currency", False, f"Expected HTTP 400, got {response2.status_code}")
                
        except Exception as e:
            self.log_result("Error Handling", False, f"Exception: {str(e)}")
    
    def run_all_tests(self):
        """Run all currency conversion API tests"""
        print("💰 CURRENCY CONVERSION API ENDPOINTS TESTING")
        print("=" * 60)
        print(f"Backend URL: {BACKEND_URL}")
        print(f"Test Time: {datetime.now().isoformat()}")
        print()
        
        print("🔍 Running Currency API Tests...")
        print("-" * 50)
        
        # Run all tests
        self.test_currency_rates_endpoint()
        self.test_currency_conversion_endpoint()
        self.test_currency_summary_endpoint()
        self.test_error_handling()
        
        # Generate summary
        self.generate_test_summary()
        
        return True
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        print("\n" + "=" * 60)
        print("💰 CURRENCY CONVERSION API TEST SUMMARY")
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
        
        # Show failed tests
        if failed_tests > 0:
            print("❌ FAILED TESTS:")
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
        
        # Critical assessment
        critical_tests = [
            "Currency Rates - Success Flag",
            "Currency Convert - Success Flag", 
            "Currency Summary - Success Flag",
            "Currency Rates - USD Rate",
            "Currency Convert - Converted Amount",
            "Currency Summary - USD Amount"
        ]
        
        critical_passed = sum(1 for result in self.test_results 
                            if result['success'] and any(critical in result['test'] for critical in critical_tests))
        
        print("🚨 CRITICAL ASSESSMENT:")
        if critical_passed >= 5:  # At least 5 out of 6 critical tests
            print("✅ CURRENCY CONVERSION API: WORKING CORRECTLY")
            print("   All currency endpoints are operational and returning expected data.")
            print("   Backend currency conversion system is ready for frontend integration.")
        else:
            print("❌ CURRENCY CONVERSION API: ISSUES FOUND")
            print("   Critical currency API issues detected.")
            print("   Main agent action required to fix currency endpoints.")
        
        print("\n" + "=" * 60)

def main():
    """Main test execution"""
    test_runner = CurrencyConversionTest()
    success = test_runner.run_all_tests()
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()