"""State detection for the Conversation Decision Framework"""
import re
from typing import List, Dict, Any, Optional
import logging

from .constants import (
    ConversationState,
    OUT_OF_SCOPE_PATTERNS,
    CONFUSION_PATTERNS,
    VALIDATION_PATTERNS,
    SELF_REFLECTION_PATTERNS,
    CAREER_PATTERNS,
    COMPARISON_PATTERNS,
    INFORMATION_PATTERNS,
    GREETING_PATTERNS
)

logger = logging.getLogger(__name__)


class StateDetector:
    """
    Detects the current conversation state based on user input.

    Priority Order (CRITICAL):
    1. OUT_OF_SCOPE - Safety first
    2. GREETING - Special handling for greetings
    3. CONFUSED - Trust building
    4. VALIDATION_SEEKING - Trust building
    5. SELF_REFLECTION - Deepening awareness
    6. CAREER_CURIOSITY - Exploration
    7. COMPARISON - Exploration with trade-offs
    8. INFORMATION_SEEKING - Factual queries

    When in doubt, choose the slower, safer state.
    """

    def __init__(self):
        self._compile_patterns()

    def _compile_patterns(self):
        """Pre-compile regex patterns for efficiency"""
        # Compile out-of-scope patterns
        self.out_of_scope_compiled = {}
        for category, patterns in OUT_OF_SCOPE_PATTERNS.items():
            self.out_of_scope_compiled[category] = [
                re.compile(r'\b' + re.escape(p) + r'\b', re.IGNORECASE)
                for p in patterns
            ]

    def _normalize_text(self, text: str) -> str:
        """Normalize text for pattern matching"""
        return text.lower().strip()

    def _check_patterns(self, text: str, patterns: List[str]) -> bool:
        """Check if any pattern matches in the text"""
        text_lower = self._normalize_text(text)
        for pattern in patterns:
            if pattern.lower() in text_lower:
                return True
        return False

    def _check_out_of_scope(self, text: str) -> Optional[str]:
        """
        Check if text contains out-of-scope topics.

        Returns the category if found, None otherwise.
        """
        text_lower = self._normalize_text(text)

        for category, compiled_patterns in self.out_of_scope_compiled.items():
            for pattern in compiled_patterns:
                if pattern.search(text_lower):
                    logger.info(f"Out-of-scope detected: {category}")
                    return category

        return None

    def _is_greeting(self, text: str) -> bool:
        """Check if the message is a greeting"""
        text_lower = self._normalize_text(text)

        # Check if it's a short message (likely greeting)
        words = text_lower.split()
        if len(words) <= 3:
            return self._check_patterns(text, GREETING_PATTERNS)

        # For longer messages, only check if it starts with a greeting
        for pattern in GREETING_PATTERNS:
            if text_lower.startswith(pattern.lower()):
                return True

        return False

    def _is_confused(self, text: str) -> bool:
        """Check if student is expressing confusion"""
        return self._check_patterns(text, CONFUSION_PATTERNS)

    def _is_validation_seeking(self, text: str) -> bool:
        """Check if student is seeking validation/approval"""
        return self._check_patterns(text, VALIDATION_PATTERNS)

    def _is_self_reflection(self, text: str) -> bool:
        """Check if student is expressing self-reflection"""
        text_lower = self._normalize_text(text)

        # Check for self-reflection patterns
        if self._check_patterns(text, SELF_REFLECTION_PATTERNS):
            # Make sure it's not also a question
            question_words = ["what", "how", "which", "where", "when", "why", "?"]
            is_question = any(q in text_lower for q in question_words)

            # Self-reflection takes priority if the student is sharing about themselves
            return not is_question or any(
                p.lower() in text_lower
                for p in ["i like", "i love", "i enjoy", "i hate", "i'm good at", "i prefer"]
            )

        return False

    def _is_career_curiosity(self, text: str) -> bool:
        """Check if student is curious about a specific career"""
        return self._check_patterns(text, CAREER_PATTERNS)

    def _is_comparison(self, text: str) -> bool:
        """Check if student is comparing options"""
        return self._check_patterns(text, COMPARISON_PATTERNS)

    def _is_information_seeking(self, text: str) -> bool:
        """Check if student is seeking factual information"""
        return self._check_patterns(text, INFORMATION_PATTERNS)

    def detect_state(
        self,
        user_input: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        student_profile: Optional[Dict[str, Any]] = None
    ) -> ConversationState:
        """
        Detect the current conversation state.

        Args:
            user_input: The student's current message
            conversation_history: List of previous messages in the conversation
            student_profile: Student's profile data (interests, etc.)

        Returns:
            The detected ConversationState

        Priority Order:
        1. OUT_OF_SCOPE
        2. GREETING
        3. CONFUSED
        4. VALIDATION_SEEKING
        5. SELF_REFLECTION
        6. CAREER_CURIOSITY
        7. COMPARISON
        8. INFORMATION_SEEKING
        """
        if not user_input or not user_input.strip():
            return ConversationState.CONFUSED

        # 1. Check for out-of-scope topics first (SAFETY)
        out_of_scope_category = self._check_out_of_scope(user_input)
        if out_of_scope_category:
            logger.info(f"State: OUT_OF_SCOPE ({out_of_scope_category})")
            return ConversationState.OUT_OF_SCOPE

        # 2. Check for greeting
        if self._is_greeting(user_input):
            logger.info("State: GREETING")
            return ConversationState.GREETING

        # 3. Check for confusion (TRUST)
        if self._is_confused(user_input):
            logger.info("State: CONFUSED")
            return ConversationState.CONFUSED

        # 4. Check for validation seeking (TRUST)
        if self._is_validation_seeking(user_input):
            logger.info("State: VALIDATION_SEEKING")
            return ConversationState.VALIDATION_SEEKING

        # 5. Check for self-reflection (AWARENESS)
        if self._is_self_reflection(user_input):
            logger.info("State: SELF_REFLECTION")
            return ConversationState.SELF_REFLECTION

        # 6. Check for comparison (EXPLORATION)
        # Check comparison before career curiosity because comparisons are more specific
        if self._is_comparison(user_input):
            logger.info("State: COMPARISON")
            return ConversationState.COMPARISON

        # 7. Check for career curiosity (EXPLORATION)
        if self._is_career_curiosity(user_input):
            logger.info("State: CAREER_CURIOSITY")
            return ConversationState.CAREER_CURIOSITY

        # 8. Check for information seeking (INFORMATION)
        if self._is_information_seeking(user_input):
            logger.info("State: INFORMATION_SEEKING")
            return ConversationState.INFORMATION_SEEKING

        # Default: Treat as career curiosity (general question about careers)
        # This encourages exploration over confusion
        logger.info("State: CAREER_CURIOSITY (default)")
        return ConversationState.CAREER_CURIOSITY

    def get_state_context(
        self,
        state: ConversationState,
        user_input: str
    ) -> Dict[str, Any]:
        """
        Get additional context for the detected state.

        Args:
            state: The detected conversation state
            user_input: The student's message

        Returns:
            Dict with additional context for response generation
        """
        context = {
            "state": state,
            "state_name": state.name,
            "user_input": user_input
        }

        # Add state-specific context
        if state == ConversationState.OUT_OF_SCOPE:
            context["out_of_scope_category"] = self._check_out_of_scope(user_input)

        elif state == ConversationState.SELF_REFLECTION:
            # Extract what they're reflecting on
            text_lower = user_input.lower()
            if "like" in text_lower or "love" in text_lower or "enjoy" in text_lower:
                context["reflection_type"] = "positive"
            elif "hate" in text_lower or "dislike" in text_lower:
                context["reflection_type"] = "negative"
            elif "good at" in text_lower:
                context["reflection_type"] = "strength"
            elif "bad at" in text_lower:
                context["reflection_type"] = "challenge"
            else:
                context["reflection_type"] = "general"

        elif state == ConversationState.COMPARISON:
            # Try to extract what's being compared
            text_lower = user_input.lower()
            if " vs " in text_lower:
                parts = text_lower.split(" vs ")
                if len(parts) == 2:
                    context["option_a"] = parts[0].strip()
                    context["option_b"] = parts[1].strip()
            elif " or " in text_lower:
                parts = text_lower.split(" or ")
                if len(parts) >= 2:
                    context["option_a"] = parts[0].strip()
                    context["option_b"] = parts[1].strip()

        return context
