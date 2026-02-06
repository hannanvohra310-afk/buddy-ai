"""Login page for Buddy AI"""
import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from auth import AuthHandler

# Page config
st.set_page_config(
    page_title="Login - Buddy AI",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Initialize auth handler
@st.cache_resource
def get_auth_handler():
    return AuthHandler(db_path=str(parent_dir / "data" / "buddy_ai.db"))

auth_handler = get_auth_handler()

# Custom CSS matching the main app style
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');

    #MainMenu, footer, header {display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}

    .stApp {
        background: #F3F4F6 !important;
    }

    .login-container {
        max-width: 400px;
        margin: 60px auto;
        padding: 40px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }

    .login-header {
        text-align: center;
        margin-bottom: 30px;
    }

    .login-logo {
        font-size: 3rem;
        margin-bottom: 12px;
    }

    .login-title {
        font-family: 'Lora', serif !important;
        font-size: 1.8rem;
        font-weight: 600;
        color: #004aad;
        margin-bottom: 8px;
    }

    .login-subtitle {
        font-family: 'Inter', sans-serif;
        color: #6B7280;
        font-size: 0.95rem;
    }

    .stTextInput > div > div > input {
        border-radius: 10px !important;
        border: 1px solid #E5E7EB !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #004aad !important;
        box-shadow: 0 0 0 3px rgba(0, 74, 173, 0.1) !important;
    }

    .stButton > button {
        width: 100%;
        background: #004aad !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 12px 24px !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        margin-top: 10px !important;
    }

    .stButton > button:hover {
        background: #003a8c !important;
    }

    .link-text {
        text-align: center;
        margin-top: 20px;
        font-size: 0.9rem;
        color: #6B7280;
    }

    .link-text a {
        color: #004aad;
        text-decoration: none;
        font-weight: 500;
    }

    .link-text a:hover {
        text-decoration: underline;
    }

    .error-message {
        background: #FEE2E2;
        color: #991B1B;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }

    .success-message {
        background: #D1FAE5;
        color: #065F46;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }

    .info-message {
        background: #DBEAFE;
        color: #1E40AF;
        padding: 12px 16px;
        border-radius: 8px;
        margin-bottom: 16px;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "login_step" not in st.session_state:
    st.session_state.login_step = "email"  # email, password, setup_password
if "login_email" not in st.session_state:
    st.session_state.login_email = ""
if "login_message" not in st.session_state:
    st.session_state.login_message = None
if "login_message_type" not in st.session_state:
    st.session_state.login_message_type = None

# Check if already logged in
if st.session_state.get("authenticated"):
    st.switch_page("app.py")

# Login container
st.markdown('<div class="login-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="login-header">
    <div class="login-logo">🎓</div>
    <div class="login-title">Buddy AI</div>
    <div class="login-subtitle">Your friendly career guide</div>
</div>
""", unsafe_allow_html=True)

# Show messages
if st.session_state.login_message:
    msg_type = st.session_state.login_message_type
    if msg_type == "error":
        st.markdown(f'<div class="error-message">{st.session_state.login_message}</div>', unsafe_allow_html=True)
    elif msg_type == "success":
        st.markdown(f'<div class="success-message">{st.session_state.login_message}</div>', unsafe_allow_html=True)
    elif msg_type == "info":
        st.markdown(f'<div class="info-message">{st.session_state.login_message}</div>', unsafe_allow_html=True)

# Step 1: Email entry
if st.session_state.login_step == "email":
    email = st.text_input("School Email", placeholder="your.name@school.edu", key="email_input")

    if st.button("Continue", key="continue_btn"):
        if email:
            email = email.strip().lower()
            status = auth_handler.check_email_status(email)

            if not status["valid_domain"]:
                st.session_state.login_message = status["message"]
                st.session_state.login_message_type = "error"
            elif not status["registered"]:
                st.session_state.login_message = status["message"]
                st.session_state.login_message_type = "error"
            else:
                st.session_state.login_email = email
                st.session_state.login_message = None
                if status["password_set"]:
                    st.session_state.login_step = "password"
                else:
                    st.session_state.login_step = "setup_password"
            st.rerun()
        else:
            st.session_state.login_message = "Please enter your email"
            st.session_state.login_message_type = "error"
            st.rerun()

# Step 2: Password entry (returning user)
elif st.session_state.login_step == "password":
    st.markdown(f'<p style="color: #6B7280; margin-bottom: 16px;">Logging in as <strong>{st.session_state.login_email}</strong></p>', unsafe_allow_html=True)

    password = st.text_input("Password", type="password", placeholder="Enter your password", key="password_input")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back", key="back_btn"):
            st.session_state.login_step = "email"
            st.session_state.login_message = None
            st.rerun()
    with col2:
        if st.button("Login", key="login_btn"):
            if password:
                success, message, token = auth_handler.login(st.session_state.login_email, password)

                if success:
                    from datetime import datetime
                    # Store session
                    st.session_state.authenticated = True
                    st.session_state.session_token = token
                    st.session_state.user_email = st.session_state.login_email
                    st.session_state.session_created_at = datetime.now().isoformat()

                    # Get user info
                    user_info = auth_handler.validate_session(token)
                    if user_info:
                        st.session_state.student_id = user_info["student_id"]
                        st.session_state.school_id = user_info["school_id"]
                        st.session_state.grade = user_info["grade"]

                    # Clear login state
                    st.session_state.login_step = "email"
                    st.session_state.login_email = ""
                    st.session_state.login_message = None

                    st.switch_page("app.py")
                else:
                    st.session_state.login_message = message
                    st.session_state.login_message_type = "error"
                    st.rerun()
            else:
                st.session_state.login_message = "Please enter your password"
                st.session_state.login_message_type = "error"
                st.rerun()

    st.markdown('<div class="link-text"><a href="forgot_password">Forgot password?</a></div>', unsafe_allow_html=True)

# Step 3: Set up password (first-time user)
elif st.session_state.login_step == "setup_password":
    st.markdown(f'<p style="color: #6B7280; margin-bottom: 8px;">Setting up account for <strong>{st.session_state.login_email}</strong></p>', unsafe_allow_html=True)
    st.markdown('<div class="info-message">Create a password to complete your account setup.</div>', unsafe_allow_html=True)

    password = st.text_input("Create Password", type="password", placeholder="At least 8 characters", key="new_password")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="confirm_password")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back", key="back_setup_btn"):
            st.session_state.login_step = "email"
            st.session_state.login_message = None
            st.rerun()
    with col2:
        if st.button("Set Password", key="setup_btn"):
            if not password:
                st.session_state.login_message = "Please enter a password"
                st.session_state.login_message_type = "error"
            elif password != confirm_password:
                st.session_state.login_message = "Passwords don't match"
                st.session_state.login_message_type = "error"
            else:
                success, message, token = auth_handler.setup_password(st.session_state.login_email, password)

                if success:
                    from datetime import datetime
                    # Store session
                    st.session_state.authenticated = True
                    st.session_state.session_token = token
                    st.session_state.user_email = st.session_state.login_email
                    st.session_state.session_created_at = datetime.now().isoformat()

                    # Get user info
                    user_info = auth_handler.validate_session(token)
                    if user_info:
                        st.session_state.student_id = user_info["student_id"]
                        st.session_state.school_id = user_info["school_id"]
                        st.session_state.grade = user_info["grade"]

                    # Clear login state
                    st.session_state.login_step = "email"
                    st.session_state.login_email = ""
                    st.session_state.login_message = None

                    st.switch_page("app.py")
                else:
                    st.session_state.login_message = message
                    st.session_state.login_message_type = "error"

            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Footer help text
st.markdown("""
<div style="text-align: center; margin-top: 24px; color: #9CA3AF; font-size: 0.85rem;">
    Need help? Contact your school administrator
</div>
""", unsafe_allow_html=True)
