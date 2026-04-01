# FIDUS Investment Mobile App - Product Requirements Document

## Overview
FIDUS Investment App is a mobile application (iOS & Android) for the FIDUS Investment Platform. It provides retail investors with access to their investment accounts, portfolio information, and investment simulation tools.

## Target Platform
- iOS (iPhone)
- Android
- Built with Expo/React Native for cross-platform compatibility

## Core Features

### 1. Authentication
- Login with email/password
- Demo account: carlos.demo@test.com / Fidus26@
- Session management with token-based auth
- Secure logout

### 2. Dashboard (Home Screen)
- Welcome greeting with user name
- Total balance display
- Earnings indicator (+$X earned)
- Product badges (1.5% monthly, FIDUS CORE)
- Quick action buttons:
  - Add Money
  - Withdraw
  - Product Info
  - Simulator
- Next payment preview with amount and date
- Payment schedule with funded/pending status

### 3. Investment Simulator
- Select additional investment amount ($500, $1,000, $5,000, $10,000, $25,000)
- Shows current vs projected:
  - Monthly returns
  - Annual returns
- 1.5% monthly return calculation

### 4. Info/FAQ Screen
- FIDUS CORE product information
- Questions answered:
  - Return rates (1.5% monthly / 18% annual target)
  - Minimum investment ($100 USD)
  - Withdrawal policy (no contracts, no lock-in)
  - Money security (user's broker account)
  - FIDUS revenue model
  - Risk factors

### 5. Settings
- User profile display (name, email, avatar)
- Language toggle (English/Spanish)
- Actions:
  - Withdraw Funds (links to LUCRUM)
  - Go to LUCRUM
- Logout
- App version

### 6. Add Money Screen
- Instructions for depositing
- Payment methods (Bank Transfer, Crypto, Card)
- Link to LUCRUM platform

### 7. Withdraw Screen
- Step-by-step withdrawal instructions
- Link to LUCRUM platform
- Processing time info

## Bilingual Support
- Full English/Spanish translation
- Language persisted in AsyncStorage
- Instant language switching without restart

## Design Specifications
- Dark theme (#0a0f1a background)
- Primary accent: Cyan (#00b4d8)
- Success: Green (#10b981)
- Warning: Amber (#f59e0b)
- Error: Red (#ef4444)
- Cards: #1a2332 with #2a3444 borders

## Technical Stack
- Frontend: Expo (React Native)
- Backend: FastAPI (Python)
- Database: MongoDB
- Authentication: JWT tokens with Bearer auth
- State Management: React Context + AsyncStorage

## API Integration
The app connects to our custom backend API that provides:
- User authentication
- Profile data
- Payment schedule generation
- Session management

## Data Model
```typescript
interface User {
  id: string;
  name: string;
  email: string;
  balance: number;
  totalEarnings: number;
  monthlyReturn: number;
  paymentSchedule: PaymentScheduleItem[];
}

interface PaymentScheduleItem {
  month: string;
  amount: number;
  status: 'Funded' | 'Pending';
}
```
