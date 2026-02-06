"""Response validation and guardrails for Buddy AI"""
import re
import logging
from typing import Tuple, List, Optional
from conversation.constants import ConversationState

logger = logging.getLogger(__name__)


class ResponseGuardrails:
    """
    Validates responses against Buddy AI's guidelines.

    Checks:
    - Question count (max 1-2 depending on state)
    - Emoji count (max 1)
    - No direct career recommendations
    - Response length (2-4 paragraphs)
    - No forbidden phrases
    """

    # Forbidden phrases that indicate direct recommendations
    FORBIDDEN_RECOMMENDATION_PHRASES = [
        "you should become",
        "you should be a",
        "you would be a great",
        "you would make a great",
        "you are suited for",
        "you're suited for",
        "you are perfect for",
        "you're perfect for",
        "i recommend",
        "i suggest you become",
        "you should pursue",
        "you should definitely",
        "you must become"
    ]

    # Forbidden corporate/coaching language
    FORBIDDEN_CORPORATE_PHRASES = [
        "unlock your potential",
        "chase your dreams",
        "synergy",
        "leverage your",
        "optimize your",
        "maximize your",
        "strategic career",
        "career trajectory",
        "professional development",
        "skill acquisition",
        "paradigm shift"
    ]

    # Forbidden judgmental phrases
    FORBIDDEN_JUDGMENTAL_PHRASES = [
        "you're not smart enough",
        "you're not good enough",
        "that's a bad choice",
        "that's a wrong choice",
        "you shouldn't",
        "that's unrealistic",
        "you can't become"
    ]

    def __init__(self):
        self.emoji_pattern = re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F700-\U0001F77F"  # alchemical symbols
            "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
            "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
            "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
            "\U0001FA00-\U0001FA6F"  # Chess Symbols
            "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
            "\U00002702-\U000027B0"  # Dingbats
            "\U000024C2-\U0001F251"
            "]+"
        )

    def count_questions(self, text: str) -> int:
        """Count the number of questions in a response"""
        # Count question marks
        question_marks = text.count('?')

        # Also look for question patterns without marks
        question_patterns = [
            r'\bwhat\b.*$',
            r'\bhow\b.*$',
            r'\bwhy\b.*$',
            r'\bwould you\b',
            r'\bdo you\b',
            r'\bcan you\b',
            r'\btell me\b'
        ]

        # Question marks are the primary indicator
        return question_marks

    def count_emojis(self, text: str) -> int:
        """Count the number of emojis in a response"""
        emojis = self.emoji_pattern.findall(text)
        return len(emojis)

    def count_paragraphs(self, text: str) -> int:
        """Count the number of paragraphs in a response"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        return len(paragraphs)

    def check_forbidden_phrases(self, text: str) -> List[str]:
        """Check for forbidden phrases in the response"""
        text_lower = text.lower()
        found_phrases = []

        all_forbidden = (
            self.FORBIDDEN_RECOMMENDATION_PHRASES +
            self.FORBIDDEN_CORPORATE_PHRASES +
            self.FORBIDDEN_JUDGMENTAL_PHRASES
        )

        for phrase in all_forbidden:
            if phrase in text_lower:
                found_phrases.append(phrase)

        return found_phrases

    def validate_response(
        self,
        response: str,
        state: ConversationState
    ) -> Tuple[bool, List[str]]:
        """
        Validate a response against all guardrails.

        Args:
            response: The response text to validate
            state: The current conversation state

        Returns:
            Tuple of (is_valid, list_of_violations)
        """
        violations = []

        # 1. Check question count
        question_count = self.count_questions(response)
        max_questions = 1 if state in [
            ConversationState.CONFUSED,
            ConversationState.VALIDATION_SEEKING,
            ConversationState.SELF_REFLECTION
        ] else 2

        if state == ConversationState.OUT_OF_SCOPE:
            max_questions = 0

        if question_count > max_questions:
            violations.append(
                f"Too many questions: {question_count} (max {max_questions} for {state.name})"
            )

        # 2. Check emoji count
        emoji_count = self.count_emojis(response)
        if emoji_count > 1:
            violations.append(f"Too many emojis: {emoji_count} (max 1)")

        # 3. Check for forbidden phrases
        forbidden = self.check_forbidden_phrases(response)
        if forbidden:
            violations.append(f"Forbidden phrases found: {', '.join(forbidden)}")

        # 4. Check response length
        paragraph_count = self.count_paragraphs(response)
        if paragraph_count > 5:
            violations.append(f"Response too long: {paragraph_count} paragraphs (max 5)")

        # 5. For OUT_OF_SCOPE, check if canonical response is used
        if state == ConversationState.OUT_OF_SCOPE:
            expected_start = "I'm sorry — I don't have the right context"
            if not response.strip().startswith(expected_start):
                violations.append("OUT_OF_SCOPE must use canonical response")

        is_valid = len(violations) == 0

        if not is_valid:
            logger.warning(f"Response validation failed: {violations}")

        return is_valid, violations

    def suggest_fixes(self, response: str, violations: List[str]) -> str:
        """
        Suggest how to fix violations (for logging/debugging).

        Args:
            response: The original response
            violations: List of violations found

        Returns:
            String with suggestions
        """
        suggestions = []

        for violation in violations:
            if "Too many questions" in violation:
                suggestions.append(
                    "- Reduce number of questions. Keep only the most important one."
                )
            elif "Too many emojis" in violation:
                suggestions.append(
                    "- Remove extra emojis. Use at most one emoji per response."
                )
            elif "Forbidden phrases" in violation:
                suggestions.append(
                    "- Rewrite to avoid direct recommendations or corporate language."
                )
            elif "too long" in violation:
                suggestions.append(
                    "- Shorten response. Offer to go deeper instead of providing all info."
                )
            elif "canonical response" in violation:
                suggestions.append(
                    "- For out-of-scope topics, use the exact canonical response."
                )

        return "\n".join(suggestions)

    def get_max_questions_for_state(self, state: ConversationState) -> int:
        """Get the maximum allowed questions for a state"""
        if state == ConversationState.OUT_OF_SCOPE:
            return 0
        elif state in [
            ConversationState.CONFUSED,
            ConversationState.VALIDATION_SEEKING,
            ConversationState.SELF_REFLECTION
        ]:
            return 1
        else:
            return 2
