"""
Age verification utilities for legal compliance
Handles country-specific minimum age requirements
"""

from datetime import date, datetime
from typing import Dict, Optional

# Country-specific legal age requirements for adult content/services
LEGAL_AGES = {
    # Most countries default to 18
    "US": 18,  # United States
    "CA": 18,  # Canada  
    "GB": 18,  # United Kingdom
    "DE": 18,  # Germany
    "FR": 18,  # France
    "IT": 18,  # Italy
    "ES": 18,  # Spain
    "AU": 18,  # Australia
    "BR": 18,  # Brazil
    "MX": 18,  # Mexico
    "JP": 18,  # Japan (20 for many things, but 18 for this platform)
    "KR": 19,  # South Korea (19 is adult age)
    "CN": 18,  # China
    "IN": 18,  # India
    "RU": 18,  # Russia
    "ZA": 18,  # South Africa
    "OTHER": 18,  # Default for all other countries
}


def get_legal_age(country_code: str) -> int:
    """Get the legal age requirement for a country"""
    return LEGAL_AGES.get(country_code.upper(), 18)


def calculate_age(birth_date: date) -> int:
    """Calculate current age from birth date"""
    today = date.today()
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
        
    return age


def is_legal_age(birth_date: date, country_code: str) -> bool:
    """Check if user meets legal age requirement for their country"""
    required_age = get_legal_age(country_code)
    current_age = calculate_age(birth_date)
    return current_age >= required_age


def validate_birth_date(birth_date_str: str, country_code: str) -> Dict[str, any]:
    """
    Validate birth date string and check legal age compliance
    
    Returns:
        Dict with 'valid', 'age', 'legal_age', 'required_age', 'error_message'
    """
    try:
        # Parse date string
        if isinstance(birth_date_str, str):
            birth_date = datetime.strptime(birth_date_str, "%Y-%m-%d").date()
        else:
            birth_date = birth_date_str
    except (ValueError, TypeError):
        return {
            "valid": False,
            "error_message": "Invalid birth date format. Use YYYY-MM-DD format."
        }
    
    # Check if date is in the future
    if birth_date > date.today():
        return {
            "valid": False,
            "error_message": "Birth date cannot be in the future."
        }
    
    # Check if date is reasonable (not too old)
    current_age = calculate_age(birth_date)
    if current_age > 120:
        return {
            "valid": False,
            "error_message": "Please enter a valid birth date."
        }
    
    # Check legal age requirement
    required_age = get_legal_age(country_code)
    is_legal = current_age >= required_age
    
    return {
        "valid": True,
        "age": current_age,
        "legal_age": is_legal,
        "required_age": required_age,
        "error_message": None if is_legal else f"You must be at least {required_age} years old to use this platform in {country_code}."
    }


def get_country_age_info(country_code: str) -> Dict[str, any]:
    """Get age requirement information for a country"""
    required_age = get_legal_age(country_code)
    return {
        "country_code": country_code.upper(),
        "required_age": required_age,
        "description": f"Legal age requirement for {country_code}: {required_age} years"
    }