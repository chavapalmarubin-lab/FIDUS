#!/usr/bin/env python3
"""
FRONTEND ENDPOINT INVESTIGATION
==============================

This script investigates what endpoints the frontend might be calling
and why there's a discrepancy between backend testing (0 documents) 
and frontend testing (5 documents) for Alejandro.
"""

import requests
import json
import sys
from datetime import datetime

# Configuration
BACKEND_URL = "https://fidus-google-sync.preview.emergentagent.com/api"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def get_admin_token():
    """Get admin authentication token"""
    response = requests.post(f"{BACKEND_URL}/auth/login", json={
        "username": ADMIN_USERNAME,
        "password": ADMIN_PASSWORD,
        "user_type": "admin"
    })
    
    if response.status_code == 200:
        return response.json().get("token")
    return None

def test_all_document_endpoints():
    """Test all possible document-related endpoints"""
    token = get_admin_token()
    if not token:
        print("❌ Failed to get admin token")
        return
    
    headers = {"Authorization": f"Bearer {token}"}
    alejandro_id = "427444c4-ab1f-44bb-a830-98bc29f4e827"
    alejandro_client_id = "client_8f04d706"
    
    print("🔍 TESTING ALL DOCUMENT ENDPOINTS FOR ALEJANDRO")
    print("=" * 60)
    
    # Test all possible endpoints
    endpoints_to_test = [
        f"/fidus/client-drive-folder/{alejandro_id}",
        f"/fidus/client-drive-folder/{alejandro_client_id}",
        f"/google/drive/client-documents/{alejandro_id}",
        f"/google/drive/client-documents/{alejandro_client_id}",
        f"/google/drive/files",
        f"/google/drive/real-files",
        f"/admin/clients/{alejandro_id}/documents",
        f"/admin/clients/{alejandro_client_id}/documents",
        f"/documents/client/{alejandro_id}",
        f"/documents/client/{alejandro_client_id}",
    ]
    
    for endpoint in endpoints_to_test:
        try:
            response = requests.get(f"{BACKEND_URL}{endpoint}", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                
                # Count documents
                doc_count = 0
                if isinstance(data, dict):
                    if 'documents' in data:
                        doc_count = len(data['documents'])
                    elif 'files' in data:
                        doc_count = len(data['files'])
                elif isinstance(data, list):
                    doc_count = len(data)
                
                status = "🚨 PRIVACY BREACH" if doc_count > 0 else "✅ SECURE"
                print(f"{status}: {endpoint} -> {doc_count} documents")
                
                # Show sample documents if any
                if doc_count > 0:
                    documents = data.get('documents', data.get('files', data if isinstance(data, list) else []))
                    if documents:
                        print(f"   Sample: {documents[0].get('name', 'Unknown')}")
                        
            elif response.status_code == 404:
                print(f"⚪ NOT FOUND: {endpoint}")
            else:
                print(f"❌ ERROR {response.status_code}: {endpoint}")
                
        except Exception as e:
            print(f"❌ EXCEPTION: {endpoint} - {str(e)}")
    
    print("\n" + "=" * 60)

def check_frontend_api_calls():
    """Check what API calls the frontend components make"""
    print("\n🔍 FRONTEND API CALL ANALYSIS")
    print("=" * 40)
    
    # Read frontend components to see what endpoints they call
    frontend_files = [
        "/app/frontend/src/components/ClientDetailModal.js",
        "/app/frontend/src/components/ClientGoogleWorkspace.js",
        "/app/frontend/src/components/AdminDashboard.js",
        "/app/frontend/src/components/GoogleWorkspaceIntegration.js"
    ]
    
    for file_path in frontend_files:
        try:
            with open(file_path, 'r') as f:
                content = f.read()
                
            # Look for API calls
            api_calls = []
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'apiAxios.get' in line or 'axios.get' in line or 'fetch(' in line:
                    # Extract the endpoint
                    if '/api/' in line or '`/' in line:
                        api_calls.append((i+1, line.strip()))
            
            if api_calls:
                print(f"\n📁 {file_path.split('/')[-1]}:")
                for line_num, call in api_calls:
                    print(f"   Line {line_num}: {call}")
                    
        except Exception as e:
            print(f"❌ Error reading {file_path}: {str(e)}")

def main():
    """Main investigation"""
    print("🕵️ FRONTEND ENDPOINT INVESTIGATION")
    print("=" * 50)
    print(f"Time: {datetime.now().isoformat()}")
    print(f"Backend URL: {BACKEND_URL}")
    print()
    
    # Test all document endpoints
    test_all_document_endpoints()
    
    # Check frontend API calls
    check_frontend_api_calls()
    
    print("\n🎯 CONCLUSION:")
    print("If backend endpoints show 0 documents but frontend shows 5,")
    print("the issue is likely:")
    print("1. Frontend caching old data")
    print("2. Frontend calling wrong endpoint")
    print("3. Frontend using different client ID")
    print("4. Browser cache not cleared")

if __name__ == "__main__":
    main()