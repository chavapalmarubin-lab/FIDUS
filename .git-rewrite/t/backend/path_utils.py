"""
Path utilities for production deployment on Render
Handles dynamic path resolution based on environment
"""

import os
from pathlib import Path

def get_base_path() -> str:
    """
    Get the appropriate base path based on environment
    Returns /tmp for Render production, /app for local development
    """
    environment = os.environ.get('ENVIRONMENT', 'development')
    if environment == 'production' or os.environ.get('RENDER'):
        return '/tmp'
    return '/app'

def get_upload_path(subdir: str = '') -> str:
    """
    Get upload directory path
    """
    base = get_base_path()
    if subdir:
        return f"{base}/uploads/{subdir}"
    return f"{base}/uploads"

def get_credentials_path(filename: str) -> str:
    """
    Get credentials file path
    """
    base = get_base_path()
    return f"{base}/{filename}"

def get_backend_path(filename: str = '') -> str:
    """
    Get backend directory path
    """
    base = get_base_path()
    if filename:
        return f"{base}/backend/{filename}"
    return f"{base}/backend"

def ensure_dir_exists(path: str) -> None:
    """
    Ensure directory exists, create if not
    """
    Path(path).mkdir(parents=True, exist_ok=True)