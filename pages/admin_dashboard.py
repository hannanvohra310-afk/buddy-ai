"""Admin dashboard page for Buddy AI - Figma Design Match"""
import streamlit as st
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path for imports
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

from admin.analytics import AnalyticsEngine
from admin.privacy_filter import PrivacyFilter

# Page config - MUST be first Streamlit command
st.set_page_config(
    page_title="Admin Dashboard - Buddy AI",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Admin role check - must be admin to access this page
if st.session_state.get("role") != "admin":
    st.error("Unauthorized - Admin access required")
    st.stop()

# Custom CSS matching Figma design
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

    .main .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* Admin Header - Blue style like Figma */
    .admin-header {
        background: #004aad;
        color: white;
        padding: 20px 30px;
        margin: -1rem -1rem 24px -1rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .admin-header-left {
        display: flex;
        align-items: center;
        gap: 12px;
    }

    .admin-header-icon {
        width: 40px;
        height: 40px;
        background: rgba(255,255,255,0.15);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.25rem;
    }

    .admin-title {
        font-family: 'Lora', serif;
        font-size: 1.5rem;
        font-weight: 600;
        color: white;
    }

    .live-badge {
        background: #10B981;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    .live-dot {
        width: 8px;
        height: 8px;
        background: white;
        border-radius: 50%;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Content Container */
    .dashboard-content {
        padding: 0 30px 30px;
        max-width: 1200px;
        margin: 0 auto;
    }

    /* Metric Cards */
    .metrics-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 20px;
        margin-bottom: 30px;
    }

    @media (max-width: 1024px) {
        .metrics-grid {
            grid-template-columns: repeat(2, 1fr);
        }
    }

    @media (max-width: 600px) {
        .metrics-grid {
            grid-template-columns: 1fr;
        }
    }

    .metric-card {
        background: white;
        border-radius: 16px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        display: flex;
        align-items: flex-start;
        gap: 16px;
    }

    .metric-icon {
        width: 52px;
        height: 52px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        flex-shrink: 0;
    }

    .metric-icon.blue {
        background: #DBEAFE;
    }

    .metric-icon.purple {
        background: #E9D5FF;
    }

    .metric-icon.green {
        background: #D1FAE5;
    }

    .metric-icon.orange {
        background: #FED7AA;
    }

    .metric-info {
        flex: 1;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1F2937;
        line-height: 1.2;
    }

    .metric-label {
        font-size: 0.9rem;
        color: #6B7280;
        margin-top: 4px;
    }

    /* Section Styles */
    .section-card {
        background: white;
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        margin-bottom: 24px;
        overflow: hidden;
    }

    .section-header {
        padding: 20px 24px;
        border-bottom: 1px solid #E5E7EB;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .section-title {
        font-family: 'Inter', sans-serif;
        font-size: 1.1rem;
        font-weight: 600;
        color: #1F2937;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .section-content {
        padding: 20px 24px;
    }

    /* Recent Chats List */
    .chat-list-item {
        display: flex;
        align-items: center;
        padding: 14px 0;
        border-bottom: 1px solid #F3F4F6;
    }

    .chat-list-item:last-child {
        border-bottom: none;
    }

    .chat-avatar {
        width: 40px;
        height: 40px;
        background: #E5E7EB;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin-right: 14px;
        font-size: 1rem;
    }

    .chat-info {
        flex: 1;
    }

    .chat-title {
        font-size: 0.95rem;
        font-weight: 500;
        color: #1F2937;
        margin-bottom: 2px;
    }

    .chat-meta {
        font-size: 0.8rem;
        color: #9CA3AF;
    }

    .chat-time {
        font-size: 0.8rem;
        color: #9CA3AF;
    }

    /* Privacy Notice */
    .privacy-notice {
        background: #DBEAFE;
        color: #1E40AF;
        padding: 14px 20px;
        border-radius: 12px;
        font-size: 0.85rem;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Back Button */
    .back-btn {
        background: white;
        border: 1px solid #E5E7EB;
        padding: 10px 20px;
        border-radius: 10px;
        font-size: 0.9rem;
        color: #374151;
        cursor: pointer;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 8px;
    }

    .back-btn:hover {
        background: #F9FAFB;
        border-color: #D1D5DB;
    }

    /* Charts Container */
    .charts-row {
        display: grid;
        grid-template-columns: repeat(2, 1fr);
        gap: 24px;
        margin-bottom: 24px;
    }

    @media (max-width: 900px) {
        .charts-row {
            grid-template-columns: 1fr;
        }
    }

    /* Keywords Cloud */
    .keywords-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    .keyword-tag {
        background: #F3F4F6;
        padding: 8px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        color: #374151;
    }

    /* Footer */
    .dashboard-footer {
        text-align: center;
        color: #9CA3AF;
        font-size: 0.8rem;
        padding: 20px;
        margin-top: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize analytics
@st.cache_resource
def get_analytics():
    return AnalyticsEngine(
        data_path=str(parent_dir / "data"),
        db_path=str(parent_dir / "data" / "buddy_ai.db")
    )

analytics = get_analytics()
privacy_filter = PrivacyFilter()

# Get dashboard data
try:
    dashboard_data = analytics.get_dashboard_summary()
    dashboard_data = privacy_filter.validate_analytics_output(dashboard_data)
except Exception as e:
    st.error(f"Failed to load analytics: {e}")
    dashboard_data = {}

# Header
st.markdown("""
<div class="admin-header">
    <div class="admin-header-left">
        <div class="admin-header-icon">🛡️</div>
        <div class="admin-title">Admin Dashboard</div>
    </div>
    <div class="live-badge">
        <span class="live-dot"></span>
        LIVE SYSTEM
    </div>
</div>
""", unsafe_allow_html=True)

# Privacy notice
st.markdown("""
<div class="privacy-notice">
    🔒 <strong>Privacy Protected:</strong> This dashboard shows only anonymized, aggregated data.
    Individual student data and chat contents are never accessible.
</div>
""", unsafe_allow_html=True)

# Metric Cards
total_chats = dashboard_data.get('total_conversations', 0)
total_messages = dashboard_data.get('total_messages', 0)
dau = dashboard_data.get('daily_active_users', {})
estimated_users = list(dau.values())[0] if dau else 0
rag_status = "Connected" if st.session_state.get('rag_status', 'offline') == 'connected' else "Offline"

st.markdown(f"""
<div class="dashboard-content">
    <div class="metrics-grid">
        <div class="metric-card">
            <div class="metric-icon blue">💬</div>
            <div class="metric-info">
                <div class="metric-value">{total_chats}</div>
                <div class="metric-label">Total Chats</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon purple">📝</div>
            <div class="metric-info">
                <div class="metric-value">{total_messages}</div>
                <div class="metric-label">Total Messages</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon green">👥</div>
            <div class="metric-info">
                <div class="metric-value">{estimated_users}</div>
                <div class="metric-label">Estimated Users</div>
            </div>
        </div>
        <div class="metric-card">
            <div class="metric-icon orange">🔗</div>
            <div class="metric-info">
                <div class="metric-value">{rag_status}</div>
                <div class="metric-label">RAG Status</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Recent Chats Section
st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-title">📋 Recent Chats</div>
        </div>
        <div class="section-content">
""", unsafe_allow_html=True)

# Get recent chats (anonymized titles only)
import json
chat_history_file = parent_dir / "data" / "chat_history.json"
recent_chats = []

try:
    if chat_history_file.exists():
        with open(chat_history_file, "r", encoding="utf-8") as f:
            chats = json.load(f)
            # Get last 5 chats, anonymized
            for chat in chats[:5]:
                title = chat.get("title", "New Chat")[:30]
                if len(chat.get("title", "")) > 30:
                    title += "..."
                msg_count = len(chat.get("messages", []))
                recent_chats.append({
                    "title": privacy_filter.redact_pii(title),
                    "messages": msg_count,
                    "time": "Recent"
                })
except Exception:
    pass

if recent_chats:
    for chat in recent_chats:
        st.markdown(f"""
            <div class="chat-list-item">
                <div class="chat-avatar">💬</div>
                <div class="chat-info">
                    <div class="chat-title">{chat['title']}</div>
                    <div class="chat-meta">{chat['messages']} messages</div>
                </div>
                <div class="chat-time">{chat['time']}</div>
            </div>
        """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div style="text-align: center; padding: 30px; color: #9CA3AF;">
            No chat history available yet.
        </div>
    """, unsafe_allow_html=True)

st.markdown("""
        </div>
    </div>
""", unsafe_allow_html=True)

# Charts Row
st.markdown("""
    <div class="charts-row">
""", unsafe_allow_html=True)

# Daily Activity Chart
col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-title">📈 Daily Activity (Last 7 Days)</div>
        </div>
        <div class="section-content">
    """, unsafe_allow_html=True)

    dau_data = dashboard_data.get('daily_active_users', {})
    if dau_data:
        import pandas as pd
        df = pd.DataFrame([
            {"Date": date, "Conversations": count}
            for date, count in dau_data.items()
        ])
        st.bar_chart(df.set_index("Date"))
    else:
        st.info("No activity data available yet.")

    st.markdown("</div></div>", unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-title">🎯 Most Discussed Careers</div>
        </div>
        <div class="section-content">
    """, unsafe_allow_html=True)

    careers = dashboard_data.get('most_discussed_careers', [])
    if careers:
        import pandas as pd
        df = pd.DataFrame(careers)
        st.bar_chart(df.set_index("career"))
    else:
        st.info("No career discussion data available yet.")

    st.markdown("</div></div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# Topic Distribution and Keywords
col3, col4 = st.columns(2)

with col3:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-title">📊 Topic Distribution</div>
        </div>
        <div class="section-content">
    """, unsafe_allow_html=True)

    topics = dashboard_data.get('topic_distribution', {})
    if topics:
        import pandas as pd
        df = pd.DataFrame([
            {"Topic": topic.replace("_", " ").title(), "Count": count}
            for topic, count in topics.items()
        ])
        st.bar_chart(df.set_index("Topic"))
    else:
        st.info("No topic data available yet.")

    st.markdown("</div></div>", unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="section-card">
        <div class="section-header">
            <div class="section-title">🏷️ Common Keywords</div>
        </div>
        <div class="section-content">
    """, unsafe_allow_html=True)

    keywords = dashboard_data.get('common_keywords', [])
    if keywords:
        keyword_html = '<div class="keywords-container">'
        for kw in keywords[:12]:
            keyword_html += f'<span class="keyword-tag">{kw["keyword"]} ({kw["count"]})</span>'
        keyword_html += '</div>'
        st.markdown(keyword_html, unsafe_allow_html=True)
    else:
        st.info("No keyword data available yet.")

    st.markdown("</div></div>", unsafe_allow_html=True)

# Close dashboard content div
st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(f"""
<div class="dashboard-footer">
    Last updated: {dashboard_data.get('generated_at', datetime.now().strftime('%Y-%m-%d %H:%M'))}<br>
    Data is anonymized and aggregated for privacy protection.
</div>
""", unsafe_allow_html=True)

# Back to app button
if st.button("← Back to Buddy AI"):
    st.switch_page("app.py")
