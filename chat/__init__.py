"""Chat management for Buddy AI"""
from .manager import (
    save_chat_history,
    load_chat_history,
    create_new_chat,
    get_chat_by_id,
    update_chat_title,
    delete_chat,
    delete_all_chats,
    add_message_to_chat,
    format_timestamp,
    generate_chat_title,
    # Single source of truth helpers
    get_active_chat,
    get_active_messages,
    add_message,
    ensure_active_chat,
    switch_to_chat
)

__all__ = [
    'save_chat_history',
    'load_chat_history',
    'create_new_chat',
    'get_chat_by_id',
    'update_chat_title',
    'delete_chat',
    'delete_all_chats',
    'add_message_to_chat',
    'format_timestamp',
    'generate_chat_title',
    # Single source of truth helpers
    'get_active_chat',
    'get_active_messages',
    'add_message',
    'ensure_active_chat',
    'switch_to_chat'
]
