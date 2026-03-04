#!/usr/bin/env python3
import requests
import json

# Configuration
BACKEND_URL = 'https://fidus-risk-deep.preview.emergentagent.com/api'
session = requests.Session()

def main():
    # Authenticate as admin
    response = session.post(f'{BACKEND_URL}/auth/login', json={
        'username': 'admin',
        'password': 'password123',
        'user_type': 'admin'
    })

    if response.status_code == 200:
        token = response.json().get('token')
        session.headers.update({'Authorization': f'Bearer {token}'})
        print('✅ Admin authenticated successfully')
        
        # Test CRM Pipeline functionality
        print('\n🔍 Testing CRM Pipeline Functionality...')
        
        # Get Alejandro's prospect ID
        response = session.get(f'{BACKEND_URL}/crm/prospects')
        if response.status_code == 200:
            prospects_data = response.json()
            prospects = prospects_data.get('prospects', []) if isinstance(prospects_data, dict) else prospects_data
            
            alejandro_prospect_id = None
            for prospect in prospects:
                if 'alejandro' in prospect.get('name', '').lower():
                    alejandro_prospect_id = prospect.get('prospect_id')
                    current_stage = prospect.get('stage')
                    print(f'✅ Found Alejandro prospect: {prospect.get("name")}')
                    print(f'   Current stage: {current_stage}')
                    print(f'   Prospect ID: {alejandro_prospect_id}')
                    break
            
            if alejandro_prospect_id:
                # Test AML/KYC process
                print(f'\n🔍 Testing AML/KYC Process for Alejandro...')
                response = session.get(f'{BACKEND_URL}/crm/prospects/{alejandro_prospect_id}/aml-kyc')
                if response.status_code == 200:
                    print('✅ AML/KYC process accessible')
                else:
                    print(f'❌ AML/KYC process failed: HTTP {response.status_code}')
            
            # Test pipeline statistics
            print(f'\n🔍 Testing Pipeline Statistics...')
            response = session.get(f'{BACKEND_URL}/crm/pipeline-stats')
            if response.status_code == 200:
                stats = response.json()
                print('✅ Pipeline statistics working')
            else:
                print(f'❌ Pipeline statistics failed: HTTP {response.status_code}')
        
        # Test fund portfolio operations
        print(f'\n🔍 Testing Fund Portfolio Operations...')
        response = session.get(f'{BACKEND_URL}/fund-portfolio/overview')
        if response.status_code == 200:
            portfolio = response.json()
            total_aum = portfolio.get('total_aum', 0)
            print(f'✅ Fund portfolio working - Total AUM: ${total_aum:,.2f}')
            if total_aum > 0:
                print('✅ Portfolio shows non-zero values (data integrity confirmed)')
            else:
                print('❌ Portfolio shows zero values (potential data issue)')
        else:
            print(f'❌ Fund portfolio failed: HTTP {response.status_code}')
        
        # Test critical endpoints for 404 errors
        print(f'\n🔍 Testing Critical Endpoints for 404 Errors...')
        critical_endpoints = [
            '/health',
            '/admin/users', 
            '/admin/clients',
            '/crm/prospects',
            '/crm/pipeline-stats',
            '/auth/google/url',
            '/google/connection/test-all',
            '/fund-portfolio/overview'
        ]
        
        error_404_count = 0
        for endpoint in critical_endpoints:
            response = session.get(f'{BACKEND_URL}{endpoint}')
            if response.status_code == 404:
                error_404_count += 1
                print(f'❌ 404 Error: {endpoint}')
            elif response.status_code == 200:
                print(f'✅ OK: {endpoint}')
            else:
                print(f'⚠️  HTTP {response.status_code}: {endpoint}')
        
        if error_404_count == 0:
            print('✅ No 404 errors found on critical endpoints')
        else:
            print(f'❌ Found {error_404_count} critical endpoints returning 404')
        
        print('\n🎯 EMERGENCY RECOVERY VERIFICATION COMPLETE')
    else:
        print('❌ Admin authentication failed')

if __name__ == "__main__":
    main()