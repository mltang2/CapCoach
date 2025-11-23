# prompt_utils.py
"""
Helper functions to build prompts for AI models.
"""

from typing import Dict

def build_empathy_prompt(user_message: str, emotions: Dict[str, float], patterns: Dict[str, float], next_question: str) -> str:
    """
    Builds a system/user prompt string for generating empathetic responses.
    """
    prompt = f"""
User message: {user_message}
Detected emotions: {emotions}
Detected patterns: {patterns}
Next question to ask: {next_question}

Write an empathetic, conversational response:
- Validate the user's emotions
- Explain detected patterns gently
- Transition smoothly into the follow-up question
"""
    return prompt
