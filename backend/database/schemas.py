"""
MongoDB Collection Schemas for FIDUS Investment Management Platform
Defines validation rules, indexes, and constraints for all collections
"""

from datetime import datetime, timezone
from typing import Dict, Any, List
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    CLIENT = "client" 
    COMPLIANCE_OFFICER = "compliance_officer"
    MANAGER = "manager"

class InvestmentStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    PENDING = "pending"
    SUSPENDED = "suspended"

class CRMStage(str, Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"

class DocumentType(str, Enum):
    KYC = "kyc"
    AML = "aml"
    CONTRACT = "contract"
    BANK_STATEMENT = "bank_statement"
    ID_DOCUMENT = "id_document"
    PROOF_OF_ADDRESS = "proof_of_address"

class FidusSchemas:
    """MongoDB collection schemas with validation rules"""
    
    @staticmethod
    def users_schema() -> Dict[str, Any]:
        """User collection schema with comprehensive validation"""
        return {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["username", "email", "user_type", "created_at"],
                    "additionalProperties": True,
                    "properties": {
                        "username": {
                            "bsonType": "string",
                            "minLength": 3,
                            "maxLength": 50,
                            "pattern": "^[a-zA-Z0-9._-]+$",
                            "description": "Username must be 3-50 characters, alphanumeric with . _ - allowed"
                        },
                        "email": {
                            "bsonType": "string",
                            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                            "description": "Valid email address required"
                        },
                        "user_type": {
                            "enum": ["admin", "client", "compliance_officer", "manager"],
                            "description": "User role in the system"
                        },
                        "password_hash": {
                            "bsonType": "string",
                            "description": "Bcrypt hashed password"
                        },
                        "full_name": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100
                        },
                        "phone": {
                            "bsonType": "string",
                            "pattern": "^\+?[1-9]\d{1,14}$",
                            "description": "International phone number format"
                        },
                        "is_active": {
                            "bsonType": "bool",
                            "description": "Account active status"
                        },
                        "is_verified": {
                            "bsonType": "bool",
                            "description": "Email/identity verification status"
                        },
                        "created_at": {
                            "bsonType": "date",
                            "description": "Account creation timestamp"
                        },
                        "updated_at": {
                            "bsonType": "date",
                            "description": "Last update timestamp"
                        },
                        "last_login": {
                            "bsonType": "date",
                            "description": "Last successful login"
                        },
                        "login_attempts": {
                            "bsonType": "int",
                            "minimum": 0,
                            "maximum": 10,
                            "description": "Failed login attempts counter"
                        },
                        "profile_picture": {
                            "bsonType": "string",
                            "description": "URL or path to profile image"
                        },
                        "kyc_status": {
                            "enum": ["pending", "approved", "rejected", "in_review"],
                            "description": "KYC verification status"
                        },
                        "aml_status": {
                            "enum": ["pending", "approved", "rejected", "in_review"],
                            "description": "AML verification status"
                        }
                    }
                }
            },
            "validationLevel": "strict",
            "validationAction": "error"
        }
    
    @staticmethod
    def investments_schema() -> Dict[str, Any]:
        """Investment collection schema with duplication prevention"""
        return {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["investment_id", "client_id", "fund_code", "principal_amount", "created_at"],
                    "additionalProperties": True,
                    "properties": {
                        "investment_id": {
                            "bsonType": "string",
                            "pattern": "^inv_[a-zA-Z0-9]{16}$",
                            "description": "Unique investment identifier"
                        },
                        "client_id": {
                            "bsonType": "string",
                            "description": "Reference to user._id or user.user_id"
                        },
                        "fund_code": {
                            "enum": ["CORE", "BALANCE", "DYNAMIC", "UNLIMITED"],
                            "description": "FIDUS fund type"
                        },
                        "principal_amount": {
                            "bsonType": "decimal",
                            "minimum": 0,
                            "description": "Investment principal in USD"
                        },
                        "current_value": {
                            "bsonType": "decimal",
                            "minimum": 0,
                            "description": "Current investment value"
                        },
                        "currency": {
                            "bsonType": "string",
                            "enum": ["USD", "EUR", "GBP"],
                            "description": "Investment currency"
                        },
                        "status": {
                            "enum": ["active", "closed", "pending", "suspended"],
                            "description": "Investment status"
                        },
                        "investment_date": {
                            "bsonType": "date",
                            "description": "Date when investment was made"
                        },
                        "created_at": {
                            "bsonType": "date",
                            "description": "Record creation timestamp"
                        },
                        "updated_at": {
                            "bsonType": "date",
                            "description": "Last update timestamp"
                        },
                        "mt5_account_id": {
                            "bsonType": "string",
                            "description": "Linked MT5 account identifier"
                        },
                        "performance_fee_rate": {
                            "bsonType": "decimal",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Performance fee percentage (0-1)"
                        },
                        "management_fee_rate": {
                            "bsonType": "decimal",
                            "minimum": 0,
                            "maximum": 1,
                            "description": "Management fee percentage (0-1)"
                        },
                        "notes": {
                            "bsonType": "string",
                            "maxLength": 1000,
                            "description": "Investment notes"
                        }
                    }
                }
            },
            "validationLevel": "strict",
            "validationAction": "error"
        }
    
    @staticmethod
    def crm_prospects_schema() -> Dict[str, Any]:
        """CRM prospects collection schema"""
        return {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["name", "email", "stage", "created_at"],
                    "additionalProperties": True,
                    "properties": {
                        "name": {
                            "bsonType": "string",
                            "minLength": 1,
                            "maxLength": 100,
                            "description": "Prospect full name"
                        },
                        "email": {
                            "bsonType": "string",
                            "pattern": "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
                            "description": "Valid email address"
                        },
                        "phone": {
                            "bsonType": "string",
                            "pattern": "^\+?[1-9]\d{1,14}$",
                            "description": "International phone number"
                        },
                        "stage": {
                            "enum": ["lead", "qualified", "negotiation", "won", "lost"],
                            "description": "Current stage in sales pipeline"
                        },
                        "source": {
                            "bsonType": "string",
                            "enum": ["website", "referral", "social_media", "cold_outreach", "event", "other"],
                            "description": "Lead source"
                        },
                        "assigned_to": {
                            "bsonType": "string",
                            "description": "Admin user ID assigned to this prospect"
                        },
                        "investment_interest": {
                            "bsonType": "decimal",
                            "minimum": 0,
                            "description": "Potential investment amount"
                        },
                        "fund_preference": {
                            "enum": ["CORE", "BALANCE", "DYNAMIC", "UNLIMITED", "undecided"],
                            "description": "Preferred fund type"
                        },
                        "notes": {
                            "bsonType": "string",
                            "maxLength": 2000,
                            "description": "Prospect notes and comments"
                        },
                        "last_contact": {
                            "bsonType": "date",
                            "description": "Last contact date"
                        },
                        "next_follow_up": {
                            "bsonType": "date",
                            "description": "Scheduled follow-up date"
                        },
                        "created_at": {
                            "bsonType": "date",
                            "description": "Record creation timestamp"
                        },
                        "updated_at": {
                            "bsonType": "date",
                            "description": "Last update timestamp"
                        },
                        "converted_to_user_id": {
                            "bsonType": "string",
                            "description": "User ID if prospect converted to client"
                        },
                        "conversion_date": {
                            "bsonType": "date",
                            "description": "Date when prospect became client"
                        }
                    }
                }
            },
            "validationLevel": "strict",
            "validationAction": "error"
        }
    
    @staticmethod
    def mt5_accounts_schema() -> Dict[str, Any]:
        """MT5 accounts collection schema"""
        return {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["account_id", "client_id", "mt5_login", "broker_code", "created_at"],
                    "additionalProperties": True,
                    "properties": {
                        "account_id": {
                            "bsonType": "string",
                            "pattern": "^mt5_[a-zA-Z0-9_]+$",
                            "description": "Unique MT5 account identifier"
                        },
                        "client_id": {
                            "bsonType": "string",
                            "description": "Reference to user ID"
                        },
                        "mt5_login": {
                            "bsonType": "int",
                            "minimum": 100000,
                            "maximum": 99999999,
                            "description": "MT5 account login number"
                        },
                        "broker_code": {
                            "enum": ["multibank", "dootechnology", "vtmarkets"],
                            "description": "Broker identifier"
                        },
                        "broker_name": {
                            "bsonType": "string",
                            "description": "Human-readable broker name"
                        },
                        "mt5_server": {
                            "bsonType": "string",
                            "description": "MT5 server name"
                        },
                        "fund_code": {
                            "enum": ["CORE", "BALANCE", "DYNAMIC", "UNLIMITED"],
                            "description": "Associated fund"
                        },
                        "is_active": {
                            "bsonType": "bool",
                            "description": "Account active status"
                        },
                        "total_allocated": {
                            "bsonType": "decimal",
                            "minimum": 0,
                            "description": "Total amount allocated to this MT5 account"
                        },
                        "current_equity": {
                            "bsonType": "decimal",
                            "minimum": 0,
                            "description": "Current equity value"
                        },
                        "profit_loss": {
                            "bsonType": "decimal",
                            "description": "Profit/Loss amount"
                        },
                        "investment_ids": {
                            "bsonType": "array",
                            "items": {"bsonType": "string"},
                            "description": "List of investment IDs using this account"
                        },
                        "last_sync": {
                            "bsonType": "date",
                            "description": "Last synchronization with MT5"
                        },
                        "created_at": {
                            "bsonType": "date",
                            "description": "Account creation timestamp"
                        },
                        "updated_at": {
                            "bsonType": "date",
                            "description": "Last update timestamp"
                        }
                    }
                }
            },
            "validationLevel": "strict",
            "validationAction": "error"
        }
    
    @staticmethod
    def sessions_schema() -> Dict[str, Any]:
        """Sessions collection schema for JWT management"""
        return {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["user_id", "token_hash", "expires_at", "created_at"],
                    "additionalProperties": True,
                    "properties": {
                        "user_id": {
                            "bsonType": "string",
                            "description": "Reference to user ID"
                        },
                        "token_hash": {
                            "bsonType": "string",
                            "description": "Hashed JWT token for security"
                        },
                        "expires_at": {
                            "bsonType": "date",
                            "description": "Token expiration timestamp"
                        },
                        "created_at": {
                            "bsonType": "date",
                            "description": "Session creation timestamp"
                        },
                        "last_used": {
                            "bsonType": "date",
                            "description": "Last time token was used"
                        },
                        "ip_address": {
                            "bsonType": "string",
                            "description": "Client IP address"
                        },
                        "user_agent": {
                            "bsonType": "string",
                            "description": "Client user agent"
                        },
                        "is_active": {
                            "bsonType": "bool",
                            "description": "Session active status"
                        }
                    }
                }
            },
            "validationLevel": "strict",
            "validationAction": "error"
        }
    
    @staticmethod
    def documents_schema() -> Dict[str, Any]:
        """Documents collection schema"""
        return {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["user_id", "document_type", "file_name", "upload_date"],
                    "additionalProperties": True,
                    "properties": {
                        "user_id": {
                            "bsonType": "string",
                            "description": "Reference to user ID"
                        },
                        "document_type": {
                            "enum": ["kyc", "aml", "contract", "bank_statement", "id_document", "proof_of_address"],
                            "description": "Type of document"
                        },
                        "file_name": {
                            "bsonType": "string",
                            "minLength": 1,
                            "description": "Original file name"
                        },
                        "file_size": {
                            "bsonType": "int",
                            "minimum": 0,
                            "description": "File size in bytes"
                        },
                        "mime_type": {
                            "bsonType": "string",
                            "description": "MIME type of the file"
                        },
                        "storage_path": {
                            "bsonType": "string",
                            "description": "Path to stored file"
                        },
                        "verification_status": {
                            "enum": ["pending", "approved", "rejected"],
                            "description": "Document verification status"
                        },
                        "verified_by": {
                            "bsonType": "string",
                            "description": "Admin user who verified the document"
                        },
                        "verification_date": {
                            "bsonType": "date",
                            "description": "Date when document was verified"
                        },
                        "upload_date": {
                            "bsonType": "date",
                            "description": "Document upload timestamp"
                        },
                        "expiry_date": {
                            "bsonType": "date",
                            "description": "Document expiry date (if applicable)"
                        },
                        "notes": {
                            "bsonType": "string",
                            "maxLength": 500,
                            "description": "Verification notes"
                        }
                    }
                }
            },
            "validationLevel": "strict",
            "validationAction": "error"
        }
    
    @staticmethod
    def admin_google_sessions_schema() -> Dict[str, Any]:
        """Google OAuth sessions for admins"""
        return {
            "validator": {
                "$jsonSchema": {
                    "bsonType": "object",
                    "required": ["admin_id", "access_token", "created_at"],
                    "additionalProperties": True,
                    "properties": {
                        "admin_id": {
                            "bsonType": "string",
                            "description": "Reference to admin user ID"
                        },
                        "access_token": {
                            "bsonType": "string",
                            "description": "Encrypted Google access token"
                        },
                        "refresh_token": {
                            "bsonType": "string",
                            "description": "Encrypted Google refresh token"
                        },
                        "token_expires_at": {
                            "bsonType": "date",
                            "description": "Access token expiration"
                        },
                        "scope": {
                            "bsonType": "string",
                            "description": "Granted OAuth scopes"
                        },
                        "google_email": {
                            "bsonType": "string",
                            "description": "Google account email"
                        },
                        "is_active": {
                            "bsonType": "bool",
                            "description": "Session active status"
                        },
                        "created_at": {
                            "bsonType": "date",
                            "description": "Session creation timestamp"
                        },
                        "last_used": {
                            "bsonType": "date",
                            "description": "Last time tokens were used"
                        }
                    }
                }
            },
            "validationLevel": "strict",
            "validationAction": "error"
        }

class FidusIndexes:
    """Index definitions for all collections"""
    
    @staticmethod
    def users_indexes() -> List[Dict[str, Any]]:
        """User collection indexes"""
        return [
            {"keys": {"email": 1}, "options": {"unique": True, "name": "email_unique"}},
            {"keys": {"username": 1}, "options": {"unique": True, "name": "username_unique"}},
            {"keys": {"user_type": 1}, "options": {"name": "user_type_idx"}},
            {"keys": {"is_active": 1}, "options": {"name": "is_active_idx"}},
            {"keys": {"created_at": -1}, "options": {"name": "created_at_desc"}},
            {"keys": {"last_login": -1}, "options": {"name": "last_login_desc"}},
            {"keys": {"kyc_status": 1, "aml_status": 1}, "options": {"name": "compliance_status_idx"}}
        ]
    
    @staticmethod
    def investments_indexes() -> List[Dict[str, Any]]:
        """Investment collection indexes"""
        return [
            {"keys": {"investment_id": 1}, "options": {"unique": True, "name": "investment_id_unique"}},
            {"keys": {"client_id": 1}, "options": {"name": "client_id_idx"}},
            {"keys": {"fund_code": 1}, "options": {"name": "fund_code_idx"}},
            {"keys": {"status": 1}, "options": {"name": "status_idx"}},
            {"keys": {"created_at": -1}, "options": {"name": "created_at_desc"}},
            {"keys": {"investment_date": -1}, "options": {"name": "investment_date_desc"}},
            {"keys": {"client_id": 1, "fund_code": 1}, "options": {"name": "client_fund_idx"}},
            {"keys": {"mt5_account_id": 1}, "options": {"name": "mt5_account_idx"}},
            # Compound index to prevent duplicate investments
            {"keys": {"client_id": 1, "fund_code": 1, "principal_amount": 1, "investment_date": 1}, 
             "options": {"name": "duplicate_prevention_idx"}}
        ]
    
    @staticmethod
    def crm_prospects_indexes() -> List[Dict[str, Any]]:
        """CRM prospects collection indexes"""
        return [
            {"keys": {"email": 1}, "options": {"unique": True, "name": "email_unique"}},
            {"keys": {"stage": 1}, "options": {"name": "stage_idx"}},
            {"keys": {"assigned_to": 1}, "options": {"name": "assigned_to_idx"}},
            {"keys": {"source": 1}, "options": {"name": "source_idx"}},
            {"keys": {"created_at": -1}, "options": {"name": "created_at_desc"}},
            {"keys": {"last_contact": -1}, "options": {"name": "last_contact_desc"}},
            {"keys": {"next_follow_up": 1}, "options": {"name": "next_follow_up_asc"}}
        ]
    
    @staticmethod
    def mt5_accounts_indexes() -> List[Dict[str, Any]]:
        """MT5 accounts collection indexes"""
        return [
            {"keys": {"account_id": 1}, "options": {"unique": True, "name": "account_id_unique"}},
            {"keys": {"client_id": 1}, "options": {"name": "client_id_idx"}},
            {"keys": {"mt5_login": 1}, "options": {"name": "mt5_login_idx"}},
            {"keys": {"broker_code": 1}, "options": {"name": "broker_code_idx"}},
            {"keys": {"fund_code": 1}, "options": {"name": "fund_code_idx"}},
            {"keys": {"is_active": 1}, "options": {"name": "is_active_idx"}},
            {"keys": {"client_id": 1, "fund_code": 1}, "options": {"name": "client_fund_idx"}},
            {"keys": {"last_sync": -1}, "options": {"name": "last_sync_desc"}}
        ]
    
    @staticmethod
    def sessions_indexes() -> List[Dict[str, Any]]:
        """Sessions collection indexes"""
        return [
            {"keys": {"token_hash": 1}, "options": {"unique": True, "name": "token_hash_unique"}},
            {"keys": {"user_id": 1}, "options": {"name": "user_id_idx"}},
            {"keys": {"expires_at": 1}, "options": {"expireAfterSeconds": 0, "name": "expires_at_ttl"}},
            {"keys": {"is_active": 1}, "options": {"name": "is_active_idx"}},
            {"keys": {"created_at": -1}, "options": {"name": "created_at_desc"}}
        ]
    
    @staticmethod
    def documents_indexes() -> List[Dict[str, Any]]:
        """Documents collection indexes"""
        return [
            {"keys": {"user_id": 1}, "options": {"name": "user_id_idx"}},
            {"keys": {"document_type": 1}, "options": {"name": "document_type_idx"}},
            {"keys": {"verification_status": 1}, "options": {"name": "verification_status_idx"}},
            {"keys": {"upload_date": -1}, "options": {"name": "upload_date_desc"}},
            {"keys": {"user_id": 1, "document_type": 1}, "options": {"name": "user_document_type_idx"}},
            {"keys": {"expiry_date": 1}, "options": {"name": "expiry_date_asc"}}
        ]
    
    @staticmethod
    def admin_google_sessions_indexes() -> List[Dict[str, Any]]:
        """Admin Google sessions collection indexes"""
        return [
            {"keys": {"admin_id": 1}, "options": {"name": "admin_id_idx"}},
            {"keys": {"google_email": 1}, "options": {"name": "google_email_idx"}},
            {"keys": {"is_active": 1}, "options": {"name": "is_active_idx"}},
            {"keys": {"token_expires_at": 1}, "options": {"name": "token_expires_at_idx"}},
            {"keys": {"created_at": -1}, "options": {"name": "created_at_desc"}}
        ]