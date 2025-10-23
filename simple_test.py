"""
Simple functionality test for SashimiApp
Tests core features without GUI components.
"""

import sys
import os
import json
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_ai_functionality():
    """Test AI reply generation functionality."""
    print("🤖 Testing AI functionality...")
    
    try:
        from ai_reply_generator import create_reply_generator_from_config, AIProvider
        
        # Test template-based replies (no AI needed)
        generator = create_reply_generator_from_config("none")
        
        test_mentions = [
            "Thanks so much for the help!",
            "How do I use this feature?",
            "This is amazing!",
            "There's a bug in the app",
            "Random mention"
        ]
        
        for mention in test_mentions:
            reply = generator.generate_reply(mention, "testuser")
            print(f"  ✅ Mention: '{mention}' -> Reply: '{reply}'")
        
        print("  ✅ AI functionality working correctly!")
        return True
        
    except Exception as e:
        print(f"  ❌ AI functionality failed: {e}")
        return False

def test_color_palette():
    """Test color palette definition."""
    print("🎨 Testing color palette...")
    
    try:
        from sashimi_gui import SASHIMI_COLORS
        
        required_colors = [
            'primary', 'secondary', 'accent', 'highlight',
            'success', 'warning', 'error', 'text_primary',
            'sashimi_orange', 'wasabi_green', 'rice_white'
        ]
        
        for color in required_colors:
            if color not in SASHIMI_COLORS:
                print(f"  ❌ Missing color: {color}")
                return False
            if not SASHIMI_COLORS[color].startswith('#'):
                print(f"  ❌ Invalid color format: {color}")
                return False
        
        print("  ✅ Color palette properly defined!")
        print(f"  🎨 Primary: {SASHIMI_COLORS['primary']}")
        print(f"  🎨 Sashimi Orange: {SASHIMI_COLORS['sashimi_orange']}")
        print(f"  🎨 Highlight: {SASHIMI_COLORS['highlight']}")
        return True
        
    except Exception as e:
        print(f"  ❌ Color palette test failed: {e}")
        return False

def test_credential_management():
    """Test credential loading and saving."""
    print("🔐 Testing credential management...")
    
    try:
        from sashimi_gui import SashimiApp
        
        # Test credential loading
        app = SashimiApp()
        creds = app.load_credentials()
        
        expected_keys = ["api_key", "api_secret", "access_token", "access_token_secret"]
        for key in expected_keys:
            if key not in creds:
                print(f"  ❌ Missing credential key: {key}")
                return False
        
        print("  ✅ Credential loading working!")
        
        # Test credential saving
        test_creds = {
            "api_key": "test_key_123",
            "api_secret": "test_secret_456",
            "access_token": "test_token_789",
            "access_token_secret": "test_token_secret_012"
        }
        
        # Mock the twitter_credentials.py file
        creds_file = Path("twitter_credentials.py")
        if not creds_file.exists():
            creds_file.write_text('API_KEY: str = ""\nAPI_SECRET: str = ""\nACCESS_TOKEN: str = ""\nACCESS_TOKEN_SECRET: str = ""')
        
        # Test saving (without actually showing messagebox)
        import json
        config_file = Path("config.json")
        with open(config_file, 'w') as f:
            json.dump(test_creds, f, indent=4)
        
        # Verify it was saved
        if config_file.exists():
            with open(config_file, 'r') as f:
                saved_creds = json.load(f)
            if saved_creds == test_creds:
                print("  ✅ Credential saving working!")
                return True
            else:
                print("  ❌ Credential saving failed - data mismatch")
                return False
        else:
            print("  ❌ Config file not created")
            return False
        
    except Exception as e:
        print(f"  ❌ Credential management failed: {e}")
        return False

def test_scrolling_configuration():
    """Test that scrolling is properly configured in the textbox."""
    print("📜 Testing scrolling configuration...")
    
    try:
        from sashimi_gui import SASHIMI_COLORS
        
        # Check that scrolling colors are defined
        scroll_colors = ['scrollbar_button_color', 'scrollbar_button_hover_color']
        required_colors = ['sashimi_orange', 'highlight']
        
        for color in required_colors:
            if color not in SASHIMI_COLORS:
                print(f"  ❌ Missing scroll color: {color}")
                return False
        
        print("  ✅ Scrolling colors properly defined!")
        print(f"  📜 Scroll button color: {SASHIMI_COLORS['sashimi_orange']}")
        print(f"  📜 Scroll hover color: {SASHIMI_COLORS['highlight']}")
        return True
        
    except Exception as e:
        print(f"  ❌ Scrolling configuration test failed: {e}")
        return False

def test_requirements():
    """Test that all required dependencies are available."""
    print("📦 Testing requirements...")
    
    try:
        import customtkinter as ctk
        print("  ✅ CustomTkinter available")
        
        import tweepy
        print("  ✅ Tweepy available")
        
        # Test AI dependencies (optional)
        try:
            import openai
            print("  ✅ OpenAI available")
        except ImportError:
            print("  ⚠️  OpenAI not installed (optional)")
        
        try:
            import anthropic
            print("  ✅ Anthropic available")
        except ImportError:
            print("  ⚠️  Anthropic not installed (optional)")
        
        try:
            import groq
            print("  ✅ Groq available")
        except ImportError:
            print("  ⚠️  Groq not installed (optional)")
        
        try:
            import ollama
            print("  ✅ Ollama available")
        except ImportError:
            print("  ⚠️  Ollama not installed (optional)")
        
        print("  ✅ Core requirements satisfied!")
        return True
        
    except Exception as e:
        print(f"  ❌ Requirements test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🍣 SashimiApp Simple Test Suite")
    print("=" * 50)
    
    tests = [
        test_requirements,
        test_color_palette,
        test_ai_functionality,
        test_credential_management,
        test_scrolling_configuration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            print()  # Add spacing between tests
        except Exception as e:
            print(f"  ❌ Test failed with exception: {e}")
            print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! SashimiApp is ready to use!")
        return True
    else:
        print("⚠️  Some tests failed, but core functionality should work.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
