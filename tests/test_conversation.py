"""
Tests for conversation state detection and response generation.
"""
import pytest


class TestConversationState:
    """Tests for ConversationState enum."""

    def test_all_states_exist(self, conversation_states):
        """Test that all expected states are defined."""
        expected_states = [
            "OUT_OF_SCOPE",
            "CONFUSED",
            "VALIDATION_SEEKING",
            "SELF_REFLECTION",
            "CAREER_CURIOSITY",
            "COMPARISON",
            "INFORMATION_SEEKING",
            "GREETING",
        ]

        for state_name in expected_states:
            assert hasattr(conversation_states, state_name), f"Missing state: {state_name}"


class TestStateDetector:
    """Tests for StateDetector class."""

    @pytest.fixture
    def detector(self):
        """Create a StateDetector instance."""
        from conversation import StateDetector
        return StateDetector()

    def test_detect_greeting(self, detector, conversation_states):
        """Test detection of greeting messages."""
        greetings = ["Hi", "Hello", "Hey there", "Good morning", "Hi buddy"]

        for msg in greetings:
            state = detector.detect_state(msg, [])
            assert state == conversation_states.GREETING, f"Failed for: {msg}"

    def test_detect_out_of_scope(self, detector, conversation_states):
        """Test detection of out-of-scope messages."""
        # These messages should be detected as out of scope
        # Using patterns from OUT_OF_SCOPE_PATTERNS in constants.py
        out_of_scope = [
            "I'm feeling depressed",
            "I have a crush",
            "I want to die",
        ]

        for msg in out_of_scope:
            state = detector.detect_state(msg, [])
            assert state == conversation_states.OUT_OF_SCOPE, f"Failed for: {msg}"

    def test_detect_confused(self, detector, conversation_states):
        """Test detection of confused state."""
        confused_msgs = [
            "I don't know what to do",
            "I'm so confused about everything",
            "I have no idea what career to choose",
            "I'm lost",
        ]

        for msg in confused_msgs:
            state = detector.detect_state(msg, [])
            assert state == conversation_states.CONFUSED, f"Failed for: {msg}"

    def test_detect_validation_seeking(self, detector, conversation_states):
        """Test detection of validation-seeking messages."""
        validation_msgs = [
            "Am I good enough to be a doctor?",
            "Can I become an engineer?",
            "Do you think I can make it?",
            "Is it possible for me to be a scientist?",
        ]

        for msg in validation_msgs:
            state = detector.detect_state(msg, [])
            assert state == conversation_states.VALIDATION_SEEKING, f"Failed for: {msg}"

    def test_detect_self_reflection(self, detector, conversation_states):
        """Test detection of self-reflection messages."""
        reflection_msgs = [
            "I like drawing",
            "I enjoy solving puzzles",
            "I hate memorizing things",
            "I'm good at math",
        ]

        for msg in reflection_msgs:
            state = detector.detect_state(msg, [])
            assert state == conversation_states.SELF_REFLECTION, f"Failed for: {msg}"

    def test_detect_career_curiosity(self, detector, conversation_states):
        """Test detection of career curiosity messages."""
        career_msgs = [
            "What does a software engineer do?",
            "Tell me about being a doctor",
            "How do I become a lawyer?",
            "What is data science?",
        ]

        for msg in career_msgs:
            state = detector.detect_state(msg, [])
            assert state == conversation_states.CAREER_CURIOSITY, f"Failed for: {msg}"

    def test_detect_comparison(self, detector, conversation_states):
        """Test detection of comparison messages."""
        comparison_msgs = [
            "Science or Commerce?",
            "Which is better, engineering or medicine?",
            "Doctor vs Engineer",
            "Arts vs Science stream",
        ]

        for msg in comparison_msgs:
            state = detector.detect_state(msg, [])
            assert state == conversation_states.COMPARISON, f"Failed for: {msg}"

    def test_detect_information_seeking(self, detector, conversation_states):
        """Test detection of information-seeking messages."""
        info_msgs = [
            "What is the fee for IIT?",
            "When is the JEE exam?",
            "What are the top engineering colleges?",
            "What's the salary of a data scientist?",
        ]

        for msg in info_msgs:
            state = detector.detect_state(msg, [])
            assert state == conversation_states.INFORMATION_SEEKING, f"Failed for: {msg}"

    def test_state_priority_out_of_scope_first(self, detector, conversation_states):
        """Test that OUT_OF_SCOPE takes priority over other states."""
        # Message that could be both out of scope and career related
        msg = "I'm depressed about my career choices"
        state = detector.detect_state(msg, [])
        assert state == conversation_states.OUT_OF_SCOPE


class TestResponseGenerator:
    """Tests for ResponseGenerator class."""

    @pytest.fixture
    def generator(self):
        """Create a ResponseGenerator instance."""
        from conversation import ResponseGenerator
        return ResponseGenerator()

    def test_build_state_instructions_returns_string(self, generator, conversation_states):
        """Test that build_state_instructions returns a string for all states."""
        for state in conversation_states:
            instructions = generator.build_state_instructions(state)
            assert isinstance(instructions, str)
            assert len(instructions) > 0

    def test_confused_state_instructions(self, generator, conversation_states):
        """Test instructions for confused state mention normalization."""
        instructions = generator.build_state_instructions(conversation_states.CONFUSED)
        # Should include guidance about normalizing confusion
        assert "normal" in instructions.lower() or "pressure" in instructions.lower()


class TestCanonicalResponse:
    """Tests for canonical out-of-scope response."""

    def test_canonical_response_exists(self):
        """Test that canonical out-of-scope response is defined."""
        from conversation.constants import CANONICAL_OUT_OF_SCOPE_RESPONSE

        assert CANONICAL_OUT_OF_SCOPE_RESPONSE is not None
        assert len(CANONICAL_OUT_OF_SCOPE_RESPONSE) > 0

    def test_canonical_response_content(self):
        """Test that canonical response contains key phrases."""
        from conversation.constants import CANONICAL_OUT_OF_SCOPE_RESPONSE

        # Should mention it can't help with this topic
        assert "sorry" in CANONICAL_OUT_OF_SCOPE_RESPONSE.lower() or "don't" in CANONICAL_OUT_OF_SCOPE_RESPONSE.lower()
        # Should redirect to appropriate help
        assert "teacher" in CANONICAL_OUT_OF_SCOPE_RESPONSE.lower() or "parent" in CANONICAL_OUT_OF_SCOPE_RESPONSE.lower()
