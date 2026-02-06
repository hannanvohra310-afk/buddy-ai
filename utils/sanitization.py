"""Input sanitization utilities for security"""
import re


def sanitize_input(text: str, max_length: int = 2000) -> str:
    """
    Sanitize user input to prevent injection and clean up text.

    Args:
        text: Raw user input
        max_length: Maximum allowed length (default 2000)

    Returns:
        Cleaned and safe text
    """
    if not text:
        return ""

    # Remove excessive whitespace
    text = " ".join(text.split())

    # Limit length to prevent abuse
    if len(text) > max_length:
        text = text[:max_length] + "..."

    # Remove potential script tags (basic XSS prevention for display)
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags

    return text.strip()
