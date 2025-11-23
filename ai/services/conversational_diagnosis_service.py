# conversational_diagnosis_service.py
from typing import Dict
import uuid
from ai.services.emotional_intelligence_service import EmotionalIntelligenceService
from ai.services.pattern_detection_service import PatternDetectionService
from ai.state.conversation_state_manager import ConversationStateManager
from ai.models.conversation import ConversationTurn

class ConversationalDiagnosisService:
    """
    Orchestrates the full diagnostic conversation.
    """

    def __init__(self):
        self.emotion_service = EmotionalIntelligenceService()
        self.pattern_service = PatternDetectionService()
        self.state_manager = ConversationStateManager()

    def initiate_diagnostic_conversation(self, user_context: Dict) -> Dict:
        session_id = str(uuid.uuid4())
        welcome = "Hi! I'm CAPcoach. Let's explore your financial habits together."
        first_question = "How would you describe your current relationship with money?"

        self.state_manager.create_session(session_id)

        return {
            "session_id": session_id,
            "welcome_message": welcome,
            "first_question": first_question
        }

    async def process_user_response(self, session_id: str, user_message: str) -> Dict:
        # Step 1: Analyze emotion
        emotional_data = self.emotion_service.analyze_emotional_content(user_message)

        # Step 2: Detect patterns
        detected_patterns = self.pattern_service.detect_patterns(user_message)

        # Step 3: Update conversation state
        self.state_manager.add_turn(
            session_id,
            ConversationTurn(
                speaker="user",
                text=user_message,
                emotions=emotional_data,
                patterns=detected_patterns
            )
        )

        # Step 4: Determine next question
        next_question_info = self.state_manager.determine_next_question(session_id)

        # Step 5: Generate AI response
        ai_reply = await self.generate_empathetic_response(
            user_message,
            emotional_data,
            detected_patterns,
            next_question_info["question_text"]
        )

        # Step 6: Add AI turn to conversation history
        self.state_manager.add_turn(
            session_id,
            ConversationTurn(
                speaker="ai",
                text=ai_reply
            )
        )

        # Step 7: Track progress
        progress = self.state_manager.track_diagnostic_progress(session_id)

        return {
            "ai_response": ai_reply,
            "diagnostic_insights": detected_patterns,
            "next_question_type": next_question_info["type"],
            "conversation_progress": progress
        }

    async def generate_empathetic_response(
        self,
        user_message: str,
        emotional_data: Dict,
        patterns: Dict,
        next_question: str
    ) -> str:
        # Simple rule-based example
        dominant_emotion = max(emotional_data, key=emotional_data.get)
        response = (
            f"I hear that you're feeling {dominant_emotion}. "
            f"I notice patterns like {', '.join([k for k,v in patterns.items() if v>0])}. "
            f"Next, {next_question}"
        )
        return response
