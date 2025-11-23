"""
CAPcoach AI Services
"""

from .emotional_intelligence_service import EmotionalIntelligenceService
from .pattern_detection_service import PatternDetectionService
from .conversational_diagnosis_service import ConversationalDiagnosisService

# Conditionally import Groq services if available
try:
    from .groq_emotional_service import GroqEmotionalIntelligenceService
    from .groq_conversation_service import GroqConversationalDiagnosisService
    GROQ_AVAILABLE = True
except ImportError:
    GROQ_AVAILABLE = False

__all__ = [
    'EmotionalIntelligenceService',
    'PatternDetectionService', 
    'ConversationalDiagnosisService'
]

if GROQ_AVAILABLE:
    __all__.extend([
        'GroqEmotionalIntelligenceService',
        'GroqConversationalDiagnosisService'
    ])