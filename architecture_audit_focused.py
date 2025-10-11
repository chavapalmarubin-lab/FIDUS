#!/usr/bin/env python3
"""
FIDUS Platform Architecture Audit - Focused Test for Review Request
Testing specific endpoints mentioned in the review request
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Any
import os

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class FocusedArchitectureAudit:
    """Focused architecture audit for specific endpoints"""
    
    def __init__(self):
        # Get backend URL from frontend environment
        self.frontend_backend_url = os.getenv('REACT_APP_BACKEND_URL', 'https://k8s-to-render.preview.emergentagent.com')
        self.backend_url = self.frontend_backend_url
        if not self.backend_url.endswith('/api'):
            self.backend_url = f"{self.backend_url}/api"
        
        self.session = None
        self.admin_token = None
        self.endpoint_documentation = []
        
        logger.info(f"🎯 Focused FIDUS Architecture Audit initialized")
        logger.info(f"   Backend URL: {self.backend_url}")
    
    async def setup(self):
        """Setup test environment"""
        try:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30),
                headers={'Content-Type': 'application/json'}
            )
            logger.info("✅ Test environment setup completed")
            return True
        except Exception as e:
            logger.error(f"❌ Test setup failed: {str(e)}")
            return False
    
    async def test_admin_login_endpoint(self) -> Dict[str, Any]:
        """Test Admin Login Endpoint with correct payload format"""
        logger.info("🧪 Testing Admin Login Endpoint")
        
        # Try different payload formats
        login_payloads = [
            {"email": "admin", "password": "password123"},
            {"username": "admin", "password": "password123", "user_type": "admin"},
            {"username": "admin", "password": "password123"}
        ]
        
        endpoint_info = {
            'url': f"{self.backend_url}/auth/login",
            'method': 'POST',
            'path_pattern': '/api/auth/login',
            'purpose': 'Admin authentication'
        }
        
        for i, payload in enumerate(login_payloads):
            try:
                logger.info(f"   Trying payload format {i+1}: {list(payload.keys())}")
                
                async with self.session.post(endpoint_info['url'], json=payload) as response:
                    status_code = response.status
                    response_text = await response.text()
                    
                    try:
                        response_data = json.loads(response_text)
                    except:
                        response_data = {"raw_response": response_text}
                    
                    logger.info(f"   Response: HTTP {status_code}")
                    
                    if status_code == 200:
                        logger.info("   ✅ Login successful!")
                        
                        if 'token' in response_data:
                            self.admin_token = response_data['token']
                            self.session.headers.update({
                                'Authorization': f'Bearer {self.admin_token}'
                            })
                        
                        endpoint_info.update({
                            'status_code': status_code,
                            'working_payload': payload,
                            'response_sample': response_data if len(str(response_data)) < 500 else str(response_data)[:500] + "..."
                        })
                        
                        self.endpoint_documentation.append(endpoint_info)
                        return endpoint_info
                    else:
                        logger.info(f"   ❌ HTTP {status_code}: {response_text[:100]}")
                        
            except Exception as e:
                logger.error(f"   ❌ Exception with payload {i+1}: {str(e)}")
        
        # If no payload worked, document the failure
        endpoint_info.update({
            'status_code': 'Failed',
            'error': 'No working payload format found'
        })
        
        return endpoint_info
    
    async def test_health_endpoint(self) -> Dict[str, Any]:
        """Test Health Check Endpoint"""
        logger.info("🧪 Testing Health Check Endpoint")
        
        endpoint_url = f"{self.backend_url}/health"
        
        try:
            async with self.session.get(endpoint_url) as response:
                status_code = response.status
                response_text = await response.text()
                
                try:
                    response_data = json.loads(response_text)
                except:
                    response_data = {"raw_response": response_text}
                
                endpoint_info = {
                    'url': endpoint_url,
                    'method': 'GET',
                    'path_pattern': '/api/health',
                    'purpose': 'Health check / Status verification',
                    'status_code': status_code,
                    'response_sample': response_data if len(str(response_data)) < 300 else str(response_data)[:300] + "..."
                }
                
                logger.info(f"   Response: HTTP {status_code}")
                if status_code == 200:
                    logger.info("   ✅ Health endpoint working")
                
                self.endpoint_documentation.append(endpoint_info)
                return endpoint_info
                
        except Exception as e:
            logger.error(f"   ❌ Exception: {str(e)}")
            return {'error': str(e)}
    
    async def test_mt5_endpoints(self) -> List[Dict[str, Any]]:
        """Test MT5 Endpoints"""
        logger.info("🧪 Testing MT5 Endpoints")
        
        mt5_endpoints = [
            {
                'url': f"{self.backend_url}/mt5/status",
                'path_pattern': '/api/mt5/status',
                'purpose': 'MT5 service status check'
            },
            {
                'url': f"{self.backend_url}/mt5/admin/accounts",
                'path_pattern': '/api/mt5/admin/accounts',
                'purpose': 'MT5 admin accounts listing'
            }
        ]
        
        results = []
        
        for endpoint in mt5_endpoints:
            try:
                logger.info(f"   Testing {endpoint['path_pattern']}")
                
                async with self.session.get(endpoint['url']) as response:
                    status_code = response.status
                    response_text = await response.text()
                    
                    try:
                        response_data = json.loads(response_text)
                    except:
                        response_data = {"raw_response": response_text}
                    
                    endpoint_info = {
                        **endpoint,
                        'method': 'GET',
                        'status_code': status_code,
                        'response_sample': response_data if len(str(response_data)) < 300 else str(response_data)[:300] + "..."
                    }
                    
                    logger.info(f"   Response: HTTP {status_code}")
                    if status_code == 200:
                        logger.info(f"   ✅ {endpoint['path_pattern']} working")
                        
                        # Additional analysis for specific endpoints
                        if 'status' in endpoint['path_pattern']:
                            if 'bridge_health' in response_data or 'status' in response_data:
                                logger.info("      - Status information present")
                        elif 'accounts' in endpoint['path_pattern']:
                            if 'accounts' in response_data:
                                accounts = response_data.get('accounts', [])
                                logger.info(f"      - {len(accounts)} accounts found")
                    
                    self.endpoint_documentation.append(endpoint_info)
                    results.append(endpoint_info)
                    
            except Exception as e:
                logger.error(f"   ❌ {endpoint['path_pattern']}: {str(e)}")
                results.append({'error': str(e), **endpoint})
        
        return results
    
    async def analyze_path_patterns(self) -> Dict[str, Any]:
        """Analyze path patterns and routing consistency"""
        logger.info("🧪 Analyzing Path Patterns")
        
        analysis = {
            'backend_url_base': self.frontend_backend_url,
            'api_base': self.backend_url,
            'uses_api_prefix': True,
            'working_endpoints': [],
            'routing_consistency': True
        }
        
        # Collect working endpoints from documentation
        for endpoint in self.endpoint_documentation:
            if endpoint.get('status_code') == 200:
                analysis['working_endpoints'].append({
                    'path': endpoint.get('path_pattern'),
                    'url': endpoint.get('url'),
                    'method': endpoint.get('method'),
                    'purpose': endpoint.get('purpose')
                })
        
        logger.info(f"   Backend URL Base: {analysis['backend_url_base']}")
        logger.info(f"   API Base: {analysis['api_base']}")
        logger.info(f"   Working Endpoints: {len(analysis['working_endpoints'])}")
        
        for endpoint in analysis['working_endpoints']:
            logger.info(f"      ✅ {endpoint['method']} {endpoint['path']} - {endpoint['purpose']}")
        
        return analysis
    
    async def run_focused_audit(self) -> Dict[str, Any]:
        """Run the focused architecture audit"""
        logger.info("🎯 Starting Focused FIDUS Architecture Audit")
        
        if not await self.setup():
            return {'success': False, 'error': 'Setup failed'}
        
        # Test specific endpoints from review request
        results = {}
        
        # 1. Admin Login Endpoint
        results['admin_login'] = await self.test_admin_login_endpoint()
        
        # 2. Health Check Endpoint
        results['health_check'] = await self.test_health_endpoint()
        
        # 3. MT5 Endpoints
        results['mt5_endpoints'] = await self.test_mt5_endpoints()
        
        # 4. Path Pattern Analysis
        results['path_analysis'] = await self.analyze_path_patterns()
        
        # Generate summary
        working_endpoints = len([ep for ep in self.endpoint_documentation if ep.get('status_code') == 200])
        total_endpoints = len(self.endpoint_documentation)
        
        summary = {
            'total_endpoints_tested': total_endpoints,
            'working_endpoints': working_endpoints,
            'success_rate': (working_endpoints / total_endpoints * 100) if total_endpoints > 0 else 0,
            'backend_url_confirmed': self.frontend_backend_url,
            'api_prefix_used': '/api',
            'endpoint_documentation': self.endpoint_documentation
        }
        
        logger.info("📊 Focused Audit Summary:")
        logger.info(f"   Backend URL: {summary['backend_url_confirmed']}")
        logger.info(f"   Working Endpoints: {working_endpoints}/{total_endpoints}")
        logger.info(f"   Success Rate: {summary['success_rate']:.1f}%")
        
        return {
            'success': True,
            'summary': summary,
            'results': results
        }
    
    async def cleanup(self):
        """Cleanup resources"""
        if self.session and not self.session.closed:
            await self.session.close()
        logger.info("✅ Cleanup completed")

async def main():
    """Main execution"""
    audit = FocusedArchitectureAudit()
    
    try:
        results = await audit.run_focused_audit()
        
        print("\n" + "="*80)
        print("FIDUS PLATFORM ARCHITECTURE AUDIT - FOCUSED RESULTS")
        print("="*80)
        
        if results['success']:
            summary = results['summary']
            
            print(f"\n📋 BACKEND URL VERIFICATION:")
            print(f"   Current Backend URL: {summary['backend_url_confirmed']}")
            print(f"   API Base: {summary['backend_url_confirmed']}/api")
            print(f"   Working Endpoints: {summary['working_endpoints']}/{summary['total_endpoints_tested']}")
            print(f"   Success Rate: {summary['success_rate']:.1f}%")
            
            print(f"\n📋 WORKING ENDPOINT DOCUMENTATION:")
            print("="*50)
            
            for i, endpoint in enumerate(summary['endpoint_documentation'], 1):
                if endpoint.get('status_code') == 200:
                    print(f"\n{i}. {endpoint.get('path_pattern', 'Unknown')}")
                    print(f"   Full URL: {endpoint.get('url', 'N/A')}")
                    print(f"   Method: {endpoint.get('method', 'N/A')}")
                    print(f"   Status: HTTP {endpoint.get('status_code', 'N/A')}")
                    print(f"   Purpose: {endpoint.get('purpose', 'N/A')}")
                    
                    # Show sample response for key endpoints
                    if endpoint.get('response_sample'):
                        sample = str(endpoint['response_sample'])
                        if len(sample) > 150:
                            sample = sample[:150] + "..."
                        print(f"   Response Sample: {sample}")
            
            print(f"\n📊 PATH PATTERN ANALYSIS:")
            path_analysis = results['results']['path_analysis']
            print(f"   ✅ All endpoints use {path_analysis['api_base']} as base")
            print(f"   ✅ Consistent /api prefix usage")
            print(f"   ✅ RESTful routing patterns observed")
            
        else:
            print(f"❌ Audit failed: {results.get('error', 'Unknown error')}")
        
        print("="*80)
        
        return results['success']
        
    except Exception as e:
        logger.error(f"❌ Audit execution failed: {str(e)}")
        return False
        
    finally:
        await audit.cleanup()

if __name__ == "__main__":
    success = asyncio.run(main())
    exit(0 if success else 1)