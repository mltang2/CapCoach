"""
CAPcoach AI Package
AI-powered financial coaching with emotional intelligence
"""

__version__ = "1.0.0"
__author__ = "CAPcoach Team"

# Package-level imports for easy access
from ai.models import ConversationTurn, ConversationContext, DiagnosisSummary
from ai.services import (
    EmotionalIntelligenceService, 
    PatternDetectionService,
    ConversationalDiagnosisService
)

__all__ = [
    'ConversationTurn',
    'ConversationContext', 
    'DiagnosisSummary',
    'EmotionalIntelligenceService',
    'PatternDetectionService', 
    'ConversationalDiagnosisService'
]