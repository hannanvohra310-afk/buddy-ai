"""Analytics engine for admin dashboard - ANONYMIZED DATA ONLY"""
import json
import re
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import Counter
from pathlib import Path

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)


class AnalyticsEngine:
    """
    Generates anonymized, aggregated analytics for admin dashboard.

    PRIVACY RULES (STRICT):
    - NO individual chat access
    - NO student-level inspection
    - ONLY anonymized, aggregated data
    """

    # Career-related keywords to track
    CAREER_KEYWORDS = [
        "engineer", "doctor", "lawyer", "teacher", "developer", "designer",
        "architect", "scientist", "writer", "artist", "accountant", "manager",
        "consultant", "analyst", "programmer", "pilot", "chef", "nurse",
        "psychologist", "journalist", "software", "marketing", "finance",
        "medicine", "business", "data scientist", "entrepreneur"
    ]

    # Topic categories
    TOPIC_KEYWORDS = {
        "career_exploration": ["career", "job", "profession", "work", "become"],
        "education": ["college", "degree", "exam", "study", "course", "university"],
        "skills": ["skill", "learn", "ability", "talent", "strength"],
        "streams": ["science", "commerce", "arts", "stream", "subject"],
        "salary": ["salary", "pay", "income", "earn", "money"],
        "confusion": ["confused", "don't know", "help", "lost", "unsure"]
    }

    def __init__(self, data_path: str = "data", db_path: str = "data/buddy_ai.db"):
        """
        Initialize analytics engine.

        Args:
            data_path: Path to data directory (for chat history)
            db_path: Path to SQLite database
        """
        self.data_path = Path(data_path)
        self.chat_history_file = self.data_path / "chat_history.json"

        # Set up database connection for student data
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def _load_chat_history(self) -> List[Dict]:
        """Load chat history from JSON file"""
        try:
            if self.chat_history_file.exists():
                with open(self.chat_history_file, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load chat history: {e}")
        return []

    def get_total_conversations(self) -> int:
        """Get total number of conversations (chats)"""
        chats = self._load_chat_history()
        return len(chats)

    def get_total_messages(self) -> int:
        """Get total number of messages across all chats"""
        chats = self._load_chat_history()
        total = 0
        for chat in chats:
            messages = chat.get("messages", [])
            total += len(messages)
        return total

    def get_daily_active_users(self, days: int = 7) -> Dict[str, int]:
        """
        Get daily active users for the past N days.

        Note: Without user authentication, this counts unique chat sessions per day.

        Args:
            days: Number of days to look back

        Returns:
            Dict with date strings as keys and counts as values
        """
        chats = self._load_chat_history()
        dau = Counter()

        cutoff = datetime.now() - timedelta(days=days)

        for chat in chats:
            updated_at = chat.get("updated_at")
            if updated_at:
                try:
                    if isinstance(updated_at, str):
                        dt = datetime.fromisoformat(updated_at)
                    else:
                        dt = updated_at

                    if dt >= cutoff:
                        date_key = dt.strftime("%Y-%m-%d")
                        dau[date_key] += 1
                except Exception:
                    pass

        # Fill in missing days with 0
        result = {}
        for i in range(days):
            date = datetime.now() - timedelta(days=i)
            date_key = date.strftime("%Y-%m-%d")
            result[date_key] = dau.get(date_key, 0)

        return dict(sorted(result.items()))

    def get_most_discussed_careers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get the most frequently discussed careers.

        Returns:
            List of dicts with career name and count
        """
        chats = self._load_chat_history()
        career_counts = Counter()

        for chat in chats:
            messages = chat.get("messages", [])
            for msg in messages:
                content = msg.get("content", "").lower()
                for career in self.CAREER_KEYWORDS:
                    if career in content:
                        career_counts[career] += 1

        return [
            {"career": career, "count": count}
            for career, count in career_counts.most_common(limit)
        ]

    def get_topic_distribution(self) -> Dict[str, int]:
        """
        Get distribution of discussion topics.

        Returns:
            Dict with topic categories and their counts
        """
        chats = self._load_chat_history()
        topic_counts = Counter()

        for chat in chats:
            messages = chat.get("messages", [])
            for msg in messages:
                if msg.get("role") == "user":  # Only count student messages
                    content = msg.get("content", "").lower()
                    for topic, keywords in self.TOPIC_KEYWORDS.items():
                        if any(kw in content for kw in keywords):
                            topic_counts[topic] += 1

        return dict(topic_counts)

    def get_common_keywords(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get most common meaningful keywords from student messages.

        Returns:
            List of dicts with keyword and count
        """
        chats = self._load_chat_history()
        word_counts = Counter()

        # Stop words to exclude
        stop_words = {
            "i", "me", "my", "we", "you", "your", "the", "a", "an", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "do",
            "does", "did", "will", "would", "could", "should", "may", "might",
            "can", "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "about", "what", "which", "who", "when",
            "where", "why", "how", "all", "each", "every", "both", "few",
            "more", "most", "other", "some", "such", "no", "nor", "not",
            "only", "same", "so", "than", "too", "very", "just", "also",
            "now", "it", "its", "this", "that", "these", "those", "and",
            "but", "or", "if", "then", "because", "while", "although", "hi",
            "hello", "hey", "thanks", "thank", "please", "yes", "no", "ok",
            "okay", "want", "know", "like", "think", "get", "make", "go"
        }

        for chat in chats:
            messages = chat.get("messages", [])
            for msg in messages:
                if msg.get("role") == "user":
                    content = msg.get("content", "").lower()
                    # Extract words (alphanumeric only)
                    words = re.findall(r'\b[a-z]+\b', content)
                    for word in words:
                        if word not in stop_words and len(word) > 2:
                            word_counts[word] += 1

        return [
            {"keyword": word, "count": count}
            for word, count in word_counts.most_common(limit)
        ]

    def get_average_conversation_length(self) -> float:
        """Get average number of messages per conversation"""
        chats = self._load_chat_history()

        if not chats:
            return 0.0

        total_messages = sum(len(chat.get("messages", [])) for chat in chats)
        return round(total_messages / len(chats), 1)

    def get_activity_by_hour(self) -> Dict[int, int]:
        """
        Get message activity distribution by hour of day.

        Returns:
            Dict with hour (0-23) as key and count as value
        """
        chats = self._load_chat_history()
        hour_counts = Counter()

        for chat in chats:
            updated_at = chat.get("updated_at")
            if updated_at:
                try:
                    if isinstance(updated_at, str):
                        dt = datetime.fromisoformat(updated_at)
                    else:
                        dt = updated_at
                    hour_counts[dt.hour] += 1
                except Exception:
                    pass

        # Fill in all hours
        return {hour: hour_counts.get(hour, 0) for hour in range(24)}

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """
        Get complete dashboard summary.

        Returns:
            Dict with all analytics metrics
        """
        return {
            "total_conversations": self.get_total_conversations(),
            "total_messages": self.get_total_messages(),
            "average_conversation_length": self.get_average_conversation_length(),
            "daily_active_users": self.get_daily_active_users(7),
            "most_discussed_careers": self.get_most_discussed_careers(10),
            "topic_distribution": self.get_topic_distribution(),
            "common_keywords": self.get_common_keywords(15),
            "activity_by_hour": self.get_activity_by_hour(),
            "generated_at": datetime.now().isoformat()
        }

    def close(self):
        """Close database connection"""
        self.session.close()
