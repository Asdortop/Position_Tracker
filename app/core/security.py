"""
Security utilities for the Position Tracker API.
"""
import secrets
from typing import Optional


def generate_secret_key() -> str:
    """
    Generate a secure secret key for JWT tokens.
    
    Returns:
        A secure random string
    """
    return secrets.token_urlsafe(32)


def hash_password(password: str) -> str:
    """
    Hash a password using a secure method.
    
    Args:
        password: The plain text password
        
    Returns:
        Hashed password
    """
    # This is a placeholder - implement proper password hashing
    # For production, use bcrypt or similar
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        password: The plain text password
        hashed: The hashed password
        
    Returns:
        True if password matches, False otherwise
    """
    return hash_password(password) == hashed
