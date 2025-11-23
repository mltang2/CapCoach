# ai/services/groq_conversation_service.py
import os
import asyncio
from openai import OpenAI
from ai.config import config, select_model
from ai.state.conversation_state_manager import ConversationStateManager
from ai.models.conversation import ConversationTurn

class GroqConversationalDiagnosisService:
    """
    Uses Groq API for intelligent financial conversations
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        )
        self.state_manager = ConversationStateManager()
        self.emotion_service = None
        self.pattern_service = None
    
    def initiate_diagnostic_conversation(self, user_context: dict) -> dict:
        """Start a new diagnostic session"""
        import uuid
        session_id = str(uuid.uuid4())
        
        # Use Groq for the initial greeting if configured
        if select_model("conversation") == "groq":
            try:
                prompt = f"""
                Create a warm, empathetic greeting for a financial coaching session.
                User: {user_context.get('name', 'User')}
                Context: Starting financial wellness conversation
                
                Return a friendly greeting that introduces you as CAPcoach and invites them to share about their financial habits.
                """
                
                response = self.client.chat.completions.create(
                    model=config.groq_chat_model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    max_tokens=100
                )
                welcome_message = response.choices[0].message.content
                first_question = "How would you describe your current relationship with money?"
            except:
                welcome_message = "Hi! I'm CAPcoach. Let's explore your financial habits together."
                first_question = "How would you describe your current relationship with money?"
        else:
            welcome_message = "Hi! I'm CAPcoach. Let's explore your financial habits together."
            first_question = "How would you describe your current relationship with money?"
        
        self.state_manager.create_session(session_id)
        
        return {
            "session_id": session_id,
            "welcome_message": welcome_message,
            "first_question": first_question
        }
    
    async def process_user_response(self, session_id: str, user_message: str) -> dict:
        """
        Use Groq to generate empathetic, context-aware responses
        """
        # Fallback to local implementation if Groq not selected
        if select_model("conversation") != "groq":
            from ai.services.conversational_diagnosis_service import ConversationalDiagnosisService
            local_service = ConversationalDiagnosisService()
            return await local_service.process_user_response(session_id, user_message)
        
        try:
            # Get conversation history for context
            recent_turns = self.state_manager.get_recent_turns(session_id, 5)
            context = "\n".join([f"{turn.speaker}: {turn.text}" for turn in recent_turns])
            
            # Initialize emotion and pattern services if needed
            if not self.emotion_service:
                from ai.services.emotional_intelligence_service import EmotionalIntelligenceService
                self.emotion_service = EmotionalIntelligenceService()
            if not self.pattern_service:
                from ai.services.pattern_detection_service import PatternDetectionService
                self.pattern_service = PatternDetectionService()
            
            # Analyze current message
            emotions = self.emotion_service.analyze_emotional_content(user_message)
            patterns = self.pattern_service.detect_patterns(user_message)
            
            prompt = f"""
            You are CAPcoach, a compassionate financial therapist AI. You're having a conversation about money habits and financial wellness.
            
            Recent conversation context:
            {context}
            
            User's latest message: "{user_message}"
            
            Detected emotions: {emotions}
            Detected financial patterns: {patterns}
            
            Your role:
            - Show deep empathy and understanding of financial emotions
            - Ask insightful, gentle questions to uncover financial patterns
            - Provide supportive guidance, not direct financial advice
            - Help users understand their relationship with money
            - Keep responses conversational, warm, and encouraging
            - Validate their feelings and experiences
            
            Respond naturally and continue the conversation in a supportive way.
            """
            
            response = self.client.chat.completions.create(
                model=config.groq_chat_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=300
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation state
            self.state_manager.add_turn(session_id, ConversationTurn(
                speaker="user", 
                text=user_message,
                emotions=emotions,
                patterns=patterns
            ))
            self.state_manager.add_turn(session_id, ConversationTurn(
                speaker="ai", 
                text=ai_response
            ))
            
            return {
                "ai_response": ai_response,
                "diagnostic_insights": patterns,
                "next_question_type": "follow_up",
                "conversation_progress": self.state_manager.track_diagnostic_progress(session_id)
            }
            
        except Exception as e:
            print(f"❌ Groq conversation failed: {e}")
            # Fallback to local implementation
            from ai.services.conversational_diagnosis_service import ConversationalDiagnosisService
            local_service = ConversationalDiagnosisService()
            return await local_service.process_user_response(session_id, user_message)