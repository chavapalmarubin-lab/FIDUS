"""
KYC Document Upload Routes for FIDUS App
==========================================
Allows users to upload identity documents (passport, ID) and proof of
residence (utility bill) through the FIDUS app.  Documents are stored
locally and an admin panel lets FIDUS staff download them for manual
submission to Lucrum.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import FileResponse
from datetime import datetime
from pathlib import Path
from typing import Optional
import shutil
import uuid as uuid_lib
import logging
import os

logger = logging.getLogger(__name__)

kyc_router = APIRouter(prefix="/kyc")

# Upload directory
UPLOAD_DIR = Path(__file__).parent / "kyc_uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

# Allowed document types
DOC_TYPES = {"id_document", "proof_of_residence"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf", ".heic", ".webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


async def _get_db():
    """Import db from server module."""
    from server import db
    return db


async def _get_current_user_from_token(token: str):
    """Validate token and return user."""
    from server import db, User
    session = await db.sessions.find_one({"token": token})
    if not session:
        return None
    user_data = await db.users.find_one({"id": session["user_id"]})
    if not user_data:
        return None
    return User(**user_data)


# ------------------------------------------------------------------ #
#  Upload Document
# ------------------------------------------------------------------ #

@kyc_router.post("/upload")
async def upload_kyc_document(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    token: str = Form(...),
):
    """
    Upload a KYC document (ID or proof of residence).
    Accepts image files (JPG, PNG, HEIC, WEBP) and PDF.
    Max size: 10 MB.
    """
    # Auth
    user = await _get_current_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    # Validate doc_type
    if doc_type not in DOC_TYPES:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid document type. Must be one of: {', '.join(DOC_TYPES)}",
        )

    # Validate file extension
    filename = file.filename or "document"
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=422,
            detail=f"File type not allowed. Accepted: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Read and validate size
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=422, detail="File too large. Maximum 10 MB.")

    # Create user directory
    user_dir = UPLOAD_DIR / user.id
    user_dir.mkdir(exist_ok=True)

    # Save file with unique name
    file_id = str(uuid_lib.uuid4())[:8]
    safe_name = f"{doc_type}_{file_id}{ext}"
    file_path = user_dir / safe_name

    with open(file_path, "wb") as f:
        f.write(contents)

    # Store metadata in MongoDB
    db = await _get_db()
    doc_record = {
        "id": str(uuid_lib.uuid4()),
        "user_id": user.id,
        "user_email": user.email,
        "user_name": user.name,
        "doc_type": doc_type,
        "original_filename": filename,
        "stored_filename": safe_name,
        "file_size": len(contents),
        "file_extension": ext,
        "status": "pending_review",
        "uploaded_at": datetime.utcnow().isoformat(),
        "reviewed_at": None,
        "reviewed_by": None,
        "notes": None,
    }

    # Upsert: replace previous document of same type for same user
    await db.kyc_documents.delete_many({"user_id": user.id, "doc_type": doc_type})
    await db.kyc_documents.insert_one(doc_record)

    logger.info(f"KYC document uploaded: {user.email} / {doc_type} / {safe_name} ({len(contents)} bytes)")

    return {
        "success": True,
        "message": f"Document uploaded successfully",
        "document": {
            "id": doc_record["id"],
            "doc_type": doc_type,
            "filename": filename,
            "size": len(contents),
            "status": "pending_review",
            "uploaded_at": doc_record["uploaded_at"],
        },
    }


# ------------------------------------------------------------------ #
#  Get User's KYC Documents Status
# ------------------------------------------------------------------ #

@kyc_router.get("/status")
async def get_kyc_status(token: str):
    """Get the KYC document upload status for the current user."""
    user = await _get_current_user_from_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    db = await _get_db()
    docs = await db.kyc_documents.find({"user_id": user.id}).to_list(10)

    documents = {}
    for doc in docs:
        documents[doc["doc_type"]] = {
            "id": doc["id"],
            "doc_type": doc["doc_type"],
            "original_filename": doc["original_filename"],
            "status": doc["status"],
            "uploaded_at": doc["uploaded_at"],
            "file_size": doc["file_size"],
        }

    return {
        "user_id": user.id,
        "user_email": user.email,
        "documents": documents,
        "id_document_uploaded": "id_document" in documents,
        "proof_of_residence_uploaded": "proof_of_residence" in documents,
        "all_uploaded": "id_document" in documents and "proof_of_residence" in documents,
    }


# ------------------------------------------------------------------ #
#  Admin: List All Pending KYC Documents
# ------------------------------------------------------------------ #

@kyc_router.get("/admin/pending")
async def admin_list_pending_documents():
    """
    Admin endpoint: List all pending KYC document submissions.
    Returns grouped by user with document details.
    """
    db = await _get_db()
    docs = await db.kyc_documents.find({}).sort("uploaded_at", -1).to_list(200)

    # Group by user
    users_map = {}
    for doc in docs:
        uid = doc["user_id"]
        if uid not in users_map:
            users_map[uid] = {
                "user_id": uid,
                "user_email": doc.get("user_email", ""),
                "user_name": doc.get("user_name", ""),
                "documents": [],
            }
        users_map[uid]["documents"].append({
            "id": doc["id"],
            "doc_type": doc["doc_type"],
            "original_filename": doc["original_filename"],
            "status": doc["status"],
            "uploaded_at": doc["uploaded_at"],
            "file_size": doc["file_size"],
            "file_extension": doc["file_extension"],
        })

    return {
        "total_users": len(users_map),
        "total_documents": len(docs),
        "users": list(users_map.values()),
    }


# ------------------------------------------------------------------ #
#  Admin: Download a KYC Document
# ------------------------------------------------------------------ #

@kyc_router.get("/admin/download/{user_id}/{doc_type}")
async def admin_download_document(user_id: str, doc_type: str):
    """
    Admin endpoint: Download a user's KYC document.
    """
    if doc_type not in DOC_TYPES:
        raise HTTPException(status_code=422, detail="Invalid document type")

    db = await _get_db()
    doc = await db.kyc_documents.find_one({"user_id": user_id, "doc_type": doc_type})
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    file_path = UPLOAD_DIR / user_id / doc["stored_filename"]
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found on disk")

    return FileResponse(
        path=str(file_path),
        filename=doc["original_filename"],
        media_type="application/octet-stream",
    )


# ------------------------------------------------------------------ #
#  Admin: Update Document Status
# ------------------------------------------------------------------ #

@kyc_router.post("/admin/review/{document_id}")
async def admin_review_document(
    document_id: str,
    status: str = Form(...),
    notes: Optional[str] = Form(None),
):
    """
    Admin endpoint: Update document review status.
    Status values: pending_review, submitted_to_lucrum, approved, rejected
    """
    valid_statuses = {"pending_review", "submitted_to_lucrum", "approved", "rejected"}
    if status not in valid_statuses:
        raise HTTPException(status_code=422, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    db = await _get_db()
    result = await db.kyc_documents.update_one(
        {"id": document_id},
        {"$set": {
            "status": status,
            "notes": notes,
            "reviewed_at": datetime.utcnow().isoformat(),
        }},
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    return {"success": True, "message": f"Document status updated to: {status}"}
