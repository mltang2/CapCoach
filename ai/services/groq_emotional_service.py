# ai/services/groq_emotional_service.py
import os
import json
from openai import OpenAI
from ai.config import config, select_model

class GroqEmotionalIntelligenceService:
    """
    Uses Groq API for advanced emotional analysis
    """
    
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv("GROQ_API_KEY"),
            base_url=os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
        )
    
    def analyze_emotional_content(self, text: str) -> dict:
        """
        Use Groq to analyze emotions in text with sophisticated understanding
        """
        # Fallback to local implementation if Groq not selected
        if select_model("emotion_analysis") != "groq":
            from ai.services.emotional_intelligence_service import EmotionalIntelligenceService
            local_service = EmotionalIntelligenceService()
            return local_service.analyze_emotional_content(text)
        
        try:
            prompt = f"""
            Analyze the emotional content of this text about finances and return ONLY a JSON object with emotion scores between 0 and 1:
            
            Text: "{text}"
            
            Consider these emotions: anxious, happy, sad, angry, fearful, overwhelmed, confident, hopeful, stressed, calm
            
            Return format: {{"emotion1": score, "emotion2": score}}
            Example: {{"anxious": 0.8, "overwhelmed": 0.6, "stressed": 0.7}}
            
            Only return the JSON object, nothing else.
            """
            
            response = self.client.chat.completions.create(
                model=config.groq_chat_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=200
            )
            
            # Parse the JSON response
            result_text = response.choices[0].message.content.strip()
            result = json.loads(result_text)
            print(f"🎭 Groq Emotion Analysis: {result}")
            return result
            
        except Exception as e:
            print(f"❌ Groq emotion analysis failed: {e}")
            # Fallback to local implementation
            from ai.services.emotional_intelligence_service import EmotionalIntelligenceService
            local_service = EmotionalIntelligenceService()
            return local_service.analyze_emotional_content(text)