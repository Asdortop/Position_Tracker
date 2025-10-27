"""
Date and time utility functions for the Position Tracker API.
"""
from datetime import datetime, timezone
from typing import Optional


def ensure_timezone_naive(dt: datetime) -> datetime:
    """
    Ensure a datetime object is timezone-naive by removing timezone info.
    
    Args:
        dt: The datetime object to process
        
    Returns:
        A timezone-naive datetime object
    """
    if dt.tzinfo is not None:
        return dt.replace(tzinfo=None)
    return dt


def ensure_timezone_aware(dt: datetime) -> datetime:
    """
    Ensure a datetime object is timezone-aware by adding UTC timezone.
    
    Args:
        dt: The datetime object to process
        
    Returns:
        A timezone-aware datetime object
    """
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def get_current_utc_time() -> datetime:
    """
    Get the current UTC time.
    
    Returns:
        Current UTC datetime
    """
    return datetime.now(timezone.utc)


def format_datetime_for_api(dt: datetime) -> str:
    """
    Format datetime for API responses.
    
    Args:
        dt: The datetime object to format
        
    Returns:
        ISO formatted datetime string
    """
    return dt.isoformat()
