"""Response generation based on conversation state"""
import logging
from typing import List, Dict, Any, Optional

from .constants import (
    ConversationState,
    CANONICAL_OUT_OF_SCOPE_RESPONSE,
    STATE_GUIDELINES
)

logger = logging.getLogger(__name__)


class ResponseGenerator:
    """
    Generates state-aware context and guidelines for LLM responses.

    This class doesn't generate responses directly but provides
    the necessary context and constraints for the LLM to generate
    appropriate responses based on the conversation state.
    """

    def get_state_prompt_context(
        self,
        state: ConversationState,
        user_input: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        student_profile: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get the prompt context for a given state.

        Args:
            state: The detected conversation state
            user_input: The student's message
            conversation_history: Previous messages
            student_profile: Student's profile data

        Returns:
            Dict containing prompt context and guidelines
        """
        guidelines = STATE_GUIDELINES.get(state, STATE_GUIDELINES[ConversationState.CAREER_CURIOSITY])

        context = {
            "state": state.name,
            "goal": guidelines["goal"],
            "do_guidelines": guidelines["do"],
            "dont_guidelines": guidelines["dont"],
            "max_questions": guidelines["max_questions"],
            "user_input": user_input
        }

        # Add history context if available
        if conversation_history:
            context["has_history"] = True
            context["history_length"] = len(conversation_history)
        else:
            context["has_history"] = False

        # Add profile context if available
        if student_profile:
            context["has_profile"] = True
            if student_profile.get("interests"):
                context["known_interests"] = student_profile["interests"]
            if student_profile.get("dislikes"):
                context["known_dislikes"] = student_profile["dislikes"]
        else:
            context["has_profile"] = False

        return context

    def get_canonical_response(self, state: ConversationState) -> Optional[str]:
        """
        Get the canonical response for a state if one exists.

        Some states have locked responses that must be used verbatim.

        Args:
            state: The conversation state

        Returns:
            The canonical response string, or None if no canonical response
        """
        if state == ConversationState.OUT_OF_SCOPE:
            return CANONICAL_OUT_OF_SCOPE_RESPONSE

        return None

    def should_use_canonical_response(self, state: ConversationState) -> bool:
        """
        Check if a state requires using the canonical response.

        Args:
            state: The conversation state

        Returns:
            True if canonical response should be used
        """
        return state == ConversationState.OUT_OF_SCOPE

    def build_state_instructions(self, state: ConversationState) -> str:
        """
        Build detailed instructions for the LLM based on state.

        Args:
            state: The conversation state

        Returns:
            Instruction string to include in the prompt
        """
        guidelines = STATE_GUIDELINES.get(state, STATE_GUIDELINES[ConversationState.CAREER_CURIOSITY])

        instructions = f"""
CURRENT CONVERSATION STATE: {state.name}
GOAL: {guidelines['goal']}

YOU MUST:
{chr(10).join(f"- {item}" for item in guidelines['do'])}

YOU MUST NOT:
{chr(10).join(f"- {item}" for item in guidelines['dont'])}

QUESTION LIMIT: Ask at most {guidelines['max_questions']} question(s) in your response.
"""

        # Add state-specific additional instructions
        if state == ConversationState.CONFUSED:
            instructions += """
ADDITIONAL CONTEXT:
The student is feeling confused or overwhelmed. Your primary job is to make them feel comfortable and reduce pressure. Don't try to solve their confusion immediately - just help them feel okay about being confused.

EXAMPLE RESPONSE STYLE:
"Hey, it's totally normal to feel a bit confused about this stuff. Most people your age feel the same way. What's one thing you enjoy doing, even if it seems small?"
"""

        elif state == ConversationState.VALIDATION_SEEKING:
            instructions += """
ADDITIONAL CONTEXT:
The student is seeking approval or permission. They may feel insecure about their choices or abilities. Never confirm or deny their ability - instead, reframe the conversation toward exploration.

EXAMPLE RESPONSE STYLE:
"That's a really thoughtful question. The truth is, careers aren't about being 'good enough' - they're about finding what fits you. What draws you to thinking about this?"
"""

        elif state == ConversationState.SELF_REFLECTION:
            instructions += """
ADDITIONAL CONTEXT:
The student is sharing something about themselves - their interests, dislikes, or self-perception. This is valuable! Acknowledge what they've shared, reflect it back, and gently explore it. Don't jump to career suggestions yet.

EXAMPLE RESPONSE STYLE:
"That's really interesting that you enjoy [what they said]. Can you tell me more about what specifically you like about it?"
"""

        elif state == ConversationState.CAREER_CURIOSITY:
            instructions += """
ADDITIONAL CONTEXT:
The student wants to learn about a career or profession. Focus on what the day-to-day work actually looks like - not prestige, not salary. Help them imagine what it would FEEL like to do this job.

EXAMPLE RESPONSE STYLE:
"[Career] is actually pretty interesting! On a typical day, someone in this role would... What part of this sounds interesting to you?"
"""

        elif state == ConversationState.COMPARISON:
            instructions += """
ADDITIONAL CONTEXT:
The student is comparing two or more options. Your job is to explain trade-offs neutrally, not to recommend one over the other. Help them think about which aspects matter more to THEM.

EXAMPLE RESPONSE STYLE:
"Both of these are great paths, but they're quite different. [Option A] tends to be more... while [Option B] is more about... Which of these aspects matters more to you?"
"""

        elif state == ConversationState.INFORMATION_SEEKING:
            instructions += """
ADDITIONAL CONTEXT:
The student wants factual information (exams, fees, colleges, etc.). Give them the key facts concisely, but don't overwhelm them with data. Offer to go deeper if they're interested.

EXAMPLE RESPONSE STYLE:
"For [topic], the basics are... Would you like me to explain more about any of these?"
"""

        elif state == ConversationState.GREETING:
            instructions += """
ADDITIONAL CONTEXT:
The student is greeting you. Be warm and welcoming, like an older sibling. Introduce yourself briefly and invite them to share what's on their mind about careers or their future.

EXAMPLE RESPONSE STYLE:
"Hey! Good to see you. I'm Buddy AI - think of me as your career exploration buddy. What's on your mind today?"
"""

        return instructions

    def get_response_constraints(self, state: ConversationState) -> Dict[str, Any]:
        """
        Get constraints that should be applied to any response.

        Args:
            state: The conversation state

        Returns:
            Dict of constraints for response validation
        """
        guidelines = STATE_GUIDELINES.get(state, STATE_GUIDELINES[ConversationState.CAREER_CURIOSITY])

        return {
            "max_questions": guidelines["max_questions"],
            "max_emojis": 1,  # Max 1 emoji per response
            "max_paragraphs": 4,  # Keep responses focused
            "require_question": state not in [
                ConversationState.OUT_OF_SCOPE,
                ConversationState.INFORMATION_SEEKING
            ],
            "use_canonical": self.should_use_canonical_response(state)
        }
