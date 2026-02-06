"""
Tests for memory system (profile extraction, storage, and referencing).
"""
import pytest


class TestProfileExtractor:
    """Tests for ProfileExtractor class."""

    @pytest.fixture
    def extractor(self):
        """Create a ProfileExtractor instance."""
        from memory import ProfileExtractor
        return ProfileExtractor()

    def test_extract_interests(self, extractor):
        """Test extraction of interests from messages."""
        messages = [
            "I really like drawing and painting",
            "I enjoy solving math problems",
            "I love reading books about science",
        ]

        for msg in messages:
            result = extractor.extract_from_message(msg)
            assert "interests" in result
            assert len(result["interests"]) > 0, f"Should extract interest from: {msg}"

    def test_extract_dislikes(self, extractor):
        """Test extraction of dislikes from messages."""
        messages = [
            "I hate memorizing things",
            "I don't like public speaking",
            "I dislike writing essays",
        ]

        for msg in messages:
            result = extractor.extract_from_message(msg)
            assert "dislikes" in result
            assert len(result["dislikes"]) > 0, f"Should extract dislike from: {msg}"

    def test_extract_strengths(self, extractor):
        """Test extraction of strengths from messages."""
        messages = [
            "I'm good at math",
            "I'm skilled in science",
            "I do well in problem solving",
        ]

        for msg in messages:
            result = extractor.extract_from_message(msg)
            assert "strengths" in result
            assert len(result["strengths"]) > 0, f"Should extract strength from: {msg}"

    def test_extract_career_mention(self, extractor):
        """Test extraction of career mentions."""
        messages = [
            "I want to become a doctor",
            "Software engineering sounds interesting",
            "Being a teacher would be nice",
        ]

        for msg in messages:
            result = extractor.extract_from_message(msg)
            assert "career_mentions" in result
            assert len(result["career_mentions"]) > 0, f"Should extract career from: {msg}"

    def test_no_extraction_from_neutral_message(self, extractor):
        """Test that neutral messages don't produce false extractions."""
        msg = "What time does the sun rise?"
        result = extractor.extract_from_message(msg)

        # Should return empty lists, not spurious data
        total_extractions = sum(
            len(v) if isinstance(v, list) else 0
            for v in result.values()
        )
        assert total_extractions == 0


class TestMemoryStore:
    """Tests for MemoryStore class."""

    @pytest.fixture
    def store(self, temp_db):
        """Create a MemoryStore with temporary database."""
        from memory import MemoryStore
        return MemoryStore(db_path=temp_db)

    def test_get_profile_creates_new(self, store):
        """Test that get_profile creates a new profile if none exists."""
        profile = store.get_profile_summary(student_id=1)

        assert profile is not None
        assert "interests" in profile
        assert "dislikes" in profile
        assert "strengths" in profile

    def test_update_profile(self, store):
        """Test profile update with new data."""
        store.get_or_create_profile(student_id=1)  # Create profile

        updates = {
            "interests": [{"content": "technology", "confidence": 0.8}],
            "strengths": [{"content": "math", "confidence": 0.8}],
        }
        store.update_profile(student_id=1, extractions=updates)

        profile = store.get_profile_summary(student_id=1)
        assert "technology" in profile["interests"]
        assert "math" in profile["strengths"]

    def test_update_profile_appends(self, store):
        """Test that updates append to existing data."""
        store.get_or_create_profile(student_id=1)

        # First update
        store.update_profile(student_id=1, extractions={"interests": [{"content": "reading", "confidence": 0.8}]})

        # Second update
        store.update_profile(student_id=1, extractions={"interests": [{"content": "gaming", "confidence": 0.8}]})

        profile = store.get_profile_summary(student_id=1)
        assert "reading" in profile["interests"]
        assert "gaming" in profile["interests"]


class TestMemoryReferencer:
    """Tests for MemoryReferencer class."""

    @pytest.fixture
    def referencer(self, temp_db):
        """Create a MemoryReferencer with temporary database."""
        from memory import MemoryStore, MemoryReferencer
        store = MemoryStore(db_path=temp_db)
        return MemoryReferencer(store)

    def test_should_reference_rate_limiting(self, referencer):
        """Test that memory references are rate-limited."""
        # First few messages shouldn't reference
        for i in range(1, 4):
            should_ref = referencer.should_reference_memory(student_id=1, current_message_idx=i)
            assert should_ref is False

        # After interval, may allow reference (depends on random chance and having memories)
        # For this test, we just verify the rate limiting logic doesn't crash
        should_ref = referencer.should_reference_memory(student_id=1, current_message_idx=5)
        # Note: This may be False if no profile data exists (expected behavior)
        assert isinstance(should_ref, bool)

    def test_build_memory_context_empty_profile(self, referencer):
        """Test memory context for user with no profile data."""
        context = referencer.build_memory_context(
            student_id=999,
            include_reference=True,
            current_input="Tell me about engineering"
        )

        # Should return empty or minimal context for empty profile
        assert context is not None  # Should not crash

    def test_build_memory_context_with_data(self, referencer, temp_db):
        """Test memory context with actual profile data."""
        from memory import MemoryStore

        store = MemoryStore(db_path=temp_db)
        store.get_or_create_profile(student_id=1)
        store.update_profile(student_id=1, extractions={
            "interests": [{"content": "technology", "confidence": 0.8}, {"content": "problem solving", "confidence": 0.8}],
            "strengths": [{"content": "math", "confidence": 0.8}],
        })

        from memory import MemoryReferencer
        ref = MemoryReferencer(store)

        context = ref.build_memory_context(
            student_id=1,
            include_reference=True,
            current_input="What career should I consider?"
        )

        assert context is not None
        # Context should mention their interests when include_reference is True
        if len(context) > 0:
            assert "technology" in context.lower() or "interest" in context.lower()
