# scoring_utils.py
"""
Utility functions for normalizing or aggregating scores.
"""

from typing import Dict

def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize a dictionary of scores to 0-1 scale.
    """
    if not scores:
        return {}
    max_score = max(scores.values())
    if max_score == 0:
        return scores
    return {k: v / max_score for k, v in scores.items()}

def aggregate_scores(existing: Dict[str, float], new: Dict[str, float]) -> Dict[str, float]:
    """
    Incrementally add new scores to an existing dictionary.
    """
    result = existing.copy()
    for k, v in new.items():
        result[k] = result.get(k, 0) + v
    return result
