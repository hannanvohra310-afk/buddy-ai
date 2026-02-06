"""
Tests for authentication system.
"""
import pytest


class TestValidators:
    """Tests for auth validators."""

    def test_valid_email_domain(self):
        """Test validation of valid school email domains."""
        from auth.validators import validate_email_domain

        allowed_domains = ["demo.school.com"]
        is_valid, _ = validate_email_domain("student@demo.school.com", allowed_domains)
        assert is_valid is True

    def test_invalid_email_domain(self):
        """Test rejection of invalid email domains."""
        from auth.validators import validate_email_domain

        allowed_domains = ["demo.school.com"]
        invalid_emails = [
            "student@gmail.com",
            "student@yahoo.com",
            "student@hotmail.com",
            "invalid-email",
            "",
        ]

        for email in invalid_emails:
            is_valid, _ = validate_email_domain(email, allowed_domains)
            assert is_valid is False, f"Should reject: {email}"

    def test_password_strength_valid(self):
        """Test validation of strong passwords."""
        from auth.validators import validate_password_strength

        # Note: Requires at least one letter AND one number
        valid_passwords = [
            "SecurePass123",
            "MyP@ssword1",
            "ValidPass99",
            "abcdefg1",  # Minimum: 8 chars, 1 letter, 1 number
        ]

        for password in valid_passwords:
            is_valid, _ = validate_password_strength(password)
            assert is_valid is True, f"Should accept: {password}"

    def test_password_strength_invalid(self):
        """Test rejection of weak passwords."""
        from auth.validators import validate_password_strength

        invalid_passwords = [
            "short",      # Too short
            "1234567",    # 7 chars, need 8
            "12345678",   # No letters
            "abcdefgh",   # No numbers
            "",           # Empty
        ]

        for password in invalid_passwords:
            is_valid, _ = validate_password_strength(password)
            assert is_valid is False, f"Should reject: {password}"


class TestAuthHandler:
    """Tests for AuthHandler class."""

    @pytest.fixture
    def auth_handler(self, temp_db):
        """Create an AuthHandler with temporary database."""
        from auth import AuthHandler
        return AuthHandler(db_path=temp_db)

    def test_register_student(self, auth_handler):
        """Test student registration."""
        result = auth_handler.register_student("test@demo.school.com", 9)
        # register_student returns (success, message) tuple
        success = result[0] if isinstance(result, tuple) else result
        assert success is True

    def test_register_duplicate_student(self, auth_handler):
        """Test that duplicate registration fails."""
        auth_handler.register_student("test@demo.school.com", 9)
        result = auth_handler.register_student("test@demo.school.com", 9)
        # register_student returns (success, message) tuple
        success = result[0] if isinstance(result, tuple) else result
        assert success is False

    def test_check_email_status_unregistered(self, auth_handler):
        """Test email status for unregistered user."""
        status = auth_handler.check_email_status("unknown@demo.school.com")

        assert status["valid_domain"] is True
        assert status["registered"] is False

    def test_check_email_status_registered(self, auth_handler):
        """Test email status for registered user."""
        auth_handler.register_student("test@demo.school.com", 9)
        status = auth_handler.check_email_status("test@demo.school.com")

        assert status["valid_domain"] is True
        assert status["registered"] is True
        assert status["password_set"] is False

    def test_setup_password(self, auth_handler):
        """Test password setup for new user."""
        auth_handler.register_student("test@demo.school.com", 9)
        success, message, token = auth_handler.setup_password("test@demo.school.com", "SecurePass123")

        assert success is True
        assert token is not None
        assert len(token) > 0

    def test_login_success(self, auth_handler):
        """Test successful login."""
        auth_handler.register_student("test@demo.school.com", 9)
        auth_handler.setup_password("test@demo.school.com", "SecurePass123")

        success, message, token = auth_handler.login("test@demo.school.com", "SecurePass123")

        assert success is True
        assert token is not None

    def test_login_wrong_password(self, auth_handler):
        """Test login with wrong password."""
        auth_handler.register_student("test@demo.school.com", 9)
        auth_handler.setup_password("test@demo.school.com", "SecurePass123")

        success, message, token = auth_handler.login("test@demo.school.com", "WrongPassword")

        assert success is False
        assert token is None

    def test_login_unregistered_user(self, auth_handler):
        """Test login for unregistered user."""
        success, message, token = auth_handler.login("unknown@demo.school.com", "AnyPassword")

        assert success is False
        assert token is None


class TestSessionManager:
    """Tests for SessionManager class."""

    @pytest.fixture
    def session_manager(self):
        """Create a SessionManager instance."""
        from auth.session_manager import SessionManager
        return SessionManager()

    def test_create_session(self, session_manager):
        """Test session token creation."""
        token = session_manager.create_session(
            student_id=1,
            email="test@demo.school.com",
            school_id=1,
            grade=9
        )

        assert token is not None
        assert len(token) > 0

    def test_validate_session(self, session_manager):
        """Test session token validation."""
        token = session_manager.create_session(
            student_id=1,
            email="test@demo.school.com",
            school_id=1,
            grade=9
        )

        payload = session_manager.validate_session(token)

        assert payload is not None
        assert payload["student_id"] == 1
        assert payload["email"] == "test@demo.school.com"

    def test_invalid_token(self, session_manager):
        """Test validation of invalid token."""
        payload = session_manager.validate_session("invalid-token-12345")

        assert payload is None

    def test_create_password_reset_token(self, session_manager):
        """Test password reset token creation."""
        token = session_manager.create_password_reset_token(
            student_id=1,
            email="test@demo.school.com"
        )

        assert token is not None
        assert len(token) > 0
