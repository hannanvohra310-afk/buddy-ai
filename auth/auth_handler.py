"""Authentication handler for Buddy AI"""
import bcrypt
import logging
from typing import Optional, Tuple, Dict, Any
from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from .session_manager import SessionManager
from .validators import validate_email_domain, validate_password_strength, validate_grade

logger = logging.getLogger(__name__)

Base = declarative_base()


class School(Base):
    """School model"""
    __tablename__ = 'schools'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    email_domain = Column(String(255), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("Student", back_populates="school")


class Student(Base):
    """Student model"""
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for first-time setup
    school_id = Column(Integer, ForeignKey('schools.id'), nullable=False)
    grade = Column(Integer, nullable=False)
    is_active = Column(Boolean, default=True)
    password_set = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    school = relationship("School", back_populates="students")


class AuthHandler:
    """Handles authentication operations"""

    def __init__(self, db_path: str = "data/buddy_ai.db", secret_key: Optional[str] = None):
        """
        Initialize authentication handler.

        Args:
            db_path: Path to SQLite database file
            secret_key: Secret key for session management
        """
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.db_session = Session()

        self.session_manager = SessionManager(secret_key=secret_key)

        # Initialize with a default school if none exists
        self._ensure_default_school()

    def _ensure_default_school(self):
        """Ensure at least one school exists for testing"""
        if self.db_session.query(School).count() == 0:
            # Add a default demo school
            demo_school = School(
                name="Demo School",
                email_domain="demo.school.com"
            )
            self.db_session.add(demo_school)
            self.db_session.commit()
            logger.info("Created default demo school")

    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')

    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

    def get_allowed_domains(self) -> list[str]:
        """Get list of allowed email domains from registered schools"""
        schools = self.db_session.query(School).all()
        return [school.email_domain for school in schools]

    def add_school(self, name: str, email_domain: str) -> Optional[School]:
        """
        Add a new school.

        Args:
            name: School name
            email_domain: Email domain for the school

        Returns:
            School object if created, None if domain already exists
        """
        # Check if domain already exists
        existing = self.db_session.query(School).filter_by(email_domain=email_domain).first()
        if existing:
            logger.warning(f"School with domain {email_domain} already exists")
            return None

        school = School(name=name, email_domain=email_domain)
        self.db_session.add(school)
        self.db_session.commit()
        logger.info(f"Added school: {name} ({email_domain})")
        return school

    def register_student(self, email: str, grade: int) -> Tuple[bool, str]:
        """
        Register a new student (admin function).

        Args:
            email: Student's school email
            grade: Student's grade (8, 9, or 10)

        Returns:
            Tuple of (success, message)
        """
        # Validate email domain
        allowed_domains = self.get_allowed_domains()
        is_valid, error = validate_email_domain(email, allowed_domains)
        if not is_valid:
            return False, error

        # Validate grade
        is_valid, error = validate_grade(grade)
        if not is_valid:
            return False, error

        # Check if student already exists
        existing = self.db_session.query(Student).filter_by(email=email.lower()).first()
        if existing:
            return False, "This email is already registered"

        # Get school from email domain
        domain = email.split('@')[1].lower()
        school = self.db_session.query(School).filter_by(email_domain=domain).first()

        if not school:
            return False, "School not found for this email domain"

        # Create student
        student = Student(
            email=email.lower(),
            school_id=school.id,
            grade=grade,
            password_set=False
        )

        self.db_session.add(student)
        self.db_session.commit()
        logger.info(f"Registered student: {email}")

        return True, "Registration successful! Please set your password to continue."

    def setup_password(self, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Set up password for first-time login.

        Args:
            email: Student's email
            password: New password

        Returns:
            Tuple of (success, message, session_token)
        """
        # Find student
        student = self.db_session.query(Student).filter_by(email=email.lower()).first()

        if not student:
            return False, "Student not found. Please contact your school administrator.", None

        if student.password_set:
            return False, "Password already set. Please use login instead.", None

        # Validate password
        is_valid, error = validate_password_strength(password)
        if not is_valid:
            return False, error, None

        # Set password
        student.password_hash = self._hash_password(password)
        student.password_set = True
        student.last_login = datetime.utcnow()
        self.db_session.commit()

        # Create session
        token = self.session_manager.create_session(
            student_id=student.id,
            email=student.email,
            school_id=student.school_id,
            grade=student.grade
        )

        logger.info(f"Password set for student: {email}")
        return True, "Password set successfully!", token

    def login(self, email: str, password: str) -> Tuple[bool, str, Optional[str]]:
        """
        Login a student.

        Args:
            email: Student's email
            password: Student's password

        Returns:
            Tuple of (success, message, session_token)
        """
        # Find student
        student = self.db_session.query(Student).filter_by(email=email.lower()).first()

        if not student:
            return False, "Invalid email or password", None

        if not student.is_active:
            return False, "Account is inactive. Please contact your school administrator.", None

        if not student.password_set:
            return False, "Please set your password first", None

        # Verify password
        if not self._verify_password(password, student.password_hash):
            return False, "Invalid email or password", None

        # Update last login
        student.last_login = datetime.utcnow()
        self.db_session.commit()

        # Create session
        token = self.session_manager.create_session(
            student_id=student.id,
            email=student.email,
            school_id=student.school_id,
            grade=student.grade
        )

        logger.info(f"Student logged in: {email}")
        return True, "Login successful!", token

    def check_email_status(self, email: str) -> Dict[str, Any]:
        """
        Check the status of an email address.

        Args:
            email: Email to check

        Returns:
            Dict with status information
        """
        # Validate email domain first
        allowed_domains = self.get_allowed_domains()
        is_valid, error = validate_email_domain(email, allowed_domains)

        if not is_valid:
            return {
                "valid_domain": False,
                "registered": False,
                "password_set": False,
                "message": error
            }

        # Check if student exists
        student = self.db_session.query(Student).filter_by(email=email.lower()).first()

        if not student:
            return {
                "valid_domain": True,
                "registered": False,
                "password_set": False,
                "message": "Email not registered. Please contact your school administrator."
            }

        return {
            "valid_domain": True,
            "registered": True,
            "password_set": student.password_set,
            "message": "Set your password" if not student.password_set else "Enter your password"
        }

    def request_password_reset(self, email: str) -> Tuple[bool, str, Optional[str]]:
        """
        Request a password reset token.

        Args:
            email: Student's email

        Returns:
            Tuple of (success, message, reset_token)
        """
        student = self.db_session.query(Student).filter_by(email=email.lower()).first()

        if not student:
            # Don't reveal if email exists
            return True, "If this email is registered, you will receive a reset link.", None

        if not student.password_set:
            return False, "Please set your password first using the signup page.", None

        # Generate reset token
        token = self.session_manager.create_password_reset_token(
            student_id=student.id,
            email=student.email
        )

        logger.info(f"Password reset requested for: {email}")
        # In production, send this token via email
        return True, "Password reset link generated!", token

    def reset_password(self, token: str, new_password: str) -> Tuple[bool, str]:
        """
        Reset password using a reset token.

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            Tuple of (success, message)
        """
        # Validate token
        payload = self.session_manager.validate_password_reset_token(token)

        if not payload:
            return False, "Invalid or expired reset link. Please request a new one."

        # Validate new password
        is_valid, error = validate_password_strength(new_password)
        if not is_valid:
            return False, error

        # Find and update student
        student = self.db_session.query(Student).filter_by(id=payload["student_id"]).first()

        if not student:
            return False, "Student not found"

        student.password_hash = self._hash_password(new_password)
        self.db_session.commit()

        logger.info(f"Password reset successful for: {student.email}")
        return True, "Password reset successful! You can now login."

    def validate_session(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate a session token.

        Args:
            token: Session token to validate

        Returns:
            Session info if valid, None otherwise
        """
        return self.session_manager.get_session_info(token)

    def get_student_by_id(self, student_id: int) -> Optional[Student]:
        """Get a student by their ID"""
        return self.db_session.query(Student).filter_by(id=student_id).first()

    def close(self):
        """Close database connection"""
        self.db_session.close()
