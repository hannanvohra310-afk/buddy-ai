"""Session management for Buddy AI authentication"""
import jwt
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user sessions using JWT tokens"""

    def __init__(self, secret_key: Optional[str] = None, token_expiry_hours: int = 24):
        """
        Initialize session manager.

        Args:
            secret_key: Secret key for JWT signing. If not provided, generates one.
            token_expiry_hours: Hours until token expires (default 24)
        """
        self.secret_key = secret_key or secrets.token_hex(32)
        self.token_expiry_hours = token_expiry_hours
        self.algorithm = "HS256"

    def create_session(self, student_id: int, email: str, school_id: int, grade: int) -> str:
        """
        Create a new session token for a student.

        Args:
            student_id: The student's database ID
            email: The student's email
            school_id: The student's school ID
            grade: The student's grade level

        Returns:
            JWT token string
        """
        expiry = datetime.utcnow() + timedelta(hours=self.token_expiry_hours)

        payload = {
            "student_id": student_id,
            "email": email,
            "school_id": school_id,
            "grade": grade,
            "exp": expiry,
            "iat": datetime.utcnow(),
            "type": "session"
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Session created for student {student_id}")
        return token

    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a session token.

        Args:
            token: The JWT token to validate

        Returns:
            Decoded payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != "session":
                logger.warning("Invalid token type")
                return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.info("Session token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid session token: {e}")
            return None

    def create_password_reset_token(self, student_id: int, email: str) -> str:
        """
        Create a password reset token.

        Args:
            student_id: The student's database ID
            email: The student's email

        Returns:
            JWT token string (expires in 1 hour)
        """
        expiry = datetime.utcnow() + timedelta(hours=1)

        payload = {
            "student_id": student_id,
            "email": email,
            "exp": expiry,
            "iat": datetime.utcnow(),
            "type": "password_reset"
        }

        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        logger.info(f"Password reset token created for student {student_id}")
        return token

    def validate_password_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a password reset token.

        Args:
            token: The JWT token to validate

        Returns:
            Decoded payload if valid, None if invalid
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])

            # Check token type
            if payload.get("type") != "password_reset":
                logger.warning("Invalid token type for password reset")
                return None

            return payload
        except jwt.ExpiredSignatureError:
            logger.info("Password reset token expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid password reset token: {e}")
            return None

    def get_session_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Get session information from a valid token.

        Args:
            token: The JWT token

        Returns:
            Dict with student_id, email, school_id, grade if valid, None otherwise
        """
        payload = self.validate_session(token)
        if payload:
            return {
                "student_id": payload.get("student_id"),
                "email": payload.get("email"),
                "school_id": payload.get("school_id"),
                "grade": payload.get("grade")
            }
        return None
