# emotions.py
# ----------------
# Models for storing emotional analysis results.
# No AI logic here—just data structures.

from pydantic import BaseModel
from typing import List, Optional


class EmotionalAnalysis(BaseModel):
    """
    Represents the emotional analysis of a single aspect of a message.
    """
    tone: str                  # e.g., "anxious", "happy"
    intensity: float           # e.g., 0.0 - 1.0
    keywords: List[str]        # words that triggered this emotion


class MessageEmotions(BaseModel):
    """
    Stores all detected emotions for a single user message.
    """
    message_id: str
    emotions: List[EmotionalAnalysis]

    def dominant_emotion(self) -> Optional[EmotionalAnalysis]:
        """
        Returns the emotion with the highest intensity.
        If no emotions detected, returns None.
        """
        if not self.emotions:
            return None
        return max(self.emotions, key=lambda e: e.intensity)


class SessionEmotions(BaseModel):
    """
    Aggregates emotional analysis across a session.
    """
    session_id: str
    message_emotions: List[MessageEmotions] = []

    def add_message_emotions(self, msg_emotions: MessageEmotions):
        """
        Add emotions from a new message to the session.
        """
        self.message_emotions.append(msg_emotions)

    def overall_dominant_emotion(self) -> Optional[EmotionalAnalysis]:
        """
        Returns the overall dominant emotion in the session based on intensity.
        """
        all_emotions = [e for msg in self.message_emotions for e in msg.emotions]
        if not all_emotions:
            return None
        return max(all_emotions, key=lambda e: e.intensity)
