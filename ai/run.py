#!/usr/bin/env python3
"""
CAPcoach - Main Application
AI-powered financial coaching with emotional intelligence
"""

import os
import asyncio
import sys
from pathlib import Path

# FIX: Add project root to Python path
current_file = Path(__file__)
project_root = current_file.parent.parent  # Go up to CapCoach/
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from ai.config import config, get_groq_client
from ai.services.groq_conversation_service import GroqConversationalDiagnosisService
from ai.services.groq_emotional_service import GroqEmotionalIntelligenceService
from ai.video_generation_service import VideoGenerationService

class CAPcoach:
    """Main CAPcoach application class"""
    
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Initialize services
        self.conversation_service = GroqConversationalDiagnosisService()
        self.emotion_service = GroqEmotionalIntelligenceService()
        self.video_service = VideoGenerationService()
        
        print("🧠 CAPcoach - Financial Wellness Assistant")
        print("=" * 50)
    
    async def start_session(self, user_profile=None):
        """Start a new coaching session"""
        if not user_profile:
            user_profile = self._get_user_profile()
        
        print(f"\n👋 Welcome, {user_profile['name']}!")
        print("I'm here to help you understand and improve your relationship with money.")
        print("Let's start with a conversation about your financial habits...\n")
        
        # Initialize conversation
        session_data = self.conversation_service.initiate_diagnostic_conversation(user_profile)
        session_id = session_data["session_id"]
        
        print(f"Session ID: {session_id}")
        print(f"\n🤖 {session_data['welcome_message']}")
        print(f"🤖 {session_data['first_question']}")
        
        return session_id
    
    def _get_user_profile(self):
        """Get basic user information"""
        print("\n📝 Let's get to know you better...")
        name = input("What's your name? ").strip() or "Friend"
        age = input("How old are you? ").strip() or "30"
        profession = input("What do you do? ").strip() or "Professional"
        
        return {
            "name": name,
            "age": age,
            "profession": profession
        }
    
    async def chat_loop(self, session_id):
        """Main conversation loop"""
        print("\n💬 Let's talk about your finances. Type 'quit' to end the session.")
        print("-" * 50)
        
        conversation_history = []
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye', 'end']:
                    print("\nThank you for the conversation! Generating your personalized insights...")
                    break
                
                if not user_input:
                    continue
                
                # Process user response
                response = await self.conversation_service.process_user_response(session_id, user_input)
                
                print(f"\n🤖 {response['ai_response']}")
                print(f"📊 Progress: {response['conversation_progress']:.0%} complete")
                
                # Store conversation turn
                conversation_history.append({
                    "user": user_input,
                    "ai": response['ai_response'],
                    "insights": response['diagnostic_insights']
                })
                
                # Check if we have enough information
                if response['conversation_progress'] >= 0.8:
                    print("\n🌟 I have a good understanding now. Let me create your personalized plan...")
                    break
                    
            except KeyboardInterrupt:
                print("\n\nSession interrupted. Saving your progress...")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                continue
        
        return conversation_history
    
    async def generate_insights(self, session_id, conversation_history, user_profile):
        """Generate personalized insights and video"""
        print("\n🎯 Analyzing your financial patterns...")
        
        # Analyze emotional patterns from conversation
        emotional_patterns = {}
        financial_patterns = {}
        
        for turn in conversation_history:
            emotions = self.emotion_service.analyze_emotional_content(turn["user"])
            patterns = turn["insights"]
            
            # Aggregate patterns
            for emotion, score in emotions.items():
                if score > 0:
                    emotional_patterns[emotion] = emotional_patterns.get(emotion, 0) + score
            
            for pattern, score in patterns.items():
                if score > 0:
                    financial_patterns[pattern] = financial_patterns.get(pattern, 0) + score
        
        # Determine dominant patterns
        dominant_emotion = max(emotional_patterns.items(), key=lambda x: x[1])[0] if emotional_patterns else "neutral"
        dominant_pattern = max(financial_patterns.items(), key=lambda x: x[1])[0] if financial_patterns else "general"
        
        print(f"🔍 Dominant Emotional Pattern: {dominant_emotion}")
        print(f"🔍 Dominant Financial Pattern: {dominant_pattern}")
        
        # Create personalized budget strategies
        budget_strategies = self._create_budget_strategies(dominant_pattern, dominant_emotion)
        
        print(f"\n💡 Your Personalized Budget Strategies:")
        for i, strategy in enumerate(budget_strategies, 1):
            print(f"   {i}. {strategy}")
        
        # Generate video
        print("\n🎬 Creating your personalized financial guide...")
        from ai.models.diagnosis import DiagnosisSummary, DisorderInsights
        
        # Create diagnosis summary
        insights = DisorderInsights(
            avoidance_score=financial_patterns.get('avoidance', 0),
            anxiety_score=emotional_patterns.get('anxious', 0),
            impulsivity_score=financial_patterns.get('impulsivity', 0),
            money_dyslexia_score=financial_patterns.get('money_dyslexia', 0)
        )
        insights.calculate_dominant_disorder()
        
        summary = DiagnosisSummary(
            session_id=session_id,
            disorder_insights=insights,
            suggested_actions=budget_strategies,
            pattern_observations=financial_patterns,
            emotional_trends=emotional_patterns,
            user_name=user_profile["name"]
        )
        
        # Generate video
        video_path = self.video_service.create_budgeting_video(summary, f"capcoach_guide_{session_id}.mp4")
        
        print(f"\n🎉 Your personalized financial guide is ready!")
        print(f"📹 Guide saved: {video_path}")
        print(f"📋 Summary: {len(budget_strategies)} personalized strategies")
        
        return {
            "video_path": video_path,
            "strategies": budget_strategies,
            "patterns": {
                "emotional": dominant_emotion,
                "financial": dominant_pattern
            }
        }
    
    def _create_budget_strategies(self, pattern, emotion):
        """Create personalized budgeting strategies"""
        strategies = {
            "avoidance": [
                "5-minute daily money check-ins with timer",
                "Automated bill payments to reduce decision fatigue",
                "Weekly 'money dates' in a comfortable environment",
                "Celebration system for small financial wins"
            ],
            "anxiety": [
                "Breathing exercises before financial tasks",
                "Separate 'worry fund' for peace of mind",
                "Gradual exposure to financial statements",
                "Focus on controllables vs. market fluctuations"
            ],
            "impulsivity": [
                "24-hour cooling off period for purchases >$50",
                "Cash envelope system for discretionary spending",
                "Shopping list requirement for all store visits",
                "Emotion-spending journal to identify triggers"
            ],
            "money_dyslexia": [
                "Color-coded budget app with simple categories",
                "Round number budgeting ($50 increments)",
                "Visual savings tracker (paper or digital)",
                "Automated savings transfers"
            ]
        }
        
        return strategies.get(pattern, [
            "50/30/20 budget (Needs/Wants/Savings)",
            "Weekly financial check-ins",
            "Goal-based savings buckets",
            "Expense tracking app"
        ])
    
    async def run(self):
        """Main application loop"""
        try:
            # Start session
            session_id = await self.start_session()
            
            # Conversation phase
            conversation_history = await self.chat_loop(session_id)
            
            if conversation_history:
                # Generate insights
                user_profile = {"name": "User"}  # Simplified for demo
                insights = await self.generate_insights(session_id, conversation_history, user_profile)
                
                print(f"\n🌈 Session Complete!")
                print(f"📊 Patterns identified: {insights['patterns']['financial']}")
                print(f"💡 Strategies provided: {len(insights['strategies'])}")
                print(f"🎬 Guide created: {insights['video_path']}")
            else:
                print("\n👋 Hope to continue our conversation soon!")
                
        except Exception as e:
            print(f"\n❌ Application error: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Application entry point"""
    app = CAPcoach()
    await app.run()

if __name__ == "__main__":
    # Run the application
    asyncio.run(main())