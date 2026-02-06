"""Database storage for student profiles and conversation memories"""
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

logger = logging.getLogger(__name__)

Base = declarative_base()


class StudentProfile(Base):
    """Student profile model for storing extracted preferences"""
    __tablename__ = 'student_profiles'

    id = Column(Integer, primary_key=True, autoincrement=True)
    student_id = Column(Integer, nullable=False, unique=True, index=True)

    # JSON fields for flexible storage
    interests_json = Column(Text, default="[]")
    dislikes_json = Column(Text, default="[]")
    strengths_json = Column(Text, default="[]")
    challenges_json = Column(Text, default="[]")
    career_mentions_json = Column(Text, default="[]")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    memories = relationship("ConversationMemory", back_populates="profile")

    @property
    def interests(self) -> List[Dict]:
        return json.loads(self.interests_json) if self.interests_json else []

    @interests.setter
    def interests(self, value: List[Dict]):
        self.interests_json = json.dumps(value)

    @property
    def dislikes(self) -> List[Dict]:
        return json.loads(self.dislikes_json) if self.dislikes_json else []

    @dislikes.setter
    def dislikes(self, value: List[Dict]):
        self.dislikes_json = json.dumps(value)

    @property
    def strengths(self) -> List[Dict]:
        return json.loads(self.strengths_json) if self.strengths_json else []

    @strengths.setter
    def strengths(self, value: List[Dict]):
        self.strengths_json = json.dumps(value)

    @property
    def challenges(self) -> List[Dict]:
        return json.loads(self.challenges_json) if self.challenges_json else []

    @challenges.setter
    def challenges(self, value: List[Dict]):
        self.challenges_json = json.dumps(value)

    @property
    def career_mentions(self) -> List[Dict]:
        return json.loads(self.career_mentions_json) if self.career_mentions_json else []

    @career_mentions.setter
    def career_mentions(self, value: List[Dict]):
        self.career_mentions_json = json.dumps(value)


class ConversationMemory(Base):
    """Individual conversation memories"""
    __tablename__ = 'conversation_memories'

    id = Column(Integer, primary_key=True, autoincrement=True)
    profile_id = Column(Integer, ForeignKey('student_profiles.id'), nullable=False)

    memory_type = Column(String(50), nullable=False)  # interest, dislike, strength, career, topic
    content = Column(Text, nullable=False)
    context = Column(Text)  # Original context where this was mentioned
    confidence = Column(Float, default=0.8)

    chat_id = Column(String(100))  # Which chat this came from
    message_index = Column(Integer)  # Which message in the chat

    created_at = Column(DateTime, default=datetime.utcnow)
    last_referenced = Column(DateTime)  # When was this last referenced in conversation

    profile = relationship("StudentProfile", back_populates="memories")


class MemoryStore:
    """Handles storage and retrieval of student memories"""

    def __init__(self, db_path: str = "data/buddy_ai.db"):
        """
        Initialize memory store.

        Args:
            db_path: Path to SQLite database
        """
        self.engine = create_engine(f"sqlite:///{db_path}", echo=False)
        Base.metadata.create_all(self.engine)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_or_create_profile(self, student_id: int) -> StudentProfile:
        """
        Get or create a student profile.

        Args:
            student_id: The student's ID

        Returns:
            StudentProfile object
        """
        profile = self.session.query(StudentProfile).filter_by(student_id=student_id).first()

        if not profile:
            profile = StudentProfile(student_id=student_id)
            self.session.add(profile)
            self.session.commit()
            logger.info(f"Created new profile for student {student_id}")

        return profile

    def update_profile(
        self,
        student_id: int,
        extractions: Dict[str, List[Dict[str, Any]]]
    ) -> StudentProfile:
        """
        Update a student's profile with new extractions.

        Args:
            student_id: The student's ID
            extractions: Dict with interests, dislikes, strengths, challenges, career_mentions

        Returns:
            Updated StudentProfile
        """
        profile = self.get_or_create_profile(student_id)

        # Merge new data with existing
        if extractions.get("interests"):
            existing = profile.interests
            profile.interests = self._merge_items(existing, extractions["interests"])

        if extractions.get("dislikes"):
            existing = profile.dislikes
            profile.dislikes = self._merge_items(existing, extractions["dislikes"])

        if extractions.get("strengths"):
            existing = profile.strengths
            profile.strengths = self._merge_items(existing, extractions["strengths"])

        if extractions.get("challenges"):
            existing = profile.challenges
            profile.challenges = self._merge_items(existing, extractions["challenges"])

        if extractions.get("career_mentions"):
            existing = profile.career_mentions
            profile.career_mentions = self._merge_items(existing, extractions["career_mentions"])

        self.session.commit()
        logger.info(f"Updated profile for student {student_id}")

        return profile

    def _merge_items(
        self,
        existing: List[Dict],
        new: List[Dict]
    ) -> List[Dict]:
        """Merge new items into existing list, avoiding duplicates"""
        # Create a dict keyed by content for deduplication
        merged = {}

        for item in existing:
            key = item.get("content", item.get("career", "")).lower()
            merged[key] = item

        for item in new:
            key = item.get("content", item.get("career", "")).lower()
            if key not in merged or item.get("confidence", 0) > merged[key].get("confidence", 0):
                merged[key] = item

        return list(merged.values())

    def add_memory(
        self,
        student_id: int,
        memory_type: str,
        content: str,
        context: Optional[str] = None,
        confidence: float = 0.8,
        chat_id: Optional[str] = None,
        message_index: Optional[int] = None
    ) -> ConversationMemory:
        """
        Add a specific memory entry.

        Args:
            student_id: The student's ID
            memory_type: Type of memory (interest, dislike, strength, career, topic)
            content: The actual memory content
            context: Original context where mentioned
            confidence: Confidence score (0-1)
            chat_id: ID of the chat this came from
            message_index: Which message in the chat

        Returns:
            Created ConversationMemory
        """
        profile = self.get_or_create_profile(student_id)

        memory = ConversationMemory(
            profile_id=profile.id,
            memory_type=memory_type,
            content=content,
            context=context,
            confidence=confidence,
            chat_id=chat_id,
            message_index=message_index
        )

        self.session.add(memory)
        self.session.commit()

        return memory

    def get_profile_summary(self, student_id: int) -> Dict[str, Any]:
        """
        Get a summary of a student's profile.

        Args:
            student_id: The student's ID

        Returns:
            Dict with profile summary
        """
        profile = self.get_or_create_profile(student_id)

        return {
            "student_id": student_id,
            "interests": [i.get("content") for i in profile.interests if i.get("content")],
            "dislikes": [d.get("content") for d in profile.dislikes if d.get("content")],
            "strengths": [s.get("content") for s in profile.strengths if s.get("content")],
            "challenges": [c.get("content") for c in profile.challenges if c.get("content")],
            "careers_discussed": [
                c.get("career") for c in profile.career_mentions
                if c.get("career") and c.get("sentiment") != "negative"
            ],
            "last_updated": profile.updated_at.isoformat() if profile.updated_at else None
        }

    def get_memories_for_context(
        self,
        student_id: int,
        memory_types: Optional[List[str]] = None,
        limit: int = 10
    ) -> List[ConversationMemory]:
        """
        Get recent memories for context building.

        Args:
            student_id: The student's ID
            memory_types: Filter by memory types
            limit: Maximum memories to return

        Returns:
            List of ConversationMemory objects
        """
        profile = self.get_or_create_profile(student_id)

        query = self.session.query(ConversationMemory).filter_by(profile_id=profile.id)

        if memory_types:
            query = query.filter(ConversationMemory.memory_type.in_(memory_types))

        query = query.order_by(ConversationMemory.created_at.desc()).limit(limit)

        return query.all()

    def mark_memory_referenced(self, memory_id: int):
        """Mark a memory as having been referenced in conversation"""
        memory = self.session.query(ConversationMemory).filter_by(id=memory_id).first()
        if memory:
            memory.last_referenced = datetime.utcnow()
            self.session.commit()

    def close(self):
        """Close database connection"""
        self.session.close()
