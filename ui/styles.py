"""CSS styles for Buddy AI - matching CLAUDE.md and Figma specs"""
import streamlit as st

# Complete CSS matching CLAUDE.md: header #004aad, Lora font, user bubble #DBEAFE
MAIN_STYLES = """
<!-- Preload fonts to prevent FOUT -->
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">

<style>
    :root {
        --primary: #004aad;
        --primary-dark: #003a8c;
        --primary-light: #0066cc;
        --bg-main: #F3F4F6;
        --bg-white: #FFFFFF;
        --bg-sidebar: #1F2937;
        --text-dark: #111827;
        --text-gray: #6B7280;
        --text-light: #9CA3AF;
        --border-color: #E5E7EB;
        --shadow: 0 1px 3px rgba(0,0,0,0.1);
        --shadow-lg: 0 4px 15px rgba(0,0,0,0.15);
        --user-bubble: #DBEAFE;
        --user-text: #1E40AF;
        --ai-bubble: #FFFFFF;
        --header-height: 60px;
        --input-height: 70px;
    }

    /* Global Reset with smooth transitions */
    * {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
        box-sizing: border-box;
    }

    /* Smooth transitions globally */
    *, *::before, *::after {
        transition: background-color 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }

    /* Hide Streamlit defaults */
    #MainMenu, footer, header {display: none !important;}
    .stDeployButton {display: none !important;}
    [data-testid="stSidebar"] {display: none !important;}
    [data-testid="collapsedControl"] {display: none !important;}
    .stApp > header {display: none !important;}

    /* Prevent layout shifts */
    html, body {
        overflow-x: hidden;
        scroll-behavior: smooth;
    }

    /* Main app container with GPU acceleration */
    .stApp {
        background: var(--bg-main) !important;
        transform: translateZ(0);
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
    }

    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
        contain: layout style;
    }

    /* ========== CUSTOM HEADER ========== */
    .custom-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: var(--header-height);
        background: #004aad;
        box-shadow: var(--shadow);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 16px;
        z-index: 1000;
        /* GPU acceleration for smooth fixed positioning */
        transform: translateZ(0);
        will-change: transform;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
    }

    .header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .hamburger-btn {
        background: none;
        border: none;
        cursor: pointer;
        padding: 8px;
        display: flex;
        flex-direction: column;
        gap: 5px;
        border-radius: 8px;
        transition: background 0.2s;
    }

    .hamburger-btn:hover {
        background: rgba(255,255,255,0.1);
    }

    .hamburger-btn span {
        display: block;
        width: 22px;
        height: 2.5px;
        background: white;
        border-radius: 2px;
        transition: all 0.3s;
    }

    .header-center {
        display: flex;
        align-items: center;
        gap: 8px;
        position: absolute;
        left: 50%;
        transform: translateX(-50%);
    }

    .header-title {
        font-family: 'Lora', serif !important;
        font-size: 1.2rem;
        font-weight: 600;
        color: white;
    }

    .header-right {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    /* ========== CHAT AREA ========== */
    .chat-container {
        margin-top: var(--header-height);
        margin-bottom: var(--input-height);
        padding: 16px;
        min-height: calc(100vh - var(--header-height) - var(--input-height));
        overflow-y: auto;
        /* Smooth scrolling */
        scroll-behavior: smooth;
        -webkit-overflow-scrolling: touch;
        /* Prevent layout shifts */
        contain: layout style;
    }

    /* Reduce Streamlit rerun jitter */
    [data-testid="stVerticalBlock"] {
        contain: layout style;
    }

    /* Spinner/loading state improvements */
    .stSpinner > div {
        border-color: var(--primary) transparent transparent transparent !important;
    }

    /* ========== WELCOME SCREEN ========== */
    .welcome-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 60px 20px;
        min-height: calc(100vh - var(--header-height) - var(--input-height) - 100px);
    }

    .welcome-icon {
        width: 100px;
        height: 100px;
        background: linear-gradient(135deg, #004aad 0%, #0066cc 100%);
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 3rem;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(0, 74, 173, 0.25);
        /* Subtle pulse animation */
        animation: subtlePulse 3s ease-in-out infinite;
    }

    @keyframes subtlePulse {
        0%, 100% { transform: scale(1); box-shadow: 0 8px 24px rgba(0, 74, 173, 0.25); }
        50% { transform: scale(1.02); box-shadow: 0 10px 28px rgba(0, 74, 173, 0.3); }
    }

    .welcome-title,
    h2.welcome-title,
    .welcome-container h2,
    .welcome-container .welcome-title {
        font-family: 'Lora', serif !important;
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: #004aad !important;
        margin-bottom: 12px !important;
    }

    .welcome-subtitle {
        font-size: 1rem;
        color: var(--text-gray);
        max-width: 450px;
        line-height: 1.7;
        margin-bottom: 8px;
    }

    /* Suggestion chips grid */
    .welcome-suggestions {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
        margin-top: 32px;
        max-width: 480px;
        width: 100%;
        padding: 0 16px;
    }

    .suggestion-chip {
        background: var(--bg-white);
        border: 1px solid var(--border-color);
        padding: 16px 20px;
        border-radius: 12px;
        font-size: 0.9rem;
        color: var(--text-dark);
        cursor: pointer;
        transition: all 0.2s;
        text-align: left;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04);
    }

    .suggestion-chip:hover {
        border-color: var(--primary);
        background: #EFF6FF;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 74, 173, 0.12);
    }

    @media (max-width: 480px) {
        .welcome-suggestions {
            grid-template-columns: 1fr;
        }
    }

    /* Suggestion button styling */
    .stButton > button {
        background: white !important;
        border: 1px solid #E5E7EB !important;
        border-radius: 12px !important;
        padding: 16px 20px !important;
        font-size: 0.9rem !important;
        color: #1F2937 !important;
        transition: all 0.2s !important;
        text-align: left !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.04) !important;
    }

    .stButton > button:hover {
        border-color: #004aad !important;
        background: #EFF6FF !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 12px rgba(0, 74, 173, 0.12) !important;
    }

    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
        box-shadow: 0 2px 6px rgba(0, 74, 173, 0.08) !important;
    }

    /* ========== MESSAGE BUBBLES ========== */
    .message-container {
        display: flex;
        margin-bottom: 16px;
        animation: fadeIn 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        /* GPU acceleration */
        transform: translateZ(0);
        will-change: opacity, transform;
    }

    @keyframes fadeIn {
        from {
            opacity: 0;
            transform: translateY(8px) translateZ(0);
        }
        to {
            opacity: 1;
            transform: translateY(0) translateZ(0);
        }
    }

    .message-container.user {
        justify-content: flex-end;
    }

    .message-container.assistant {
        justify-content: flex-start;
    }

    .message-avatar {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        flex-shrink: 0;
    }

    .message-container.assistant .message-avatar {
        background: var(--primary);
        color: white;
        margin-right: 10px;
    }

    .message-container.user .message-avatar {
        background: var(--text-gray);
        color: white;
        margin-left: 10px;
        order: 2;
    }

    .message-bubble {
        max-width: 75%;
        padding: 12px 16px;
        border-radius: 18px;
        font-size: 0.95rem;
        line-height: 1.5;
    }

    .message-container.user .message-bubble {
        background: var(--user-bubble);
        color: var(--user-text);
        border-bottom-right-radius: 4px;
    }

    .message-container.assistant .message-bubble {
        background: var(--ai-bubble);
        color: var(--text-dark);
        border-bottom-left-radius: 4px;
        box-shadow: var(--shadow);
    }

    /* ========== INPUT SECTION ========== */
    .input-container {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: var(--bg-white);
        padding: 12px 16px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1);
        z-index: 999;
    }

    .input-wrapper {
        display: flex;
        align-items: center;
        gap: 10px;
        max-width: 800px;
        margin: 0 auto;
        background: var(--bg-main);
        border-radius: 25px;
        padding: 8px 8px 8px 16px;
        border: 1px solid var(--border-color);
        transition: all 0.2s;
    }

    .input-wrapper:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
    }

    .send-btn {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: var(--primary);
        border: none;
        color: white;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        transition: all 0.2s;
        flex-shrink: 0;
    }

    .send-btn:hover {
        background: var(--primary-dark);
        transform: scale(1.05);
    }

    /* Style Streamlit chat input */
    [data-testid="stChatInput"] {
        position: fixed !important;
        bottom: 0 !important;
        left: 0 !important;
        right: 0 !important;
        background: var(--bg-white) !important;
        padding: 12px 16px !important;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1) !important;
        z-index: 999 !important;
        /* GPU acceleration for smooth fixed positioning */
        transform: translateZ(0) !important;
        will-change: transform !important;
        -webkit-backface-visibility: hidden !important;
        backface-visibility: hidden !important;
    }

    [data-testid="stChatInput"] > div {
        max-width: 800px !important;
        margin: 0 auto !important;
        background: var(--bg-main) !important;
        border: 1px solid var(--border-color) !important;
        border-radius: 25px !important;
        overflow: hidden !important;
    }

    [data-testid="stChatInput"] > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
    }

    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        border: none !important;
        padding: 12px 16px !important;
        font-size: 1rem !important;
        color: var(--text-dark) !important;
    }

    [data-testid="stChatInput"] textarea::placeholder {
        color: var(--text-light) !important;
    }

    [data-testid="stChatInput"] button {
        background: var(--primary) !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        min-width: 40px !important;
        min-height: 40px !important;
        margin: 4px !important;
        border: none !important;
    }

    [data-testid="stChatInput"] button:hover {
        background: var(--primary-dark) !important;
        transform: scale(1.05) !important;
    }

    [data-testid="stChatInput"] button:active {
        transform: scale(0.95) !important;
    }

    [data-testid="stChatInput"] button svg {
        fill: white !important;
    }

    /* Streamlit message styling override */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        padding: 0 !important;
    }

    /* ========== RESPONSIVE ========== */
    @media (min-width: 768px) {
        .message-bubble {
            max-width: 65%;
        }

        .chat-container {
            padding: 24px 40px;
        }
    }

    @media (min-width: 1024px) {
        .chat-container {
            max-width: 900px;
            margin-left: auto;
            margin-right: auto;
        }
    }
</style>
"""

SIDEBAR_STYLES = """
<style>
    /* Sidebar overlay with fade */
    .sidebar-overlay-active {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        z-index: 1001;
        animation: fadeInOverlay 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    @keyframes fadeInOverlay {
        from { opacity: 0; }
        to { opacity: 1; }
    }

    /* Sidebar positioning with GPU acceleration */
    [data-testid="stVerticalBlock"]:has(button[key="close_sidebar_btn"]),
    section[data-testid="stMain"] > div > div > div > div:nth-child(2) {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 300px !important;
        height: 100vh !important;
        background: #1F2937 !important;
        z-index: 1002 !important;
        padding: 16px !important;
        overflow-y: auto !important;
        animation: slideIn 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        /* GPU acceleration */
        transform: translateZ(0);
        will-change: transform;
        -webkit-backface-visibility: hidden;
        backface-visibility: hidden;
    }

    @keyframes slideIn {
        from { transform: translateX(-100%) translateZ(0); }
        to { transform: translateX(0) translateZ(0); }
    }

    /* Style buttons in sidebar */
    [data-testid="stVerticalBlock"]:has(button[key="close_sidebar_btn"]) button {
        background: rgba(255,255,255,0.1) !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
    }

    [data-testid="stVerticalBlock"]:has(button[key="close_sidebar_btn"]) button:hover {
        background: rgba(255,255,255,0.2) !important;
    }

    [data-testid="stVerticalBlock"]:has(button[key="close_sidebar_btn"]) button[data-testid="stBaseButton-primary"] {
        background: #3B82F6 !important;
        border: none !important;
    }

    /* Sidebar dividers */
    [data-testid="stVerticalBlock"]:has(button[key="close_sidebar_btn"]) hr {
        border-color: rgba(255,255,255,0.1) !important;
        margin: 16px 0 !important;
    }
</style>
"""


def inject_styles() -> None:
    """Inject all CSS styles into the page"""
    st.markdown(MAIN_STYLES, unsafe_allow_html=True)


def inject_sidebar_styles() -> None:
    """Inject sidebar-specific styles"""
    st.markdown(SIDEBAR_STYLES, unsafe_allow_html=True)
