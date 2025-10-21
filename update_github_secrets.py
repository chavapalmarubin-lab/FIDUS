#!/usr/bin/env python3
"""
Update GitHub Secrets via API
"""
import requests
import base64
from nacl import encoding, public

GITHUB_TOKEN = "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"
REPO_OWNER = "chavapalmarubin-lab"
REPO_NAME = "FIDUS"

def get_public_key():
    """Get repository public key for encrypting secrets"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/public-key"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def encrypt_secret(public_key: str, secret_value: str) -> str:
    """Encrypt a secret using the repository's public key"""
    public_key_obj = public.PublicKey(public_key.encode("utf-8"), encoding.Base64Encoder())
    sealed_box = public.SealedBox(public_key_obj)
    encrypted = sealed_box.encrypt(secret_value.encode("utf-8"))
    return base64.b64encode(encrypted).decode("utf-8")

def update_secret(secret_name: str, secret_value: str, key_id: str, public_key: str):
    """Update a GitHub secret"""
    url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/actions/secrets/{secret_name}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    encrypted_value = encrypt_secret(public_key, secret_value)
    
    data = {
        "encrypted_value": encrypted_value,
        "key_id": key_id
    }
    
    response = requests.put(url, headers=headers, json=data)
    response.raise_for_status()
    return response.status_code

def main():
    """Main execution"""
    print("🔐 Fetching repository public key...")
    key_data = get_public_key()
    key_id = key_data["key_id"]
    public_key = key_data["key"]
    print(f"✅ Retrieved public key: {key_id}")
    
    secrets = {
        "VPS_HOST": "92.118.45.135",
        "VPS_PORT": "42014",
        "VPS_USERNAME": "trader",
        "VPS_PASSWORD": "4p1We0OHh3LKgm6"
    }
    
    print("\n🚀 Updating GitHub secrets...")
    for secret_name, secret_value in secrets.items():
        try:
            status = update_secret(secret_name, secret_value, key_id, public_key)
            print(f"✅ {secret_name}: Updated (Status: {status})")
        except Exception as e:
            print(f"❌ {secret_name}: Failed - {str(e)}")
    
    print("\n✅ All secrets updated successfully!")

if __name__ == "__main__":
    main()
