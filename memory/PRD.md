# FIDUS Investment Mobile App - Product Requirements Document

## Overview
FIDUS Investment App is a mobile application (iOS & Android) for the FIDUS Investment Platform. It provides retail investors with access to their investment accounts, portfolio information, and investment simulation tools.

## Target Platform
- iOS (iPhone)
- Android
- Built with Expo/React Native for cross-platform compatibility

## Version 2.0 Features

### 1. Authentication
- Login with email/password
- **Biometric Login (Face ID / Touch ID)** - NEW
- Demo account: carlos.demo@test.com / Fidus26@
- Session management with token-based auth
- Secure logout

### 2. Dashboard (Home Screen)
- Welcome greeting with user name
- Total balance display
- Earnings indicator (+$X earned)
- Product badges (1.5% monthly, FIDUS CORE)
- Quick action buttons: Add Money, Withdraw, Product Info, Simulator
- **Portfolio Performance Chart** - NEW
- **Recent Transactions Preview** - NEW
- Next payment preview with amount and date
- Payment schedule with funded/pending status

### 3. Investment Simulator
- Select additional investment amount ($500-$25,000)
- Shows current vs projected monthly/annual returns
- 1.5% monthly return calculation

### 4. Info/FAQ Screen
- FIDUS CORE product information
- 6 FAQs about returns, risks, withdrawals

### 5. Settings - ENHANCED
- User profile display (name, email, avatar)
- **Edit Profile** - NEW
- Language toggle (English/Spanish)
- **Security Section** - NEW
  - Biometric Login toggle
  - Change Password
- **Notification Preferences** - NEW
  - Push Notifications
  - Payment Reminders
  - Deposit Alerts
  - Monthly Reports
- Transaction History link
- Withdraw Funds link
- Go to LUCRUM link
- Logout

### 6. Transaction History - NEW
- List of all transactions (deposits, withdrawals, returns)
- Filter tabs: All, Deposits, Withdrawals, Returns
- Status badges (Completed, Pending)
- Pull-to-refresh

### 7. Profile Management - NEW
- Edit name and phone
- Change password with validation

### 8. Add Money / Withdraw Screens
- Step-by-step instructions
- Payment method options
- Links to LUCRUM platform

## Bilingual Support
- Full English/Spanish translation
- Instant language switching

## Design Specifications
- Dark theme (#0a0f1a background)
- Primary accent: Cyan (#00b4d8)
- Success: Green (#10b981)
- Warning: Amber (#f59e0b)
- Error: Red (#ef4444)

## Technical Stack
- Frontend: Expo (React Native)
- Backend: FastAPI (Python)
- Database: MongoDB
- Authentication: JWT tokens + Biometric
- State Management: React Context + AsyncStorage + SecureStore

## API Endpoints
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
- GET /api/user/profile - Get user profile
- PUT /api/user/profile - Update profile
- POST /api/user/change-password - Change password
- PUT /api/user/biometric - Toggle biometric
- PUT /api/user/notifications - Update notification prefs
- GET /api/transactions - Get transaction history
- GET /api/portfolio/history - Get portfolio chart data
