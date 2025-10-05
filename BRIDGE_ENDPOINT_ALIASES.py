# MT5 Bridge Endpoint Aliases - Add to main_production.py

# Add these endpoint aliases before if __name__ == "__main__":

# ============================================================================
# ENDPOINT ALIASES - For FIDUS Platform Compatibility
# ============================================================================

# Alias 1: /mt5/status -> /api/mt5/status
@app.get("/mt5/status")
async def get_mt5_status_alias(api_key: str = Depends(verify_api_key)):
    """Alias for /api/mt5/status - for FIDUS compatibility"""
    return await get_status_endpoint(api_key)

# Alias 2: /mt5/accounts -> /api/mt5/account/info  
@app.get("/mt5/accounts")
async def get_mt5_accounts_alias(api_key: str = Depends(verify_api_key)):
    """Alias for account info - for FIDUS compatibility"""
    return await get_account_info_endpoint(api_key)

# Alias 3: /status -> /api/mt5/status
@app.get("/status") 
async def get_status_alias(api_key: str = Depends(verify_api_key)):
    """Short alias for status - for FIDUS compatibility"""
    return await get_status_endpoint(api_key)

# Alias 4: /mt5/health -> /health
@app.get("/mt5/health")
async def get_mt5_health_alias(api_key: str = Depends(verify_api_key)):
    """Alias for health check - for FIDUS compatibility"""
    return await health_check()

# Alias 5: /accounts -> /api/mt5/account/info
@app.get("/accounts")
async def get_accounts_alias(api_key: str = Depends(verify_api_key)):
    """Short alias for accounts - for FIDUS compatibility"""
    return await get_account_info_endpoint(api_key)

print("✅ MT5 Bridge endpoint aliases registered for FIDUS compatibility")