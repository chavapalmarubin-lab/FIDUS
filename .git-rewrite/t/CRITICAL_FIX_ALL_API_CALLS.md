# CRITICAL PRODUCTION FIX: Update All Components to Use JWT-Enabled API Calls

## Components That Need Immediate Fix:
1. ProspectManagement.js - 10+ axios calls
2. MetaQuotesData.js - 6 axios calls  
3. CRMDashboard.js - 5 axios calls
4. UserRegistration.js - 2 axios calls
5. PasswordReset.js - 3 axios calls
6. RedemptionManagement.js - 3 axios calls
7. MT5Management.js - Multiple calls
8. ClientManagement.js - Multiple calls
9. DocumentPortal.js - Multiple calls
10. GmailSettings.js - Multiple calls

## Fix Strategy:
1. Replace `import axios from "axios"` with `import apiAxios from "../utils/apiAxios"`
2. Replace `axios.get/post/put/delete` with `apiAxios.get/post/put/delete`
3. Update API endpoint paths to remove `${API}` or `${backendUrl}/api` prefix
4. Keep only relative paths like `/admin/cashflow/overview`

## Login/Auth Endpoints Exception:
- Keep LoginSelection.js, PasswordReset.js using regular axios since they don't need JWT tokens
- These are public endpoints that run before authentication

## Priority: IMMEDIATE - Production system cannot have database errors