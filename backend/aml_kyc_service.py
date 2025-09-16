"""
AML/KYC Service for FIDUS Investment Management
==============================================

This service handles Anti-Money Laundering (AML) and Know Your Customer (KYC) 
compliance checks including OFAC screening for prospect-to-client conversion.
"""

import os
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
import re
import requests
import json
import asyncio
from dataclasses import dataclass, asdict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AMLStatus(str, Enum):
    PENDING = "pending"
    CLEAR = "clear"
    HIT = "hit"
    MANUAL_REVIEW = "manual_review"
    APPROVED = "approved" 
    REJECTED = "rejected"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class PersonData:
    first_name: str
    last_name: str
    full_name: str
    date_of_birth: str
    nationality: str
    address: str
    city: str
    country: str
    email: str
    phone: str

@dataclass
class OFACSearchResult:
    search_id: str
    status: AMLStatus
    risk_level: RiskLevel
    matches_found: int
    match_details: List[Dict]
    search_timestamp: datetime
    search_parameters: Dict
    confidence_score: float

@dataclass 
class KYCDocument:
    document_id: str
    document_type: str  # identity, proof_of_residence, etc.
    file_path: str
    verification_status: str  # pending, approved, rejected
    extracted_data: Optional[Dict] = None
    verification_notes: str = ""
    verified_by: Optional[str] = None
    verified_at: Optional[datetime] = None

@dataclass
class AMLKYCResult:
    result_id: str
    client_id: str
    prospect_id: str
    overall_status: AMLStatus
    risk_assessment: RiskLevel
    ofac_result: OFACSearchResult
    kyc_documents: List[KYCDocument]
    compliance_notes: str
    created_at: datetime
    completed_at: Optional[datetime]
    approved_by: Optional[str]
    approval_document_path: Optional[str]

class AMLKYCService:
    """AML/KYC compliance service for FIDUS"""
    
    def __init__(self):
        self.ofac_api_key = os.environ.get('OFAC_API_KEY')
        self.aml_api_endpoint = os.environ.get('AML_API_ENDPOINT', 'https://api.sanctionscanner.com/api/v1/person')
        self.results_storage = {}  # In production, use proper database
        
    async def search_ofac_sanctions(self, person_data: PersonData) -> OFACSearchResult:
        """
        Perform OFAC sanctions list search for a person
        """
        search_id = str(uuid.uuid4())
        
        try:
            # Prepare search parameters
            search_params = {
                "name": person_data.full_name,
                "first_name": person_data.first_name,
                "last_name": person_data.last_name,
                "date_of_birth": person_data.date_of_birth,
                "nationality": person_data.nationality,
                "country": person_data.country
            }
            
            logger.info(f"Starting OFAC search for: {person_data.full_name}")
            
            # For demo purposes, simulate OFAC search
            # In production, integrate with real OFAC/sanctions API
            matches_found, match_details = await self._simulate_ofac_search(person_data)
            
            # Determine status and risk level based on matches
            if matches_found == 0:
                status = AMLStatus.CLEAR
                risk_level = RiskLevel.LOW
                confidence_score = 0.0
            elif matches_found == 1 and match_details[0].get('confidence', 0) < 0.5:
                status = AMLStatus.MANUAL_REVIEW
                risk_level = RiskLevel.MEDIUM  
                confidence_score = match_details[0].get('confidence', 0)
            else:
                status = AMLStatus.HIT
                risk_level = RiskLevel.HIGH
                confidence_score = max(m.get('confidence', 0) for m in match_details)
            
            result = OFACSearchResult(
                search_id=search_id,
                status=status,
                risk_level=risk_level,
                matches_found=matches_found,
                match_details=match_details,
                search_timestamp=datetime.now(timezone.utc),
                search_parameters=search_params,
                confidence_score=confidence_score
            )
            
            logger.info(f"OFAC search completed: {status.value}, {matches_found} matches")
            return result
            
        except Exception as e:
            logger.error(f"OFAC search failed: {str(e)}")
            
            # Return failed result
            return OFACSearchResult(
                search_id=search_id,
                status=AMLStatus.MANUAL_REVIEW,
                risk_level=RiskLevel.MEDIUM,
                matches_found=0,
                match_details=[],
                search_timestamp=datetime.now(timezone.utc),
                search_parameters=search_params,
                confidence_score=0.0
            )
    
    async def _simulate_ofac_search(self, person_data: PersonData) -> Tuple[int, List[Dict]]:
        """
        Simulate OFAC search results for demo purposes
        In production, replace with real OFAC API integration
        """
        # Simulate API delay
        await asyncio.sleep(1)
        
        # Check for common test names that should trigger hits
        test_hit_names = [
            "vladimir putin",
            "kim jong un", 
            "nicolas maduro",
            "test sanctions",
            "demo blocked"
        ]
        
        full_name_lower = person_data.full_name.lower()
        
        # Simulate a hit for test names
        for test_name in test_hit_names:
            if test_name in full_name_lower:
                match_details = [{
                    "list_name": "OFAC SDN List",
                    "matched_name": test_name.title(),
                    "match_type": "name",
                    "confidence": 0.85,
                    "date_added": "2020-01-15",
                    "reason": "Financial sanctions",
                    "entity_type": "Individual"
                }]
                return 1, match_details
        
        # Check for partial matches (manual review cases)
        if "john smith" in full_name_lower or "maria garcia" in full_name_lower:
            match_details = [{
                "list_name": "OFAC SDN List", 
                "matched_name": "John A. Smith",
                "match_type": "partial_name",
                "confidence": 0.35,
                "date_added": "2019-05-20",
                "reason": "Possible match - manual review required",
                "entity_type": "Individual"
            }]
            return 1, match_details
        
        # Most legitimate users will have no matches
        return 0, []
    
    async def verify_kyc_documents(self, documents: List[KYCDocument]) -> Dict[str, str]:
        """
        Verify uploaded KYC documents
        """
        verification_results = {}
        
        for doc in documents:
            try:
                if doc.document_type == "identity":
                    # Simulate identity document verification
                    verification_results[doc.document_id] = await self._verify_identity_document(doc)
                elif doc.document_type == "proof_of_residence":
                    # Simulate address verification
                    verification_results[doc.document_id] = await self._verify_address_document(doc)
                else:
                    verification_results[doc.document_id] = "pending"
                    
            except Exception as e:
                logger.error(f"Document verification failed for {doc.document_id}: {str(e)}")
                verification_results[doc.document_id] = "failed"
        
        return verification_results
    
    async def _verify_identity_document(self, document: KYCDocument) -> str:
        """Simulate identity document verification"""
        await asyncio.sleep(0.5)  # Simulate processing time
        
        # In production, integrate with OCR service and document verification API
        # For demo, randomly approve most documents
        import random
        
        verification_score = random.uniform(0.7, 1.0)
        if verification_score > 0.8:
            return "approved"
        elif verification_score > 0.6:
            return "manual_review"
        else:
            return "rejected"
    
    async def _verify_address_document(self, document: KYCDocument) -> str:
        """Simulate address document verification"""
        await asyncio.sleep(0.3)  # Simulate processing time
        
        # In production, verify address matches and document authenticity
        import random
        
        verification_score = random.uniform(0.6, 1.0)
        if verification_score > 0.75:
            return "approved"
        elif verification_score > 0.5:
            return "manual_review"
        else:
            return "rejected"
    
    async def perform_full_aml_kyc_check(self, prospect_id: str, person_data: PersonData, 
                                       documents: List[KYCDocument]) -> AMLKYCResult:
        """
        Perform complete AML/KYC compliance check
        """
        result_id = str(uuid.uuid4())
        
        try:
            logger.info(f"Starting full AML/KYC check for prospect: {prospect_id}")
            
            # Step 1: OFAC search
            ofac_result = await self.search_ofac_sanctions(person_data)
            
            # Step 2: Document verification
            doc_verification_results = await self.verify_kyc_documents(documents)
            
            # Step 3: Overall risk assessment
            overall_status, risk_level = self._assess_overall_risk(ofac_result, doc_verification_results)
            
            # Step 4: Create compliance notes
            compliance_notes = self._generate_compliance_notes(ofac_result, doc_verification_results)
            
            # Update document statuses
            for doc in documents:
                if doc.document_id in doc_verification_results:
                    doc.verification_status = doc_verification_results[doc.document_id]
                    doc.verified_at = datetime.now(timezone.utc)
                    doc.verified_by = "system"
            
            # Create final result
            result = AMLKYCResult(
                result_id=result_id,
                client_id="",  # Will be set when prospect converts to client
                prospect_id=prospect_id,
                overall_status=overall_status,
                risk_assessment=risk_level,
                ofac_result=ofac_result,
                kyc_documents=documents,
                compliance_notes=compliance_notes,
                created_at=datetime.now(timezone.utc),
                completed_at=datetime.now(timezone.utc) if overall_status in [AMLStatus.CLEAR, AMLStatus.REJECTED] else None,
                approved_by=None,
                approval_document_path=None
            )
            
            # Store result
            self.results_storage[result_id] = result
            
            logger.info(f"AML/KYC check completed: {overall_status.value} for prospect {prospect_id}")
            return result
            
        except Exception as e:
            logger.error(f"AML/KYC check failed for prospect {prospect_id}: {str(e)}")
            
            # Return failed result requiring manual review
            return AMLKYCResult(
                result_id=result_id,
                client_id="",
                prospect_id=prospect_id,
                overall_status=AMLStatus.MANUAL_REVIEW,
                risk_assessment=RiskLevel.MEDIUM,
                ofac_result=ofac_result if 'ofac_result' in locals() else None,
                kyc_documents=documents,
                compliance_notes=f"AML/KYC check failed due to system error: {str(e)}",
                created_at=datetime.now(timezone.utc),
                completed_at=None,
                approved_by=None,
                approval_document_path=None
            )
    
    def _assess_overall_risk(self, ofac_result: OFACSearchResult, 
                           doc_results: Dict[str, str]) -> Tuple[AMLStatus, RiskLevel]:
        """Assess overall risk based on OFAC and document verification results"""
        
        # Check OFAC results first
        if ofac_result.status == AMLStatus.HIT:
            return AMLStatus.REJECTED, RiskLevel.CRITICAL
        elif ofac_result.status == AMLStatus.MANUAL_REVIEW:
            return AMLStatus.MANUAL_REVIEW, RiskLevel.HIGH
        
        # Check document verification results
        rejected_docs = [status for status in doc_results.values() if status == "rejected"]
        manual_review_docs = [status for status in doc_results.values() if status == "manual_review"]
        
        if len(rejected_docs) > 0:
            return AMLStatus.MANUAL_REVIEW, RiskLevel.MEDIUM
        elif len(manual_review_docs) > 1:
            return AMLStatus.MANUAL_REVIEW, RiskLevel.MEDIUM
        elif len(manual_review_docs) == 1:
            return AMLStatus.MANUAL_REVIEW, RiskLevel.LOW
        
        # All checks passed
        return AMLStatus.CLEAR, RiskLevel.LOW
    
    def _generate_compliance_notes(self, ofac_result: OFACSearchResult, 
                                 doc_results: Dict[str, str]) -> str:
        """Generate compliance notes for the AML/KYC result"""
        
        notes = []
        
        # OFAC notes
        if ofac_result.status == AMLStatus.CLEAR:
            notes.append("✅ OFAC SANCTIONS CHECK: CLEAR - No matches found in sanctions lists.")
        elif ofac_result.status == AMLStatus.HIT:
            notes.append(f"🚨 OFAC SANCTIONS CHECK: HIT - {ofac_result.matches_found} match(es) found. CLIENT REJECTED.")
        elif ofac_result.status == AMLStatus.MANUAL_REVIEW:
            notes.append(f"⚠️ OFAC SANCTIONS CHECK: MANUAL REVIEW REQUIRED - {ofac_result.matches_found} potential match(es) found.")
        
        # Document verification notes
        approved_docs = sum(1 for status in doc_results.values() if status == "approved")
        total_docs = len(doc_results)
        
        if approved_docs == total_docs:
            notes.append(f"✅ DOCUMENT VERIFICATION: ALL APPROVED - {approved_docs}/{total_docs} documents verified.")
        else:
            pending_docs = sum(1 for status in doc_results.values() if status in ["manual_review", "pending"])
            rejected_docs = sum(1 for status in doc_results.values() if status == "rejected")
            
            if rejected_docs > 0:
                notes.append(f"❌ DOCUMENT VERIFICATION: {rejected_docs} document(s) rejected, {pending_docs} require review.")
            else:
                notes.append(f"⚠️ DOCUMENT VERIFICATION: {pending_docs} document(s) require manual review.")
        
        # Risk assessment summary
        if ofac_result.risk_level == RiskLevel.LOW and approved_docs == total_docs:
            notes.append("✅ RISK ASSESSMENT: LOW RISK - Client approved for onboarding.")
        elif ofac_result.risk_level in [RiskLevel.MEDIUM, RiskLevel.HIGH]:
            notes.append("⚠️ RISK ASSESSMENT: ELEVATED RISK - Manual compliance review required.")
        elif ofac_result.risk_level == RiskLevel.CRITICAL:
            notes.append("🚨 RISK ASSESSMENT: CRITICAL RISK - Client must be rejected.")
        
        return "\n".join(notes)
    
    async def generate_aml_approval_document(self, result: AMLKYCResult) -> str:
        """
        Generate AML/KYC approval document for internal compliance records
        """
        try:
            if result.overall_status != AMLStatus.CLEAR:
                raise ValueError("Cannot generate approval document for non-approved result")
            
            # Create approval document content
            document_content = f"""
# AML/KYC COMPLIANCE APPROVAL DOCUMENT
**FIDUS Investment Management - Internal Use Only**

---

## CLIENT INFORMATION
- **Result ID:** {result.result_id}
- **Prospect ID:** {result.prospect_id}
- **Client ID:** {result.client_id or 'Not yet assigned'}
- **Approval Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## OFAC SANCTIONS SCREENING
- **Search ID:** {result.ofac_result.search_id}
- **Status:** {result.ofac_result.status.value.upper()}
- **Risk Level:** {result.ofac_result.risk_level.value.upper()}
- **Matches Found:** {result.ofac_result.matches_found}
- **Confidence Score:** {result.ofac_result.confidence_score:.2f}
- **Search Date:** {result.ofac_result.search_timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}

---

## DOCUMENT VERIFICATION
"""
            
            for doc in result.kyc_documents:
                document_content += f"""
- **{doc.document_type.upper()}:** {doc.verification_status.upper()}
  - Document ID: {doc.document_id}
  - Verified: {doc.verified_at.strftime('%Y-%m-%d %H:%M:%S UTC') if doc.verified_at else 'Pending'}
  - Verified By: {doc.verified_by or 'System'}
"""
            
            document_content += f"""
---

## COMPLIANCE ASSESSMENT
{result.compliance_notes}

---

## APPROVAL DETAILS
- **Overall Status:** {result.overall_status.value.upper()}
- **Risk Assessment:** {result.risk_assessment.value.upper()}
- **Completed At:** {result.completed_at.strftime('%Y-%m-%d %H:%M:%S UTC') if result.completed_at else 'Pending'}
- **Approved By:** System Automated Review
- **Approval Authority:** FIDUS Compliance Department

---

**This document certifies that the above-mentioned client has been screened for AML/KYC compliance in accordance with FIDUS Investment Management policies and applicable regulations.**

**Document Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**System:** FIDUS AML/KYC Compliance Service v1.0
"""
            
            # Save document to file system
            import os
            from pathlib import Path
            
            # Create compliance documents directory
            compliance_dir = Path("/app/compliance_documents")
            compliance_dir.mkdir(exist_ok=True)
            
            # Generate filename
            filename = f"AML_KYC_APPROVAL_{result.prospect_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            file_path = compliance_dir / filename
            
            # Write document
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(document_content)
            
            logger.info(f"AML/KYC approval document generated: {file_path}")
            return str(file_path)
            
        except Exception as e:
            logger.error(f"Failed to generate approval document: {str(e)}")
            raise
    
    def get_aml_result(self, result_id: str) -> Optional[AMLKYCResult]:
        """Get AML/KYC result by ID"""
        return self.results_storage.get(result_id)
    
    async def approve_manual_review(self, result_id: str, approved_by: str, notes: str = "") -> AMLKYCResult:
        """Manually approve a result that was flagged for review"""
        result = self.get_aml_result(result_id)
        if not result:
            raise ValueError(f"Result not found: {result_id}")
        
        if result.overall_status != AMLStatus.MANUAL_REVIEW:
            raise ValueError(f"Result is not in manual review status: {result.overall_status}")
        
        # Update result
        result.overall_status = AMLStatus.APPROVED
        result.approved_by = approved_by
        result.completed_at = datetime.now(timezone.utc)
        result.compliance_notes += f"\n\n--- MANUAL APPROVAL ---\nApproved by: {approved_by}\nApproval notes: {notes}\nApproval date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}"
        
        # Generate approval document
        result.approval_document_path = await self.generate_aml_approval_document(result)
        
        return result

# Create global instance
aml_kyc_service = AMLKYCService()