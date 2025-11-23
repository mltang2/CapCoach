# conversation_state_manager.py
# ----------------
# Tracks full conversation context, session-level emotions, patterns, and progress.

from typing import Dict, List, Optional
from ai.models.conversation import ConversationTurn, ConversationContext
from ai.models.emotions import SessionEmotions
from ai.models.patterns import SessionPatterns


class ConversationStateManager:
    """
    Manages all active conversation sessions and state.
    """

    def __init__(self):
        # session_id -> ConversationContext
        self.sessions: Dict[str, ConversationContext] = {}

    # ---------------------------------------------------------
    def create_session(self, session_id: str):
        """
        Initialize a new conversation context for a session.
        """
        self.sessions[session_id] = ConversationContext(session_id=session_id)

    # ---------------------------------------------------------
    def add_turn(self, session_id: str, turn: ConversationTurn):
        """
        Add a new turn (user or AI) to the session.
        Updates patterns and emotions automatically.
        """
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} does not exist.")
        
        session.add_turn(turn)  # This will handle all the pattern/emotion updates

    def last_user_message(self, session_id: str) -> Optional[ConversationTurn]:
        """
        Return the last user message in this session.
        """
        session = self.sessions.get(session_id)
        if not session:
            return None
        return session.last_user_message()

    def get_recent_turns(self, session_id: str, n: int = 5) -> List[ConversationTurn]:
        """
        Return the last n turns for AI prompting.
        """
        session = self.sessions.get(session_id)
        if not session:
            return []
        return session.get_recent_context(n)

    def determine_next_question(self, session_id: str) -> Dict:
        """
        Decide the next question type based on detected patterns/emotions.
        """
        session = self.sessions.get(session_id)
        if not session or not session.turns:
            return {"type": "general", "question_text": "Tell me more about your finances."}
        
        # Simple logic based on patterns
        if session.detected_patterns_summary:
            dominant_pattern = max(session.detected_patterns_summary.items(), key=lambda x: x[1])[0]
            questions = {
                "avoidance": "What makes you want to avoid dealing with money?",
                "impulsivity": "What triggers your impulse spending?",
                "money_dyslexia": "What parts of money management feel confusing?"
            }
            return {"type": dominant_pattern, "question_text": questions.get(dominant_pattern, "Can you tell me more?")}
        
        return {"type": "general", "question_text": "How does that make you feel?"}

    def track_diagnostic_progress(self, session_id: str) -> float:
        """
        Return a progress score based on number of turns or completed sections.
        """
        session = self.sessions.get(session_id)
        if not session:
            return 0.0
        
        # Simple progress based on number of turns
        max_turns = 10  # Assume 10 turns for complete diagnosis
        progress = min(len(session.turns) / max_turns, 1.0)
        return progress
