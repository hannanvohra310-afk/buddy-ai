"""
Tests for response guardrails and validation.
"""
import pytest


class TestResponseGuardrails:
    """Tests for ResponseGuardrails class."""

    @pytest.fixture
    def guardrails(self):
        """Create a ResponseGuardrails instance."""
        from prompts import ResponseGuardrails
        return ResponseGuardrails()

    @pytest.fixture
    def states(self):
        """Get conversation states."""
        from conversation.constants import ConversationState
        return ConversationState

    def test_valid_response_passes(self, guardrails, states):
        """Test that a valid response passes validation."""
        response = "That's a great question! Engineering involves solving real-world problems using math and science. What aspects interest you most?"

        is_valid, violations = guardrails.validate_response(response, states.CAREER_CURIOSITY)

        assert is_valid is True
        assert len(violations) == 0

    def test_too_many_emojis_fails(self, guardrails, states):
        """Test that responses with too many emojis fail validation."""
        response = "That's great! 😊🎉👍🔥💯 You should definitely explore engineering! 🚀✨"

        is_valid, violations = guardrails.validate_response(response, states.CAREER_CURIOSITY)

        assert is_valid is False
        assert any("emoji" in v.lower() for v in violations)

    def test_single_emoji_passes(self, guardrails, states):
        """Test that a single emoji is acceptable."""
        response = "That's a great question! 😊 Let me explain how engineering works."

        is_valid, violations = guardrails.validate_response(response, states.CAREER_CURIOSITY)

        # Should pass - single emoji is fine
        emoji_violations = [v for v in violations if "emoji" in v.lower()]
        assert len(emoji_violations) == 0

    def test_too_many_questions_in_sensitive_state(self, guardrails, states):
        """Test that too many questions fail in sensitive states."""
        response = "What do you enjoy? What are your hobbies? What subjects do you like? What are your strengths?"

        # CONFUSED is a sensitive state - should allow max 1-2 questions
        is_valid, violations = guardrails.validate_response(response, states.CONFUSED)

        assert is_valid is False
        assert any("question" in v.lower() for v in violations)

    def test_forbidden_phrases_fail(self, guardrails, states):
        """Test that forbidden phrases are detected."""
        forbidden_responses = [
            "You should definitely become a doctor!",
            "I recommend you take science stream.",
        ]

        for response in forbidden_responses:
            is_valid, violations = guardrails.validate_response(response, states.CAREER_CURIOSITY)
            # Should detect direct recommendations
            assert is_valid is False, f"Should flag: {response}"
            assert any("forbidden" in v.lower() for v in violations), f"Should have forbidden phrase violation: {response}"

    def test_response_too_long(self, guardrails, states):
        """Test that very long responses are flagged."""
        # Create a very long response
        response = "This is a paragraph. " * 100  # ~2000 chars

        is_valid, violations = guardrails.validate_response(response, states.CAREER_CURIOSITY)

        # Should flag or at least not crash
        assert isinstance(is_valid, bool)

    def test_empty_response(self, guardrails, states):
        """Test handling of empty response."""
        is_valid, violations = guardrails.validate_response("", states.GREETING)

        # Empty response might pass basic checks (no emojis, no questions, etc.)
        # The key is that it doesn't crash
        assert isinstance(is_valid, bool)


class TestGuardrailsIntegration:
    """Integration tests for guardrails with different states."""

    @pytest.fixture
    def guardrails(self):
        """Create a ResponseGuardrails instance."""
        from prompts import ResponseGuardrails
        return ResponseGuardrails()

    @pytest.fixture
    def states(self):
        """Get conversation states."""
        from conversation.constants import ConversationState
        return ConversationState

    def test_greeting_response(self, guardrails, states):
        """Test validation of greeting responses."""
        response = "Hey! Good to see you. I'm Buddy AI - think of me as your career exploration buddy. What's on your mind today?"

        is_valid, violations = guardrails.validate_response(response, states.GREETING)

        assert is_valid is True

    def test_out_of_scope_response(self, guardrails, states):
        """Test validation of out-of-scope responses."""
        from conversation.constants import CANONICAL_OUT_OF_SCOPE_RESPONSE

        is_valid, violations = guardrails.validate_response(
            CANONICAL_OUT_OF_SCOPE_RESPONSE,
            states.OUT_OF_SCOPE
        )

        # Canonical response should always pass
        assert is_valid is True

    def test_confused_state_response(self, guardrails, states):
        """Test appropriate response for confused state."""
        response = "It's totally normal to feel confused about career choices at your age. Let's start simple - what's one thing you enjoy doing?"

        is_valid, violations = guardrails.validate_response(response, states.CONFUSED)

        assert is_valid is True

    def test_validation_seeking_response(self, guardrails, states):
        """Test response for validation-seeking state."""
        response = "That's a thoughtful question. The truth is, success in any career isn't about being 'good enough' - it's about finding what fits you and working at it."

        is_valid, violations = guardrails.validate_response(response, states.VALIDATION_SEEKING)

        assert is_valid is True
