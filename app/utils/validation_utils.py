"""
Data validation utilities for the Position Tracker API.
"""
from decimal import Decimal
from typing import Any, Optional


def validate_positive_decimal(value: Any, field_name: str) -> Decimal:
    """
    Validate that a value is a positive decimal.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error messages
        
    Returns:
        Validated decimal value
        
    Raises:
        ValueError: If value is not positive
    """
    try:
        decimal_value = Decimal(str(value))
        if decimal_value <= 0:
            raise ValueError(f"{field_name} must be positive, got {value}")
        return decimal_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid {field_name}: {value}") from e


def validate_quantity(value: Any) -> Decimal:
    """
    Validate quantity value.
    
    Args:
        value: The quantity value to validate
        
    Returns:
        Validated quantity as Decimal
    """
    return validate_positive_decimal(value, "quantity")


def validate_price(value: Any) -> Decimal:
    """
    Validate price value.
    
    Args:
        value: The price value to validate
        
    Returns:
        Validated price as Decimal
    """
    return validate_positive_decimal(value, "price")


def validate_charges(value: Any) -> Decimal:
    """
    Validate charges value (can be zero or positive).
    
    Args:
        value: The charges value to validate
        
    Returns:
        Validated charges as Decimal
    """
    try:
        decimal_value = Decimal(str(value))
        if decimal_value < 0:
            raise ValueError(f"Charges must be non-negative, got {value}")
        return decimal_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid charges: {value}") from e


def validate_user_id(user_id: Any) -> int:
    """
    Validate user ID.
    
    Args:
        user_id: The user ID to validate
        
    Returns:
        Validated user ID as int
    """
    try:
        int_value = int(user_id)
        if int_value <= 0:
            raise ValueError(f"User ID must be positive, got {user_id}")
        return int_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid user ID: {user_id}") from e


def validate_security_id(security_id: Any) -> int:
    """
    Validate security ID.
    
    Args:
        security_id: The security ID to validate
        
    Returns:
        Validated security ID as int
    """
    try:
        int_value = int(security_id)
        if int_value <= 0:
            raise ValueError(f"Security ID must be positive, got {security_id}")
        return int_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid security ID: {security_id}") from e
