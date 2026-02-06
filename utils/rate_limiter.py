"""Rate limiting for API protection"""
import time
import streamlit as st

# Rate limiting configuration
RATE_LIMIT_MESSAGES = 30  # Max messages per window
RATE_LIMIT_WINDOW = 60  # Window in seconds


def check_rate_limit() -> bool:
    """
    Check if user has exceeded rate limit.

    Returns:
        True if request is allowed, False if rate limited
    """
    now = time.time()

    # Initialize rate limit tracking
    if "message_timestamps" not in st.session_state:
        st.session_state.message_timestamps = []

    # Remove timestamps outside the window
    st.session_state.message_timestamps = [
        ts for ts in st.session_state.message_timestamps
        if now - ts < RATE_LIMIT_WINDOW
    ]

    # Check if under limit
    if len(st.session_state.message_timestamps) >= RATE_LIMIT_MESSAGES:
        return False

    # Add current timestamp
    st.session_state.message_timestamps.append(now)
    return True
