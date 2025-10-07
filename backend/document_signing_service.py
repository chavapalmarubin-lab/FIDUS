"""
Document Signing Service
Provides PDF viewing, document upload, and electronic signature functionality
"""

import os
import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
import base64
import io

from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import black, red
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from PIL import Image, ImageDraw, ImageFont

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentSigningService:
    """
    Comprehensive document signing service for FIDUS investment management
    Handles PDF viewing, electronic signatures, and document workflow
    """
    
    def __init__(self):
        from path_utils import get_upload_path
        self.upload_directory = get_upload_path("documents")
        self.signed_directory = get_upload_path("signed")
        
        # Create directories if they don't exist
        os.makedirs(self.upload_directory, exist_ok=True)
        os.makedirs(self.signed_directory, exist_ok=True)
        
        logger.info("Document Signing Service initialized")
    
    async def upload_document(self, file_data: bytes, filename: str, mime_type: str, user_id: str) -> Dict:
        """
        Upload document for signing
        
        Args:
            file_data: Document file data
            filename: Original filename
            mime_type: MIME type of the document
            user_id: ID of user uploading the document
            
        Returns:
            Upload result with document information
        """
        try:
            # Generate unique document ID
            document_id = str(uuid.uuid4())
            
            # Create safe filename
            safe_filename = self._create_safe_filename(filename)
            file_path = os.path.join(self.upload_directory, f"{document_id}_{safe_filename}")
            
            # Save file
            with open(file_path, 'wb') as f:
                f.write(file_data)
            
            # Get file info
            file_size = len(file_data)
            
            # If PDF, get page info
            page_count = 0
            if mime_type == 'application/pdf':
                try:
                    pdf_reader = PdfReader(io.BytesIO(file_data))
                    page_count = len(pdf_reader.pages)
                except Exception as e:
                    logger.warning(f"Could not read PDF page count: {str(e)}")
            
            document_info = {
                'document_id': document_id,
                'filename': filename,
                'safe_filename': safe_filename,
                'mime_type': mime_type,
                'file_size': file_size,
                'page_count': page_count,
                'file_path': file_path,
                'uploaded_by': user_id,
                'uploaded_at': datetime.now(timezone.utc),
                'status': 'uploaded',
                'signatures': []
            }
            
            logger.info(f"Document uploaded: {document_id} - {filename}")
            
            return {
                'success': True,
                'document': document_info,
                'message': 'Document uploaded successfully'
            }
            
        except Exception as e:
            logger.error(f"Document upload error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_safe_filename(self, filename: str) -> str:
        """Create a safe filename for storage"""
        # Remove unsafe characters
        safe_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-_"
        safe_filename = ''.join(c for c in filename if c in safe_chars)
        
        # Ensure it's not empty
        if not safe_filename:
            safe_filename = "document.pdf"
        
        return safe_filename
    
    async def get_document_pdf_data(self, document_id: str) -> Dict:
        """
        Get PDF data for viewing
        
        Args:
            document_id: Document identifier
            
        Returns:
            PDF data for frontend viewing
        """
        try:
            # Find document file
            document_files = [f for f in os.listdir(self.upload_directory) if f.startswith(document_id)]
            
            if not document_files:
                return {
                    'success': False,
                    'error': 'Document not found'
                }
            
            file_path = os.path.join(self.upload_directory, document_files[0])
            
            # Read PDF file
            with open(file_path, 'rb') as f:
                pdf_data = f.read()
            
            # Convert to base64 for frontend
            pdf_base64 = base64.b64encode(pdf_data).decode('utf-8')
            
            # Get PDF info
            pdf_reader = PdfReader(io.BytesIO(pdf_data))
            page_count = len(pdf_reader.pages)
            
            return {
                'success': True,
                'document_id': document_id,
                'pdf_data': pdf_base64,
                'page_count': page_count,
                'mime_type': 'application/pdf',
                'filename': document_files[0].split('_', 1)[1] if '_' in document_files[0] else document_files[0]
            }
            
        except Exception as e:
            logger.error(f"Get PDF data error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def add_signature(self, document_id: str, signature_data: Dict, user_info: Dict) -> Dict:
        """
        Add electronic signature to document
        
        Args:
            document_id: Document identifier
            signature_data: Signature information (coordinates, image, etc.)
            user_info: Information about the signer
            
        Returns:
            Signature result
        """
        try:
            # Find document file
            document_files = [f for f in os.listdir(self.upload_directory) if f.startswith(document_id)]
            
            if not document_files:
                return {
                    'success': False,
                    'error': 'Document not found'
                }
            
            source_file = os.path.join(self.upload_directory, document_files[0])
            
            # Generate signed document filename
            signed_filename = f"{document_id}_signed_{int(datetime.now().timestamp())}.pdf"
            signed_file_path = os.path.join(self.signed_directory, signed_filename)
            
            # Create signature
            signature_result = await self._create_signature_pdf(
                source_file,
                signed_file_path,
                signature_data,
                user_info
            )
            
            if signature_result['success']:
                # Store signature info (in production, this would go to database)
                signature_info = {
                    'signature_id': str(uuid.uuid4()),
                    'document_id': document_id,
                    'signer_name': user_info.get('name', 'Unknown'),
                    'signer_email': user_info.get('email', 'unknown@example.com'),
                    'signed_at': datetime.now(timezone.utc),
                    'signature_coordinates': signature_data.get('coordinates', {}),
                    'signed_file_path': signed_file_path,
                    'signed_filename': signed_filename
                }
                
                logger.info(f"Document signed: {document_id} by {user_info.get('email')}")
                
                return {
                    'success': True,
                    'signature': signature_info,
                    'signed_document_url': f'/api/documents/signed/{signed_filename}',
                    'message': 'Document signed successfully'
                }
            else:
                return signature_result
            
        except Exception as e:
            logger.error(f"Add signature error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _create_signature_pdf(self, source_file: str, output_file: str, signature_data: Dict, user_info: Dict) -> Dict:
        """
        Create PDF with signature overlay
        
        Args:
            source_file: Path to source PDF
            output_file: Path for signed PDF
            signature_data: Signature information
            user_info: Signer information
            
        Returns:
            Success/failure result
        """
        try:
            # Read source PDF
            pdf_reader = PdfReader(source_file)
            pdf_writer = PdfWriter()
            
            # Get signature details
            page_number = signature_data.get('page', 1) - 1  # Convert to 0-based index
            x_position = signature_data.get('x', 100)
            y_position = signature_data.get('y', 100)
            signature_text = signature_data.get('text', user_info.get('name', 'Digital Signature'))
            signature_image_data = signature_data.get('image_data')  # Base64 image data
            
            # Process each page
            for page_index, page in enumerate(pdf_reader.pages):
                if page_index == page_number:
                    # Add signature to this page
                    signature_overlay = self._create_signature_overlay(
                        x_position, y_position, signature_text, signature_image_data, user_info
                    )
                    
                    if signature_overlay:
                        page.merge_page(signature_overlay.pages[0])
                
                pdf_writer.add_page(page)
            
            # Write signed PDF
            with open(output_file, 'wb') as output_pdf:
                pdf_writer.write(output_pdf)
            
            return {
                'success': True,
                'message': 'Signature added successfully'
            }
            
        except Exception as e:
            logger.error(f"Create signature PDF error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_signature_overlay(self, x: float, y: float, signature_text: str, image_data: str, user_info: Dict) -> Optional[Any]:
        """
        Create signature overlay for PDF
        
        Args:
            x: X coordinate for signature
            y: Y coordinate for signature  
            signature_text: Text signature
            image_data: Base64 image data (if available)
            user_info: Signer information
            
        Returns:
            PDF overlay with signature
        """
        try:
            # Create temporary PDF for signature overlay
            overlay_buffer = io.BytesIO()
            overlay_canvas = canvas.Canvas(overlay_buffer, pagesize=letter)
            
            if image_data:
                # Use signature image if provided
                try:
                    # Decode base64 image
                    image_bytes = base64.b64decode(image_data)
                    image = Image.open(io.BytesIO(image_bytes))
                    
                    # Save image temporarily
                    temp_image_path = f"/tmp/signature_{uuid.uuid4()}.png"
                    image.save(temp_image_path)
                    
                    # Add image to PDF
                    overlay_canvas.drawImage(temp_image_path, x, y, width=120, height=40)
                    
                    # Clean up temp file
                    os.remove(temp_image_path)
                    
                except Exception as e:
                    logger.warning(f"Could not process signature image: {str(e)}")
                    # Fall back to text signature
                    overlay_canvas.setFont("Helvetica", 12)
                    overlay_canvas.setFillColor(red)
                    overlay_canvas.drawString(x, y, signature_text)
            else:
                # Use text signature
                overlay_canvas.setFont("Helvetica", 12)
                overlay_canvas.setFillColor(red)
                overlay_canvas.drawString(x, y, signature_text)
            
            # Add signature metadata
            overlay_canvas.setFont("Helvetica", 8)
            overlay_canvas.setFillColor(black)
            overlay_canvas.drawString(x, y - 15, f"Signed by: {user_info.get('name', 'Unknown')}")
            overlay_canvas.drawString(x, y - 25, f"Date: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}")
            overlay_canvas.drawString(x, y - 35, f"Email: {user_info.get('email', 'unknown@example.com')}")
            
            overlay_canvas.save()
            overlay_buffer.seek(0)
            
            # Create PDF from overlay
            return PdfReader(overlay_buffer)
            
        except Exception as e:
            logger.error(f"Create signature overlay error: {str(e)}")
            return None
    
    async def get_signed_document(self, filename: str) -> Dict:
        """
        Get signed document for download
        
        Args:
            filename: Signed document filename
            
        Returns:
            Document data
        """
        try:
            file_path = os.path.join(self.signed_directory, filename)
            
            if not os.path.exists(file_path):
                return {
                    'success': False,
                    'error': 'Signed document not found'
                }
            
            with open(file_path, 'rb') as f:
                document_data = f.read()
            
            return {
                'success': True,
                'document_data': document_data,
                'filename': filename,
                'mime_type': 'application/pdf'
            }
            
        except Exception as e:
            logger.error(f"Get signed document error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def send_signed_document_notification(self, google_apis_service, token_data: Dict, document_info: Dict, recipient_email: str) -> Dict:
        """
        Send email notification with signed document
        
        Args:
            google_apis_service: Google APIs service instance
            token_data: OAuth token data
            document_info: Document information
            recipient_email: Email to send notification to
            
        Returns:
            Email send result
        """
        try:
            subject = f"FIDUS Investment Management - Document Signed: {document_info.get('filename', 'Document')}"
            
            body = f"""
Dear Client,

Your document has been successfully signed and is ready for review.

Document Details:
- Filename: {document_info.get('filename', 'N/A')}
- Signed by: {document_info.get('signer_name', 'N/A')}
- Signed on: {document_info.get('signed_at', 'N/A')}

You can access the signed document through your FIDUS client portal or contact our team for assistance.

Best regards,
FIDUS Investment Management Team

---
This is an automated notification from FIDUS Investment Management Platform.
            """
            
            html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="background: linear-gradient(135deg, #1e40af, #06b6d4); padding: 20px; border-radius: 8px; color: white; margin-bottom: 20px;">
            <h2 style="margin: 0;">FIDUS Investment Management</h2>
            <p style="margin: 5px 0 0 0; opacity: 0.9;">Document Signing Notification</p>
        </div>
        
        <p>Dear Client,</p>
        
        <p>Your document has been successfully signed and is ready for review.</p>
        
        <div style="background: #f8fafc; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3 style="margin-top: 0; color: #1e40af;">Document Details:</h3>
            <ul style="list-style: none; padding: 0;">
                <li><strong>Filename:</strong> {document_info.get('filename', 'N/A')}</li>
                <li><strong>Signed by:</strong> {document_info.get('signer_name', 'N/A')}</li>
                <li><strong>Signed on:</strong> {document_info.get('signed_at', 'N/A')}</li>
            </ul>
        </div>
        
        <p>You can access the signed document through your FIDUS client portal or contact our team for assistance.</p>
        
        <p>Best regards,<br>
        <strong>FIDUS Investment Management Team</strong></p>
        
        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
        
        <p style="font-size: 12px; color: #6b7280;">
            This is an automated notification from FIDUS Investment Management Platform.
        </p>
    </div>
</body>
</html>
            """
            
            # Send email using Gmail API
            result = await google_apis_service.send_gmail_message(
                token_data=token_data,
                to=recipient_email,
                subject=subject,
                body=body,
                html_body=html_body
            )
            
            logger.info(f"Document signing notification sent to: {recipient_email}")
            return result
            
        except Exception as e:
            logger.error(f"Send notification error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
document_signing_service = DocumentSigningService()