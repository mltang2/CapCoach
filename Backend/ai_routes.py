"""
AI Integration Routes for CAPcoach
"""

import sys
from pathlib import Path
from flask import Blueprint, request, jsonify
import asyncio
import uuid
import os

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Initialize as None - lazy load
conversation_service = None
emotion_service = None
AI_ENABLED = False
AI_ERROR = None

def initialize_ai_services():
    global conversation_service, emotion_service, AI_ENABLED, AI_ERROR
    
    if conversation_service is not None:
        return
    
    try:
        if not os.getenv('GROQ_API_KEY'):
            AI_ERROR = "GROQ_API_KEY not set"
            print(f"⚠️ AI services disabled: {AI_ERROR}")
            return
        
        from ai.services.groq_conversation_service import GroqConversationalDiagnosisService
        from ai.services.groq_emotional_service import GroqEmotionalIntelligenceService
        
        conversation_service = GroqConversationalDiagnosisService()
        emotion_service = GroqEmotionalIntelligenceService()
        AI_ENABLED = True
        print("✅ AI services loaded")
        
    except Exception as e:
        AI_ERROR = f"Failed to initialize: {e}"
        print(f"⚠️ AI services disabled: {AI_ERROR}")

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/health', methods=['GET'])
def ai_health():
    initialize_ai_services()
    return jsonify({
        "ai_services": "enabled" if AI_ENABLED else "disabled",
        "status": "healthy" if AI_ENABLED else "unavailable",
        "error": AI_ERROR
    })

@ai_bp.route('/session/start', methods=['POST'])
def start_ai_session():
    initialize_ai_services()
    if not AI_ENABLED:
        return jsonify({"error": AI_ERROR or "AI unavailable"}), 503
    
    try:
        user_profile = request.json or {}
        session_data = conversation_service.initiate_diagnostic_conversation(user_profile)
        return jsonify(session_data)
    except Exception as e:
        return jsonify({"error": f"Session failed: {str(e)}"}), 500

@ai_bp.route('/chat/send', methods=['POST'])
def send_ai_message():
    initialize_ai_services()
    if not AI_ENABLED:
        return jsonify({"error": AI_ERROR or "AI unavailable"}), 503
    
    try:
        data = request.json
        response = asyncio.run(conversation_service.process_user_response(
            data.get('session_id'), 
            data.get('message')
        ))
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Message failed: {str(e)}"}), 500

@ai_bp.route('/analyze-emotions', methods=['POST'])
def analyze_emotions():
    initialize_ai_services()
    if not AI_ENABLED:
        return jsonify({"error": AI_ERROR or "AI unavailable"}), 503
    
    try:
        text = request.json.get('text', '')
        emotions = emotion_service.analyze_emotional_content(text)
        return jsonify({
            "text": text,
            "emotional_analysis": emotions,
            "dominant_emotion": max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral"
        })
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

@ai_bp.route('/session/<session_id>/insights', methods=['GET'])
def get_ai_insights(session_id):
    initialize_ai_services()
    if not AI_ENABLED:
        return jsonify({"error": AI_ERROR or "AI unavailable"}), 503
    
    return jsonify({
        "session_id": session_id,
        "emotional_patterns": {"dominant_emotion": "anxious", "confidence": 0.8},
        "financial_behavior": {"pattern": "avoidance", "suggested_strategies": ["Start small", "Automate savings"]},
        "personalized_advice": "Focus on consistent small habits"
    })

