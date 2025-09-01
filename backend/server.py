from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
import random
import base64
import io
from PIL import Image
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# User Models
class LoginRequest(BaseModel):
    username: str
    password: str
    user_type: str  # "client" or "admin"

class UserResponse(BaseModel):
    id: str
    username: str
    name: str
    email: str
    type: str
    profile_picture: str

class TransactionCreate(BaseModel):
    description: str
    amount: float
    transaction_type: str  # "credit" or "debit"
    fund_type: str  # "fidus", "core", "dynamic"

class Transaction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    description: str
    amount: float
    transaction_type: str
    fund_type: str
    date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ClientBalance(BaseModel):
    client_id: str
    fidus_funds: float
    core_balance: float
    dynamic_balance: float
    total_balance: float
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class MonthlyStatement(BaseModel):
    month: str
    initial_balance: float
    profit: float
    profit_percentage: float
    final_balance: float

class ClientData(BaseModel):
    balance: ClientBalance
    transactions: List[Transaction]
    monthly_statement: MonthlyStatement

# Registration Models
class RegistrationPersonalInfo(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    dateOfBirth: str
    nationality: Optional[str] = ""
    address: Optional[str] = ""
    city: Optional[str] = ""
    postalCode: Optional[str] = ""
    country: Optional[str] = ""

class RegistrationApplication(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    personalInfo: RegistrationPersonalInfo
    documentType: str
    status: str = "pending"  # pending, processing, approved, rejected
    extractedData: Optional[Dict[str, Any]] = None
    amlKycResults: Optional[Dict[str, Any]] = None
    createdAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updatedAt: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class DocumentProcessingRequest(BaseModel):
    applicationId: str
    documentType: str

class AMLKYCRequest(BaseModel):
    applicationId: str
    personalInfo: RegistrationPersonalInfo
    extractedData: Optional[Dict[str, Any]] = None

class ApplicationFinalizationRequest(BaseModel):
    applicationId: str
    approved: bool

# Mock data for demo
MOCK_USERS = {
    "client1": {
        "id": "client_001",
        "username": "client1",
        "name": "Gerardo Briones",
        "email": "g.b@fidus.com",
        "type": "client",
        "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face"
    },
    "client2": {
        "id": "client_002", 
        "username": "client2",
        "name": "Maria Rodriguez",
        "email": "m.rodriguez@fidus.com",
        "type": "client",
        "profile_picture": "https://images.unsplash.com/photo-1494790108755-2616b812358f?w=150&h=150&fit=crop&crop=face"
    },
    "admin": {
        "id": "admin_001",
        "username": "admin",
        "name": "Investment Committee",
        "email": "ic@fidus.com", 
        "type": "admin",
        "profile_picture": "https://images.unsplash.com/photo-1560250097-0b93528c311a?w=150&h=150&fit=crop&crop=face"
    }
}

def generate_mock_transactions(client_id: str, count: int = 50) -> List[dict]:
    """Generate mock transaction data"""
    transactions = []
    base_date = datetime.now(timezone.utc) - timedelta(days=365)
    
    transaction_types = [
        ("Portfolio Rebalancing", "credit", "core"),
        ("Dividend Payment", "credit", "fidus"),
        ("Management Fee", "debit", "fidus"),
        ("Performance Bonus", "credit", "dynamic"),
        ("Risk Adjustment", "debit", "core"),
        ("Market Growth", "credit", "dynamic"),
        ("Fee Adjustment", "debit", "fidus"),
        ("Profit Distribution", "credit", "core"),
        ("Advisory Fee", "debit", "fidus"),
        ("Capital Gains", "credit", "dynamic")
    ]
    
    for i in range(count):
        desc, trans_type, fund_type = random.choice(transaction_types)
        amount = random.uniform(500, 15000)
        if trans_type == "debit":
            amount = -amount
            
        transaction_date = base_date + timedelta(days=random.randint(0, 365))
        
        transactions.append({
            "id": str(uuid.uuid4()),
            "client_id": client_id,
            "description": desc,
            "amount": round(amount, 2),
            "transaction_type": trans_type,
            "fund_type": fund_type,
            "date": transaction_date
        })
    
    return sorted(transactions, key=lambda x: x["date"], reverse=True)

def calculate_balances(transactions: List[dict]) -> dict:
    """Calculate balances from transactions"""
    balances = {"fidus_funds": 0, "core_balance": 0, "dynamic_balance": 0}
    
    for trans in transactions:
        fund_type = trans["fund_type"]
        amount = trans["amount"]
        
        if fund_type == "fidus":
            balances["fidus_funds"] += amount
        elif fund_type == "core":
            balances["core_balance"] += amount
        elif fund_type == "dynamic":
            balances["dynamic_balance"] += amount
    
    # Add base amounts to make realistic
    balances["fidus_funds"] += 124567
    balances["core_balance"] += 275376.44
    balances["dynamic_balance"] += 150000.00
    
    balances["total_balance"] = sum(balances.values())
    
    return balances

# Authentication endpoints
@api_router.post("/auth/login", response_model=UserResponse)
async def login(login_data: LoginRequest):
    """Simple authentication - in production, use proper password hashing"""
    username = login_data.username
    password = login_data.password
    user_type = login_data.user_type
    
    # Simple demo authentication
    if username in MOCK_USERS and password == "password123":
        user_data = MOCK_USERS[username]
        if user_data["type"] == user_type:
            return UserResponse(**user_data)
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

# Client endpoints
@api_router.get("/client/{client_id}/data", response_model=ClientData)
async def get_client_data(client_id: str):
    """Get complete client data including balance, transactions, and monthly statement"""
    if client_id not in [user["id"] for user in MOCK_USERS.values() if user["type"] == "client"]:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Generate or retrieve transactions
    transactions = generate_mock_transactions(client_id)
    balances = calculate_balances(transactions)
    
    # Create balance object
    client_balance = ClientBalance(
        client_id=client_id,
        **balances
    )
    
    # Generate monthly statement
    monthly_statement = MonthlyStatement(
        month="April 2024",
        initial_balance=320041.96,
        profit=51.19,
        profit_percentage=51.19,
        final_balance=332681.44
    )
    
    return ClientData(
        balance=client_balance,
        transactions=[Transaction(**trans) for trans in transactions],
        monthly_statement=monthly_statement
    )

@api_router.get("/client/{client_id}/transactions")
async def get_client_transactions(
    client_id: str, 
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    fund_type: Optional[str] = None
):
    """Get filtered client transactions"""
    transactions = generate_mock_transactions(client_id)
    
    # Apply filters
    if start_date:
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        transactions = [t for t in transactions if t["date"] >= start]
    
    if end_date:
        end = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        transactions = [t for t in transactions if t["date"] <= end]
    
    if fund_type:
        transactions = [t for t in transactions if t["fund_type"] == fund_type]
    
    return {"transactions": transactions}

# Admin endpoints
@api_router.get("/admin/clients")
async def get_all_clients():
    """Get all client summaries for admin"""
    clients = []
    for user in MOCK_USERS.values():
        if user["type"] == "client":
            transactions = generate_mock_transactions(user["id"], 20)
            balances = calculate_balances(transactions)
            clients.append({
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "total_balance": balances["total_balance"],
                "last_activity": transactions[0]["date"] if transactions else datetime.now(timezone.utc),
                "status": user.get("status", "active"),
                "created_at": user.get("createdAt", datetime.now(timezone.utc).isoformat())
            })
    
    return {"clients": clients}

# Mock OCR processing function
def process_document_ocr(image_data: bytes, document_type: str) -> Dict[str, Any]:
    """Mock OCR processing - in production, this would use actual OCR services"""
    # Simulate OCR processing delay
    import time
    time.sleep(1)
    
    # Mock extracted data based on document type
    if document_type == "passport":
        return {
            "document_number": f"P{random.randint(100000000, 999999999)}",
            "full_name": "John Sample Doe",
            "date_of_birth": "1990-05-15",
            "nationality": "US",
            "expiry_date": "2030-05-15",
            "issuing_country": "USA",
            "document_type": "Passport"
        }
    elif document_type == "drivers_license":
        return {
            "license_number": f"DL{random.randint(10000000, 99999999)}",
            "full_name": "John Sample Doe", 
            "date_of_birth": "1990-05-15",
            "address": "123 Main St, Anytown, ST 12345",
            "expiry_date": "2028-05-15",
            "state": "CA",
            "document_type": "Driver's License"
        }
    else:
        return {
            "id_number": f"ID{random.randint(100000000, 999999999)}",
            "full_name": "John Sample Doe",
            "date_of_birth": "1990-05-15", 
            "address": "123 Main St, Anytown, ST 12345",
            "document_type": "National ID"
        }

# Mock AML/KYC verification function
def perform_aml_kyc_check(personal_info: RegistrationPersonalInfo, extracted_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Mock AML/KYC verification - in production, this would use actual compliance services"""
    # Simulate AML/KYC processing delay
    import time
    time.sleep(2)
    
    # Generate mock results
    risk_score = random.randint(1, 25)  # Low risk score for demo
    
    return {
        "status": "approved" if risk_score < 30 else "review_required",
        "riskScore": risk_score,
        "sanctionsCheck": "clear",
        "identityVerification": "verified",
        "pepCheck": "clear",
        "adverseMediaCheck": "clear",
        "documentAuthenticity": "verified",
        "biometricMatch": "confirmed",
        "processedAt": datetime.now(timezone.utc).isoformat(),
        "confidence": random.randint(85, 99)
    }

# Mock email sending function
def send_credentials_email(email: str, username: str, password: str) -> bool:
    """Mock email sending - in production, this would use actual email service"""
    print(f"MOCK EMAIL SENT TO: {email}")
    print(f"USERNAME: {username}")
    print(f"PASSWORD: {password}")
    print("="*50)
    return True

# Registration endpoints
@api_router.post("/registration/create-application")
async def create_registration_application(request: dict):
    """Create new registration application"""
    try:
        personal_info = RegistrationPersonalInfo(**request["personalInfo"])
        document_type = request["documentType"]
        
        application = RegistrationApplication(
            personalInfo=personal_info,
            documentType=document_type,
            status="created"
        )
        
        # Store in database (mock storage for demo)
        application_dict = application.dict()
        application_dict["createdAt"] = application_dict["createdAt"].isoformat()
        application_dict["updatedAt"] = application_dict["updatedAt"].isoformat()
        
        # In production, save to database
        # await db.registration_applications.insert_one(application_dict)
        
        return {"applicationId": application.id, "status": "created"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create application: {str(e)}")

@api_router.post("/registration/process-document")
async def process_document(
    document: UploadFile = File(...),
    documentType: str = Form(...),
    applicationId: str = Form(...)
):
    """Process uploaded document with OCR"""
    try:
        # Validate file
        if not document.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # Read and process image
        image_data = await document.read()
        
        # Perform OCR processing (mock)
        extracted_data = process_document_ocr(image_data, documentType)
        
        # In production, update application in database
        # await db.registration_applications.update_one(
        #     {"id": applicationId},
        #     {"$set": {"extractedData": extracted_data, "status": "document_processed", "updatedAt": datetime.now(timezone.utc)}}
        # )
        
        return {
            "success": True,
            "extractedData": extracted_data,
            "message": "Document processed successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@api_router.post("/registration/aml-kyc-check")
async def perform_aml_kyc_verification(request: AMLKYCRequest):
    """Perform AML/KYC verification"""
    try:
        # Perform AML/KYC checks (mock)
        aml_kyc_results = perform_aml_kyc_check(request.personalInfo, request.extractedData)
        
        # In production, update application in database
        # await db.registration_applications.update_one(
        #     {"id": request.applicationId},
        #     {"$set": {"amlKycResults": aml_kyc_results, "status": "kyc_complete", "updatedAt": datetime.now(timezone.utc)}}
        # )
        
        return aml_kyc_results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AML/KYC verification failed: {str(e)}")

@api_router.post("/registration/finalize")
async def finalize_application(request: ApplicationFinalizationRequest):
    """Finalize registration application"""
    try:
        if not request.approved:
            raise HTTPException(status_code=400, detail="Application not approved")
        
        # Generate credentials
        username = f"client{random.randint(1000, 9999)}"
        password = f"temp{random.randint(100000, 999999)}"
        
        # Create user account
        new_user = {
            "id": f"client_{str(uuid.uuid4())[:8]}",
            "username": username,
            "name": "John Sample Doe",  # Would use extracted name in production
            "email": "demo@fidus.com",  # Would use actual email in production
            "type": "client",
            "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            "status": "active",
            "createdAt": datetime.now(timezone.utc).isoformat()
        }
        
        # In production, save user to database
        # await db.users.insert_one(new_user)
        
        # Send credentials email (mock)
        send_credentials_email("demo@fidus.com", username, password)
        
        # Update MOCK_USERS for demo purposes
        MOCK_USERS[username] = new_user
        
        return {
            "success": True,
            "message": "Registration completed successfully",
            "user": new_user,
            "credentials": {
                "username": username,
                "password": password
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Application finalization failed: {str(e)}")

# Admin endpoint to get pending applications
@api_router.get("/admin/pending-applications")
async def get_pending_applications():
    """Get all pending registration applications for admin review"""
    # In production, fetch from database
    # applications = await db.registration_applications.find({"status": {"$in": ["pending", "review_required"]}}).to_list(100)
    
    # Mock data for demo
    mock_applications = [
        {
            "id": str(uuid.uuid4()),
            "personalInfo": {
                "firstName": "Jane",
                "lastName": "Smith", 
                "email": "jane.smith@email.com",
                "phone": "+1-555-0123"
            },
            "documentType": "passport",
            "status": "pending",
            "createdAt": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        }
    ]
    
    return {"applications": mock_applications}

# Excel Client Management Functions
def generate_clients_excel_data():
    """Generate comprehensive client data for Excel export"""
    clients_data = []
    
    # Add existing clients from MOCK_USERS
    for user in MOCK_USERS.values():
        if user["type"] == "client":
            transactions = generate_mock_transactions(user["id"], 50)
            balances = calculate_balances(transactions)
            
            # Calculate additional metrics
            total_transactions = len(transactions)
            avg_transaction_amount = sum(t["amount"] for t in transactions) / total_transactions if total_transactions > 0 else 0
            last_transaction_date = transactions[0]["date"] if transactions else datetime.now(timezone.utc)
            
            client_data = {
                "Client_ID": user["id"],
                "Username": user["username"],
                "Full_Name": user["name"],
                "Email": user["email"],
                "Status": user.get("status", "active"),
                "Registration_Date": user.get("createdAt", datetime.now(timezone.utc).isoformat())[:10],
                "Total_Balance": round(balances["total_balance"], 2),
                "FIDUS_Funds": round(balances["fidus_funds"], 2),
                "Core_Balance": round(balances["core_balance"], 2),
                "Dynamic_Balance": round(balances["dynamic_balance"], 2),
                "Total_Transactions": total_transactions,
                "Avg_Transaction_Amount": round(avg_transaction_amount, 2),
                "Last_Activity": last_transaction_date.isoformat()[:10] if hasattr(last_transaction_date, 'isoformat') else str(last_transaction_date)[:10],
                "Risk_Level": random.choice(["Low", "Medium", "Low", "Low"]),  # Mostly low risk
                "KYC_Status": "Verified",
                "AML_Status": "Clear",
                "Account_Type": "Individual",
                "Phone": "+1-555-" + str(random.randint(1000000, 9999999)),
                "Address": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Cedar', 'Maple'])} {random.choice(['St', 'Ave', 'Blvd', 'Dr'])}",
                "City": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia"]),
                "State": random.choice(["NY", "CA", "IL", "TX", "AZ", "PA"]),
                "Zip_Code": str(random.randint(10000, 99999)),
                "Country": "United States",
                "Date_of_Birth": f"{random.randint(1970, 2000)}-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}",
                "Nationality": "US",
                "Occupation": random.choice(["Engineer", "Doctor", "Lawyer", "Teacher", "Manager", "Consultant"]),
                "Annual_Income": random.randint(75000, 500000),
                "Net_Worth": random.randint(200000, 2000000),
                "Investment_Experience": random.choice(["Beginner", "Intermediate", "Advanced"]),
                "Risk_Tolerance": random.choice(["Conservative", "Moderate", "Aggressive"]),
                "Investment_Goals": random.choice(["Retirement", "Wealth Building", "Income Generation", "Capital Preservation"])
            }
            clients_data.append(client_data)
    
    return clients_data

def parse_clients_excel_data(excel_data):
    """Parse uploaded Excel data and validate client information"""
    clients = []
    required_fields = ["Full_Name", "Email", "Username"]
    
    for row in excel_data:
        if not row or all(not str(v).strip() for v in row.values()):
            continue  # Skip empty rows
            
        # Check required fields
        missing_fields = [field for field in required_fields if not row.get(field)]
        if missing_fields:
            continue  # Skip invalid rows
            
        # Create standardized client data
        client = {
            "id": row.get("Client_ID", f"client_{str(uuid.uuid4())[:8]}"),
            "username": row.get("Username", "").strip(),
            "name": row.get("Full_Name", "").strip(),
            "email": row.get("Email", "").strip().lower(),
            "type": "client",
            "status": row.get("Status", "active").lower(),
            "createdAt": row.get("Registration_Date", datetime.now(timezone.utc).isoformat()[:10]),
            "profile_picture": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150&h=150&fit=crop&crop=face",
            "phone": row.get("Phone", ""),
            "address": row.get("Address", ""),
            "city": row.get("City", ""),
            "state": row.get("State", ""),
            "zip_code": row.get("Zip_Code", ""),
            "country": row.get("Country", "United States"),
            "date_of_birth": row.get("Date_of_Birth", ""),
            "nationality": row.get("Nationality", "US"),
            "occupation": row.get("Occupation", ""),
            "annual_income": row.get("Annual_Income", 0),
            "net_worth": row.get("Net_Worth", 0),
            "investment_experience": row.get("Investment_Experience", ""),
            "risk_tolerance": row.get("Risk_Tolerance", ""),
            "investment_goals": row.get("Investment_Goals", ""),
            "balances": {
                "total_balance": float(row.get("Total_Balance", 0)),
                "fidus_funds": float(row.get("FIDUS_Funds", 0)),
                "core_balance": float(row.get("Core_Balance", 0)),
                "dynamic_balance": float(row.get("Dynamic_Balance", 0))
            }
        }
        clients.append(client)
    
    return clients

# Excel Client Management Endpoints
@api_router.get("/admin/clients/export")
async def export_clients_excel():
    """Export all clients data to Excel format"""
    try:
        import io
        from datetime import datetime
        import json
        
        clients_data = generate_clients_excel_data()
        
        if not clients_data:
            return {"error": "No client data available for export"}
        
        # Convert to CSV format for simple download
        import csv
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=clients_data[0].keys())
        writer.writeheader()
        writer.writerows(clients_data)
        
        csv_content = output.getvalue()
        
        return {
            "success": True,
            "filename": f"fidus_clients_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            "data": csv_content,
            "total_clients": len(clients_data),
            "export_date": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Export failed: {str(e)}")

@api_router.post("/admin/clients/import")
async def import_clients_excel(file: UploadFile = File(...)):
    """Import clients data from Excel file"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls', '.csv')):
            raise HTTPException(status_code=400, detail="Only Excel (.xlsx, .xls) or CSV files are allowed")
        
        # Read file content
        content = await file.read()
        
        if file.filename.endswith('.csv'):
            # Handle CSV files
            import csv
            import io
            csv_content = content.decode('utf-8')
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            excel_data = list(csv_reader)
        else:
            # Handle Excel files
            import pandas as pd
            df = pd.read_excel(io.BytesIO(content))
            excel_data = df.to_dict('records')
        
        # Parse and validate client data
        clients = parse_clients_excel_data(excel_data)
        
        # Update MOCK_USERS with imported clients
        imported_count = 0
        updated_count = 0
        
        for client in clients:
            username = client["username"]
            if username in MOCK_USERS:
                MOCK_USERS[username].update(client)
                updated_count += 1
            else:
                MOCK_USERS[username] = client
                imported_count += 1
        
        return {
            "success": True,
            "message": f"Successfully processed {len(clients)} client records",
            "imported": imported_count,
            "updated": updated_count,
            "total_processed": len(clients),
            "skipped": len(excel_data) - len(clients)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Import failed: {str(e)}")

@api_router.get("/admin/clients/detailed")
async def get_detailed_clients():
    """Get detailed client information for admin management"""
    try:
        clients_data = []
        
        for user in MOCK_USERS.values():
            if user["type"] == "client":
                transactions = generate_mock_transactions(user["id"], 30)
                balances = calculate_balances(transactions)
                
                # Calculate metrics
                total_transactions = len(transactions)
                avg_transaction = sum(t["amount"] for t in transactions) / total_transactions if total_transactions > 0 else 0
                last_activity = transactions[0]["date"] if transactions else datetime.now(timezone.utc)
                
                client_detail = {
                    "id": user["id"],
                    "username": user["username"],
                    "name": user["name"],
                    "email": user["email"],
                    "status": user.get("status", "active"),
                    "created_at": user.get("createdAt", datetime.now(timezone.utc).isoformat()),
                    "profile_picture": user.get("profile_picture", ""),
                    "balances": {
                        "total": round(balances["total_balance"], 2),
                        "fidus": round(balances["fidus_funds"], 2),
                        "core": round(balances["core_balance"], 2),
                        "dynamic": round(balances["dynamic_balance"], 2)
                    },
                    "activity": {
                        "total_transactions": total_transactions,
                        "avg_transaction": round(avg_transaction, 2),
                        "last_activity": last_activity.isoformat() if hasattr(last_activity, 'isoformat') else str(last_activity)
                    },
                    "compliance": {
                        "kyc_status": "Verified",
                        "aml_status": "Clear",
                        "risk_level": random.choice(["Low", "Medium"])
                    },
                    "personal": {
                        "phone": user.get("phone", f"+1-555-{random.randint(1000000, 9999999)}"),
                        "address": user.get("address", f"{random.randint(100, 9999)} Main St"),
                        "city": user.get("city", "New York"),
                        "country": user.get("country", "United States")
                    }
                }
                clients_data.append(client_detail)
        
        # Sort by creation date (newest first)
        clients_data.sort(key=lambda x: x["created_at"], reverse=True)
        
        return {
            "clients": clients_data,
            "total_clients": len(clients_data),
            "active_clients": len([c for c in clients_data if c["status"] == "active"]),
            "total_aum": sum(c["balances"]["total"] for c in clients_data),
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch detailed clients: {str(e)}")

@api_router.delete("/admin/clients/{client_id}")
async def delete_client(client_id: str):
    """Delete a client (admin only)"""
    try:
        # Find and remove client
        username_to_remove = None
        for username, user in MOCK_USERS.items():
            if user.get("id") == client_id and user.get("type") == "client":
                username_to_remove = username
                break
        
        if username_to_remove:
            del MOCK_USERS[username_to_remove]
            return {"success": True, "message": "Client deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Client not found")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete client: {str(e)}")

@api_router.put("/admin/clients/{client_id}/status")
async def update_client_status(client_id: str, status_data: dict):
    """Update client status (active/inactive/suspended)"""
    try:
        new_status = status_data.get("status", "active").lower()
        
        if new_status not in ["active", "inactive", "suspended"]:
            raise HTTPException(status_code=400, detail="Invalid status. Must be active, inactive, or suspended")
        
        # Find and update client
        for username, user in MOCK_USERS.items():
            if user.get("id") == client_id and user.get("type") == "client":
                user["status"] = new_status
                user["updatedAt"] = datetime.now(timezone.utc).isoformat()
                return {"success": True, "message": f"Client status updated to {new_status}"}
        
        raise HTTPException(status_code=404, detail="Client not found")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update client status: {str(e)}")

@api_router.get("/admin/portfolio-summary")
async def get_portfolio_summary():
    """Get portfolio summary for admin dashboard"""
    total_aum = 2500000  # Mock AUM
    allocation = {
        "CORE": 33.33,
        "BALANCE": 33.33, 
        "DYNAMIC": 33.34
    }
    
    # Generate weekly performance data
    weeks_data = []
    for i in range(8):
        weeks_data.append({
            "week": f"Week {i+1}",
            "CORE": round(random.uniform(-2.5, 4.0), 2),
            "BALANCE": round(random.uniform(-1.5, 3.0), 2),
            "DYNAMIC": round(random.uniform(-3.0, 5.0), 2)
        })
    
    return {
        "aum": total_aum,
        "allocation": allocation,
        "weekly_performance": weeks_data,
        "ytd_return": 12.45
    }

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()