"""UI components for Buddy AI"""
import streamlit as st
from chat.manager import format_timestamp, get_active_messages


def render_header() -> None:
    """Render the custom header - CLAUDE.md spec: #004aad, white text, Lora font"""
    st.markdown("""
    <div class="custom-header">
        <div class="header-left">
            <button class="hamburger-btn" onclick="window.parent.postMessage({type: 'toggleSidebar'}, '*')">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
        <div class="header-center">
            <span class="header-title">Buddy AI</span>
        </div>
        <div class="header-right"></div>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar() -> None:
    """Render the sidebar with chat list and navigation"""
    from chat.manager import create_new_chat, delete_chat, save_chat_history, switch_to_chat

    # Dark overlay
    st.markdown('<div class="sidebar-overlay-active"></div>', unsafe_allow_html=True)

    # Close button row
    close_col1, close_col2 = st.columns([4, 1])
    with close_col1:
        st.markdown('<div style="color: white; font-size: 1.1rem; font-weight: 600; padding: 10px 0;">🎓 Buddy AI</div>', unsafe_allow_html=True)
    with close_col2:
        if st.button("✕", key="close_sidebar_btn", help="Close"):
            st.session_state.sidebar_open = False
            st.rerun()

    # Menu option 1: Create New Chat
    if st.button("➕ Create New Chat", key="new_chat_sidebar", use_container_width=True, type="primary"):
        new_chat = create_new_chat()
        st.session_state.current_chat_id = new_chat["id"]
        st.session_state.sidebar_open = False
        st.rerun()

    st.markdown("---")

    # Menu option 2: Past Chats
    st.markdown('<p style="color: rgba(255,255,255,0.5); font-size: 0.75rem; text-transform: uppercase;">Past Chats</p>', unsafe_allow_html=True)

    if not st.session_state.chat_list:
        st.markdown('<p style="color: rgba(255,255,255,0.4); text-align: center; padding: 20px;">No chats yet</p>', unsafe_allow_html=True)
    else:
        for chat in st.session_state.chat_list:
            chat_col1, chat_col2 = st.columns([5, 1])
            with chat_col1:
                btn_type = "primary" if chat["id"] == st.session_state.current_chat_id else "secondary"
                title = f"💬 {chat['title'][:22]}..." if len(chat['title']) > 22 else f"💬 {chat['title']}"
                if st.button(title, key=f"sidebar_chat_{chat['id']}", use_container_width=True, type=btn_type):
                    switch_to_chat(chat['id'])
                    st.session_state.sidebar_open = False
                    st.rerun()
            with chat_col2:
                if st.button("🗑️", key=f"sidebar_del_{chat['id']}"):
                    if st.session_state.current_chat_id == chat['id']:
                        st.session_state.current_chat_id = None
                    delete_chat(chat['id'])
                    st.rerun()
            st.markdown(f'<p style="color: rgba(255,255,255,0.4); font-size: 0.7rem; margin-top: -10px; padding-left: 10px;">{format_timestamp(chat["updated_at"])}</p>', unsafe_allow_html=True)

    # Menu option 3: Logout
    st.markdown("---")
    if st.button("🚪 Logout", key="logout_btn", use_container_width=True):
        save_chat_history()
        st.session_state.authenticated = False
        st.session_state.session_token = None
        st.session_state.user_email = None
        st.session_state.student_id = None
        st.session_state.sidebar_open = False
        st.switch_page("pages/login.py")
        st.stop()


def render_welcome() -> None:
    """Render the welcome screen with suggestion chips"""
    st.markdown("""
    <div class="welcome-container">
        <div class="welcome-icon">🎓</div>
        <h2 class="welcome-title">Welcome to Buddy AI!</h2>
        <p class="welcome-subtitle">
            I'm your friendly career guide. Ask me about careers, skills,
            education paths, or anything about your future!
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Clickable suggestion chips
    st.markdown('<div style="display: flex; justify-content: center; margin-top: -20px;">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("💼 What careers suit me?", key="suggest_1", use_container_width=True):
            st.session_state.suggestion_clicked = "What careers would suit my personality and interests?"
            st.rerun()
        if st.button("🎓 How to become an engineer?", key="suggest_3", use_container_width=True):
            st.session_state.suggestion_clicked = "How do I become an engineer? What are the steps?"
            st.rerun()
    with col2:
        if st.button("🛠️ Best skills to learn", key="suggest_2", use_container_width=True):
            st.session_state.suggestion_clicked = "What are the best skills to learn for my future career?"
            st.rerun()
        if st.button("💻 Career in tech", key="suggest_4", use_container_width=True):
            st.session_state.suggestion_clicked = "Tell me about careers in the tech industry"
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def render_messages() -> None:
    """Render chat messages from the active chat (single source of truth)"""
    messages = get_active_messages()
    for msg in messages:
        role_class = msg["role"]
        avatar = "🎓" if msg["role"] == "assistant" else "👤"
        st.markdown(f"""
        <div class="message-container {role_class}">
            <div class="message-avatar">{avatar}</div>
            <div class="message-bubble">{msg["content"]}</div>
        </div>
        """, unsafe_allow_html=True)
