# MOCK_USERS to MongoDB Migration Plan

## Current Status
- ✅ Login endpoint already uses MongoDB-only authentication (line 1361)
- ❌ 57 references to MOCK_USERS still exist throughout server.py
- ❌ Data persistence issues causing client data loss
- ❌ Dual database system causing synchronization problems

## Migration Strategy

### Phase 1: Data Migration & Verification
1. **Ensure all MOCK_USERS data is in MongoDB**
   - Verify admin user exists in MongoDB
   - Verify all clients (client1-5, alejandro_mariscal) exist in MongoDB  
   - Transfer any missing data from MOCK_USERS to MongoDB

### Phase 2: Endpoint Migration (Systematic Replacement)
**Priority Order (High to Low Impact):**

#### Critical Client Management Endpoints
1. `/admin/clients` - Line 2167 (get_all_clients)
2. `/admin/clients/{client_id}/details` - Line 2189 (get_client_details) 
3. `/client/{client_id}/data` - Line 2095 (get_client_data)
4. `/admin/clients/{client_id}/update` - Line 2273 (update_client_details)

#### User Administration Endpoints  
5. `/admin/users` - Line 4212 (get_admin_users)
6. `/admin/users/create` - Line 4242 (create_admin_user)
7. `/fidus/register-client` - Line 4259 (register_fidus_client)

#### Authentication & Account Management
8. Password reset endpoints - Lines 3677, 3811
9. User creation endpoints - Lines 3565, 4703, 7928, 13708

#### Investment & Financial Endpoints
10. MT5 integration functions - Lines 6400, 6553, 7093, etc.
11. Fund performance functions - Lines 7270, 10569, etc.
12. Redemption management - Line 11275

### Phase 3: Data Structure Removal
1. Remove MOCK_USERS definition (lines 1176-1275)
2. Remove all MOCK_USERS update operations
3. Clean up helper functions that reference MOCK_USERS

### Phase 4: Testing & Verification
1. Test all migrated endpoints
2. Verify data consistency
3. Ensure Google OAuth still works
4. Validate client authentication

## Implementation Notes
- **Data Integrity**: Preserve all existing client data during migration
- **Field Mapping**: Ensure MongoDB documents match MOCK_USERS structure  
- **Error Handling**: Add proper error handling for missing clients
- **Backward Compatibility**: Maintain same API response formats