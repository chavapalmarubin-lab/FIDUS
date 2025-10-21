"""
API Registry - Comprehensive API Documentation Data
Phase 4: API Documentation & Testing Interface
"""

from typing import List, Dict, Any

# Complete API Registry with all FIDUS platform endpoints
API_REGISTRY = {
    "categories": [
        {
            "id": "authentication",
            "name": "Authentication",
            "description": "User authentication and JWT token management endpoints",
            "icon": "🔐",
            "color": "#3B82F6",
            "endpoints": [
                {
                    "id": "auth_login",
                    "method": "POST",
                    "path": "/api/auth/login",
                    "summary": "User Login",
                    "description": "Authenticate user with email and password, receive JWT token for subsequent requests",
                    "authentication": "None (public)",
                    "tags": ["auth", "login", "jwt"],
                    "parameters": [],
                    "request_body": {
                        "required": True,
                        "content_type": "application/json",
                        "schema": {
                            "email": {"type": "string", "required": True, "example": "admin@fidus.com"},
                            "password": {"type": "string", "required": True, "example": "password123"},
                            "user_type": {"type": "string", "required": False, "example": "admin", "description": "User type: admin or client"}
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Login successful",
                            "example": {
                                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                "token_type": "bearer",
                                "user": {
                                    "id": "admin_001",
                                    "username": "admin",
                                    "email": "chavapalmarubin@gmail.com",
                                    "role": "admin"
                                }
                            }
                        },
                        "401": {
                            "description": "Invalid credentials",
                            "example": {"error": "Invalid email or password"}
                        }
                    }
                },
                {
                    "id": "auth_profile",
                    "method": "GET",
                    "path": "/api/auth/profile",
                    "summary": "Get User Profile",
                    "description": "Retrieve current authenticated user's profile information",
                    "authentication": "Bearer Token",
                    "tags": ["auth", "profile"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Profile retrieved successfully",
                            "example": {
                                "id": "admin_001",
                                "username": "admin",
                                "email": "chavapalmarubin@gmail.com",
                                "role": "admin",
                                "full_name": "Chava Palma Rubin",
                                "created_at": "2025-09-01T00:00:00Z"
                            }
                        },
                        "401": {
                            "description": "Unauthorized - Invalid or missing token",
                            "example": {"error": "Unauthorized"}
                        }
                    }
                },
                {
                    "id": "auth_refresh",
                    "method": "POST",
                    "path": "/api/auth/refresh",
                    "summary": "Refresh JWT Token",
                    "description": "Refresh expired JWT token using refresh token",
                    "authentication": "Bearer Token",
                    "tags": ["auth", "refresh", "jwt"],
                    "parameters": [],
                    "request_body": {
                        "required": True,
                        "content_type": "application/json",
                        "schema": {
                            "refresh_token": {"type": "string", "required": True, "example": "eyJhbGciOiJIUzI1NiIs..."}
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Token refreshed successfully",
                            "example": {
                                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                                "token_type": "bearer",
                                "expires_in": 3600
                            }
                        }
                    }
                }
            ]
        },
        {
            "id": "clients",
            "name": "Client Management",
            "description": "Client onboarding, KYC/AML, and profile management endpoints",
            "icon": "👥",
            "color": "#10B981",
            "endpoints": [
                {
                    "id": "clients_list",
                    "method": "GET",
                    "path": "/api/clients",
                    "summary": "List All Clients",
                    "description": "Retrieve list of all clients with optional filtering and pagination",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["clients", "list"],
                    "parameters": [
                        {"name": "status", "in": "query", "type": "string", "required": False, "description": "Filter by status: approved, pending, rejected"},
                        {"name": "search", "in": "query", "type": "string", "required": False, "description": "Search by name or email"},
                        {"name": "limit", "in": "query", "type": "integer", "required": False, "default": 50, "description": "Results per page"},
                        {"name": "offset", "in": "query", "type": "integer", "required": False, "default": 0, "description": "Pagination offset"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Clients retrieved successfully",
                            "example": {
                                "total": 45,
                                "limit": 50,
                                "offset": 0,
                                "clients": [
                                    {
                                        "id": "cl_alejandro_001",
                                        "full_name": "Alejandro Mariscal",
                                        "email": "alexmar7609@gmail.com",
                                        "status": "approved",
                                        "aml_kyc_completed": True,
                                        "agreement_signed": True,
                                        "created_at": "2025-10-01T00:00:00Z",
                                        "investments_count": 2,
                                        "total_invested": 118151.41
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "id": "clients_create",
                    "method": "POST",
                    "path": "/api/clients/create",
                    "summary": "Create New Client",
                    "description": "Create new client record with initial onboarding information",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["clients", "create", "onboarding"],
                    "parameters": [],
                    "request_body": {
                        "required": True,
                        "content_type": "application/json",
                        "schema": {
                            "full_name": {"type": "string", "required": True, "example": "Juan Pérez"},
                            "email": {"type": "string", "required": True, "example": "juan.perez@example.com"},
                            "phone": {"type": "string", "required": True, "example": "+52 1 55 1234 5678"},
                            "country": {"type": "string", "required": True, "example": "Mexico"},
                            "date_of_birth": {"type": "date", "required": True, "example": "1985-05-15"},
                            "identification": {
                                "type": "object",
                                "required": True,
                                "properties": {
                                    "type": {"type": "string", "example": "passport"},
                                    "number": {"type": "string", "example": "A1234567"},
                                    "expiry_date": {"type": "date", "example": "2030-05-15"}
                                }
                            }
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Client created successfully",
                            "example": {
                                "success": True,
                                "client_id": "cl_juan_001",
                                "message": "Client created successfully"
                            }
                        }
                    }
                },
                {
                    "id": "clients_get",
                    "method": "GET",
                    "path": "/api/clients/:id",
                    "summary": "Get Client Details",
                    "description": "Retrieve detailed information for specific client including investments and documents",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["clients", "details"],
                    "parameters": [
                        {"name": "id", "in": "path", "type": "string", "required": True, "description": "Client ID"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Client details retrieved successfully",
                            "example": {
                                "id": "cl_alejandro_001",
                                "full_name": "Alejandro Mariscal",
                                "email": "alexmar7609@gmail.com",
                                "phone": "+52 1 55 9876 5432",
                                "status": "approved",
                                "aml_kyc_completed": True,
                                "investments": [
                                    {"id": "inv_001", "product": "BALANCE", "amount": 100000.00},
                                    {"id": "inv_002", "product": "CORE", "amount": 18151.41}
                                ],
                                "total_invested": 118151.41
                            }
                        }
                    }
                },
                {
                    "id": "clients_ready",
                    "method": "GET",
                    "path": "/api/clients/ready-for-investment",
                    "summary": "Get Investment-Ready Clients",
                    "description": "List all clients who have completed KYC/AML and are ready for investment allocation",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["clients", "investment", "ready"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Ready clients retrieved successfully",
                            "example": {
                                "count": 12,
                                "clients": [
                                    {
                                        "id": "cl_alejandro_001",
                                        "full_name": "Alejandro Mariscal",
                                        "email": "alexmar7609@gmail.com",
                                        "aml_kyc_completed": True,
                                        "agreement_signed": True,
                                        "ready": True
                                    }
                                ]
                            }
                        }
                    }
                }
            ]
        },
        {
            "id": "investments",
            "name": "Investment Management",
            "description": "Investment creation, allocation, and portfolio management endpoints",
            "icon": "💰",
            "color": "#8B5CF6",
            "endpoints": [
                {
                    "id": "investments_list",
                    "method": "GET",
                    "path": "/api/investments",
                    "summary": "List All Investments",
                    "description": "Retrieve all investments across all clients with filtering options",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["investments", "list", "portfolio"],
                    "parameters": [
                        {"name": "client_id", "in": "query", "type": "string", "required": False, "description": "Filter by client ID"},
                        {"name": "product", "in": "query", "type": "string", "required": False, "description": "Filter by product: CORE, BALANCE, DYNAMIC, UNLIMITED"},
                        {"name": "status", "in": "query", "type": "string", "required": False, "description": "Filter by status: active, completed, cancelled"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Investments retrieved successfully",
                            "example": {
                                "total": 23,
                                "total_value": 2450000.00,
                                "investments": [
                                    {
                                        "id": "inv_balance_alejandro_001",
                                        "client_id": "cl_alejandro_001",
                                        "client_name": "Alejandro Mariscal",
                                        "product": "BALANCE",
                                        "amount": 100000.00,
                                        "start_date": "2025-10-01",
                                        "incubation_end": "2025-12-01",
                                        "contract_end": "2026-12-01",
                                        "mt5_accounts": [
                                            {"account": 886557, "allocation": 80000.00},
                                            {"account": 886602, "allocation": 10000.00},
                                            {"account": 886066, "allocation": 10000.00}
                                        ],
                                        "status": "active",
                                        "current_value": 102500.00,
                                        "total_return": 2500.00,
                                        "return_percentage": 2.5
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "id": "investments_create",
                    "method": "POST",
                    "path": "/api/investments/create",
                    "summary": "Create New Investment",
                    "description": "Create new investment for approved client with MT5 account allocation",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["investments", "create"],
                    "parameters": [],
                    "request_body": {
                        "required": True,
                        "content_type": "application/json",
                        "schema": {
                            "client_id": {"type": "string", "required": True, "example": "cl_alejandro_001"},
                            "product": {"type": "string", "required": True, "enum": ["CORE", "BALANCE", "DYNAMIC", "UNLIMITED"], "example": "BALANCE"},
                            "amount": {"type": "number", "required": True, "example": 100000.00, "minimum": 50000},
                            "start_date": {"type": "date", "required": True, "example": "2025-10-01"},
                            "mt5_accounts": {
                                "type": "array",
                                "required": True,
                                "items": {
                                    "account_number": {"type": "integer", "example": 886557},
                                    "allocation": {"type": "number", "example": 80000.00}
                                }
                            },
                            "notes": {"type": "string", "required": False, "example": "Initial investment allocation"}
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Investment created successfully",
                            "example": {
                                "success": True,
                                "investment_id": "inv_balance_alejandro_001",
                                "message": "Investment created and MT5 accounts allocated successfully"
                            }
                        },
                        "400": {
                            "description": "Validation error",
                            "example": {
                                "error": "Sum of MT5 allocations (90000.00) does not equal investment amount (100000.00)"
                            }
                        }
                    }
                },
                {
                    "id": "investments_get",
                    "method": "GET",
                    "path": "/api/investments/:id",
                    "summary": "Get Investment Details",
                    "description": "Retrieve detailed information for specific investment including performance and allocations",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["investments", "details"],
                    "parameters": [
                        {"name": "id", "in": "path", "type": "string", "required": True, "description": "Investment ID"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Investment details retrieved successfully"
                        }
                    }
                }
            ]
        },
        {
            "id": "mt5",
            "name": "MT5 Integration",
            "description": "MetaTrader 5 account management and real-time data synchronization",
            "icon": "📊",
            "color": "#F59E0B",
            "endpoints": [
                {
                    "id": "mt5_accounts",
                    "method": "GET",
                    "path": "/api/mt5/accounts",
                    "summary": "List MT5 Accounts",
                    "description": "Retrieve all MT5 accounts with real-time balance and equity data from VPS bridge",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["mt5", "accounts", "trading"],
                    "parameters": [
                        {"name": "client_id", "in": "query", "type": "string", "required": False, "description": "Filter by allocated client"},
                        {"name": "status", "in": "query", "type": "string", "required": False, "description": "Filter by status: active, inactive, allocated"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "MT5 accounts retrieved successfully",
                            "example": {
                                "total": 15,
                                "accounts": [
                                    {
                                        "account_number": 886557,
                                        "broker": "MEXAtlantic",
                                        "balance": 80234.56,
                                        "equity": 80456.78,
                                        "profit": 222.22,
                                        "margin": 5000.00,
                                        "free_margin": 75456.78,
                                        "margin_level": 1609.14,
                                        "allocated_to_client": "cl_alejandro_001",
                                        "allocated_to_investment": "inv_balance_alejandro_001",
                                        "allocation_amount": 80000.00,
                                        "last_sync": "2025-10-12T14:30:00Z",
                                        "connection_status": "connected"
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "id": "mt5_account_get",
                    "method": "GET",
                    "path": "/api/mt5/accounts/:account_number",
                    "summary": "Get MT5 Account Details",
                    "description": "Retrieve detailed information for specific MT5 account including recent trades and positions",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["mt5", "account", "details"],
                    "parameters": [
                        {"name": "account_number", "in": "path", "type": "integer", "required": True, "description": "MT5 account number"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "MT5 account details retrieved successfully"
                        }
                    }
                },
                {
                    "id": "mt5_sync_status",
                    "method": "GET",
                    "path": "/api/mt5/sync-status",
                    "summary": "Get MT5 Sync Status",
                    "description": "Check status of MT5 VPS bridge synchronization service",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["mt5", "sync", "status"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Sync status retrieved successfully",
                            "example": {
                                "vps_ip": "92.118.45.135",
                                "vps_port": 8000,
                                "bridge_status": "running",
                                "last_successful_sync": "2025-10-12T14:30:00Z",
                                "total_accounts_synced": 15,
                                "successful_syncs": 15,
                                "failed_syncs": 0,
                                "next_sync_in": 180,
                                "sync_interval": "120 seconds"
                            }
                        }
                    }
                },
                {
                    "id": "mt5_sync_now",
                    "method": "POST",
                    "path": "/api/mt5/sync-now",
                    "summary": "Trigger MT5 Sync",
                    "description": "Manually trigger immediate synchronization of MT5 account data from VPS bridge",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["mt5", "sync", "manual"],
                    "parameters": [],
                    "request_body": {
                        "required": False,
                        "content_type": "application/json",
                        "schema": {
                            "account_number": {"type": "integer", "required": False, "description": "Sync specific account, or all if omitted"}
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Sync triggered successfully",
                            "example": {
                                "success": True,
                                "message": "MT5 sync triggered successfully",
                                "synced_accounts": 15
                            }
                        }
                    }
                }
            ]
        },
        {
            "id": "fund_performance",
            "name": "Fund Performance",
            "description": "Fund profitability analysis, cash flow management, and financial reporting",
            "icon": "📈",
            "color": "#EF4444",
            "endpoints": [
                {
                    "id": "fund_performance_corrected",
                    "method": "GET",
                    "path": "/api/fund-performance/corrected",
                    "summary": "Get Fund Performance Analysis",
                    "description": "Retrieve complete fund performance with separation account (886528) included in calculations",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["fund", "performance", "profitability"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Fund performance retrieved successfully",
                            "example": {
                                "fund_assets": {
                                    "mt5_trading_pnl": 264.87,
                                    "broker_rebates": 0.00,
                                    "separation_interest": 3405.53,
                                    "total": 3670.40
                                },
                                "fund_liabilities": {
                                    "client_interest_obligations": 32995.00,
                                    "management_fees": 500.00,
                                    "operational_costs": 0.00,
                                    "total": 33495.00
                                },
                                "net_fund_profitability": -29824.60,
                                "profitability_percentage": -89.04,
                                "analysis": {
                                    "status": "loss_making",
                                    "real_time_revenue": 3670.40,
                                    "future_obligations": 33495.00,
                                    "revenue_gap": -29824.60,
                                    "required_additional_revenue": 29824.60,
                                    "recommendation": "Fund needs to generate additional $29,824.60 to meet obligations"
                                },
                                "separation_account": {
                                    "account_number": 886528,
                                    "balance": 3405.53,
                                    "purpose": "Interest payments reserve",
                                    "included_in_assets": True
                                },
                                "last_updated": "2025-10-12T14:30:00Z"
                            }
                        }
                    }
                },
                {
                    "id": "fund_cashflow",
                    "method": "GET",
                    "path": "/api/admin/cashflow/overview",
                    "summary": "Get Cash Flow Overview",
                    "description": "Retrieve fund cash flow management breakdown with separation account analysis",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["fund", "cashflow", "financial"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Cash flow overview retrieved successfully"
                        }
                    }
                },
                {
                    "id": "fund_calendar",
                    "method": "GET",
                    "path": "/api/admin/cashflow/calendar",
                    "summary": "Get Cash Flow Calendar",
                    "description": "Retrieve 12-month cash flow obligations calendar with payment timeline",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["fund", "cashflow", "calendar", "obligations"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Cash flow calendar retrieved successfully",
                            "example": {
                                "current_revenue": 2909.31,
                                "total_future_obligations": 159190.93,
                                "final_balance": -156281.62,
                                "monthly_obligations": [
                                    {
                                        "month": "December 2025",
                                        "days_away": 60,
                                        "total_due": 272.27,
                                        "core_interest": 272.27,
                                        "balance_interest": 0.00,
                                        "principal": 0.00,
                                        "running_balance": 2637.04,
                                        "status": "funded"
                                    }
                                ],
                                "milestones": {
                                    "next_payment": {"date": "2025-12-30", "amount": 272.27},
                                    "first_large_payment": {"date": "2026-02-28", "amount": 7772.27},
                                    "contract_end": {"date": "2026-12-01", "amount": 125923.68}
                                }
                            }
                        }
                    }
                }
            ]
        },
        {
            "id": "redemptions",
            "name": "Redemptions",
            "description": "Client redemption request management and processing",
            "icon": "💸",
            "color": "#EC4899",
            "endpoints": [
                {
                    "id": "redemptions_list",
                    "method": "GET",
                    "path": "/api/redemptions",
                    "summary": "List Redemption Requests",
                    "description": "Retrieve all redemption requests with filtering options",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["redemptions", "list"],
                    "parameters": [
                        {"name": "status", "in": "query", "type": "string", "required": False, "description": "Filter by: pending, approved, completed, rejected"},
                        {"name": "client_id", "in": "query", "type": "string", "required": False, "description": "Filter by client"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Redemptions retrieved successfully"
                        }
                    }
                },
                {
                    "id": "redemptions_create",
                    "method": "POST",
                    "path": "/api/redemptions/request",
                    "summary": "Create Redemption Request",
                    "description": "Create new redemption request for client investment (client or admin can create)",
                    "authentication": "Bearer Token",
                    "tags": ["redemptions", "create"],
                    "parameters": [],
                    "request_body": {
                        "required": True,
                        "content_type": "application/json",
                        "schema": {
                            "investment_id": {"type": "string", "required": True, "example": "inv_balance_alejandro_001"},
                            "amount": {"type": "number", "required": True, "example": 10000.00},
                            "reason": {"type": "string", "required": False, "example": "Partial withdrawal for personal use"}
                        }
                    },
                    "responses": {
                        "201": {
                            "description": "Redemption request created successfully"
                        }
                    }
                },
                {
                    "id": "redemptions_approve",
                    "method": "PUT",
                    "path": "/api/redemptions/:id/approve",
                    "summary": "Approve Redemption",
                    "description": "Approve or reject redemption request",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["redemptions", "approve"],
                    "parameters": [
                        {"name": "id", "in": "path", "type": "string", "required": True, "description": "Redemption ID"}
                    ],
                    "request_body": {
                        "required": True,
                        "content_type": "application/json",
                        "schema": {
                            "approved": {"type": "boolean", "required": True, "example": True},
                            "notes": {"type": "string", "required": False, "example": "Approved for processing"},
                            "payment_date": {"type": "date", "required": False, "example": "2025-10-20"}
                        }
                    },
                    "responses": {
                        "200": {
                            "description": "Redemption status updated successfully"
                        }
                    }
                }
            ]
        },
        {
            "id": "google",
            "name": "Google Workspace",
            "description": "Google OAuth, Gmail, Calendar, and Drive integration endpoints",
            "icon": "🔗",
            "color": "#3B82F6",
            "endpoints": [
                {
                    "id": "google_auth_url",
                    "method": "GET",
                    "path": "/api/auth/google/authorize",
                    "summary": "Get OAuth URL",
                    "description": "Generate Google OAuth authorization URL for connecting Google Workspace",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["google", "oauth", "auth"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "OAuth URL generated successfully",
                            "example": {
                                "success": True,
                                "auth_url": "https://accounts.google.com/o/oauth2/v2/auth?client_id=...",
                                "message": "Please visit the auth_url to grant permissions"
                            }
                        }
                    }
                },
                {
                    "id": "google_gmail",
                    "method": "GET",
                    "path": "/api/google/gmail/real-messages",
                    "summary": "Get Gmail Messages",
                    "description": "Retrieve Gmail messages from authenticated Google account",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["google", "gmail", "email"],
                    "parameters": [
                        {"name": "max_results", "in": "query", "type": "integer", "required": False, "default": 10, "description": "Maximum messages to return"},
                        {"name": "query", "in": "query", "type": "string", "required": False, "description": "Gmail search query"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Gmail messages retrieved successfully",
                            "example": {
                                "success": True,
                                "messages": [
                                    {
                                        "id": "msg_123",
                                        "subject": "Investment Update",
                                        "sender": "client@example.com",
                                        "date": "2025-10-12T10:00:00Z",
                                        "snippet": "Thank you for the investment report..."
                                    }
                                ],
                                "count": 20
                            }
                        },
                        "401": {
                            "description": "Google authentication required",
                            "example": {
                                "success": False,
                                "auth_required": True,
                                "error": "Google authentication required. Please connect your Google account first."
                            }
                        }
                    }
                },
                {
                    "id": "google_calendar",
                    "method": "GET",
                    "path": "/api/admin/google/calendar/events",
                    "summary": "Get Calendar Events",
                    "description": "Retrieve calendar events from authenticated Google account",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["google", "calendar", "events"],
                    "parameters": [
                        {"name": "time_min", "in": "query", "type": "datetime", "required": False, "description": "Start date filter"},
                        {"name": "time_max", "in": "query", "type": "datetime", "required": False, "description": "End date filter"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Calendar events retrieved successfully"
                        }
                    }
                },
                {
                    "id": "google_drive",
                    "method": "GET",
                    "path": "/api/admin/google/drive/files",
                    "summary": "Get Drive Files",
                    "description": "Retrieve files from authenticated Google Drive account",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["google", "drive", "files"],
                    "parameters": [
                        {"name": "folder_id", "in": "query", "type": "string", "required": False, "description": "Specific folder ID"},
                        {"name": "query", "in": "query", "type": "string", "required": False, "description": "Search query"}
                    ],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Drive files retrieved successfully"
                        }
                    }
                },
                {
                    "id": "google_status",
                    "method": "GET",
                    "path": "/api/admin/google/individual-status",
                    "summary": "Get Connection Status",
                    "description": "Check Google Workspace connection status for current admin user",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["google", "status", "connection"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Connection status retrieved successfully",
                            "example": {
                                "success": True,
                                "connected": True,
                                "is_expired": False,
                                "google_info": {
                                    "email": "chavapalmarubin@gmail.com",
                                    "name": "Chava Palma Rubin"
                                },
                                "scopes": [
                                    "https://www.googleapis.com/auth/gmail.readonly",
                                    "https://www.googleapis.com/auth/calendar",
                                    "https://www.googleapis.com/auth/drive"
                                ]
                            }
                        }
                    }
                }
            ]
        },
        {
            "id": "system",
            "name": "System & Health",
            "description": "System health checks, component registry, and platform status monitoring",
            "icon": "⚙️",
            "color": "#6B7280",
            "endpoints": [
                {
                    "id": "system_health",
                    "method": "GET",
                    "path": "/api/health",
                    "summary": "Health Check",
                    "description": "Basic health check endpoint to verify system is running",
                    "authentication": "None (public)",
                    "tags": ["system", "health", "status"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "System healthy",
                            "example": {
                                "status": "healthy",
                                "timestamp": "2025-10-12T14:30:00Z",
                                "version": "1.0.0",
                                "uptime": "45 days 12 hours"
                            }
                        }
                    }
                },
                {
                    "id": "system_components",
                    "method": "GET",
                    "path": "/api/system/components",
                    "summary": "Get System Components",
                    "description": "Retrieve registry of all system components with health status",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["system", "components", "registry"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "Components retrieved successfully",
                            "example": {
                                "total": 11,
                                "components": [
                                    {
                                        "id": "frontend",
                                        "name": "React Frontend",
                                        "type": "application",
                                        "status": "online",
                                        "url": "https://fidus-invest.emergent.host",
                                        "health_check_url": "https://fidus-invest.emergent.host/health"
                                    },
                                    {
                                        "id": "backend",
                                        "name": "FastAPI Backend",
                                        "type": "application",
                                        "status": "online",
                                        "url": "https://fidus-invest.emergent.host/api"
                                    }
                                ]
                            }
                        }
                    }
                },
                {
                    "id": "system_status",
                    "method": "GET",
                    "path": "/api/system/health-summary",
                    "summary": "Get System Status",
                    "description": "Get comprehensive system status including all components and integrations",
                    "authentication": "Bearer Token (Admin)",
                    "tags": ["system", "status", "monitoring"],
                    "parameters": [],
                    "request_body": None,
                    "responses": {
                        "200": {
                            "description": "System status retrieved successfully"
                        }
                    }
                }
            ]
        }
    ],
    "authentication_types": {
        "None (public)": {
            "description": "Publicly accessible endpoint - no authentication required",
            "color": "#10B981"
        },
        "Bearer Token": {
            "description": "Requires valid JWT token in Authorization header",
            "format": "Authorization: Bearer <token>",
            "color": "#3B82F6"
        },
        "Bearer Token (Admin)": {
            "description": "Requires valid JWT token with admin role",
            "format": "Authorization: Bearer <admin_token>",
            "color": "#8B5CF6"
        },
        "API Key": {
            "description": "Requires API key in header",
            "format": "X-API-Key: <api_key>",
            "color": "#F59E0B"
        }
    },
    "status_codes": {
        "200": {"description": "Success - Request completed successfully", "color": "#10B981"},
        "201": {"description": "Created - Resource created successfully", "color": "#10B981"},
        "400": {"description": "Bad Request - Invalid parameters or request body", "color": "#EF4444"},
        "401": {"description": "Unauthorized - Missing or invalid authentication token", "color": "#EF4444"},
        "403": {"description": "Forbidden - Insufficient permissions", "color": "#F59E0B"},
        "404": {"description": "Not Found - Resource does not exist", "color": "#F59E0B"},
        "500": {"description": "Internal Server Error - Something went wrong on the server", "color": "#EF4444"},
        "502": {"description": "Bad Gateway - Backend service unavailable", "color": "#EF4444"},
        "503": {"description": "Service Unavailable - System temporarily down", "color": "#EF4444"}
    }
}


def get_api_registry() -> Dict[str, Any]:
    """Get the complete API registry"""
    return API_REGISTRY


def get_category(category_id: str) -> Dict[str, Any]:
    """Get specific API category by ID"""
    for category in API_REGISTRY["categories"]:
        if category["id"] == category_id:
            return category
    return None


def get_endpoint(endpoint_id: str) -> Dict[str, Any]:
    """Get specific endpoint by ID"""
    for category in API_REGISTRY["categories"]:
        for endpoint in category["endpoints"]:
            if endpoint["id"] == endpoint_id:
                return endpoint
    return None


def search_endpoints(query: str) -> List[Dict[str, Any]]:
    """Search endpoints by name, path, description, or tags"""
    results = []
    query_lower = query.lower()
    
    for category in API_REGISTRY["categories"]:
        for endpoint in category["endpoints"]:
            # Search in multiple fields
            searchable_text = f"{endpoint['path']} {endpoint['summary']} {endpoint['description']} {' '.join(endpoint['tags'])}".lower()
            
            if query_lower in searchable_text:
                results.append({
                    **endpoint,
                    "category": category["name"],
                    "category_id": category["id"]
                })
    
    return results
