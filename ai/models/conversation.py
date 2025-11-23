"""
conversation.py
----------------
Model classes for managing conversation turns and the overall
conversation context for CAPcoach.

This file defines the core data structures for storing conversation history,
emotional analysis results, and pattern detection results.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime

# Import emotion and pattern models
from .emotions import EmotionalAnalysis, MessageEmotions, SessionEmotions
from .patterns import Pattern, MessagePatterns, SessionPatterns


class ConversationTurn(BaseModel):
    """
    Represents a single message in the conversation between user and AI.
    
    Each turn captures:
    - Who spoke (user or AI)
    - What was said
    - Emotional analysis results (if available)
    - Pattern detection results (if available)
    - When the message occurred
    
    This is the fundamental building block of conversation history.
    
    Example:
    --------
    >>> user_turn = ConversationTurn(
    ...     speaker="user",
    ...     text="I feel anxious about checking my bank account",
    ...     emotions={"anxiety": 0.8, "fear": 0.6},
    ...     patterns={"avoidance": 0.7, "financial_anxiety": 0.9}
    ... )
    """
    
    speaker: str = Field(..., description="Either 'user' or 'ai'")
    text: str = Field(..., description="The actual message content")
    emotions: Optional[Dict[str, float]] = Field(
        None, 
        description="Emotion analysis results from EmotionalIntelligenceService"
    )
    patterns: Optional[Dict[str, float]] = Field(
        None,
        description="Pattern detection results from PatternDetectionService"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this message was created"
    )


class ConversationContext(BaseModel):
    """
    Tracks the complete state of a diagnostic conversation session.
    
    This class serves as the central repository for all conversation data,
    including:
    - Complete message history
    - Running emotional analysis summaries
    - Running pattern detection summaries  
    - Session-level emotion and pattern tracking
    
    This context is passed to all AI services for analysis and decision-making.
    
    Fields:
    -------
    session_id : str
        Unique identifier for this diagnostic session
        
    turns : List[ConversationTurn]
        Chronological record of all messages in the conversation
        
    emotional_state_summary : Optional[Dict]
        Aggregated emotional analysis across all turns
        
    detected_patterns_summary : Optional[Dict] 
        Aggregated pattern detection across all turns
        
    session_emotions : Optional[SessionEmotions]
        Structured emotional analysis at session level
        
    session_patterns : Optional[SessionPatterns]
        Structured pattern detection at session level
    """
    
    session_id: str = Field(..., description="Unique session identifier")
    turns: List[ConversationTurn] = Field(default=[], description="All conversation messages")
    emotional_state_summary: Optional[Dict[str, float]] = Field(
        None, 
        description="Running summary of emotional states across conversation"
    )
    detected_patterns_summary: Optional[Dict[str, float]] = Field(
        None,
        description="Running summary of detected patterns across conversation"
    )
    session_emotions: Optional[SessionEmotions] = Field(
        None,
        description="Structured session-level emotional analysis"
    )
    session_patterns: Optional[SessionPatterns] = Field(
        None,
        description="Structured session-level pattern detection"
    )

    def add_turn(self, turn: ConversationTurn) -> None:
        """
        Add a new conversation turn and update all summaries.
        
        This is the main method for adding messages to the conversation.
        It automatically:
        - Validates the turn
        - Updates emotional summaries
        - Updates pattern summaries
        - Maintains session-level tracking
        
        Parameters:
        -----------
        turn : ConversationTurn
            The conversation turn to add
            
        Example:
        --------
        >>> context = ConversationContext(session_id="test_123")
        >>> user_turn = ConversationTurn(speaker="user", text="I'm worried about money")
        >>> context.add_turn(user_turn)
        >>> len(context.turns)
        1
        """
        # Validate and add the turn to history
        if turn.speaker in ('user', 'ai') and turn.text.strip():
            self.turns.append(turn)
        
        # Process emotional data if available
        if turn.emotions:
            self._update_emotional_analysis(turn)
        
        # Process pattern data if available  
        if turn.patterns:
            self._update_pattern_analysis(turn)

    def _update_emotional_analysis(self, turn: ConversationTurn) -> None:
        """
        Update emotional analysis summaries with data from a new turn.
        
        This internal method:
        - Updates the simple emotional state summary (dict-based)
        - Maintains the structured session emotions (SessionEmotions)
        
        Parameters:
        -----------
        turn : ConversationTurn
            The turn containing emotional data to process
        """
        # Initialize emotional state summary if needed
        if self.emotional_state_summary is None:
            self.emotional_state_summary = {}
        
        # Convert turn emotions to EmotionalAnalysis objects
        message_emotions_list = []
        for emotion_type, intensity in turn.emotions.items():
            # Add to simple summary (aggregate scores)
            if emotion_type in self.emotional_state_summary:
                self.emotional_state_summary[emotion_type] += intensity
            else:
                self.emotional_state_summary[emotion_type] = intensity
            
            # Create structured emotion object
            emotion_analysis = EmotionalAnalysis(
                tone=emotion_type,
                intensity=intensity,
                keywords=[]  # Could be populated with triggering words
            )
            message_emotions_list.append(emotion_analysis)
        
        # Update structured session emotions
        if self.session_emotions is None:
            self.session_emotions = SessionEmotions(session_id=self.session_id)
        
        # Create message-level emotions and add to session
        msg_emotions = MessageEmotions(
            message_id=str(turn.timestamp),
            emotions=message_emotions_list
        )
        self.session_emotions.add_message_emotions(msg_emotions)

    def _update_pattern_analysis(self, turn: ConversationTurn) -> None:
        """
        Update pattern detection summaries with data from a new turn.
        
        This internal method:
        - Updates the simple pattern summary (dict-based)
        - Maintains the structured session patterns (SessionPatterns)
        
        Parameters:
        -----------
        turn : ConversationTurn
            The turn containing pattern data to process
        """
        # Initialize pattern summary if needed
        if self.detected_patterns_summary is None:
            self.detected_patterns_summary = {}
        
        # Update simple pattern summary
        for pattern_type, score in turn.patterns.items():
            if pattern_type in self.detected_patterns_summary:
                self.detected_patterns_summary[pattern_type] += score
            else:
                self.detected_patterns_summary[pattern_type] = score
        
        # Update structured session patterns
        if self.session_patterns is None:
            self.session_patterns = SessionPatterns(session_id=self.session_id)
        
        # Convert turn patterns to Pattern objects
        pattern_objects = [
            Pattern(type=pattern_type, score=score)
            for pattern_type, score in turn.patterns.items()
        ]
        
        # Create message-level patterns and add to session
        msg_patterns = MessagePatterns(
            message_id=str(turn.timestamp),
            patterns=pattern_objects
        )
        self.session_patterns.add_message_patterns(msg_patterns)

    def last_user_message(self) -> Optional[ConversationTurn]:
        """
        Get the most recent message from the user.
        
        This is useful for services that need to analyze only the user's
        most recent input without processing the entire conversation history.
        
        Returns:
        --------
        Optional[ConversationTurn]
            The last user message, or None if no user messages exist
            
        Example:
        --------
        >>> context = ConversationContext(session_id="test_123")
        >>> user_turn = ConversationTurn(speaker="user", text="Hello")
        >>> context.add_turn(user_turn)
        >>> context.last_user_message().text
        'Hello'
        """
        # Search backwards through turns to find the most recent user message
        for turn in reversed(self.turns):
            if turn.speaker == 'user':
                return turn
        return None

    def get_recent_context(self, n: int = 5) -> List[ConversationTurn]:
        """
        Get the most recent conversation turns for context.
        
        This method is particularly useful for AI services that need
        recent conversation history to generate context-aware responses.
        
        Parameters:
        -----------
        n : int, default=5
            Number of recent turns to return
            
        Returns:
        --------
        List[ConversationTurn]
            The last n turns from the conversation
            
        Example:
        --------
        >>> context = ConversationContext(session_id="test_123")
        >>> # Add several turns...
        >>> recent = context.get_recent_context(3)
        >>> len(recent)  # Returns up to 3 most recent turns
        3
        """
        if not self.turns:
            return []
        
        # Return the last n turns (or all turns if fewer than n exist)
        return self.turns[-n:]

    def get_conversation_length(self) -> int:
        """
        Get the total number of turns in the conversation.
        
        Returns:
        --------
        int
            Number of conversation turns
            
        Example:
        --------
        >>> context = ConversationContext(session_id="test_123")
        >>> context.add_turn(ConversationTurn(speaker="user", text="Hi"))
        >>> context.get_conversation_length()
        1
        """
        return len(self.turns)

    def get_user_turns(self) -> List[ConversationTurn]:
        """
        Get all turns from the user.
        
        Returns:
        --------
        List[ConversationTurn]
            All user messages in chronological order
            
        Example:
        --------
        >>> context = ConversationContext(session_id="test_123")
        >>> context.add_turn(ConversationTurn(speaker="user", text="Hi"))
        >>> context.add_turn(ConversationTurn(speaker="ai", text="Hello"))
        >>> user_turns = context.get_user_turns()
        >>> len(user_turns)
        1
        """
        return [turn for turn in self.turns if turn.speaker == 'user']

    def get_ai_turns(self) -> List[ConversationTurn]:
        """
        Get all turns from the AI.
        
        Returns:
        --------
        List[ConversationTurn]
            All AI responses in chronological order
        """
        return [turn for turn in self.turns if turn.speaker == 'ai']

    def clear_conversation(self) -> None:
        """
        Clear all conversation history while preserving session ID.
        
        This can be useful for testing or for starting a fresh conversation
        within the same session context.
        
        Example:
        --------
        >>> context = ConversationContext(session_id="test_123")
        >>> context.add_turn(ConversationTurn(speaker="user", text="Hi"))
        >>> context.clear_conversation()
        >>> len(context.turns)
        0
        """
        self.turns.clear()
        self.emotional_state_summary = None
        self.detected_patterns_summary = None
        self.session_emotions = None
        self.session_patterns = None
