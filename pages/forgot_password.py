"""Forgot password page for Buddy AI"""
import streamlit as st
from pathlib import Path
import sys

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from auth import AuthHandler

# Page config
st.set_page_config(
    page_title="Reset Password - Buddy AI",
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

    .reset-container {
        max-width: 400px;
        margin: 60px auto;
        padding: 40px;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.1);
    }

    .reset-header {
        text-align: center;
        margin-bottom: 30px;
    }

    .reset-logo {
        font-size: 3rem;
        margin-bottom: 12px;
    }

    .reset-title {
        font-family: 'Lora', serif !important;
        font-size: 1.5rem;
        font-weight: 600;
        color: #004aad;
        margin-bottom: 8px;
    }

    .reset-subtitle {
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
if "reset_step" not in st.session_state:
    st.session_state.reset_step = "email"  # email, token, new_password
if "reset_email" not in st.session_state:
    st.session_state.reset_email = ""
if "reset_token" not in st.session_state:
    st.session_state.reset_token = ""
if "reset_message" not in st.session_state:
    st.session_state.reset_message = None
if "reset_message_type" not in st.session_state:
    st.session_state.reset_message_type = None

# Reset container
st.markdown('<div class="reset-container">', unsafe_allow_html=True)

# Header
st.markdown("""
<div class="reset-header">
    <div class="reset-logo">🔐</div>
    <div class="reset-title">Reset Password</div>
    <div class="reset-subtitle">We'll help you get back in</div>
</div>
""", unsafe_allow_html=True)

# Show messages
if st.session_state.reset_message:
    msg_type = st.session_state.reset_message_type
    if msg_type == "error":
        st.markdown(f'<div class="error-message">{st.session_state.reset_message}</div>', unsafe_allow_html=True)
    elif msg_type == "success":
        st.markdown(f'<div class="success-message">{st.session_state.reset_message}</div>', unsafe_allow_html=True)
    elif msg_type == "info":
        st.markdown(f'<div class="info-message">{st.session_state.reset_message}</div>', unsafe_allow_html=True)

# Step 1: Email entry
if st.session_state.reset_step == "email":
    st.markdown('<div class="info-message">Enter your school email and we\'ll help you reset your password.</div>', unsafe_allow_html=True)

    email = st.text_input("School Email", placeholder="your.name@school.edu", key="reset_email_input")

    if st.button("Request Reset", key="request_btn"):
        if email:
            email = email.strip().lower()
            success, message, token = auth_handler.request_password_reset(email)

            if success and token:
                st.session_state.reset_email = email
                st.session_state.reset_token = token
                st.session_state.reset_step = "new_password"
                st.session_state.reset_message = "You can now set a new password."
                st.session_state.reset_message_type = "success"
            elif success:
                # Email not found but we don't reveal that
                st.session_state.reset_message = message
                st.session_state.reset_message_type = "info"
            else:
                st.session_state.reset_message = message
                st.session_state.reset_message_type = "error"
            st.rerun()
        else:
            st.session_state.reset_message = "Please enter your email"
            st.session_state.reset_message_type = "error"
            st.rerun()

    st.markdown('<div class="link-text">Remember your password? <a href="login">Back to login</a></div>', unsafe_allow_html=True)

# Step 2: Set new password
elif st.session_state.reset_step == "new_password":
    st.markdown(f'<p style="color: #6B7280; margin-bottom: 16px;">Setting new password for <strong>{st.session_state.reset_email}</strong></p>', unsafe_allow_html=True)

    new_password = st.text_input("New Password", type="password", placeholder="At least 8 characters", key="new_pwd")
    confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="confirm_pwd")

    col1, col2 = st.columns([1, 1])
    with col1:
        if st.button("Back", key="back_btn"):
            st.session_state.reset_step = "email"
            st.session_state.reset_message = None
            st.session_state.reset_token = ""
            st.rerun()
    with col2:
        if st.button("Reset Password", key="reset_btn"):
            if not new_password:
                st.session_state.reset_message = "Please enter a new password"
                st.session_state.reset_message_type = "error"
            elif new_password != confirm_password:
                st.session_state.reset_message = "Passwords don't match"
                st.session_state.reset_message_type = "error"
            else:
                success, message = auth_handler.reset_password(st.session_state.reset_token, new_password)

                if success:
                    st.session_state.reset_step = "email"
                    st.session_state.reset_email = ""
                    st.session_state.reset_token = ""
                    st.session_state.reset_message = "Password reset successful! You can now login."
                    st.session_state.reset_message_type = "success"
                else:
                    st.session_state.reset_message = message
                    st.session_state.reset_message_type = "error"

            st.rerun()

st.markdown('</div>', unsafe_allow_html=True)

# Back to login link
if st.session_state.reset_step == "new_password":
    st.markdown('<div class="link-text"><a href="login">Back to login</a></div>', unsafe_allow_html=True)
