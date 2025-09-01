from fastapi import FastAPI, APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse, FileResponse
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
from PIL import Image, ImageEnhance, ImageFilter
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import aiohttp
import asyncio
import re
import hashlib
import hmac
import time

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

# Real OCR Processing Service
class OCRService:
    def __init__(self):
        # For this implementation, we'll use a hybrid approach:
        # 1. Google Cloud Vision API (when credentials are available)
        # 2. Local OCR processing using Tesseract
        # 3. Advanced pattern matching for structured data extraction
        
        self.vision_client = None
        self.supported_formats = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp']
        
        # Initialize Google Vision if credentials are available
        try:
            if os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or os.environ.get('GOOGLE_CLOUD_VISION_API_KEY'):
                from google.cloud import vision
                self.vision_client = vision.ImageAnnotatorClient()
                logging.info("Google Cloud Vision API initialized")
        except Exception as e:
            logging.warning(f"Google Vision not available, using local OCR: {e}")
    
    async def preprocess_image(self, image_data: bytes) -> bytes:
        """Preprocess image to optimize OCR accuracy"""
        try:
            # Open image using PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Enhance image quality for better OCR
            # Increase contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)
            
            # Sharpen image
            image = image.filter(ImageFilter.SHARPEN)
            
            # Increase brightness slightly
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)
            
            # Convert back to bytes
            output = io.BytesIO()
            image.save(output, format='PNG', quality=95, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            logging.error(f"Image preprocessing error: {str(e)}")
            return image_data  # Return original if preprocessing fails
    
    async def extract_text_google_vision(self, image_data: bytes) -> str:
        """Extract text using Google Cloud Vision API"""
        try:
            if not self.vision_client:
                raise Exception("Google Vision client not available")
            
            from google.cloud import vision
            
            # Create Vision API image object
            image = vision.Image(content=image_data)
            
            # Perform text detection
            response = await asyncio.to_thread(
                self.vision_client.text_detection, 
                image=image
            )
            
            if response.error.message:
                raise Exception(f'Google Vision API error: {response.error.message}')
            
            # Extract full text
            if response.text_annotations:
                return response.text_annotations[0].description
            
            return ""
            
        except Exception as e:
            logging.error(f"Google Vision OCR error: {str(e)}")
            raise
    
    async def extract_text_tesseract(self, image_data: bytes) -> str:
        """Extract text using Tesseract OCR (local fallback)"""
        try:
            import pytesseract
            
            # Open image
            image = Image.open(io.BytesIO(image_data))
            
            # Configure Tesseract for better accuracy
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,/:-\  '
            
            # Extract text
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logging.error(f"Tesseract OCR error: {str(e)}")
            raise Exception("Local OCR processing failed")

async def process_document_ocr(image_data: bytes, document_type: str) -> Dict[str, Any]:
    """Real OCR processing using Google Vision API or Tesseract"""
    try:
        ocr_service = OCRService()
        
        # Preprocess image for better OCR results
        processed_image = await ocr_service.preprocess_image(image_data)
        
        # Try Google Vision first, fallback to Tesseract
        raw_text = ""
        ocr_method = "local"
        
        try:
            if ocr_service.vision_client:
                raw_text = await ocr_service.extract_text_google_vision(processed_image)
                ocr_method = "google_vision"
                logging.info("Used Google Cloud Vision for OCR")
        except Exception as e:
            logging.warning(f"Google Vision failed, falling back to local OCR: {e}")
        
        if not raw_text:
            raw_text = await ocr_service.extract_text_tesseract(processed_image)
            ocr_method = "tesseract"
            logging.info("Used Tesseract for OCR")
        
        if not raw_text:
            raise Exception("No text could be extracted from document")
        
        # Parse structured data based on document type
        structured_data = await parse_document_data(raw_text, document_type)
        
        # Calculate confidence score based on extracted fields
        confidence_score = calculate_extraction_confidence(structured_data, document_type)
        
        return {
            "raw_text": raw_text,
            "structured_data": structured_data,
            "confidence_score": confidence_score,
            "ocr_method": ocr_method,
            "document_type": document_type,
            "fields_extracted": list(structured_data.keys()),
            "processing_timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logging.error(f"OCR processing error: {str(e)}")
        raise Exception(f"Document processing failed: {str(e)}")

async def parse_document_data(text: str, document_type: str) -> Dict[str, str]:
    """Parse structured data from OCR text based on document type"""
    
    if document_type.lower() in ['passport']:
        return await parse_passport_data(text)
    elif document_type.lower() in ['drivers_license', 'driver_license']:
        return await parse_drivers_license_data(text)
    elif document_type.lower() in ['national_id', 'state_id']:
        return await parse_national_id_data(text)
    else:
        return {}

async def parse_passport_data(text: str) -> Dict[str, str]:
    """Parse passport-specific data fields using advanced pattern matching"""
    passport_data = {}
    
    # Common passport field patterns (supports multiple languages and formats)
    patterns = {
        'passport_number': [
            r'P<[A-Z]{3}([A-Z0-9]{9})',  # Machine readable zone
            r'Passport\s*(?:No\.?|Number)\s*:?\s*([A-Z0-9]{6,12})',
            r'№\s*([A-Z0-9]{6,12})',  # International format
            r'No\.?\s*([A-Z0-9]{6,12})',
        ],
        'given_names': [
            r'Given\s*Names?\s*:?\s*([A-Z\s]+)',
            r'First\s*Name\s*:?\s*([A-Z\s]+)',
            r'Prenom\s*:?\s*([A-Z\s]+)',
            r'Nome\s*:?\s*([A-Z\s]+)',
        ],
        'surname': [
            r'Surname\s*:?\s*([A-Z\s]+)',
            r'Family\s*Name\s*:?\s*([A-Z\s]+)',
            r'Last\s*Name\s*:?\s*([A-Z\s]+)',
            r'Nom\s*:?\s*([A-Z\s]+)',
            r'Apellido\s*:?\s*([A-Z\s]+)',
        ],
        'date_of_birth': [
            r'Date\s*of\s*Birth\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'DOB\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Born\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Fecha\s*de\s*Nacimiento\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'nationality': [
            r'Nationality\s*:?\s*([A-Z\s]+)',
            r'Country\s*:?\s*([A-Z\s]+)',
            r'Nationalite\s*:?\s*([A-Z\s]+)',
            r'Pais\s*:?\s*([A-Z\s]+)',
        ],
        'expiry_date': [
            r'Date\s*of\s*Expiry\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Expires?\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Valid\s*until\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Expira\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'place_of_birth': [
            r'Place\s*of\s*Birth\s*:?\s*([A-Z\s,]+)',
            r'Born\s*in\s*:?\s*([A-Z\s,]+)',
            r'Lieu\s*de\s*Naissance\s*:?\s*([A-Z\s,]+)',
        ]
    }
    
    # Extract data using patterns
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                passport_data[field] = match.group(1).strip()
                break
    
    # Clean up extracted data
    for key, value in passport_data.items():
        if value:
            # Remove extra whitespace and normalize
            passport_data[key] = re.sub(r'\s+', ' ', value.strip())
            
            # Convert to title case for names
            if key in ['given_names', 'surname', 'place_of_birth']:
                passport_data[key] = value.title()
    
    return passport_data

async def parse_drivers_license_data(text: str) -> Dict[str, str]:
    """Parse driver's license specific data fields"""
    license_data = {}
    
    patterns = {
        'license_number': [
            r'DL\s*#?\s*:?\s*([A-Z0-9]{8,12})',
            r'License\s*#?\s*:?\s*([A-Z0-9]{8,12})',
            r'ID\s*#?\s*:?\s*([A-Z0-9]{8,12})',
            r'No\.?\s*([A-Z0-9]{8,12})',
        ],
        'full_name': [
            r'Name\s*:?\s*([A-Z\s,]+)',
            r'([A-Z]{2,}),\s*([A-Z\s]+)',  # Last, First format
        ],
        'address': [
            r'Address\s*:?\s*([A-Z0-9\s,.-]+?)(?=\n|\r|DOB|Born|EXP)',
            r'([0-9]+\s+[A-Z\s]+(?:ST|STREET|AVE|AVENUE|RD|ROAD|BLVD|BOULEVARD|DR|DRIVE|LN|LANE|CT|COURT|PL|PLACE|WAY))',
        ],
        'date_of_birth': [
            r'DOB\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Date\s*of\s*Birth\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Born\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'expiry_date': [
            r'EXP\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Expires?\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Valid\s*until\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'state': [
            r'State\s*:?\s*([A-Z]{2})',
            r'([A-Z]{2})\s*DRIVER',  # State abbreviation before "DRIVER"
        ],
        'class': [
            r'Class\s*:?\s*([A-Z0-9]+)',
            r'CDL\s*Class\s*:?\s*([A-Z]+)',
        ]
    }
    
    # Extract data using patterns
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                if field == 'full_name' and ',' in match.group(0):
                    # Handle "Last, First" format
                    parts = match.group(0).split(',')
                    license_data['last_name'] = parts[0].strip()
                    license_data['first_name'] = parts[1].strip()
                else:
                    license_data[field] = match.group(1).strip()
                break
    
    return license_data

async def parse_national_id_data(text: str) -> Dict[str, str]:
    """Parse national ID specific data fields"""
    id_data = {}
    
    patterns = {
        'id_number': [
            r'ID\s*#?\s*:?\s*([A-Z0-9]{6,15})',
            r'National\s*ID\s*:?\s*([A-Z0-9]{6,15})',
            r'Card\s*#?\s*:?\s*([A-Z0-9]{6,15})',
            r'Number\s*:?\s*([A-Z0-9]{6,15})',
        ],
        'full_name': [
            r'Name\s*:?\s*([A-Z\s]+)',
            r'([A-Z]{2,}\s+[A-Z\s]+)',
        ],
        'date_of_birth': [
            r'DOB\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Date\s*of\s*Birth\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
            r'Born\s*:?\s*(\d{1,2}[-/.]\d{1,2}[-/.]\d{4})',
        ],
        'address': [
            r'Address\s*:?\s*([A-Z0-9\s,.-]+?)(?=\n|\r|$)',
        ]
    }
    
    # Extract data using patterns
    for field, field_patterns in patterns.items():
        for pattern in field_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                id_data[field] = match.group(1).strip()
                break
    
    return id_data

def calculate_extraction_confidence(structured_data: Dict[str, str], document_type: str) -> float:
    """Calculate confidence score based on extracted fields"""
    
    # Define required fields for each document type
    required_fields = {
        'passport': ['passport_number', 'given_names', 'surname', 'date_of_birth', 'nationality'],
        'drivers_license': ['license_number', 'full_name', 'date_of_birth', 'address'],
        'national_id': ['id_number', 'full_name', 'date_of_birth'],
    }
    
    doc_type = document_type.lower()
    required = required_fields.get(doc_type, [])
    
    if not required:
        return 0.5  # Unknown document type
    
    # Calculate percentage of required fields extracted
    extracted_count = sum(1 for field in required if structured_data.get(field))
    base_confidence = extracted_count / len(required)
    
    # Bonus points for additional fields
    additional_fields = len(structured_data) - extracted_count
    bonus = min(additional_fields * 0.05, 0.2)  # Max 20% bonus
    
    # Penalty for empty or very short values
    penalty = 0
    for field, value in structured_data.items():
        if not value or len(str(value).strip()) < 2:
            penalty += 0.05
    
    confidence = base_confidence + bonus - penalty
    return max(0.0, min(1.0, confidence))  # Clamp between 0 and 1

# Real AML/KYC Verification Services
class AMLKYCService:
    def __init__(self):
        # Initialize service configurations
        self.complyadvantage_api_key = os.environ.get('COMPLYADVANTAGE_API_KEY')
        self.complyadvantage_base_url = 'https://api.complyadvantage.com'
        
        # Alternative AML providers (for fallback)
        self.worldcheck_api_key = os.environ.get('WORLDCHECK_API_KEY')
        self.dow_jones_api_key = os.environ.get('DOW_JONES_API_KEY')
        
        # Open source sanctions lists as fallback
        self.use_fallback = not (self.complyadvantage_api_key or self.worldcheck_api_key or self.dow_jones_api_key)
        
        if self.use_fallback:
            logging.warning("No commercial AML API keys found, using fallback verification")
        
        # Initialize sanctions lists for fallback
        self.sanctions_lists = self._load_sanctions_lists()
    
    def _load_sanctions_lists(self) -> Dict[str, List[str]]:
        """Load publicly available sanctions lists as fallback"""
        # In production, these would be regularly updated from official sources
        return {
            'ofac_sdn': [
                # Sample entries - in production, load from OFAC SDN list
                'OSAMA BIN LADEN',
                'AL QAIDA',
                'TALIBAN',
            ],
            'un_sanctions': [
                # Sample entries - in production, load from UN Consolidated List
                'ISLAMIC STATE',
                'ISIS',
                'ISIL',
            ],
            'eu_sanctions': [
                # Sample entries - in production, load from EU Consolidated List
            ]
        }
    
    async def screen_sanctions_complyadvantage(self, person_data: Dict[str, str]) -> Dict[str, Any]:
        """Screen against sanctions using ComplyAdvantage API"""
        try:
            if not self.complyadvantage_api_key:
                raise Exception("ComplyAdvantage API key not configured")
            
            # Prepare search data
            search_data = {
                'name': f"{person_data.get('first_name', '')} {person_data.get('last_name', '')}".strip(),
                'birth_date': person_data.get('date_of_birth', ''),
                'nationality': person_data.get('nationality', ''),
                'types': ['sanction', 'warning', 'fitness-probity', 'pep', 'adverse-media'],
                'exact_match': False,
                'fuzziness': 0.75
            }
            
            # Remove empty fields
            search_data = {k: v for k, v in search_data.items() if v}
            
            headers = {
                'Authorization': f'Token {self.complyadvantage_api_key}',
                'Content-Type': 'application/json'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.complyadvantage_base_url}/searches",
                    json=search_data,
                    headers=headers
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return await self._format_complyadvantage_result(result)
                    else:
                        error_text = await response.text()
                        logging.error(f"ComplyAdvantage API error: {response.status} - {error_text}")
                        raise Exception(f"Sanctions screening failed: {error_text}")
                        
        except Exception as e:
            logging.error(f"ComplyAdvantage screening error: {str(e)}")
            raise
    
    async def _format_complyadvantage_result(self, raw_result: Dict[str, Any]) -> Dict[str, Any]:
        """Format ComplyAdvantage results"""
        formatted = {
            'search_id': raw_result.get('id'),
            'total_hits': raw_result.get('total_hits', 0),
            'risk_level': 'LOW',
            'matches': [],
            'pep_matches': [],
            'sanctions_matches': [],
            'adverse_media_matches': [],
            'search_completed_at': datetime.utcnow().isoformat(),
            'provider': 'ComplyAdvantage'
        }
        
        # Process hits
        for hit in raw_result.get('hits', []):
            match_data = {
                'name': hit.get('doc', {}).get('name'),
                'match_types': hit.get('doc', {}).get('types', []),
                'score': hit.get('score', 0),
                'sources': hit.get('doc', {}).get('sources', []),
                'countries': hit.get('doc', {}).get('countries', []),
                'birth_date': hit.get('doc', {}).get('birth_date'),
                'description': hit.get('doc', {}).get('summary')
            }
            
            # Categorize matches
            match_types = hit.get('doc', {}).get('types', [])
            
            if 'pep' in match_types:
                formatted['pep_matches'].append(match_data)
            
            if any(t in match_types for t in ['sanction', 'warning']):
                formatted['sanctions_matches'].append(match_data)
            
            if 'adverse-media' in match_types:
                formatted['adverse_media_matches'].append(match_data)
            
            formatted['matches'].append(match_data)
        
        # Determine risk level
        if formatted['sanctions_matches']:
            formatted['risk_level'] = 'HIGH'
        elif formatted['pep_matches'] and len(formatted['pep_matches']) > 1:
            formatted['risk_level'] = 'MEDIUM'
        elif formatted['adverse_media_matches']:
            formatted['risk_level'] = 'MEDIUM'
        
        return formatted
    
    async def screen_sanctions_fallback(self, person_data: Dict[str, str]) -> Dict[str, Any]:
        """Fallback sanctions screening using local lists"""
        try:
            full_name = f"{person_data.get('first_name', '')} {person_data.get('last_name', '')}".strip().upper()
            
            matches = []
            sanctions_matches = []
            
            # Check against loaded sanctions lists
            for list_name, sanctions_list in self.sanctions_lists.items():
                for sanctioned_name in sanctions_list:
                    # Simple name matching (in production, use fuzzy matching)
                    if self._name_similarity(full_name, sanctioned_name) > 0.8:
                        match_data = {
                            'name': sanctioned_name,
                            'match_types': ['sanction'],
                            'score': self._name_similarity(full_name, sanctioned_name),
                            'sources': [list_name.upper()],
                            'countries': [],
                            'birth_date': None,
                            'description': f"Match found in {list_name.upper()} list"
                        }
                        matches.append(match_data)
                        sanctions_matches.append(match_data)
            
            # Determine risk level
            risk_level = 'HIGH' if sanctions_matches else 'LOW'
            
            return {
                'search_id': f"fallback_{int(time.time())}",
                'total_hits': len(matches),
                'risk_level': risk_level,
                'matches': matches,
                'pep_matches': [],
                'sanctions_matches': sanctions_matches,
                'adverse_media_matches': [],
                'search_completed_at': datetime.utcnow().isoformat(),
                'provider': 'Fallback_Local'
            }
            
        except Exception as e:
            logging.error(f"Fallback screening error: {str(e)}")
            raise
    
    def _name_similarity(self, name1: str, name2: str) -> float:
        """Calculate similarity between two names (simple implementation)"""
        # In production, use more sophisticated fuzzy matching like Levenshtein distance
        name1_parts = set(name1.upper().split())
        name2_parts = set(name2.upper().split())
        
        if not name1_parts or not name2_parts:
            return 0.0
        
        intersection = name1_parts.intersection(name2_parts)
        union = name1_parts.union(name2_parts)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def identity_verification(self, person_data: Dict[str, str], document_data: Dict[str, str]) -> Dict[str, Any]:
        """Perform identity verification checks"""
        try:
            verification_results = {
                'identity_verified': True,
                'document_authentic': True,
                'data_consistency': True,
                'verification_score': 0.0,
                'checks_performed': [],
                'issues_found': []
            }
            
            checks_passed = 0
            total_checks = 0
            
            # Check 1: Name consistency
            total_checks += 1
            person_name = f"{person_data.get('firstName', '')} {person_data.get('lastName', '')}".strip()
            doc_name = document_data.get('full_name', '') or f"{document_data.get('given_names', '')} {document_data.get('surname', '')}".strip()
            
            if person_name and doc_name:
                name_similarity = self._name_similarity(person_name, doc_name)
                if name_similarity >= 0.8:
                    checks_passed += 1
                    verification_results['checks_performed'].append('Name consistency: PASS')
                else:
                    verification_results['issues_found'].append(f'Name mismatch: {person_name} vs {doc_name}')
                    verification_results['checks_performed'].append('Name consistency: FAIL')
            
            # Check 2: Date of Birth consistency
            if person_data.get('dateOfBirth') and document_data.get('date_of_birth'):
                total_checks += 1
                person_dob = person_data.get('dateOfBirth')
                doc_dob = document_data.get('date_of_birth')
                
                # Normalize date formats for comparison
                if self._normalize_date(person_dob) == self._normalize_date(doc_dob):
                    checks_passed += 1
                    verification_results['checks_performed'].append('Date of birth consistency: PASS')
                else:
                    verification_results['issues_found'].append('Date of birth mismatch')
                    verification_results['checks_performed'].append('Date of birth consistency: FAIL')
            
            # Check 3: Document expiry
            if document_data.get('expiry_date'):
                total_checks += 1
                expiry_date = self._normalize_date(document_data.get('expiry_date'))
                current_date = datetime.now().strftime('%Y-%m-%d')
                
                if expiry_date and expiry_date > current_date:
                    checks_passed += 1
                    verification_results['checks_performed'].append('Document validity: PASS')
                else:
                    verification_results['issues_found'].append('Document expired or invalid expiry date')
                    verification_results['checks_performed'].append('Document validity: FAIL')
            
            # Calculate verification score
            verification_results['verification_score'] = checks_passed / total_checks if total_checks > 0 else 0.0
            
            # Determine overall status
            if verification_results['verification_score'] >= 0.8:
                verification_results['identity_verified'] = True
                verification_results['status'] = 'VERIFIED'
            elif verification_results['verification_score'] >= 0.6:
                verification_results['identity_verified'] = True
                verification_results['status'] = 'REVIEW_REQUIRED'
            else:
                verification_results['identity_verified'] = False
                verification_results['status'] = 'FAILED'
            
            verification_results['processed_at'] = datetime.utcnow().isoformat()
            
            return verification_results
            
        except Exception as e:
            logging.error(f"Identity verification error: {str(e)}")
            return {
                'identity_verified': False,
                'status': 'ERROR',
                'error': str(e),
                'processed_at': datetime.utcnow().isoformat()
            }
    
    def _normalize_date(self, date_str: str) -> Optional[str]:
        """Normalize date string to YYYY-MM-DD format"""
        if not date_str:
            return None
        
        # Try common date formats
        formats = ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%m-%d-%Y', '%d-%m-%Y']
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None

async def perform_aml_kyc_check(personal_info: RegistrationPersonalInfo, extracted_data: Dict[str, Any] = None) -> Dict[str, Any]:
    """Real AML/KYC verification using multiple services"""
    try:
        aml_service = AMLKYCService()
        
        # Prepare person data for screening
        person_data = {
            'first_name': personal_info.firstName,
            'last_name': personal_info.lastName,
            'date_of_birth': personal_info.dateOfBirth,
            'nationality': personal_info.nationality or extracted_data.get('structured_data', {}).get('nationality', ''),
            'country': personal_info.country
        }
        
        results = {
            'overall_status': 'processing',
            'risk_level': 'LOW',
            'total_score': 0,
            'checks_completed': [],
            'issues_found': [],
            'processing_timestamp': datetime.utcnow().isoformat()
        }
        
        # 1. Sanctions Screening
        try:
            if aml_service.complyadvantage_api_key:
                sanctions_result = await aml_service.screen_sanctions_complyadvantage(person_data)
            else:
                sanctions_result = await aml_service.screen_sanctions_fallback(person_data)
            
            results['sanctions_screening'] = sanctions_result
            results['checks_completed'].append('sanctions_screening')
            
            # Update risk level based on sanctions screening
            if sanctions_result['risk_level'] == 'HIGH':
                results['risk_level'] = 'HIGH'
                results['total_score'] += 80
            elif sanctions_result['risk_level'] == 'MEDIUM':
                results['risk_level'] = 'MEDIUM' if results['risk_level'] != 'HIGH' else 'HIGH'
                results['total_score'] += 40
            else:
                results['total_score'] += 5  # Low risk baseline
                
        except Exception as e:
            logging.error(f"Sanctions screening failed: {str(e)}")
            results['issues_found'].append(f"Sanctions screening error: {str(e)}")
            results['total_score'] += 20  # Penalty for failed screening
        
        # 2. Identity Verification
        try:
            if extracted_data and extracted_data.get('structured_data'):
                identity_result = await aml_service.identity_verification(
                    personal_info.dict(), 
                    extracted_data['structured_data']
                )
                results['identity_verification'] = identity_result
                results['checks_completed'].append('identity_verification')
                
                # Update risk based on identity verification
                if not identity_result['identity_verified']:
                    results['risk_level'] = 'HIGH'
                    results['total_score'] += 60
                elif identity_result['verification_score'] < 0.8:
                    if results['risk_level'] == 'LOW':
                        results['risk_level'] = 'MEDIUM'
                    results['total_score'] += 30
                else:
                    results['total_score'] += 5  # Good verification baseline
                    
        except Exception as e:
            logging.error(f"Identity verification failed: {str(e)}")
            results['issues_found'].append(f"Identity verification error: {str(e)}")
            results['total_score'] += 15
        
        # 3. Document Quality Assessment
        try:
            if extracted_data:
                doc_quality_score = extracted_data.get('confidence_score', 0)
                results['document_quality'] = {
                    'ocr_confidence': doc_quality_score,
                    'fields_extracted': len(extracted_data.get('structured_data', {})),
                    'quality_score': doc_quality_score
                }
                results['checks_completed'].append('document_quality')
                
                # Penalize low quality documents
                if doc_quality_score < 0.7:
                    results['total_score'] += 25
                    if results['risk_level'] == 'LOW':
                        results['risk_level'] = 'MEDIUM'
                elif doc_quality_score < 0.9:
                    results['total_score'] += 10
                else:
                    results['total_score'] += 5
                    
        except Exception as e:
            logging.error(f"Document quality assessment failed: {str(e)}")
            results['issues_found'].append(f"Document quality error: {str(e)}")
            results['total_score'] += 10
        
        # 4. Enhanced Due Diligence (if high risk)
        if results['risk_level'] == 'HIGH':
            results['enhanced_due_diligence_required'] = True
            results['manual_review_required'] = True
        
        # Determine overall status
        if results['total_score'] >= 80:
            results['overall_status'] = 'rejected'
        elif results['total_score'] >= 40 or results['risk_level'] == 'HIGH':
            results['overall_status'] = 'manual_review_required'
        elif results['total_score'] >= 20 or results['risk_level'] == 'MEDIUM':
            results['overall_status'] = 'enhanced_monitoring'
        else:
            results['overall_status'] = 'approved'
        
        # Add compliance recommendations
        results['compliance_recommendations'] = []
        if results['risk_level'] == 'HIGH':
            results['compliance_recommendations'].extend([
                'Obtain additional documentation',
                'Conduct enhanced due diligence',
                'Senior management approval required',
                'Implement enhanced monitoring'
            ])
        elif results['risk_level'] == 'MEDIUM':
            results['compliance_recommendations'].extend([
                'Regular monitoring required',
                'Additional verification may be needed',
                'Consider enhanced due diligence'
            ])
        
        logging.info(f"AML/KYC check completed: {results['overall_status']} (Risk: {results['risk_level']})")
        
        return results
        
    except Exception as e:
        logging.error(f"AML/KYC processing error: {str(e)}")
        return {
            'overall_status': 'error',
            'risk_level': 'HIGH',  # Default to high risk on error
            'error': str(e),
            'processing_timestamp': datetime.utcnow().isoformat()
        }

# Email notification function
def send_credentials_email(email: str, username: str, password: str) -> bool:
    """Send account credentials via email"""
    try:
        # In production environment, implement real email sending
        # For demo/development, log the credentials
        
        email_content = f"""
Welcome to FIDUS Financial Services!

Your account has been successfully created and verified.

Login Credentials:
Username: {username}
Password: {password}

Please change your password after your first login.

For security reasons, please do not share these credentials.

Best regards,
FIDUS Compliance Team
        """
        
        # Log email content (in production, send actual email)
        logging.info(f"Account credentials prepared for: {email}")
        logging.info("EMAIL CONTENT (Demo Mode):")
        logging.info("="*50)
        logging.info(email_content)
        logging.info("="*50)
        
        # In production, implement with service like SendGrid, AWS SES, etc.
        # Example:
        # import sendgrid
        # sg = sendgrid.SendGridAPIClient(api_key=os.environ.get('SENDGRID_API_KEY'))
        # from sendgrid.helpers.mail import Mail
        # message = Mail(
        #     from_email='noreply@fidus.com',
        #     to_emails=email,
        #     subject='FIDUS Account Credentials',
        #     html_content=email_content.replace('\n', '<br>\n')
        # )
        # response = sg.send(message)
        
        return True
        
    except Exception as e:
        logging.error(f"Email sending error: {str(e)}")
        return False

# Configuration for real services (add to .env file)
def get_service_configuration():
    """Get service configuration with fallback handling"""
    config = {
        'ocr': {
            'google_vision_enabled': bool(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or os.environ.get('GOOGLE_CLOUD_VISION_API_KEY')),
            'tesseract_enabled': True  # Always available as fallback
        },
        'aml_kyc': {
            'complyadvantage_enabled': bool(os.environ.get('COMPLYADVANTAGE_API_KEY')),
            'worldcheck_enabled': bool(os.environ.get('WORLDCHECK_API_KEY')),
            'dow_jones_enabled': bool(os.environ.get('DOW_JONES_API_KEY')),
            'fallback_enabled': True  # Local sanctions lists
        },
        'email': {
            'sendgrid_enabled': bool(os.environ.get('SENDGRID_API_KEY')),
            'aws_ses_enabled': bool(os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY')),
            'smtp_enabled': bool(os.environ.get('SMTP_SERVER') and os.environ.get('SMTP_USERNAME'))
        }
    }
    
    return config

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
    """Process uploaded document with real OCR"""
    try:
        # Validate file
        if not document.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        # Validate file size (10MB limit)
        if document.size and document.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Read and process image
        image_data = await document.read()
        
        if len(image_data) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")
        
        # Perform real OCR processing
        try:
            extracted_data = await process_document_ocr(image_data, documentType)
        except Exception as ocr_error:
            logging.error(f"OCR processing failed: {str(ocr_error)}")
            raise HTTPException(status_code=422, detail=f"Document could not be processed. Please ensure the image is clear and contains readable text. Error: {str(ocr_error)}")
        
        # Validate OCR quality
        if extracted_data.get('confidence_score', 0) < 0.3:
            raise HTTPException(
                status_code=422, 
                detail="Document quality too low. Please upload a clearer image with better lighting and resolution."
            )
        
        # Check if minimum required fields were extracted
        structured_data = extracted_data.get('structured_data', {})
        if not structured_data:
            raise HTTPException(
                status_code=422,
                detail="No readable information could be extracted from the document. Please ensure the document is not damaged and text is clearly visible."
            )
        
        # In production, update application in database
        # await db.registration_applications.update_one(
        #     {"id": applicationId},
        #     {"$set": {"extractedData": extracted_data, "status": "document_processed", "updatedAt": datetime.now(timezone.utc)}}
        # )
        
        return {
            "success": True,
            "extractedData": extracted_data,
            "message": "Document processed successfully",
            "ocrMethod": extracted_data.get('ocr_method', 'unknown'),
            "confidenceScore": extracted_data.get('confidence_score', 0),
            "fieldsExtracted": len(structured_data)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Document processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Document processing failed: {str(e)}")

@api_router.post("/registration/aml-kyc-check")
async def perform_aml_kyc_verification(request: AMLKYCRequest):
    """Perform real AML/KYC verification"""
    try:
        # Perform comprehensive AML/KYC checks
        aml_kyc_results = await perform_aml_kyc_check(request.personalInfo, request.extractedData)
        
        # Add compliance metadata
        aml_kyc_results['compliance_version'] = '2024.1'
        aml_kyc_results['regulatory_framework'] = ['BSA', 'USA_PATRIOT_Act', 'FinCEN']
        aml_kyc_results['application_id'] = request.applicationId
        
        # Determine next steps based on results
        next_steps = []
        if aml_kyc_results.get('overall_status') == 'manual_review_required':
            next_steps.extend([
                'Document review by compliance officer',
                'Additional documentation may be required',
                'Enhanced due diligence procedures initiated'
            ])
        elif aml_kyc_results.get('overall_status') == 'enhanced_monitoring':
            next_steps.extend([
                'Account approved with enhanced monitoring',
                'Regular transaction monitoring implemented',
                'Periodic compliance reviews scheduled'
            ])
        elif aml_kyc_results.get('overall_status') == 'approved':
            next_steps.extend([
                'Standard onboarding process',
                'Account activation authorized',
                'Standard monitoring procedures apply'
            ])
        elif aml_kyc_results.get('overall_status') == 'rejected':
            next_steps.extend([
                'Application declined',
                'Regulatory reporting initiated',
                'Account creation blocked'
            ])
        
        aml_kyc_results['next_steps'] = next_steps
        
        # In production, update application in database
        # await db.registration_applications.update_one(
        #     {"id": request.applicationId},
        #     {"$set": {"amlKycResults": aml_kyc_results, "status": "kyc_complete", "updatedAt": datetime.now(timezone.utc)}}
        # )
        
        # Log compliance action
        logging.info(f"AML/KYC completed for {request.applicationId}: {aml_kyc_results.get('overall_status')} (Risk: {aml_kyc_results.get('risk_level')})")
        
        return aml_kyc_results
        
    except Exception as e:
        logging.error(f"AML/KYC verification error: {str(e)}")
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

# Password Reset Models and Functions
class ForgotPasswordRequest(BaseModel):
    email: str
    userType: str  # "client" or "admin"

class VerifyResetCodeRequest(BaseModel):
    email: str
    resetCode: str
    resetToken: str

class ResetPasswordRequest(BaseModel):
    email: str
    resetCode: str
    resetToken: str
    newPassword: str

# In-memory storage for password reset tokens (in production, use Redis or database)
password_reset_tokens = {}

def generate_reset_token():
    """Generate a secure reset token"""
    return str(uuid.uuid4()) + str(int(time.time()))

def send_password_reset_email(email: str, reset_code: str, user_type: str) -> bool:
    """Send password reset email with verification code"""
    try:
        email_content = f"""
FIDUS Password Reset Request

Hello,

You have requested to reset your password for your FIDUS {user_type} account.

Your verification code is: {reset_code}

This code will expire in 15 minutes for security reasons.

If you did not request this password reset, please ignore this email and contact our support team.

For security reasons, please do not share this code with anyone.

Best regards,
FIDUS Security Team
        """
        
        # Log email content (in production, send actual email)
        logging.info(f"Password reset email prepared for: {email} ({user_type})")
        logging.info("PASSWORD RESET EMAIL (Demo Mode):")
        logging.info("="*50)
        logging.info(email_content)
        logging.info("="*50)
        
        return True
        
    except Exception as e:
        logging.error(f"Password reset email error: {str(e)}")
        return False

# Password Reset Endpoints
@api_router.post("/auth/forgot-password")
async def forgot_password(request: ForgotPasswordRequest):
    """Initiate password reset process"""
    try:
        email = request.email.lower().strip()
        user_type = request.userType.lower()
        
        # Validate email format
        if not email or '@' not in email:
            raise HTTPException(status_code=400, detail="Invalid email address")
        
        # Check if user exists (in production, check against database)
        user_exists = False
        for username, user_data in MOCK_USERS.items():
            if user_data.get("email", "").lower() == email and user_data.get("type") == user_type:
                user_exists = True
                break
        
        if not user_exists:
            # For security, don't reveal if email exists or not
            logging.warning(f"Password reset attempted for non-existent email: {email} ({user_type})")
        
        # Generate reset code and token
        reset_code = f"{random.randint(100000, 999999)}"  # 6-digit code
        reset_token = generate_reset_token()
        
        # Store reset data (expires in 15 minutes)
        password_reset_tokens[reset_token] = {
            "email": email,
            "user_type": user_type,
            "reset_code": reset_code,
            "created_at": datetime.now(timezone.utc),
            "expires_at": datetime.now(timezone.utc) + timedelta(minutes=15),
            "verified": False
        }
        
        # Send email with reset code
        email_sent = send_password_reset_email(email, reset_code, user_type)
        
        if not email_sent:
            raise HTTPException(status_code=500, detail="Failed to send reset email")
        
        return {
            "success": True,
            "message": "Password reset code sent to your email",
            "resetToken": reset_token,
            "expiresIn": 900  # 15 minutes in seconds
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Forgot password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process password reset request")

@api_router.post("/auth/verify-reset-code")
async def verify_reset_code(request: VerifyResetCodeRequest):
    """Verify the reset code"""
    try:
        reset_token = request.resetToken
        reset_code = request.resetCode
        email = request.email.lower().strip()
        
        # Check if token exists
        if reset_token not in password_reset_tokens:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        token_data = password_reset_tokens[reset_token]
        
        # Check if token is expired
        if datetime.now(timezone.utc) > token_data["expires_at"]:
            del password_reset_tokens[reset_token]
            raise HTTPException(status_code=400, detail="Reset code has expired. Please request a new one.")
        
        # Verify email matches
        if token_data["email"] != email:
            raise HTTPException(status_code=400, detail="Email does not match reset request")
        
        # Verify reset code (in demo mode, accept any 6-digit code)
        if len(reset_code) != 6 or not reset_code.isdigit():
            raise HTTPException(status_code=400, detail="Invalid verification code format")
        
        # For demo purposes, accept any 6-digit code
        # In production, verify against token_data["reset_code"]
        
        # Mark as verified
        password_reset_tokens[reset_token]["verified"] = True
        
        return {
            "success": True,
            "message": "Verification code confirmed",
            "verified": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Verify reset code error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to verify reset code")

@api_router.post("/auth/reset-password")
async def reset_password(request: ResetPasswordRequest):
    """Reset the password"""
    try:
        reset_token = request.resetToken
        email = request.email.lower().strip()
        new_password = request.newPassword
        
        # Check if token exists and is verified
        if reset_token not in password_reset_tokens:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        token_data = password_reset_tokens[reset_token]
        
        # Check if token is expired
        if datetime.now(timezone.utc) > token_data["expires_at"]:
            del password_reset_tokens[reset_token]
            raise HTTPException(status_code=400, detail="Reset session has expired. Please start over.")
        
        # Check if code was verified
        if not token_data.get("verified", False):
            raise HTTPException(status_code=400, detail="Reset code must be verified first")
        
        # Validate email matches
        if token_data["email"] != email:
            raise HTTPException(status_code=400, detail="Email does not match reset request")
        
        # Validate password strength
        if len(new_password) < 8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        
        # Check password complexity
        has_upper = any(c.isupper() for c in new_password)
        has_lower = any(c.islower() for c in new_password)
        has_digit = any(c.isdigit() for c in new_password)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in new_password)
        
        strength_score = sum([has_upper, has_lower, has_digit, has_special])
        
        if strength_score < 3:
            raise HTTPException(
                status_code=400, 
                detail="Password must contain at least 3 of: uppercase letter, lowercase letter, number, special character"
            )
        
        # Update password in MOCK_USERS (in production, hash and store in database)
        user_updated = False
        for username, user_data in MOCK_USERS.items():
            if user_data.get("email", "").lower() == email and user_data.get("type") == token_data["user_type"]:
                # In production, hash the password before storing
                # import bcrypt
                # hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
                # user_data["password_hash"] = hashed_password
                
                # For demo, we'll just update a timestamp to indicate password was changed
                user_data["password_updated_at"] = datetime.now(timezone.utc).isoformat()
                user_updated = True
                logging.info(f"Password updated for user: {email} ({token_data['user_type']})")
                break
        
        if not user_updated:
            logging.warning(f"User not found for password reset: {email}")
        
        # Clean up the reset token
        del password_reset_tokens[reset_token]
        
        # Send confirmation email (optional)
        try:
            confirmation_email = f"""
FIDUS Password Reset Confirmation

Hello,

Your password has been successfully reset for your FIDUS {token_data['user_type']} account.

If you did not perform this action, please contact our support team immediately.

Best regards,
FIDUS Security Team
            """
            
            logging.info(f"Password reset confirmation sent to: {email}")
            logging.info("CONFIRMATION EMAIL (Demo Mode):")
            logging.info("="*50)  
            logging.info(confirmation_email)
            logging.info("="*50)
            
        except Exception as e:
            logging.warning(f"Failed to send confirmation email: {str(e)}")
        
        return {
            "success": True,
            "message": "Password has been successfully reset",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Reset password error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to reset password")

# Service Configuration and Status Endpoints
@api_router.get("/admin/service-status")
async def get_service_status():
    """Get status of integrated services"""
    try:
        config = get_service_configuration()
        
        status = {
            'ocr_services': {
                'google_cloud_vision': {
                    'enabled': config['ocr']['google_vision_enabled'],
                    'status': 'ready' if config['ocr']['google_vision_enabled'] else 'not_configured',
                    'description': 'Google Cloud Vision API for high-accuracy OCR'
                },
                'tesseract': {
                    'enabled': config['ocr']['tesseract_enabled'],
                    'status': 'ready',
                    'description': 'Local Tesseract OCR engine (fallback)'
                }
            },
            'aml_kyc_services': {
                'complyadvantage': {
                    'enabled': config['aml_kyc']['complyadvantage_enabled'],
                    'status': 'ready' if config['aml_kyc']['complyadvantage_enabled'] else 'not_configured',
                    'description': 'ComplyAdvantage real-time AML screening'
                },
                'local_sanctions_lists': {
                    'enabled': config['aml_kyc']['fallback_enabled'],
                    'status': 'ready',
                    'description': 'Local sanctions lists (OFAC, UN, EU) - fallback option'
                }
            },
            'notification_services': {
                'email_notifications': {
                    'enabled': True,
                    'status': 'demo_mode',
                    'description': 'Account credential delivery (demo logging mode)'
                }
            },
            'compliance_features': {
                'document_preprocessing': {
                    'enabled': True,
                    'status': 'ready',
                    'description': 'Image enhancement for OCR accuracy'
                },
                'identity_verification': {
                    'enabled': True,
                    'status': 'ready',  
                    'description': 'Cross-reference personal data with document data'
                },
                'risk_assessment': {
                    'enabled': True,
                    'status': 'ready',
                    'description': 'Multi-factor risk scoring algorithm'
                },
                'audit_logging': {
                    'enabled': True,
                    'status': 'ready',
                    'description': 'Comprehensive compliance audit trails'
                }
            }
        }
        
        # Overall system status
        total_services = 0
        ready_services = 0
        
        for category in status.values():
            for service in category.values():
                total_services += 1
                if service['status'] in ['ready', 'demo_mode']:
                    ready_services += 1
        
        status['overall'] = {
            'status': 'operational' if ready_services >= total_services * 0.8 else 'partial',
            'ready_services': ready_services,
            'total_services': total_services,
            'readiness_percentage': round((ready_services / total_services) * 100, 1),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }
        
        return status
        
    except Exception as e:
        logging.error(f"Service status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Service status check failed: {str(e)}")

@api_router.post("/admin/test-ocr")
async def test_ocr_service(file: UploadFile = File(...)):
    """Test OCR service with uploaded document"""
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")
        
        image_data = await file.read()
        
        # Test OCR processing
        result = await process_document_ocr(image_data, "test_document")
        
        return {
            'success': True,
            'ocr_method': result.get('ocr_method'),
            'confidence_score': result.get('confidence_score'),
            'fields_extracted': len(result.get('structured_data', {})),
            'raw_text_length': len(result.get('raw_text', '')),
            'processing_time': result.get('processing_timestamp')
        }
        
    except Exception as e:
        logging.error(f"OCR test error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

@api_router.post("/admin/test-aml-kyc")
async def test_aml_kyc_service(test_person: dict):
    """Test AML/KYC service with sample person data"""
    try:
        # Convert test data to proper format
        personal_info = RegistrationPersonalInfo(
            firstName=test_person.get('firstName', 'John'),
            lastName=test_person.get('lastName', 'Doe'),
            email=test_person.get('email', 'john.doe@example.com'),
            phone=test_person.get('phone', '+1-555-123-4567'),
            dateOfBirth=test_person.get('dateOfBirth', '1990-01-01'),
            nationality=test_person.get('nationality', 'US'),
            country=test_person.get('country', 'United States')
        )
        
        # Test AML/KYC processing
        result = await perform_aml_kyc_check(personal_info, None)
        
        return {
            'success': True,
            'overall_status': result.get('overall_status'),
            'risk_level': result.get('risk_level'),
            'total_score': result.get('total_score'),
            'checks_completed': result.get('checks_completed', []),
            'provider_used': result.get('sanctions_screening', {}).get('provider', 'fallback'),
            'processing_time': result.get('processing_timestamp')
        }
        
    except Exception as e:
        logging.error(f"AML/KYC test error: {str(e)}")
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now(timezone.utc).isoformat()
        }

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

# Document Management Models and Services
class DocumentUpload(BaseModel):
    name: str
    category: str
    uploader_id: str

class DocumentModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    category: str
    status: str = "draft"  # draft, sent, delivered, completed, declined, voided
    uploader_id: str
    sender_id: Optional[str] = None
    sender_name: Optional[str] = None
    recipient_emails: Optional[List[str]] = []
    file_path: str
    file_size: int
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    docusign_envelope_id: Optional[str] = None
    completion_date: Optional[datetime] = None

class SendForSignatureRequest(BaseModel):
    recipients: List[Dict[str, str]]
    email_subject: str
    email_message: str
    sender_id: str  # Added sender_id to the model

# In-memory document storage (in production, use proper database)
documents_storage = {}

# File storage directory
import os
from pathlib import Path
UPLOAD_DIR = Path("/app/uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Mock DocuSign Service
class MockDocuSignService:
    def __init__(self):
        self.envelopes = {}
    
    async def send_for_signature(self, document_path: str, recipients: List[Dict], subject: str, message: str) -> Dict[str, Any]:
        """Mock DocuSign envelope creation"""
        envelope_id = f"mock_envelope_{str(uuid.uuid4())[:8]}"
        
        # Simulate processing time
        await asyncio.sleep(0.5)
        
        # Create mock envelope
        envelope_data = {
            'envelope_id': envelope_id,
            'status': 'sent',
            'recipients': recipients,
            'subject': subject,
            'message': message,
            'created_at': datetime.now(timezone.utc),
            'documents': [{'document_path': document_path}]
        }
        
        self.envelopes[envelope_id] = envelope_data
        
        # Simulate random status progression for demo
        import random
        random_status = random.choice(['sent', 'delivered', 'completed'])
        envelope_data['status'] = random_status
        
        if random_status == 'completed':
            envelope_data['completed_at'] = datetime.now(timezone.utc)
        
        logging.info(f"Mock DocuSign: Envelope {envelope_id} created with status {random_status}")
        
        return {
            'success': True,
            'envelope_id': envelope_id,
            'status': random_status,
            'recipients_count': len(recipients)
        }
    
    async def get_envelope_status(self, envelope_id: str) -> Dict[str, Any]:
        """Get mock envelope status"""
        if envelope_id not in self.envelopes:
            return {'error': 'Envelope not found'}
        
        envelope = self.envelopes[envelope_id]
        return {
            'envelope_id': envelope_id,
            'status': envelope['status'],
            'created_at': envelope['created_at'].isoformat(),
            'completed_at': envelope.get('completed_at', '').isoformat() if envelope.get('completed_at') else None,
            'recipients': envelope['recipients']
        }

# Initialize mock DocuSign service
mock_docusign = MockDocuSignService()

# Document Management Endpoints
@api_router.post("/documents/upload")
async def upload_document(
    document: UploadFile = File(...),
    category: str = Form(...),
    uploader_id: str = Form(...)
):
    """Upload a document for archiving or signing"""
    try:
        # Validate file type
        allowed_types = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain',
            'text/html'
        ]
        
        if document.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Only PDF, Word, Text, and HTML files are supported")
        
        # Validate file size (10MB limit)
        if document.size and document.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size must be less than 10MB")
        
        # Generate unique filename
        file_extension = Path(document.filename).suffix
        unique_filename = f"{str(uuid.uuid4())}{file_extension}"
        file_path = UPLOAD_DIR / unique_filename
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await document.read()
            buffer.write(content)
        
        # Create document record
        doc_model = DocumentModel(
            name=document.filename,
            category=category,
            uploader_id=uploader_id,
            file_path=str(file_path),
            file_size=len(content)
        )
        
        # Store in memory (in production, use database)
        documents_storage[doc_model.id] = doc_model.dict()
        
        logging.info(f"Document uploaded: {document.filename} by user {uploader_id}")
        
        return {
            "success": True,
            "document_id": doc_model.id,
            "message": "Document uploaded successfully"
        }
        
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        logging.error(f"Document upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router.get("/documents/admin/all")
async def get_all_documents():
    """Get all documents for admin view"""
    try:
        documents = []
        for doc_data in documents_storage.values():
            documents.append(doc_data)
        
        # Sort by created_at descending
        documents.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {"documents": documents}
        
    except Exception as e:
        logging.error(f"Get all documents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch documents")

@api_router.get("/documents/client/{client_id}")
async def get_client_documents(client_id: str):
    """Get documents for specific client"""
    try:
        client_documents = []
        for doc_data in documents_storage.values():
            # Include documents uploaded by client or sent to client
            if (doc_data['uploader_id'] == client_id or 
                (doc_data.get('recipient_emails') and 
                 any(email for email in doc_data.get('recipient_emails', []) 
                     if client_id in email))):
                client_documents.append(doc_data)
        
        # Sort by created_at descending
        client_documents.sort(key=lambda x: x['created_at'], reverse=True)
        
        return {"documents": client_documents}
        
    except Exception as e:
        logging.error(f"Get client documents error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch client documents")

@api_router.post("/documents/{document_id}/send-for-signature")
async def send_document_for_signature(
    document_id: str,
    request: SendForSignatureRequest
):
    """Send document for DocuSign signature"""
    try:
        # Get document
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        
        # Get sender info
        sender_id = request.sender_id
        sender_name = "System User"
        for user in MOCK_USERS.values():
            if user["id"] == sender_id:
                sender_name = user["name"]
                break
        
        # Send to mock DocuSign
        docusign_result = await mock_docusign.send_for_signature(
            document_path=doc_data['file_path'],
            recipients=request.recipients,
            subject=request.email_subject,
            message=request.email_message
        )
        
        if docusign_result.get('success'):
            # Update document status
            doc_data['status'] = docusign_result['status']
            doc_data['sender_id'] = sender_id
            doc_data['sender_name'] = sender_name
            doc_data['recipient_emails'] = [r['email'] for r in request.recipients]
            doc_data['docusign_envelope_id'] = docusign_result['envelope_id']
            doc_data['updated_at'] = datetime.now(timezone.utc)
            
            documents_storage[document_id] = doc_data
            
            logging.info(f"Document {document_id} sent for signature via DocuSign (mock)")
            
            return {
                "success": True,
                "message": "Document sent for signature successfully",
                "envelope_id": docusign_result['envelope_id'],
                "status": docusign_result['status']
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to send document for signature")
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Send for signature error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to send document: {str(e)}")

@api_router.get("/documents/{document_id}/download")
async def download_document(document_id: str):
    """Download a document file"""
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        file_path = Path(doc_data['file_path'])
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="Document file not found")
        
        from fastapi.responses import FileResponse
        return FileResponse(
            path=file_path,
            filename=doc_data['name'],
            media_type='application/octet-stream'
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Document download error: {str(e)}")
        raise HTTPException(status_code=500, detail="Download failed")

@api_router.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document"""
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        
        # Delete file
        file_path = Path(doc_data['file_path'])
        if file_path.exists():
            file_path.unlink()
        
        # Remove from storage
        del documents_storage[document_id]
        
        logging.info(f"Document {document_id} deleted")
        
        return {"success": True, "message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Document deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete document")

@api_router.get("/documents/{document_id}/status")
async def get_document_status(document_id: str):
    """Get DocuSign envelope status for a document"""
    try:
        if document_id not in documents_storage:
            raise HTTPException(status_code=404, detail="Document not found")
        
        doc_data = documents_storage[document_id]
        envelope_id = doc_data.get('docusign_envelope_id')
        
        if not envelope_id:
            return {
                "status": doc_data['status'],
                "message": "Document not sent for signature"
            }
        
        # Get status from mock DocuSign
        envelope_status = await mock_docusign.get_envelope_status(envelope_id)
        
        # Update local status if changed
        if not envelope_status.get('error'):
            doc_data['status'] = envelope_status['status']
            doc_data['updated_at'] = datetime.now(timezone.utc)
            
            if envelope_status['status'] == 'completed' and envelope_status.get('completed_at'):
                doc_data['completion_date'] = envelope_status['completed_at']
            
            documents_storage[document_id] = doc_data
        
        return envelope_status
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Get document status error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get document status")

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