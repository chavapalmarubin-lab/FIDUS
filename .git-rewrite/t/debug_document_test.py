#!/usr/bin/env python3
"""
Debug Document Storage Issue
"""

import requests
import json

BACKEND_URL = "https://fidus-invest.emergent.host/api"
ADMIN_CREDENTIALS = {"username": "admin", "password": "password123", "user_type": "admin"}

def debug_document_storage():
    session = requests.Session()
    
    # Authenticate
    response = session.post(f"{BACKEND_URL}/auth/login", json=ADMIN_CREDENTIALS)
    if response.status_code != 200:
        print(f"❌ Auth failed: {response.status_code}")
        return
    
    token = response.json().get("token")
    session.headers.update({"Authorization": f"Bearer {token}"})
    print(f"✅ Authenticated with token: {token[:30]}...")
    
    # Upload document
    test_content = b"Debug test document content"
    files = {"document": ("debug_test.txt", test_content, "text/plain")}
    data = {
        "category": "client_agreements",
        "uploader_id": "admin_001",
        "uploader_type": "admin"
    }
    
    response = session.post(f"{BACKEND_URL}/documents/upload", files=files, data=data)
    print(f"Upload response: {response.status_code}")
    print(f"Upload data: {response.json()}")
    
    if response.status_code == 200:
        document_id = response.json().get("document_id")
        print(f"Document ID: {document_id}")
        
        # Try to get document status
        response = session.get(f"{BACKEND_URL}/documents/{document_id}/status")
        print(f"Status response: {response.status_code}")
        print(f"Status data: {response.text}")
        
        # Try to check if document exists in storage
        response = session.get(f"{BACKEND_URL}/documents/admin/all")
        print(f"All documents response: {response.status_code}")
        if response.status_code == 200:
            docs = response.json().get("documents", [])
            print(f"Total documents: {len(docs)}")
            for doc in docs:
                if doc.get("document_id") == document_id:
                    print(f"Found our document: {doc}")
                    break
            else:
                print("Our document not found in all documents list")

if __name__ == "__main__":
    debug_document_storage()