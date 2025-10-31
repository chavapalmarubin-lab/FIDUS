# FIDUS Investment Platform - Technical Documentation

## System Architecture

### Technology Stack
- **Frontend**: React.js with Vite
- **Backend**: Python FastAPI with async/await
- **Database**: MongoDB Atlas
- **Authentication**: JWT tokens with Google OAuth 2.0
- **MT5 Integration**: Custom FastAPI bridge service
- **Deployment**: Kubernetes with Docker containers

### Service Configuration
```
Frontend: http://localhost:3000 (development)
Backend:  http://localhost:8001 (internal)
MongoDB:  Atlas connection via MONGO_URL
Production: https://fidus-invest.emergent.host
```

---

## Database Schema

### Users Collection
```javascript
{
  id: "client_alejandro",           // Unique identifier
  username: "alejandro_mariscal",   // Login username
  name: "Alejandro Mariscal Romero", // Full display name
  email: "alexmar7609@gmail.com",   // Contact email
  type: "client",                   // User type: "client" | "admin"
  status: "active",                 // Account status
  created_at: "2025-10-06T17:11:21.683923+00:00",
  phone: "+1234567890",            // Optional contact
  notes: "Investment client"        // Optional notes
}
```

### Client Readiness Collection
```javascript
{
  client_id: "client_alejandro",
  aml_kyc_completed: true,
  agreement_signed: true,
  investment_ready: true,
  readiness_override: true,         // If override was used
  readiness_override_reason: "TESTING - System validation",
  readiness_override_by: "admin",
  readiness_override_date: "2025-10-06T20:02:52.533083+00:00",
  updated_at: "2025-10-06T20:02:52.533083+00:00",
  updated_by: "admin"
}
```

### Investments Collection
```javascript
{
  id: "inv_cd955aac85f94e29",      // Unique investment ID
  client_id: "client_alejandro",    // Reference to client
  fund_code: "BALANCE",            // Product type
  principal_amount: 100000.00,     // Investment amount
  currency: "USD",
  
  // Investment timeline
  creation_date: "2025-10-06T20:02:52.892Z",
  incubation_start_date: "2025-10-06T20:02:52.892Z", 
  incubation_end_date: "2025-12-06T20:02:52.892Z",   // +2 months
  interest_start_date: "2025-12-06T20:02:52.892Z",   // After incubation
  contract_end_date: "2026-12-06T20:02:52.892Z",     // +14 months
  next_redemption_date: "2026-03-06T20:02:52.892Z",  // Product-specific
  
  // Investment status
  status: "incubation",            // Current lifecycle stage
  current_value: 100000.00,       // Current worth
  total_interest_paid: 0.00,      // Interest paid to date
  next_interest_payment_date: "2025-12-06T20:02:52.892Z",
  
  // Creation metadata  
  created_by: "admin",
  creation_notes: "Complete investment test...",
  updated_at: "2025-10-06T20:02:52.892Z"
}
```

### MT5 Accounts Collection
```javascript
{
  id: "mt5_acc_unique_id",
  investment_id: "inv_cd955aac85f94e29",
  client_id: "client_alejandro",
  mt5_account_number: 886557,
  account_type: "INVESTMENT_ALLOCATION", // or INTEREST_SEPARATION, GAINS_SEPARATION
  broker_name: "MULTIBANK",
  mt5_server: "MULTIBANK-Live",
  allocated_amount: 40000.00,      // For allocation accounts
  allocation_percentage: 40.0,     // Calculated percentage
  allocation_notes: "Primary allocation for conservative strategy",
  investor_password_encrypted: "...", // Encrypted storage
  created_at: "2025-10-06T20:02:52.892Z",
  created_by: "admin",
  status: "allocated"              // available | allocated | deallocated
}
```

---

## API Endpoints Reference

### Authentication Endpoints

#### POST /api/auth/login
**Purpose**: Admin authentication
```javascript
Request:
{
  "username": "admin",
  "password": "password123", 
  "user_type": "admin"
}

Response:
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "admin",
    "name": "Admin User",
    "type": "admin"
  }
}
```

### Client Management Endpoints

#### GET /api/clients/ready-for-investment
**Purpose**: Get clients ready for investment (for dropdown)
```javascript
Headers: Authorization: Bearer {jwt_token}

Response:
{
  "success": true,
  "ready_clients": [
    {
      "client_id": "client_alejandro",
      "name": "Alejandro Mariscal Romero", 
      "email": "alexmar7609@gmail.com",
      "username": "alejandro_mariscal"
    }
  ],
  "total_ready": 1
}
```

#### GET /api/clients/{client_id}/readiness
**Purpose**: Get individual client readiness status
```javascript
Response:
{
  "success": true,
  "client_id": "client_alejandro",
  "readiness": {
    "investment_ready": true,
    "aml_kyc_completed": true,
    "agreement_signed": true,
    "readiness_override": true,
    "readiness_override_reason": "TESTING - System validation"
  }
}
```

#### POST /api/clients/{client_id}/readiness
**Purpose**: Update client readiness (apply override)
```javascript
Request:
{
  "readiness_override": true,
  "readiness_override_reason": "TESTING - Mark client ready for system validation",
  "aml_kyc_completed": true,
  "agreement_signed": true
}

Response:
{
  "success": true,
  "message": "Client readiness updated successfully",
  "investment_ready": true
}
```

### Investment Management Endpoints

#### POST /api/mt5/pool/create-investment-with-mt5
**Purpose**: Create complete investment with MT5 accounts
```javascript
Request:
{
  "client_id": "client_alejandro",
  "fund_code": "BALANCE",
  "principal_amount": 100000.00,
  "mt5_accounts": [
    {
      "mt5_account_number": 886557,
      "investor_password": "investor_pass_1",
      "broker_name": "MULTIBANK",
      "allocated_amount": 40000.00,
      "allocation_notes": "Primary allocation for conservative strategy",
      "mt5_server": "MULTIBANK-Live"
    }
  ],
  "interest_separation_account": {
    "mt5_account_number": 886528,
    "investor_password": "interest_pass",
    "broker_name": "MULTIBANK",
    "account_type": "INTEREST_SEPARATION"
  },
  "gains_separation_account": {
    "mt5_account_number": 886529, 
    "investor_password": "gains_pass",
    "broker_name": "MULTIBANK",
    "account_type": "GAINS_SEPARATION"
  },
  "creation_notes": "Investment creation notes (minimum 20 chars)"
}

Response:
{
  "success": true,
  "investment_id": "inv_cd955aac85f94e29",
  "message": "Investment and MT5 accounts created successfully",
  "mt5_accounts_created": 5,
  "total_allocated": 100000.00
}
```

#### GET /api/investments/{investment_id}
**Purpose**: Get detailed investment information
```javascript
Response:
{
  "id": "inv_cd955aac85f94e29",
  "client_name": "Alejandro Mariscal Romero",
  "fund_code": "BALANCE", 
  "principal_amount": 100000.00,
  "status": "incubation",
  "creation_date": "2025-10-06T20:02:52.892Z",
  "incubation_end_date": "2025-12-06T20:02:52.892Z",
  "contract_end_date": "2026-12-06T20:02:52.892Z",
  "mt5_accounts": [...],
  "interest_separation_account": {...},
  "gains_separation_account": {...}
}
```

### MT5 Management Endpoints

#### GET /api/mt5/pool/test
**Purpose**: Health check for MT5 system
```javascript
Response:
{
  "status": "healthy",
  "message": "MT5 Pool router is working correctly"
}
```

#### GET /api/mt5/pool/statistics  
**Purpose**: Get MT5 account pool statistics
```javascript
Response:
{
  "total_accounts": 15,
  "available_accounts": 10, 
  "allocated_accounts": 5,
  "last_updated": "2025-10-06T20:02:52.892Z"
}
```

---

## Authentication Flow

### JWT Token Management
1. Admin login via `/api/auth/login`
2. JWT token returned and stored in localStorage as 'fidus_token'
3. All subsequent API calls include: `Authorization: Bearer {token}`
4. Token expires after session - re-login required

### Frontend Authentication
```javascript
// Token storage
localStorage.setItem('fidus_token', userData.token);
localStorage.setItem('fidus_user', JSON.stringify(userData));

// API requests (apiAxios.js)
const token = localStorage.getItem('fidus_token');
headers['Authorization'] = `Bearer ${token}`;
```

### Backend Authentication  
```javascript
// JWT validation
@api_router.get("/protected-endpoint")
async def protected_function(request: Request):
    admin_user = get_current_admin_user(request)
    # Admin user validated, proceed with operation
```

---

## MT5 Account Lifecycle

### Account States
```
AVAILABLE    - Account not allocated to any client
ALLOCATED    - Account assigned to specific investment  
DEALLOCATED  - Account removed from investment (future)
```

### Allocation Process
1. Admin creates investment with MT5 account numbers
2. System validates account numbers aren't already allocated
3. System creates MT5 account records linked to investment
4. Accounts marked as ALLOCATED with client association
5. Investor passwords encrypted and stored

### Account Types
```
INVESTMENT_ALLOCATION - Primary accounts for investment funds
INTEREST_SEPARATION   - Dedicated accounts for interest tracking
GAINS_SEPARATION     - Dedicated accounts for gains tracking
```

### Exclusivity Rules
- Each MT5 account can only be allocated to ONE client
- System prevents reuse across different clients/investments
- Accounts remain allocated until investment completion

---

## Investment Product Configuration

### Product Specifications
```javascript
const PRODUCT_CONFIG = {
  CORE: {
    minimum_investment: 10000,
    redemption_frequency: "monthly",
    redemption_schedule: "every_month_after_incubation"
  },
  BALANCE: {
    minimum_investment: 50000,
    redemption_frequency: "quarterly", 
    redemption_schedule: "every_3_months_after_incubation"
  },
  DYNAMIC: {
    minimum_investment: 250000,
    redemption_frequency: "semi_annual",
    redemption_schedule: "every_6_months_after_incubation"  
  },
  UNLIMITED: {
    minimum_investment: 100000,
    redemption_frequency: "at_contract_end",
    redemption_schedule: "14_months_from_creation"
  }
};
```

### Timeline Calculations
```javascript
const currentDate = new Date();

// Standard for all products
creation_date: currentDate,
incubation_start_date: currentDate, 
incubation_end_date: addMonths(currentDate, 2),
interest_start_date: addMonths(currentDate, 2),
contract_end_date: addMonths(currentDate, 14),

// Product-specific redemptions
next_redemption_date: {
  CORE: addMonths(currentDate, 3),     // Month 3
  BALANCE: addMonths(currentDate, 5),  // Month 5 (quarterly after incubation)
  DYNAMIC: addMonths(currentDate, 8),  // Month 8 (semi-annual after incubation)
  UNLIMITED: addMonths(currentDate, 14) // Month 14 (at contract end)
}
```

---

## Error Handling

### Common Error Responses
```javascript
// Authentication Error
{
  "detail": "Could not validate credentials",
  "status_code": 401
}

// Validation Error
{
  "detail": "Investment amount must be at least $50,000 for BALANCE fund",
  "status_code": 400
}

// MT5 Account Conflict
{
  "detail": "MT5 account 886557 is already allocated to another client", 
  "status_code": 409
}

// Client Not Ready
{
  "detail": "Client is not ready for investment. Complete KYC/AML process first",
  "status_code": 403
}
```

### Frontend Error Handling
```javascript
try {
  const response = await apiAxios.post('/mt5/pool/create-investment-with-mt5', data);
  // Success handling
} catch (error) {
  if (error.response?.status === 409) {
    setError('MT5 account already in use by another client');
  } else if (error.response?.status === 403) {
    setError('Client not ready for investment');
  } else {
    setError('Investment creation failed. Please try again.');
  }
}
```

---

## Security Considerations

### Password Security
- MT5 investor passwords encrypted before database storage
- Never store trading passwords - investor passwords only
- System displays security warnings throughout UI
- Passwords transmitted over HTTPS only

### Access Control
- All administrative functions require JWT authentication
- Client data access restricted to authenticated admins
- Investment creation requires explicit admin approval
- Audit logs maintained for all investment operations

### Data Protection
- All API communications over HTTPS
- JWT tokens expire after session
- Database connections use encrypted Atlas URLs
- Client data includes PII - handle according to regulations

---

## Monitoring and Logging

### System Health Checks
```javascript
// Backend health
GET /api/mt5/pool/test

// Database connectivity  
GET /api/clients/ready-for-investment

// Authentication system
POST /api/auth/login
```

### Logging Locations
```
Backend API: /var/log/supervisor/backend.out.log
Frontend:    Browser console (development)
Supervisor:  /var/log/supervisor/
```

### Key Metrics to Monitor
- Investment creation success rate
- Client readiness conversion rate  
- MT5 account allocation accuracy
- Authentication failure rate
- API response times