# video_generation_service.py
# ----------------
# Generates high-quality educational budgeting videos

from typing import Optional, List, Dict
import os
import json
import traceback
from datetime import datetime

# Global flag for moviepy availability
try:
    from moviepy import TextClip, ColorClip, CompositeVideoClip, concatenate_videoclips
    import numpy as np
    MOVIEPY_AVAILABLE = True
    print("✅ MoviePy successfully imported!")
except ImportError as e:
    MOVIEPY_AVAILABLE = False
    print(f"⚠️  MoviePy not available: {e}")

class VideoGenerationService:
    """
    Generates high-quality educational budgeting videos tailored to user's financial patterns.
    """

    def __init__(self):
        self.moviepy_available = MOVIEPY_AVAILABLE
        self.video_quality = {
            'resolution': (1920, 1080),  # Full HD
            'fps': 30,
            'codec': 'libx264',
            'audio_codec': 'aac',
            'bitrate': '5000k'
        }
        
        if self.moviepy_available:
            print("✅ Video service initialized with MoviePy - High Quality Mode")
        else:
            print("⚠️  Video generation running in limited mode")

        # Enhanced budgeting content with more detailed tips
        self.budgeting_content = {
            "avoidance": {
                "title": "Overcoming Financial Avoidance",
                "subtitle": "Building Confidence with Money",
                "tips": [
                    "📅 Start with 5-minute daily money check-ins\nBuild consistency without overwhelm",
                    "🤖 Use automatic bill payments & savings\nReduce decision fatigue and stress", 
                    "🎯 Break financial tasks into tiny steps\n'Open bank app' → 'Check balance' → 'Review transactions'",
                    "🎉 Celebrate small wins consistently\nTrack progress and reward yourself"
                ],
                "color": (255, 140, 0),  # Orange
                "gradient": [(255, 165, 0), (255, 100, 0)]
            },
            "anxiety": {
                "title": "Managing Financial Anxiety", 
                "subtitle": "Finding Peace with Your Finances",
                "tips": [
                    "🌬️ Practice breathing exercises before money tasks\nCalm your nervous system first",
                    "⏰ Set specific 'worry time' for financial concerns\nContain anxiety to designated times",
                    "🛡️ Create a safety net with 3-month emergency fund\nBuild security step by step", 
                    "🎯 Focus on what you can control daily\nLet go of market fluctuations and unknowns"
                ],
                "color": (30, 144, 255),  # Dodger Blue
                "gradient": [(30, 144, 255), (70, 130, 180)]
            },
            "impulsivity": {
                "title": "Controlling Impulse Spending",
                "subtitle": "Building Mindful Spending Habits", 
                "tips": [
                    "⏳ Implement 24-hour waiting period for purchases\nLet impulses pass before deciding",
                    "💵 Use cash envelopes for discretionary spending\nCreate physical spending boundaries",
                    "📧 Unsubscribe from shopping emails & delete apps\nRemove temptation triggers",
                    "🧠 Practice mindful spending with 'why' checklist\n'Need vs Want vs Love' evaluation"
                ],
                "color": (220, 20, 60),  # Crimson
                "gradient": [(220, 20, 60), (178, 34, 34)]
            },
            "money_dyslexia": {
                "title": "Simplifying Money Management",
                "subtitle": "Making Numbers Work for You",
                "tips": [
                    "🎨 Use visual budgeting apps with color coding\nSee your money flow at a glance",
                    "📊 Create simple categories: Needs, Wants, Savings\n50/30/20 rule for easy allocation",
                    "💸 Set up automatic transfers to build savings\n'Pay yourself first' automatically", 
                    "🔢 Use round numbers for easier mental math\n$100 increments instead of exact amounts"
                ],
                "color": (60, 180, 75),  # Green
                "gradient": [(60, 180, 75), (34, 139, 34)]
            }
        }

    def create_budgeting_video(self, diagnosis_summary, output_path: str = None) -> str:
        """
        Creates a high-quality educational video with budgeting tips.
        """
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"budgeting_video_{timestamp}.mp4"
        
        print("🎬 Creating high-quality budgeting video...")
        
        # Get the dominant pattern to personalize content
        dominant_pattern = diagnosis_summary.disorder_insights.dominant_disorder
        user_name = getattr(diagnosis_summary, 'user_name', 'there')
        
        print(f"📊 Creating video for pattern: {dominant_pattern}")
        print(f"🎯 User: {user_name}")
        
        # Build enhanced video content
        video_script = self._build_enhanced_script(dominant_pattern, user_name, diagnosis_summary)
        
        if self.moviepy_available:
            try:
                return self._generate_high_quality_video(video_script, dominant_pattern, output_path)
            except Exception as e:
                print(f"❌ High-quality video generation failed: {e}")
                print("🔄 Falling back to standard quality...")
                try:
                    return self._generate_standard_video(video_script, dominant_pattern, output_path)
                except Exception as e2:
                    print(f"❌ Standard video failed: {e2}")
                    return self._create_video_script_file(video_script, output_path)
        else:
            return self._create_video_script_file(video_script, output_path)

    def _build_enhanced_script(self, pattern: str, user_name: str, diagnosis) -> Dict:
        """Build enhanced video script with richer content."""
        
        content = self.budgeting_content.get(pattern, self.budgeting_content["anxiety"])
        
        script = {
            "title": f"Financial Freedom Guide for {user_name}",
            "pattern": pattern,
            "theme": content,
            "sections": [
                {
                    "type": "intro",
                    "title": "Your Personal Financial Assessment",
                    "content": f"Our analysis shows you have tendencies toward\n**{pattern.replace('_', ' ').title()}**\n\nThis is completely normal and manageable!\nMany successful people share this pattern.",
                    "duration": 8,
                    "animation": "fade_in"
                },
                {
                    "type": "strategy", 
                    "title": content["title"],
                    "content": content["subtitle"],
                    "duration": 6,
                    "animation": "slide_up"
                },
                {
                    "type": "tip",
                    "title": "🎯 Action Step 1",
                    "content": content["tips"][0],
                    "duration": 10,
                    "animation": "typewriter"
                },
                {
                    "type": "tip",
                    "title": "🔄 Action Step 2", 
                    "content": content["tips"][1],
                    "duration": 10,
                    "animation": "typewriter"
                },
                {
                    "type": "tip",
                    "title": "💡 Action Step 3",
                    "content": content["tips"][2],
                    "duration": 10, 
                    "animation": "typewriter"
                },
                {
                    "type": "tip",
                    "title": "🚀 Action Step 4",
                    "content": content["tips"][3],
                    "duration": 10,
                    "animation": "typewriter"
                },
                {
                    "type": "outro",
                    "title": "You're On Your Way!",
                    "content": "Remember: Progress over perfection.\n\nSmall consistent steps → Big financial changes\n\nYou have everything you need to succeed!",
                    "duration": 8,
                    "animation": "fade_in"
                }
            ]
        }
        
        script["total_duration"] = sum(section["duration"] for section in script["sections"])
        return script

    def _generate_high_quality_video(self, script: Dict, pattern: str, output_path: str) -> str:
        """Generate high-quality video with enhanced visuals."""
        try:
            print("🎥 Creating high-quality video...")
            
            from moviepy import concatenate_videoclips
            
            scenes = []
            content = script["theme"]
            width, height = self.video_quality['resolution']
            
            for i, section in enumerate(script["sections"]):
                print(f"🎞️ Creating scene {i+1}: {section['title']}")
                
                # Create animated background
                background = self._create_animated_background(
                    width, height, 
                    content["gradient"], 
                    section["duration"]
                )
                
                # Create main title
                title_text = TextClip(
                    text=section["title"],
                    font_size=64 if section["type"] == "intro" else 52,
                    color='white',
                    stroke_color='rgba(0,0,0,0.8)',
                    stroke_width=3
                ).with_duration(section["duration"]).with_position(('center', height * 0.2))
                
                # Create content with better formatting
                content_lines = section["content"].split('\n')
                content_clips = []
                
                for j, line in enumerate(content_lines):
                    line_clip = TextClip(
                        text=line.strip(),
                        font_size=36 if line.startswith(('🎯','🔄','💡','🚀')) else 32,
                        color='white',
                        stroke_color='rgba(0,0,0,0.6)',
                        stroke_width=2
                    ).with_duration(section["duration"]).with_position(('center', height * 0.4 + j * 50))
                    content_clips.append(line_clip)
                
                # Combine all elements
                scene_elements = [background, title_text] + content_clips
                
                # Add progress indicator for tips
                if section["type"] == "tip":
                    progress_text = TextClip(
                        text=f"Step {i-1}/4",
                        font_size=24,
                        color='rgba(255,255,255,0.8)'
                    ).with_duration(section["duration"]).with_position(('center', height * 0.85))
                    scene_elements.append(progress_text)
                
                scene = CompositeVideoClip(scene_elements)
                scenes.append(scene)
            
            # Concatenate scenes with crossfade
            print(f"🎬 Combining {len(scenes)} scenes with transitions...")
            final_video = concatenate_videoclips(scenes, method="compose", padding=0.5)
            
            # Write high-quality video
            print("💾 Rendering high-quality video...")
            final_video.write_videofile(
                output_path,
                fps=self.video_quality['fps'],
                codec=self.video_quality['codec'],
                audio_codec=self.video_quality['audio_codec'],
                bitrate=self.video_quality['bitrate'],
                threads=4,
                preset='medium',
                ffmpeg_params=[
                    '-pix_fmt', 'yuv420p',
                    '-movflags', '+faststart'
                ]
            )
            
            print(f"✅ High-quality video created: {output_path}")
            print(f"📊 Video specs: {self.video_quality['resolution'][0]}p, {self.video_quality['fps']}fps")
            
            return output_path
            
        except Exception as e:
            print(f"❌ High-quality generation failed: {e}")
            raise

    def _generate_standard_video(self, script: Dict, pattern: str, output_path: str) -> str:
        """Generate standard quality video as fallback."""
        try:
            print("🎥 Creating standard quality video...")
            
            from moviepy import concatenate_videoclips
            
            scenes = []
            content = script["theme"]
            
            for i, section in enumerate(script["sections"]):
                # Simple background
                background = ColorClip(
                    size=(1280, 720), 
                    color=content["color"], 
                    duration=section["duration"]
                )
                
                # Title
                title_text = TextClip(
                    text=section["title"],
                    font_size=48,
                    color='white'
                ).with_duration(section["duration"]).with_position(('center', 150))
                
                # Content
                content_text = TextClip(
                    text=section["content"],
                    font_size=28,
                    color='white'
                ).with_duration(section["duration"]).with_position(('center', 280))
                
                scene = CompositeVideoClip([background, title_text, content_text])
                scenes.append(scene)
            
            final_video = concatenate_videoclips(scenes)
            final_video.write_videofile(output_path, fps=24)
            
            print(f"✅ Standard video created: {output_path}")
            return output_path
            
        except Exception as e:
            print(f"❌ Standard video failed: {e}")
            raise

    def _create_animated_background(self, width: int, height: int, gradient: list, duration: float):
        """Create an animated gradient background."""
        try:
            # For now, use a solid color - animated backgrounds are complex
            return ColorClip(size=(width, height), color=gradient[0], duration=duration)
        except:
            # Fallback to simple color
            return ColorClip(size=(width, height), color=gradient[0], duration=duration)

    def _create_video_script_file(self, script: Dict, output_path: str) -> str:
        """Create a detailed script file when video generation isn't available."""
        txt_path = output_path.replace('.mp4', '_script.txt')
        
        content = script["theme"]
        
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write("🎬 CAPcoach Premium Budgeting Video Script\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Title: {script['title']}\n")
            f.write(f"Financial Pattern: {script['pattern'].replace('_', ' ').title()}\n")
            f.write(f"Video Theme: {content['title']}\n")
            f.write(f"Subtitle: {content['subtitle']}\n")
            f.write(f"Total Duration: {script['total_duration']} seconds\n")
            f.write(f"Quality: {self.video_quality['resolution'][0]}p {self.video_quality['fps']}fps\n\n")
            
            f.write("VIDEO SCENE BREAKDOWN:\n")
            f.write("=" * 40 + "\n")
            
            for i, section in enumerate(script['sections'], 1):
                f.write(f"\nSCENE {i}: {section['title']}\n")
                f.write(f"Type: {section['type'].upper()}\n")
                f.write(f"Duration: {section['duration']} seconds\n")
                f.write(f"Animation: {section.get('animation', 'fade_in')}\n")
                f.write("Content:\n")
                for line in section['content'].split('\n'):
                    f.write(f"  {line}\n")
                f.write("-" * 50 + "\n")
            
            f.write(f"\nPERSONALIZED BUDGETING STRATEGIES:\n")
            f.write("=" * 45 + "\n")
            for tip in content['tips']:
                f.write(f"• {tip}\n")
            
            f.write(f"\n[High-quality video would be generated as: {output_path}]\n")
            f.write(f"[Video specs: {self.video_quality['resolution'][0]}p, {self.video_quality['fps']}fps, {self.video_quality['bitrate']}]\n")
        
        print(f"📹 Premium video script saved: {txt_path}")
        return txt_path

# Test function for high-quality video generation
def test_premium_video():
    """Test the premium video generation"""
    print("🧪 Testing Premium VideoGenerationService...")
    
    # Create mock data
    class DisorderInsights:
        def __init__(self):
            self.avoidance_score = 0.8
            self.anxiety_score = 0.9
            self.impulsivity_score = 0.3
            self.money_dyslexia_score = 0.2
            self.dominant_disorder = "anxiety"
        
        def calculate_dominant_disorder(self):
            self.dominant_disorder = "anxiety"
    
    class DiagnosisSummary:
        def __init__(self):
            self.session_id = "premium-test"
            self.disorder_insights = DisorderInsights()
            self.suggested_actions = ["Test action 1", "Test action 2"]
            self.user_name = "Premium User"
    
    service = VideoGenerationService()
    summary = DiagnosisSummary()
    
    print(f"🎯 MoviePy available: {service.moviepy_available}")
    print(f"🎯 Quality settings: {service.video_quality['resolution'][0]}p")
    
    result = service.create_budgeting_video(summary, "premium_demo.mp4")
    
    print(f"🎯 Test result: {result}")

if __name__ == "__main__":
    test_premium_video()