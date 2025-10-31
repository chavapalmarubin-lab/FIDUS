# FIDUS Investment Platform - Admin User Guide

## Overview
The FIDUS Investment Platform is a complete investment management system with integrated MT5 trading account allocation. This guide covers all administrative functions for managing clients and investments.

## Table of Contents
1. [System Login](#system-login)
2. [Client Management](#client-management)
3. [Investment Creation](#investment-creation)
4. [MT5 Account Management](#mt5-account-management)
5. [Investment Dashboard](#investment-dashboard)
6. [Troubleshooting](#troubleshooting)

---

## System Login

### Accessing the Platform
- **URL**: `https://fidus-invest.emergent.host`
- **Admin Credentials**: admin / password123
- **Login Type**: Select "Admin Login" (orange button)

### After Login
- Dashboard displays: Investment Committee [JWT-FIXED]
- Navigation tabs: Fund Portfolio, Investments, Clients, MT5 Accounts, etc.
- All administrative functions accessible from main dashboard

---

## Client Management

### Current Client Data
- **Active Client**: Alejandro Mariscal Romero
- **Email**: alexmar7609@gmail.com
- **Status**: Ready for Investment
- **Location**: Clients tab → View client details

### Client Readiness Process

#### Standard Process (Future Implementation)
Clients require 5 documents before becoming investment-ready:
1. Passport
2. Government ID  
3. Proof of Residence
4. AML/KYC Report
5. Signed FIDUS Investment Agreement

#### Override Process (Current Testing Method)
For immediate testing/exceptional circumstances:

1. Navigate to **Clients** tab
2. Click **View** on client row
3. Go to **KYC/AML** tab
4. Check "Override readiness requirements"
5. Enter reason (minimum 10 characters):
   ```
   "TESTING - Mark client ready for investment system testing and validation"
   ```
6. Click **Apply Override**
7. Client status changes to "Ready for Investment"

**⚠️ Important**: Override is for testing only. Production requires proper document upload.

---

## Investment Creation

### Process Overview
Creating an investment with MT5 accounts follows these steps:

1. **Navigate to Investments**
   - Click "Investments" tab
   - Click "Create Investment" button (turquoise, top-right)

2. **Select Client**
   - Dropdown shows only "Ready for Investment" clients
   - Select: "Alejandro Mariscal Romero (alexmar7609@gmail.com)"

3. **Choose Investment Product**
   ```
   FIDUS CORE     - $10,000 minimum  - Monthly redemptions
   FIDUS BALANCE  - $50,000 minimum  - Quarterly redemptions  
   FIDUS DYNAMIC  - $250,000 minimum - Semi-annual redemptions
   FIDUS UNLIMITED- $100,000 minimum - At contract end
   ```

4. **Enter Investment Amount**
   - Must meet product minimum
   - Example: $100,000 for FIDUS BALANCE

### MT5 Account Configuration

#### Investment Allocation Accounts
Add multiple MT5 accounts that sum to total investment:

**Example for $100,000 BALANCE investment:**
```
Account 1: MT5 #886557
- Broker: MULTIBANK
- Allocation: $40,000
- Password: [investor password only]
- Notes: "Primary allocation for conservative strategy"

Account 2: MT5 #886602  
- Broker: MULTIBANK
- Allocation: $35,000
- Password: [investor password only]
- Notes: "Secondary allocation for balanced exposure"

Account 3: MT5 #886066
- Broker: MULTIBANK
- Allocation: $25,000
- Password: [investor password only] 
- Notes: "Tertiary allocation for portfolio diversification"

Total: $100,000 ✓
```

#### Separation Tracking Accounts (Required)

**Interest Separation Account:**
```
MT5 Account: #886528
Broker: MULTIBANK
Password: [investor password only]
Purpose: Track interest payments separately
```

**Gains Separation Account:**
```
MT5 Account: #886529
Broker: MULTIBANK  
Password: [investor password only]
Purpose: Track capital gains separately
```

### 🚨 Critical Security Requirements

**INVESTOR PASSWORDS ONLY**
- ⚠️ NEVER enter MT5 Trading Passwords
- ✅ ONLY use MT5 Investor Passwords (read-only access)
- System displays warnings throughout form
- Investor passwords allow monitoring without trading access

**Allocation Validation**
- Total MT5 allocations MUST equal investment amount
- System validates before submission
- Allocation notes are mandatory (minimum 10 characters)

### Investment Timeline
System automatically calculates:
- **Creation Date**: Today
- **Incubation Period**: 2 months (no interest payments)
- **Interest Start**: After incubation period
- **Contract End**: 14 months from creation
- **Next Redemption**: Based on product schedule

---

## MT5 Account Management

### Viewing MT5 Accounts
1. Navigate to **MT5 Accounts** tab
2. View shows allocated accounts with:
   - Account numbers
   - Associated client
   - Investment product
   - Allocation amount
   - Allocation date

### Account Status Types
```
INVESTMENT_ALLOCATION - Accounts allocated to specific investments
INTEREST_SEPARATION   - Dedicated interest tracking accounts  
GAINS_SEPARATION     - Dedicated gains tracking accounts
```

### Account Exclusivity
- Each MT5 account can only be used for ONE client
- System prevents reuse across different investments
- Accounts remain allocated until investment completion

---

## Investment Dashboard

### Viewing Investment Details
1. Navigate to **Investments** tab
2. Click on investment row or use "View" action
3. Dashboard displays:

**Investment Summary:**
- Client information
- Product type (CORE/BALANCE/DYNAMIC/UNLIMITED)
- Principal amount
- Current status (incubation/active/completed)

**Investment Timeline:**
- Creation date
- Incubation period dates
- Interest payment start date
- Next redemption date  
- Contract end date

**MT5 Account Breakdown:**
- All allocation accounts with amounts and percentages
- Interest separation account details
- Gains separation account details
- Account-specific notes

**Financial Performance:**
- Current value
- Total interest paid to date
- Total return percentage
- Next scheduled payment date

### Investment Status Meanings
```
INCUBATION - 2-month period with no interest payments
ACTIVE     - Interest payments occurring per schedule
COMPLETED  - Contract finished, all payments made
CANCELLED  - Investment terminated early
```

---

## Troubleshooting

### Common Issues

**Client Dropdown Empty**
- **Cause**: Client not marked as "Ready for Investment"
- **Solution**: Use KYC/AML override process (see Client Management section)

**MT5 Account Already Allocated Error**
- **Cause**: Attempting to reuse MT5 account from another client
- **Solution**: Use different MT5 account numbers for each client

**Allocation Amount Mismatch**
- **Cause**: MT5 account allocations don't sum to investment total
- **Solution**: Verify all allocations add up correctly before submission

**Authentication Issues**  
- **Cause**: JWT token expired or invalid
- **Solution**: Logout and login again with admin credentials

### System Status Checks

**Verify Backend Health:**
- Dashboard should show "Investment Committee [JWT-FIXED]"
- Client count should show "1" (Alejandro only)
- All tabs should be accessible

**Test Investment Creation:**
- Client dropdown should show Alejandro
- All form fields should accept input
- Submission should create investment successfully

### Contact Support
For technical issues beyond this guide:
- Check browser console for error messages
- Verify all required fields are completed
- Ensure proper investor passwords are used
- Document exact error messages for support

---

## Appendix: Test Data

**Working Test Investment:**
- Investment ID: inv_cd955aac85f94e29
- Client: Alejandro Mariscal Romero  
- Product: FIDUS BALANCE - $100,000
- Status: Incubation
- MT5 Accounts: 886557, 886602, 886066, 886528, 886529

This investment demonstrates all system features working correctly.