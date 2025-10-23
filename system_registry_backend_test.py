#!/usr/bin/env python3
"""
System Registry API Endpoints Testing
Tests the newly implemented System Registry API endpoints for Technical Documentation Project (Phase 1)

Test Coverage:
1. GET /api/system/components - All 11 system components organized by category
2. GET /api/system/status - Overall system health status with real-time health checks
3. GET /api/system/components/{component_id} - Individual component details with health status
4. GET /api/system/connections - Component connections/dependencies

Expected Health Statuses:
- Frontend: online (200 OK)
- Backend: online (running)
- MongoDB: online (ping successful)
- MT5 Bridge: May be degraded (depends on last sync time)
- VPS: online (if reachable)
"""

import requests
import json
import time
from datetime import datetime
import sys

# Backend URL from frontend configuration
BACKEND_URL = "https://prospect-portal.preview.emergentagent.com"
BASE_API_URL = f"{BACKEND_URL}/api"

def print_header(title):
    """Print a formatted test section header"""
    print(f"\n{'='*60}")
    print(f"🧪 {title}")
    print(f"{'='*60}")

def print_result(test_name, success, details=""):
    """Print formatted test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if details:
        print(f"   📋 {details}")

def test_system_components():
    """Test GET /api/system/components endpoint"""
    print_header("Testing System Components Endpoint")
    
    try:
        url = f"{BASE_API_URL}/system/components"
        print(f"🔗 Testing: {url}")
        
        response = requests.get(url, timeout=10)
        
        # Check status code
        if response.status_code != 200:
            print_result("Status Code Check", False, f"Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print_result("Status Code Check", True, "200 OK")
        
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print_result("JSON Parse", False, f"Invalid JSON: {e}")
            return False
        
        print_result("JSON Parse", True, "Valid JSON response")
        
        # Check response structure
        required_fields = ['success', 'total_components', 'components', 'timestamp']
        for field in required_fields:
            if field not in data:
                print_result(f"Field '{field}' Present", False, f"Missing required field")
                return False
            print_result(f"Field '{field}' Present", True)
        
        # Check success flag
        if not data.get('success'):
            print_result("Success Flag", False, f"success = {data.get('success')}")
            return False
        
        print_result("Success Flag", True, "success = True")
        
        # Check total components count
        total_components = data.get('total_components', 0)
        if total_components < 11:
            print_result("Component Count", False, f"Expected >= 11, got {total_components}")
            return False
        
        print_result("Component Count", True, f"Found {total_components} components")
        
        # Check components structure
        components = data.get('components', {})
        expected_categories = ['applications', 'databases', 'services', 'integrations', 'infrastructure']
        
        for category in expected_categories:
            if category not in components:
                print_result(f"Category '{category}'", False, "Missing category")
                return False
            
            category_components = components[category]
            if not isinstance(category_components, list):
                print_result(f"Category '{category}' Structure", False, "Not a list")
                return False
            
            print_result(f"Category '{category}'", True, f"{len(category_components)} components")
        
        # Check specific components exist
        all_components = []
        for category_list in components.values():
            all_components.extend(category_list)
        
        component_ids = [comp.get('id') for comp in all_components]
        expected_components = ['frontend', 'backend', 'mongodb', 'mt5_bridge', 'vps']
        
        for comp_id in expected_components:
            if comp_id in component_ids:
                print_result(f"Component '{comp_id}' Found", True)
            else:
                print_result(f"Component '{comp_id}' Found", False, "Missing expected component")
        
        # Check component structure
        sample_component = all_components[0] if all_components else {}
        required_comp_fields = ['id', 'name', 'type', 'category', 'status']
        
        for field in required_comp_fields:
            if field in sample_component:
                print_result(f"Component Field '{field}'", True)
            else:
                print_result(f"Component Field '{field}'", False, "Missing in component structure")
        
        print(f"\n📊 Components Summary:")
        for category, comps in components.items():
            print(f"   {category}: {len(comps)} components")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_result("Network Request", False, f"Request failed: {e}")
        return False
    except Exception as e:
        print_result("Unexpected Error", False, f"Error: {e}")
        return False

def test_system_status():
    """Test GET /api/system/status endpoint"""
    print_header("Testing System Status Endpoint")
    
    try:
        url = f"{BASE_API_URL}/system/status"
        print(f"🔗 Testing: {url}")
        
        response = requests.get(url, timeout=15)  # Longer timeout for health checks
        
        # Check status code
        if response.status_code != 200:
            print_result("Status Code Check", False, f"Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print_result("Status Code Check", True, "200 OK")
        
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print_result("JSON Parse", False, f"Invalid JSON: {e}")
            return False
        
        print_result("JSON Parse", True, "Valid JSON response")
        
        # Check response structure
        required_fields = ['success', 'overall_status', 'health_summary', 'components', 'timestamp']
        for field in required_fields:
            if field not in data:
                print_result(f"Field '{field}' Present", False, f"Missing required field")
                return False
            print_result(f"Field '{field}' Present", True)
        
        # Check success flag
        if not data.get('success'):
            print_result("Success Flag", False, f"success = {data.get('success')}")
            return False
        
        print_result("Success Flag", True, "success = True")
        
        # Check overall status
        overall_status = data.get('overall_status')
        valid_statuses = ['all_systems_operational', 'partial_outage', 'degraded_performance', 'unknown']
        if overall_status not in valid_statuses:
            print_result("Overall Status Valid", False, f"Invalid status: {overall_status}")
        else:
            print_result("Overall Status Valid", True, f"Status: {overall_status}")
        
        # Check health summary
        health_summary = data.get('health_summary', '')
        if 'components online' in health_summary:
            print_result("Health Summary Format", True, health_summary)
        else:
            print_result("Health Summary Format", False, f"Unexpected format: {health_summary}")
        
        # Check components health data
        components = data.get('components', {})
        expected_health_components = ['frontend', 'backend', 'mongodb', 'mt5_bridge', 'vps']
        
        print(f"\n🏥 Health Check Results:")
        for comp_id in expected_health_components:
            if comp_id in components:
                comp_health = components[comp_id]
                status = comp_health.get('status', 'unknown')
                response_time = comp_health.get('response_time_ms', 'N/A')
                error = comp_health.get('error')
                
                print(f"   {comp_id}: {status} ({response_time}ms)")
                if error:
                    print(f"      Error: {error}")
                
                print_result(f"Health Check '{comp_id}'", True, f"Status: {status}")
            else:
                print_result(f"Health Check '{comp_id}'", False, "Missing health data")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_result("Network Request", False, f"Request failed: {e}")
        return False
    except Exception as e:
        print_result("Unexpected Error", False, f"Error: {e}")
        return False

def test_individual_component(component_id):
    """Test GET /api/system/components/{component_id} endpoint"""
    print_header(f"Testing Individual Component: {component_id}")
    
    try:
        url = f"{BASE_API_URL}/system/components/{component_id}"
        print(f"🔗 Testing: {url}")
        
        response = requests.get(url, timeout=10)
        
        # Check status code
        if response.status_code != 200:
            print_result("Status Code Check", False, f"Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print_result("Status Code Check", True, "200 OK")
        
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print_result("JSON Parse", False, f"Invalid JSON: {e}")
            return False
        
        print_result("JSON Parse", True, "Valid JSON response")
        
        # Check response structure
        required_fields = ['success', 'component', 'health', 'timestamp']
        for field in required_fields:
            if field not in data:
                print_result(f"Field '{field}' Present", False, f"Missing required field")
                return False
            print_result(f"Field '{field}' Present", True)
        
        # Check success flag
        if not data.get('success'):
            print_result("Success Flag", False, f"success = {data.get('success')}")
            return False
        
        print_result("Success Flag", True, "success = True")
        
        # Check component data
        component = data.get('component', {})
        if component.get('id') != component_id:
            print_result("Component ID Match", False, f"Expected {component_id}, got {component.get('id')}")
            return False
        
        print_result("Component ID Match", True, f"ID: {component_id}")
        
        # Check component fields
        required_comp_fields = ['id', 'name', 'type', 'category', 'status']
        for field in required_comp_fields:
            if field in component:
                print_result(f"Component Field '{field}'", True, f"{field}: {component.get(field)}")
            else:
                print_result(f"Component Field '{field}'", False, "Missing field")
        
        # Check health data
        health = data.get('health', {})
        if 'status' in health:
            health_status = health.get('status')
            response_time = health.get('response_time_ms', 'N/A')
            print_result("Health Data Present", True, f"Status: {health_status}, Response: {response_time}ms")
        else:
            print_result("Health Data Present", False, "Missing health status")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_result("Network Request", False, f"Request failed: {e}")
        return False
    except Exception as e:
        print_result("Unexpected Error", False, f"Error: {e}")
        return False

def test_nonexistent_component():
    """Test GET /api/system/components/{component_id} with non-existent ID"""
    print_header("Testing Non-existent Component (Error Handling)")
    
    try:
        component_id = "nonexistent_component_12345"
        url = f"{BASE_API_URL}/system/components/{component_id}"
        print(f"🔗 Testing: {url}")
        
        response = requests.get(url, timeout=10)
        
        # Should return 404
        if response.status_code != 404:
            print_result("404 Status Code", False, f"Expected 404, got {response.status_code}")
            return False
        
        print_result("404 Status Code", True, "Correctly returns 404 for non-existent component")
        
        # Check error message
        try:
            data = response.json()
            if 'detail' in data and 'not found' in data['detail'].lower():
                print_result("Error Message", True, f"Message: {data['detail']}")
            else:
                print_result("Error Message", False, f"Unexpected error format: {data}")
        except json.JSONDecodeError:
            print_result("Error Response Format", False, "Non-JSON error response")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_result("Network Request", False, f"Request failed: {e}")
        return False
    except Exception as e:
        print_result("Unexpected Error", False, f"Error: {e}")
        return False

def test_system_connections():
    """Test GET /api/system/connections endpoint"""
    print_header("Testing System Connections Endpoint")
    
    try:
        url = f"{BASE_API_URL}/system/connections"
        print(f"🔗 Testing: {url}")
        
        response = requests.get(url, timeout=10)
        
        # Check status code
        if response.status_code != 200:
            print_result("Status Code Check", False, f"Expected 200, got {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        print_result("Status Code Check", True, "200 OK")
        
        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            print_result("JSON Parse", False, f"Invalid JSON: {e}")
            return False
        
        print_result("JSON Parse", True, "Valid JSON response")
        
        # Check response structure
        required_fields = ['success', 'total_connections', 'connections', 'timestamp']
        for field in required_fields:
            if field not in data:
                print_result(f"Field '{field}' Present", False, f"Missing required field")
                return False
            print_result(f"Field '{field}' Present", True)
        
        # Check success flag
        if not data.get('success'):
            print_result("Success Flag", False, f"success = {data.get('success')}")
            return False
        
        print_result("Success Flag", True, "success = True")
        
        # Check connections data
        connections = data.get('connections', [])
        total_connections = data.get('total_connections', 0)
        
        if len(connections) != total_connections:
            print_result("Connection Count Match", False, f"Count mismatch: {len(connections)} vs {total_connections}")
        else:
            print_result("Connection Count Match", True, f"Found {total_connections} connections")
        
        # Check connection structure
        if connections:
            sample_connection = connections[0]
            required_conn_fields = ['from', 'to', 'type', 'protocol']
            
            for field in required_conn_fields:
                if field in sample_connection:
                    print_result(f"Connection Field '{field}'", True)
                else:
                    print_result(f"Connection Field '{field}'", False, "Missing field")
        
        # Display connections summary
        print(f"\n🔗 Connections Summary:")
        for i, conn in enumerate(connections[:5]):  # Show first 5
            from_comp = conn.get('from', 'unknown')
            to_comp = conn.get('to', 'unknown')
            conn_type = conn.get('type', 'unknown')
            protocol = conn.get('protocol', 'unknown')
            print(f"   {i+1}. {from_comp} → {to_comp} ({conn_type} via {protocol})")
        
        if len(connections) > 5:
            print(f"   ... and {len(connections) - 5} more connections")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print_result("Network Request", False, f"Request failed: {e}")
        return False
    except Exception as e:
        print_result("Unexpected Error", False, f"Error: {e}")
        return False

def main():
    """Run all System Registry API tests"""
    print("🚀 Starting System Registry API Endpoints Testing")
    print(f"📡 Backend URL: {BACKEND_URL}")
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    test_results = []
    
    # Test 1: System Components
    result1 = test_system_components()
    test_results.append(("System Components", result1))
    
    # Test 2: System Status
    result2 = test_system_status()
    test_results.append(("System Status", result2))
    
    # Test 3: Individual Components
    test_components = ['frontend', 'backend', 'mongodb', 'mt5_bridge', 'vps']
    for comp_id in test_components:
        result = test_individual_component(comp_id)
        test_results.append((f"Component '{comp_id}'", result))
    
    # Test 4: Non-existent Component (Error Handling)
    result4 = test_nonexistent_component()
    test_results.append(("Error Handling (404)", result4))
    
    # Test 5: System Connections
    result5 = test_system_connections()
    test_results.append(("System Connections", result5))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    print(f"📊 Results: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    print()
    
    for test_name, result in test_results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    if passed == total:
        print(f"\n🎉 ALL TESTS PASSED! System Registry API endpoints are working correctly.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the issues above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)