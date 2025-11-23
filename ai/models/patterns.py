# patterns.py
# ----------------
# Models for storing pattern detection results.
# No AI logic here—just data structures.

from pydantic import BaseModel
from typing import List, Optional


class Pattern(BaseModel):
    """
    Represents a single detected pattern in a message.
    """
    type: str          # e.g., "avoidance_detected", "impulse_spending"
    score: float       # e.g., 0.0 - 1.0


class MessagePatterns(BaseModel):
    """
    Stores all detected patterns for a single message.
    """
    message_id: str
    patterns: List[Pattern]

    def dominant_pattern(self) -> Optional[Pattern]:
        """
        Returns the pattern with the highest score.
        If no patterns detected, returns None.
        """
        if not self.patterns:
            return None
        return max(self.patterns, key=lambda p: p.score)


class SessionPatterns(BaseModel):
    """
    Aggregates pattern detection results across a session.
    """
    session_id: str
    message_patterns: List[MessagePatterns] = []

    def add_message_patterns(self, msg_patterns: MessagePatterns):
        """
        Add patterns from a new message to the session.
        """
        self.message_patterns.append(msg_patterns)

    def aggregate_scores(self) -> dict:
        """
        Returns a dict of pattern types with total scores across the session.
        """
        summary = {}
        for msg in self.message_patterns:
            for pattern in msg.patterns:
                summary[pattern.type] = summary.get(pattern.type, 0) + pattern.score
        return summary

    def dominant_pattern_overall(self) -> Optional[Pattern]:
        """
        Returns the highest scoring pattern across the session.
        """
        all_patterns = [p for msg in self.message_patterns for p in msg.patterns]
        if not all_patterns:
            return None
        return max(all_patterns, key=lambda p: p.score)
