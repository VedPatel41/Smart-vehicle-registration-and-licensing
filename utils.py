"""
Utility Functions Module
Contains helper functions for ID generation, validation, etc.
"""

import random
import string
import re
from datetime import datetime, timedelta

def validate_gujarat_plate(number_plate): 
    """
    Validates Gujarat (GJ) vehicle number plate
    Format examples:
    GJ01AB1234
    GJ5CD6789
    """
    pattern = r'^GJ\d{1,2}[A-Z]{1,2}\d{4}$'
    return re.match(pattern, number_plate) is not None


def generate_random_id(prefix, length=8):
    """
    Generates a random ID with given prefix
    Args:
        prefix: String prefix for the ID (e.g., 'USR', 'OFF', 'VEH')
        length: Length of random part (default: 8)
    Returns: Generated ID string
    """
    random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
    return f"{prefix}{random_part}"


def validate_email(email):
    """
    Validates email format using regex
    Args:
        email: Email string to validate
    Returns: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_password(password):
    """
    Validates password strength
    Requirements: At least 6 characters
    Args:
        password: Password string to validate
    Returns: True if valid, False otherwise
    """
    return len(password) >= 6


    
def get_future_date(years=1):
    """   
    Gets a future date (for license/insurance expiry)
    Args:
        years: Number of years to add (default: 1)
    Returns: Date string in YYYY-MM-DD format
    """
    future_date = datetime.now() + timedelta(days=years * 365)
    return future_date.strftime('%Y-%m-%d')


def format_date(date_str):
    """
    Formats date string for display
    Args:
        date_str: Date string in YYYY-MM-DD format
    Returns: Formatted date string
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
        return date_obj.strftime('%d-%m-%Y')
    except:
        return date_str
