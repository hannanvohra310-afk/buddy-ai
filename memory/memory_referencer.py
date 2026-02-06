"""Generate natural memory references for conversation"""
import random
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from .memory_store import MemoryStore

logger = logging.getLogger(__name__)


class MemoryReferencer:
    """
    Generates natural references to past conversations.

    Rules:
    - Max 1 reference per 5 messages (rate limiting)
    - Only reference if relevant to current topic
    - Memory is felt, never displayed as data
    - References should feel natural, not robotic
    """

    # Natural reference templates
    REFERENCE_TEMPLATES = {
        "interest": [
            "Earlier you mentioned you enjoy {content}...",
            "I remember you said you like {content}...",
            "You told me before that you find {content} interesting...",
            "Since you mentioned enjoying {content}...",
        ],
        "dislike": [
            "I know you mentioned not enjoying {content}...",
            "Since you said {content} isn't really your thing...",
            "You mentioned before that you don't particularly like {content}...",
        ],
        "strength": [
            "You mentioned being good at {content}...",
            "Since you said you're skilled at {content}...",
            "I remember you saying you do well in {content}...",
        ],
        "challenge": [
            "You mentioned finding {content} challenging...",
            "Since you said {content} is difficult for you...",
        ],
        "career": [
            "Last time we talked about {content}...",
            "When we discussed {content} before...",
            "You seemed interested in {content} earlier...",
        ]
    }

    def __init__(
        self,
        memory_store: MemoryStore,
        min_messages_between_refs: int = 5
    ):
        """
        Initialize memory referencer.

        Args:
            memory_store: MemoryStore instance
            min_messages_between_refs: Minimum messages between memory references
        """
        self.memory_store = memory_store
        self.min_messages_between = min_messages_between_refs

        # Track last reference for each student
        self._last_reference_message_idx: Dict[int, int] = {}

    def should_reference_memory(
        self,
        student_id: int,
        current_message_idx: int,
        current_topic: Optional[str] = None
    ) -> bool:
        """
        Determine if we should reference a memory in this response.

        Args:
            student_id: The student's ID
            current_message_idx: Current message index in conversation
            current_topic: Current topic being discussed (optional)

        Returns:
            True if we should include a memory reference
        """
        # Check rate limiting
        last_ref_idx = self._last_reference_message_idx.get(student_id, -self.min_messages_between)

        if current_message_idx - last_ref_idx < self.min_messages_between:
            logger.debug(f"Rate limited: {current_message_idx - last_ref_idx} msgs since last ref")
            return False

        # Check if we have relevant memories
        profile_summary = self.memory_store.get_profile_summary(student_id)

        has_memories = (
            profile_summary.get("interests") or
            profile_summary.get("dislikes") or
            profile_summary.get("strengths") or
            profile_summary.get("careers_discussed")
        )

        if not has_memories:
            return False

        # Random chance to include reference (don't always reference)
        # This makes it feel more natural
        return random.random() < 0.4  # 40% chance when eligible

    def get_relevant_reference(
        self,
        student_id: int,
        current_topic: Optional[str] = None,
        current_input: Optional[str] = None
    ) -> Optional[Tuple[str, str]]:
        """
        Get a relevant memory reference for the current context.

        Args:
            student_id: The student's ID
            current_topic: Current topic being discussed
            current_input: Current user input

        Returns:
            Tuple of (reference_text, memory_type) or None if no relevant memory
        """
        profile_summary = self.memory_store.get_profile_summary(student_id)

        # Try to find a relevant memory based on current context
        current_context = (current_topic or "") + " " + (current_input or "")
        current_context_lower = current_context.lower()

        # Check for career relevance first
        for career in profile_summary.get("careers_discussed", []):
            if career.lower() in current_context_lower:
                reference = self._generate_reference("career", career)
                return (reference, "career")

        # Check for interest relevance
        for interest in profile_summary.get("interests", []):
            if self._is_relevant(interest, current_context_lower):
                reference = self._generate_reference("interest", interest)
                return (reference, "interest")

        # Check for strength relevance
        for strength in profile_summary.get("strengths", []):
            if self._is_relevant(strength, current_context_lower):
                reference = self._generate_reference("strength", strength)
                return (reference, "strength")

        # If no specific relevance, maybe reference a general interest
        if profile_summary.get("interests") and random.random() < 0.3:
            interest = random.choice(profile_summary["interests"])
            reference = self._generate_reference("interest", interest)
            return (reference, "interest")

        return None

    def _is_relevant(self, memory_content: str, current_context: str) -> bool:
        """Check if a memory is relevant to current context"""
        # Simple keyword overlap check
        memory_words = set(memory_content.lower().split())
        context_words = set(current_context.split())

        # Check for any meaningful word overlap
        overlap = memory_words & context_words
        # Filter out common words
        common_words = {"i", "the", "a", "an", "is", "are", "was", "were", "to", "in", "on", "at", "for"}
        meaningful_overlap = overlap - common_words

        return len(meaningful_overlap) > 0

    def _generate_reference(self, memory_type: str, content: str) -> str:
        """Generate a natural reference sentence"""
        templates = self.REFERENCE_TEMPLATES.get(memory_type, self.REFERENCE_TEMPLATES["interest"])
        template = random.choice(templates)
        return template.format(content=content)

    def record_reference_used(self, student_id: int, message_idx: int):
        """Record that a memory reference was used"""
        self._last_reference_message_idx[student_id] = message_idx
        logger.debug(f"Recorded reference at message {message_idx} for student {student_id}")

    def build_memory_context(
        self,
        student_id: int,
        include_reference: bool = False,
        current_topic: Optional[str] = None,
        current_input: Optional[str] = None
    ) -> str:
        """
        Build memory context for the system prompt.

        Args:
            student_id: The student's ID
            include_reference: Whether to include a memory reference
            current_topic: Current topic being discussed
            current_input: Current user input

        Returns:
            Memory context string for prompt
        """
        profile_summary = self.memory_store.get_profile_summary(student_id)

        context_parts = []

        # Add known information (for LLM context, not for display)
        if profile_summary.get("interests"):
            interests_str = ", ".join(profile_summary["interests"][:5])
            context_parts.append(f"Student's interests: {interests_str}")

        if profile_summary.get("dislikes"):
            dislikes_str = ", ".join(profile_summary["dislikes"][:3])
            context_parts.append(f"Student's dislikes: {dislikes_str}")

        if profile_summary.get("strengths"):
            strengths_str = ", ".join(profile_summary["strengths"][:3])
            context_parts.append(f"Student's strengths: {strengths_str}")

        if profile_summary.get("careers_discussed"):
            careers_str = ", ".join(profile_summary["careers_discussed"][:5])
            context_parts.append(f"Careers previously discussed: {careers_str}")

        # Add reference instruction if applicable
        if include_reference:
            reference = self.get_relevant_reference(student_id, current_topic, current_input)
            if reference:
                context_parts.append(f"\nYou may naturally reference: '{reference[0]}'")
                context_parts.append("(Only use this if it fits naturally in your response)")

        if context_parts:
            return "\n".join(context_parts)

        return ""
