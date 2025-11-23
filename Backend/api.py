from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import os
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / 'ai' / '.env')

# Add project root to path to import AI module
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

app = Flask(__name__)
CORS(app)

# Initialize AI services as None first
conversation_service = None
emotion_service = None
AI_ENABLED = False

# Debug: Check if API key is loaded
print(f"🔑 GROQ_API_KEY loaded: {'Yes' if os.getenv('GROQ_API_KEY') else 'No'}")

def initialize_ai_services():
    global conversation_service, emotion_service, AI_ENABLED
    
    if conversation_service is not None:
        return
    
    try:
        # Check for API key
        if not os.getenv('GROQ_API_KEY'):
            print("⚠️ GROQ_API_KEY not set - AI services disabled")
            return
        
        from ai.services.groq_conversation_service import GroqConversationalDiagnosisService
        from ai.services.groq_emotional_service import GroqEmotionalIntelligenceService
        
        conversation_service = GroqConversationalDiagnosisService()
        emotion_service = GroqEmotionalIntelligenceService()
        AI_ENABLED = True
        print("✅ Real AI services loaded successfully!")
        
    except ImportError as e:
        print(f"⚠️ AI modules not found: {e}")
    except Exception as e:
        print(f"⚠️ Failed to initialize AI services: {e}")

# Initialize on import
initialize_ai_services()

# Your existing routes here...
@app.route('/')
def home():
    return jsonify({"message": "CAPcoach API", "status": "running", "ai_enabled": AI_ENABLED})

@app.route('/api/health')
def health():
    return jsonify({"status": "healthy", "ai_services": "enabled" if AI_ENABLED else "disabled"})

# AI Routes using REAL services
@app.route('/api/ai/health', methods=['GET'])
def ai_health():
    return jsonify({
        "ai_services": "enabled" if AI_ENABLED else "disabled",
        "status": "healthy" if AI_ENABLED else "unavailable"
    })

@app.route('/api/ai/session/start', methods=['POST'])
def ai_session_start():
    if not AI_ENABLED:
        return jsonify({"error": "AI services not available. Check GROQ_API_KEY."}), 503
    
    try:
        user_profile = request.json or {}
        session_data = conversation_service.initiate_diagnostic_conversation(user_profile)
        return jsonify(session_data)
    except Exception as e:
        return jsonify({"error": f"Session start failed: {str(e)}"}), 500

@app.route('/api/ai/chat/send', methods=['POST'])
def ai_chat_send():
    if not AI_ENABLED:
        return jsonify({"error": "AI services not available"}), 503
    
    try:
        data = request.json
        session_id = data.get('session_id')
        message = data.get('message')
        
        response = asyncio.run(conversation_service.process_user_response(session_id, message))
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": f"Message processing failed: {str(e)}"}), 500

@app.route('/api/ai/analyze-emotions', methods=['POST'])
def analyze_emotions():
    if not AI_ENABLED:
        return jsonify({"error": "AI services not available"}), 503
    
    try:
        data = request.json
        text = data.get('text', '')
        emotions = emotion_service.analyze_emotional_content(text)
        return jsonify({
            "text": text,
            "emotional_analysis": emotions,
            "dominant_emotion": max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral"
        })
    except Exception as e:
        return jsonify({"error": f"Emotion analysis failed: {str(e)}"}), 500

# Add your financial routes here (they should work regardless of AI status)
@app.route('/api/financial/risk-score', methods=['GET'])
def risk_score():
    return jsonify({
        "risk_score": 45,
        "risk_level": "Medium",
        "message": "Risk score calculated successfully"
    })

@app.route('/api/financial/predict', methods=['POST'])
def predict():
    data = request.get_json() or {}
    additional_savings = data.get('additional_monthly_savings', 0)
    
    return jsonify({
        "current_net_worth": 25000.0,
        "predicted_net_worth_12mo": 28750.0,
        "net_worth_growth": 3750.0,
        "growth_percentage": 15.0,
        "additional_savings": additional_savings,
        "message": "Prediction generated successfully"
    })
@app.route('/api/test', methods=['GET'])
def test():
    return jsonify({"message": "Test endpoint is working!", "status": "success"})

# Lightweight video generation stub
@app.route('/api/ai/generate-video/<session_id>', methods=['POST'])
def generate_video_summary(session_id):
    """
    Stub endpoint that pretends to generate a video and returns a text path.
    This keeps the UI video button functional without heavy dependencies.
    """
    try:
        video_path = f"videos/capcoach_{session_id}.txt"
        return jsonify({
            "success": True,
            "video_path": video_path,
            "message": "Personalized financial guide created!",
            "pattern": "balanced",
            "session_id": session_id
        })
    except Exception as e:
        return jsonify({"error": f"Video generation failed: {str(e)}"}), 500

if __name__ == '__main__':
    print("🚀 CAPcoach Backend with REAL AI Services")
    print("📍 AI Status:", "ENABLED" if AI_ENABLED else "DISABLED")
    app.run(port=5001, debug=True)
