#!/usr/bin/env python3
"""
CAPcoach AI Setup - Fixed for Python 3.14 compatibility
"""

import os
import sys
import subprocess
from pathlib import Path

def setup_ai_environment():
    """Setup specifically for running from ai/ directory"""
    print("🚀 CAPcoach AI Setup")
    print("=" * 50)
    
    # Get current directory (should be ai/)
    current_dir = Path(__file__).parent
    project_root = current_dir.parent  # Go up to CapCoach/
    
    print(f"🔧 Current directory: {current_dir}")
    print(f"🔧 Project root: {project_root}")
    
    # Add project root to Python path - THIS IS THE KEY FIX
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    return project_root

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"✅ Python version: {version.major}.{version.minor}.{version.micro}")
    return True

def verify_dependencies_safe():
    """Verify dependencies without crashing on spaCy"""
    print("\n📦 Verifying dependencies...")
    
    dependencies = [
        ("pydantic", "pydantic"),
        ("python-dotenv", "dotenv"), 
        ("requests", "requests"),
        ("openai", "openai"),
        ("groq", "groq"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("scikit-learn", "sklearn"),
        ("nltk", "nltk"),
        ("moviepy", "moviepy"),
        ("pyttsx3", "pyttsx3"),
        ("matplotlib", "matplotlib"),
        ("Pillow", "PIL")
    ]
    
    all_ok = True
    for pkg_name, import_name in dependencies:
        try:
            if import_name == "dotenv":
                __import__("dotenv")
            elif import_name == "PIL":
                __import__("PIL.Image")
            else:
                __import__(import_name)
            print(f"✅ {pkg_name}")
        except ImportError as e:
            print(f"❌ {pkg_name} - {e}")
            all_ok = False
    
    # Handle spaCy separately to avoid crash
    print("\n🔍 Checking spaCy (with compatibility workaround)...")
    try:
        # Try to import spaCy with error suppression
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            import spacy
        print("✅ spacy - Installed (with compatibility warnings)")
    except Exception as e:
        print(f"⚠️  spacy - Not compatible with Python 3.14: {e}")
        print("   This is OK - CAPcoach will work without advanced NLP")
    
    return all_ok

def setup_nltk_data():
    """Setup NLTK data"""
    print("\n🧠 Setting up NLTK data...")
    try:
        import nltk
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True) 
        nltk.download('vader_lexicon', quiet=True)
        print("✅ NLTK data ready")
        return True
    except Exception as e:
        print(f"⚠️  NLTK setup: {e}")
        return False

def check_environment():
    """Check environment variables"""
    print("\n🔑 Checking environment...")
    
    # Load from project root .env
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"
    
    if env_file.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print(f"✅ .env file loaded from: {env_file}")
        except ImportError:
            print("❌ python-dotenv not installed - cannot load .env file")
            return False
    else:
        print(f"❌ .env file not found at: {env_file}")
        return False
    
    if os.getenv('GROQ_API_KEY'):
        print("✅ GROQ_API_KEY is set")
        return True
    else:
        print("❌ GROQ_API_KEY is not set")
        return False

def test_ai_imports():
    """Test that AI modules can be imported"""
    print("\n🧪 Testing AI module imports...")
    
    # First, make sure Python path is correct
    project_root = Path(__file__).parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    # Test imports relative to current ai/ directory
    modules_to_test = [
        "config",
        "models.conversation",
        "models.emotions", 
        "models.patterns",
        "models.diagnosis",
        "services.emotional_intelligence_service",
        "services.pattern_detection_service", 
        "services.conversational_diagnosis_service",
        "state.conversation_state_manager",
        "video_generation_service"
    ]
    
    all_ok = True
    for module in modules_to_test:
        try:
            # Import from current package (ai.)
            full_module = f"ai.{module}"
            __import__(full_module)
            print(f"✅ {full_module}")
        except ImportError as e:
            print(f"❌ ai.{module} - {e}")
            all_ok = False
    
    return all_ok

def install_missing_dependencies():
    """Install missing dependencies"""
    print("\n🔧 Installing missing dependencies...")
    
    missing_packages = []
    
    # Check which packages are missing
    try:
        __import__("dotenv")
    except ImportError:
        missing_packages.append("python-dotenv")
    
    if missing_packages:
        print(f"Installing: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing_packages)
            print("✅ Missing dependencies installed")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install missing dependencies")
            return False
    else:
        print("✅ No missing dependencies to install")
        return True

def main():
    """Main setup function"""
    # Setup environment first
    project_root = setup_ai_environment()
    
    # Check Python
    check_python_version()
    
    # Install missing dependencies first
    install_missing_dependencies()
    
    # Verify dependencies (safe version)
    verify_dependencies_safe()
    
    # Setup NLP
    setup_nltk_data()
    
    # Test imports - THIS IS THE CRITICAL TEST
    print("\n" + "="*50)
    print("🧪 FINAL IMPORT TEST")
    print("="*50)
    
    if test_ai_imports():
        print("\n🎉 SUCCESS: All AI modules imported successfully!")
        print("💡 Your CAPcoach AI system is ready to use!")
    else:
        print("\n⚠️  Some imports failed. This may be due to:")
        print("   - Missing files in the ai/ directory")
        print("   - Python path issues")
        print("   - Incomplete module implementations")
        print(f"💡 Project root: {project_root}")
        print(f"💡 Current dir: {Path(__file__).parent}")
    
    # Check environment
    print("\n" + "="*50)
    print("🔑 ENVIRONMENT CHECK")
    print("="*50)
    
    env_ok = check_environment()
    if env_ok:
        print("✅ Environment is ready!")
    else:
        print("⚠️  Environment needs setup:")
        print("   - Create .env file in project root")
        print("   - Add GROQ_API_KEY=your_key_here")
    
    print("\n" + "="*50)
    print("🚀 NEXT STEPS")
    print("="*50)
    print("1. Run: python tester.py (from ai/ directory)")
    print("2. Or: python -m ai.tester (from project root)") 
    print("3. Or: python run.py (from project root)")
    print("\n💡 The spaCy warning is normal with Python 3.14")
    print("   Your CAPcoach will work without advanced NLP features")

if __name__ == "__main__":
    main()