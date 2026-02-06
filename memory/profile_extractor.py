"""Extract student interests, strengths, and preferences from conversation"""
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)


class ProfileExtractor:
    """
    Extracts student profile information from conversations.

    Looks for:
    - Interests (things they enjoy, like)
    - Dislikes (things they don't enjoy)
    - Strengths (things they're good at)
    - Challenges (things they struggle with)
    - Career interests (careers they've shown interest in)
    """

    # Patterns for extracting interests
    INTEREST_PATTERNS = [
        (r"i (?:really )?(?:like|love|enjoy) (?:to )?(.+?)(?:\.|,|$|!)", "interest"),
        (r"i'm (?:really )?interested in (.+?)(?:\.|,|$|!)", "interest"),
        (r"i find (.+?) (?:interesting|fascinating|exciting)", "interest"),
        (r"(.+?) is (?:really )?(?:fun|interesting|exciting) (?:to me|for me)?", "interest"),
        (r"i've always (?:liked|loved|enjoyed) (.+?)(?:\.|,|$|!)", "interest"),
    ]

    # Patterns for extracting dislikes
    DISLIKE_PATTERNS = [
        (r"i (?:really )?(?:hate|dislike|don't like) (.+?)(?:\.|,|$|!)", "dislike"),
        (r"i'm not (?:really )?interested in (.+?)(?:\.|,|$|!)", "dislike"),
        (r"(.+?) is (?:boring|dull|not for me)", "dislike"),
        (r"i (?:can't stand|avoid) (.+?)(?:\.|,|$|!)", "dislike"),
    ]

    # Patterns for extracting strengths
    STRENGTH_PATTERNS = [
        (r"i'm (?:really )?good at (.+?)(?:\.|,|$|!)", "strength"),
        (r"i'm (?:quite )?skilled (?:at|in) (.+?)(?:\.|,|$|!)", "strength"),
        (r"i do well (?:at|in|with) (.+?)(?:\.|,|$|!)", "strength"),
        (r"my (?:strength|strong point) is (.+?)(?:\.|,|$|!)", "strength"),
        (r"people say i'm good at (.+?)(?:\.|,|$|!)", "strength"),
    ]

    # Patterns for extracting challenges
    CHALLENGE_PATTERNS = [
        (r"i'm (?:not (?:really )?)?(?:bad|weak) at (.+?)(?:\.|,|$|!)", "challenge"),
        (r"i struggle with (.+?)(?:\.|,|$|!)", "challenge"),
        (r"(.+?) is (?:difficult|hard|challenging) for me", "challenge"),
        (r"i (?:can't|cannot) (?:do|handle) (.+?) well", "challenge"),
    ]

    # Career-related keywords
    CAREER_KEYWORDS = [
        "engineer", "doctor", "lawyer", "teacher", "developer", "designer",
        "architect", "scientist", "writer", "artist", "musician", "accountant",
        "manager", "consultant", "analyst", "programmer", "pilot", "chef",
        "entrepreneur", "psychologist", "journalist", "photographer",
        "software", "marketing", "finance", "medicine", "law", "business"
    ]

    def __init__(self):
        # Compile all patterns
        self.compiled_patterns = {
            "interest": [(re.compile(p[0], re.IGNORECASE), p[1]) for p in self.INTEREST_PATTERNS],
            "dislike": [(re.compile(p[0], re.IGNORECASE), p[1]) for p in self.DISLIKE_PATTERNS],
            "strength": [(re.compile(p[0], re.IGNORECASE), p[1]) for p in self.STRENGTH_PATTERNS],
            "challenge": [(re.compile(p[0], re.IGNORECASE), p[1]) for p in self.CHALLENGE_PATTERNS],
        }

    def extract_from_message(self, message: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract profile information from a single message.

        Args:
            message: The user's message text

        Returns:
            Dict with lists of extracted items by category
        """
        extractions = {
            "interests": [],
            "dislikes": [],
            "strengths": [],
            "challenges": [],
            "career_mentions": []
        }

        message_lower = message.lower()

        # Extract using patterns
        for category, patterns in self.compiled_patterns.items():
            for pattern, _ in patterns:
                matches = pattern.findall(message)
                for match in matches:
                    cleaned = self._clean_extraction(match)
                    if cleaned and len(cleaned) > 2:  # Avoid very short matches
                        key = f"{category}s" if category != "challenge" else "challenges"
                        if category == "interest":
                            key = "interests"
                        elif category == "dislike":
                            key = "dislikes"
                        elif category == "strength":
                            key = "strengths"

                        extractions[key].append({
                            "content": cleaned,
                            "confidence": 0.8,
                            "extracted_at": datetime.now().isoformat()
                        })

        # Extract career mentions
        for keyword in self.CAREER_KEYWORDS:
            if keyword in message_lower:
                # Check context to determine interest level
                context_window = 50
                idx = message_lower.find(keyword)
                context = message_lower[max(0, idx-context_window):min(len(message_lower), idx+context_window)]

                # Determine if it's positive, negative, or neutral mention
                sentiment = self._determine_career_sentiment(context, keyword)

                extractions["career_mentions"].append({
                    "career": keyword,
                    "sentiment": sentiment,
                    "context": message[max(0, idx-30):min(len(message), idx+30)],
                    "extracted_at": datetime.now().isoformat()
                })

        return extractions

    def extract_from_conversation(
        self,
        messages: List[Dict[str, str]],
        student_only: bool = True
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract profile information from a conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'
            student_only: If True, only extract from user messages

        Returns:
            Aggregated profile information
        """
        all_extractions = {
            "interests": [],
            "dislikes": [],
            "strengths": [],
            "challenges": [],
            "career_mentions": []
        }

        for msg in messages:
            if student_only and msg.get("role") != "user":
                continue

            content = msg.get("content", "")
            if content:
                extractions = self.extract_from_message(content)

                for key in all_extractions:
                    all_extractions[key].extend(extractions[key])

        # Deduplicate while keeping highest confidence
        for key in all_extractions:
            all_extractions[key] = self._deduplicate(all_extractions[key])

        return all_extractions

    def _clean_extraction(self, text: str) -> str:
        """Clean extracted text"""
        if isinstance(text, tuple):
            text = text[0] if text else ""

        # Remove common filler words at start
        fillers = ["to", "the", "a", "an", "doing", "being", "that", "this"]
        words = text.strip().split()
        while words and words[0].lower() in fillers:
            words.pop(0)

        return " ".join(words).strip()

    def _determine_career_sentiment(self, context: str, career: str) -> str:
        """Determine sentiment about a career mention"""
        positive_indicators = ["like", "love", "want", "interested", "curious", "dream", "hope"]
        negative_indicators = ["hate", "dislike", "don't want", "not interested", "boring"]

        for indicator in positive_indicators:
            if indicator in context:
                return "positive"

        for indicator in negative_indicators:
            if indicator in context:
                return "negative"

        return "neutral"

    def _deduplicate(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Deduplicate items, keeping the one with highest confidence"""
        seen = {}

        for item in items:
            key = item.get("content", item.get("career", "")).lower()
            if key in seen:
                if item.get("confidence", 0) > seen[key].get("confidence", 0):
                    seen[key] = item
            else:
                seen[key] = item

        return list(seen.values())

    def merge_profiles(
        self,
        existing: Dict[str, List[Dict[str, Any]]],
        new: Dict[str, List[Dict[str, Any]]]
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Merge new extractions into existing profile.

        Args:
            existing: Existing profile data
            new: Newly extracted data

        Returns:
            Merged profile
        """
        merged = {}

        all_keys = set(existing.keys()) | set(new.keys())

        for key in all_keys:
            combined = existing.get(key, []) + new.get(key, [])
            merged[key] = self._deduplicate(combined)

        return merged
