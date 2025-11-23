# emotional_intelligence_service.py
from typing import Dict

class EmotionalIntelligenceService:
    """
    Analyzes textual input and returns structured emotional data.
    Simple rule-based implementation.
    """

    def __init__(self):
        # Define some basic keywords for emotions
        self.emotion_keywords = {
            "anxious": ["worried", "nervous", "scared", "anxious"],
            "happy": ["happy", "joy", "excited", "pleased"],
            "sad": ["sad", "unhappy", "depressed", "down"],
            "angry": ["angry", "mad", "frustrated", "upset"]
        }

    def analyze_emotional_content(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        scores = {emotion: 0.0 for emotion in self.emotion_keywords}

        for emotion, keywords in self.emotion_keywords.items():
            for word in keywords:
                if word in text_lower:
                    scores[emotion] += 1.0

        # Normalize scores to 0–1
        max_score = max(scores.values()) or 1.0
        for k in scores:
            scores[k] = scores[k] / max_score

        return scores
