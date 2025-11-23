from pydantic import BaseModel
from typing import Optional, List, Dict
from datetime import datetime


class DisorderInsights(BaseModel):
    """
    Stores the scores for various disorders and identifies the dominant one.
    """
    avoidance_score: float
    impulsivity_score: float
    anxiety_score: float
    money_dyslexia_score: float
    dominant_disorder: Optional[str] = None  # can be calculated later

    def calculate_dominant_disorder(self) -> str:
        """
        Determines the dominant disorder based on scores.
        Uses a fixed priority order for tie-breaking.
        """
        scores = {
            "avoidance": self.avoidance_score,
            "impulsivity": self.impulsivity_score,
            "anxiety": self.anxiety_score,
            "money_dyslexia": self.money_dyslexia_score
        }

        max_score = max(scores.values())
        priority = ["anxiety", "avoidance", "impulsivity", "money_dyslexia"]

        for disorder in priority:
            if scores[disorder] == max_score:
                self.dominant_disorder = disorder
                break

        return self.dominant_disorder


class DiagnosisSummary(BaseModel):
    """
    Stores the overall diagnosis for a session.
    """
    session_id: str
    timestamp: datetime = datetime.utcnow()
    disorder_insights: DisorderInsights
    suggested_actions: Optional[List[str]] = None
    pattern_observations: Optional[Dict[str, float]] = None
    emotional_trends: Optional[Dict[str, float]] = None

    def update_dominant_disorder(self) -> str:
        """
        Updates the dominant disorder in the disorder_insights.
        """
        return self.disorder_insights.calculate_dominant_disorder()

print("File Ran!")

print("File Ran!")

print("File Ran!")