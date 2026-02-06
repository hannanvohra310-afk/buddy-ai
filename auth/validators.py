"""Validation utilities for authentication"""
import re
from typing import Tuple, Optional


def validate_email_domain(email: str, allowed_domains: list[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that email belongs to an allowed school domain.

    Args:
        email: The email address to validate
        allowed_domains: List of allowed email domains (e.g., ['school.edu', 'academy.org'])

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "Email is required"

    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False, "Please enter a valid email address"

    # Extract domain from email
    try:
        domain = email.split('@')[1].lower()
    except IndexError:
        return False, "Invalid email format"

    # Check if domain is allowed
    allowed_domains_lower = [d.lower() for d in allowed_domains]
    if domain not in allowed_domains_lower:
        return False, "Please use your school email address"

    return True, None


def validate_password_strength(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password meets minimum requirements.

    Requirements:
    - At least 8 characters
    - At least one letter
    - At least one number

    Args:
        password: The password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"

    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.search(r'[a-zA-Z]', password):
        return False, "Password must contain at least one letter"

    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"

    return True, None


def validate_grade(grade: int) -> Tuple[bool, Optional[str]]:
    """
    Validate that grade is within allowed range (8-10).

    Args:
        grade: The grade level

    Returns:
        Tuple of (is_valid, error_message)
    """
    if grade not in [8, 9, 10]:
        return False, "Grade must be 8, 9, or 10"

    return True, None


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.

    Args:
        text: The input text to sanitize

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove any HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # Escape special characters
    text = text.strip()

    return text
