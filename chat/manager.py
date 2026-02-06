"""Chat history management and persistence"""
import json
import uuid
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

import streamlit as st

logger = logging.getLogger(__name__)

# Paths
APP_DIR = Path(__file__).parent.parent.resolve()
DATA_PATH = APP_DIR / "data"
CHAT_HISTORY_FILE = DATA_PATH / "chat_history.json"


def save_chat_history() -> None:
    """Save chat history to JSON file"""
    try:
        DATA_PATH.mkdir(parents=True, exist_ok=True)

        chats_to_save = []
        for chat in st.session_state.get("chat_list", []):
            chat_copy = chat.copy()
            if isinstance(chat_copy.get("created_at"), datetime):
                chat_copy["created_at"] = chat_copy["created_at"].isoformat()
            if isinstance(chat_copy.get("updated_at"), datetime):
                chat_copy["updated_at"] = chat_copy["updated_at"].isoformat()
            chats_to_save.append(chat_copy)

        with open(CHAT_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(chats_to_save, f, ensure_ascii=False, indent=2)
        logger.debug("Chat history saved successfully")
    except IOError as e:
        logger.error(f"Failed to save chat history: {e}")
    except TypeError as e:
        logger.error(f"Failed to serialize chat history: {e}")


def load_chat_history() -> List[Dict[str, Any]]:
    """Load chat history from JSON file"""
    try:
        if CHAT_HISTORY_FILE.exists():
            with open(CHAT_HISTORY_FILE, "r", encoding="utf-8") as f:
                chats = json.load(f)

            for chat in chats:
                if isinstance(chat.get("created_at"), str):
                    chat["created_at"] = datetime.fromisoformat(chat["created_at"])
                if isinstance(chat.get("updated_at"), str):
                    chat["updated_at"] = datetime.fromisoformat(chat["updated_at"])

            logger.info(f"Loaded {len(chats)} chats from history")
            return chats
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse chat history JSON: {e}")
    except IOError as e:
        logger.error(f"Failed to read chat history file: {e}")
    except ValueError as e:
        logger.error(f"Failed to parse datetime in chat history: {e}")
    return []


def format_timestamp(dt: Any) -> str:
    """Format timestamp for display"""
    try:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        now = datetime.now(dt.tzinfo) if dt.tzinfo else datetime.now()
        diff = now - dt

        if diff < timedelta(minutes=1):
            return "Just now"
        elif diff < timedelta(hours=1):
            mins = int(diff.total_seconds() / 60)
            return f"{mins}m ago"
        elif diff < timedelta(days=1):
            hours = int(diff.total_seconds() / 3600)
            return f"{hours}h ago"
        elif diff < timedelta(days=2):
            return "Yesterday"
        elif diff < timedelta(days=7):
            return f"{diff.days}d ago"
        else:
            return dt.strftime("%b %d")
    except (ValueError, TypeError, AttributeError) as e:
        logger.debug(f"Failed to format timestamp: {e}")
        return ""


def generate_chat_title(first_message: str) -> str:
    """Generate a title from the first message"""
    title = first_message[:35].strip()
    if len(first_message) > 35:
        title += "..."
    return title


def create_new_chat() -> Dict[str, Any]:
    """Create a new chat in session state"""
    chat_id = str(uuid.uuid4())
    new_chat = {
        "id": chat_id,
        "title": "New Chat",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "messages": []
    }
    st.session_state.chat_list.insert(0, new_chat)
    save_chat_history()
    return new_chat


def get_chat_by_id(chat_id: str) -> Optional[Dict[str, Any]]:
    """Get a chat by its ID"""
    for chat in st.session_state.chat_list:
        if chat["id"] == chat_id:
            return chat
    return None


def update_chat_title(chat_id: str, new_title: str) -> bool:
    """Update a chat's title"""
    chat = get_chat_by_id(chat_id)
    if chat:
        chat["title"] = new_title
        chat["updated_at"] = datetime.now()
        return True
    return False


def delete_chat(chat_id: str) -> bool:
    """Delete a chat"""
    st.session_state.chat_list = [c for c in st.session_state.chat_list if c["id"] != chat_id]
    save_chat_history()
    return True


def delete_all_chats() -> None:
    """Delete all chats"""
    st.session_state.chat_list = []
    st.session_state.current_chat_id = None
    st.session_state.messages = []
    save_chat_history()


def add_message_to_chat(chat_id: str, content: str, role: str) -> bool:
    """Add a message to a chat"""
    chat = get_chat_by_id(chat_id)
    if chat:
        chat["messages"].append({"role": role, "content": content})
        chat["updated_at"] = datetime.now()
        if role == "user" and chat["title"] == "New Chat":
            chat["title"] = generate_chat_title(content)
        save_chat_history()
        return True
    return False


# ========== SINGLE SOURCE OF TRUTH HELPERS ==========

def get_active_chat() -> Optional[Dict[str, Any]]:
    """Get the currently active chat"""
    chat_id = st.session_state.get("current_chat_id")
    if chat_id:
        return get_chat_by_id(chat_id)
    return None


def get_active_messages() -> List[Dict[str, str]]:
    """Get messages from the active chat (single source of truth)"""
    chat = get_active_chat()
    return chat["messages"] if chat else []


def add_message(role: str, content: str) -> bool:
    """Add a message to the active chat"""
    chat_id = st.session_state.get("current_chat_id")
    if chat_id:
        return add_message_to_chat(chat_id, content, role)
    return False


def ensure_active_chat() -> str:
    """Ensure there's an active chat, create one if needed. Returns chat_id."""
    if not st.session_state.get("current_chat_id"):
        new_chat = create_new_chat()
        st.session_state.current_chat_id = new_chat["id"]
    return st.session_state.current_chat_id


def switch_to_chat(chat_id: str) -> bool:
    """Switch to a different chat"""
    chat = get_chat_by_id(chat_id)
    if chat:
        st.session_state.current_chat_id = chat_id
        return True
    return False
