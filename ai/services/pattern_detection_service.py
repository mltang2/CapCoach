# pattern_detection_service.py
from typing import Dict

class PatternDetectionService:
    """
    Detects behavioral patterns like avoidance, impulsivity, and money dyslexia.
    Simple keyword-based scoring.
    """

    def __init__(self):
        self.pattern_keywords = {
            "avoidance": ["ignore", "avoid", "delay", "put off"],
            "impulsivity": ["buy", "spend", "impulse", "urge"],
            "money_dyslexia": ["confused", "mix up", "forget"]
        }

    def detect_patterns(self, text: str) -> Dict[str, float]:
        text_lower = text.lower()
        scores = {pattern: 0.0 for pattern in self.pattern_keywords}

        for pattern, keywords in self.pattern_keywords.items():
            for word in keywords:
                if word in text_lower:
                    scores[pattern] += 1.0

        # Normalize scores
        max_score = max(scores.values()) or 1.0
        for k in scores:
            scores[k] = scores[k] / max_score

        return scores
