"""Privacy filter for admin analytics - ensures no PII is exposed"""
import re
import logging
from typing import Dict, List, Any

logger = logging.getLogger(__name__)


class PrivacyFilter:
    """
    Ensures privacy compliance for admin analytics.

    STRICT RULES:
    - NO individual chat content
    - NO student names or emails
    - NO personally identifiable information
    - ONLY aggregated, anonymized data
    """

    # Patterns that might indicate PII
    PII_PATTERNS = [
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
        r'\b\d{10}\b',  # Phone number (10 digits)
        r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Aadhaar-like numbers
    ]

    def __init__(self):
        self.compiled_patterns = [re.compile(p) for p in self.PII_PATTERNS]

    def contains_pii(self, text: str) -> bool:
        """Check if text contains potential PII"""
        for pattern in self.compiled_patterns:
            if pattern.search(text):
                return True
        return False

    def redact_pii(self, text: str) -> str:
        """Redact any potential PII from text"""
        result = text
        for pattern in self.compiled_patterns:
            result = pattern.sub("[REDACTED]", result)
        return result

    def filter_keywords(self, keywords: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filter keywords list to remove any that might be PII.

        Args:
            keywords: List of keyword dicts

        Returns:
            Filtered list
        """
        filtered = []
        for kw in keywords:
            word = kw.get("keyword", "")
            # Skip if it looks like PII or is too specific
            if not self.contains_pii(word) and len(word) <= 20:
                filtered.append(kw)
        return filtered

    def validate_analytics_output(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize analytics output.

        Args:
            data: Analytics data dict

        Returns:
            Sanitized data dict
        """
        # Ensure no individual chat data
        if "individual_chats" in data:
            logger.warning("Attempted to expose individual chat data - blocked")
            del data["individual_chats"]

        if "student_data" in data:
            logger.warning("Attempted to expose student data - blocked")
            del data["student_data"]

        if "chat_content" in data:
            logger.warning("Attempted to expose chat content - blocked")
            del data["chat_content"]

        # Filter keywords for PII
        if "common_keywords" in data:
            data["common_keywords"] = self.filter_keywords(data["common_keywords"])

        return data

    def is_aggregate_only(self, data: Dict[str, Any]) -> bool:
        """
        Verify that data contains only aggregate metrics.

        Args:
            data: Data to check

        Returns:
            True if data is aggregate-only
        """
        forbidden_keys = [
            "individual_chats", "chat_content", "student_data",
            "student_names", "student_emails", "messages"
        ]

        for key in forbidden_keys:
            if key in data:
                return False

        return True
