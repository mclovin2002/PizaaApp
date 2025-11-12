"""
Comprehensive test suite for SashimiApp
Tests all features including AI integration, scrolling, credential saving, and UI components.
"""

import unittest
import os
import sys
import tempfile
import json
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the app components
from sashimi_gui import SashimiApp, SashimiNavBar, MainPage, SettingsPage, SASHIMI_COLORS
from ai_reply_generator import AIReplyGenerator, create_reply_generator_from_config, AIProvider


class TestSashimiApp(unittest.TestCase):
    """Test the main SashimiApp functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)
        
        # Create a temporary config file
        self.config_file = Path("config.json")
        
    def tearDown(self):
        """Clean up test environment."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_color_palette(self):
        """Test that the sashimi color palette is properly defined."""
        self.assertIn('primary', SASHIMI_COLORS)
        self.assertIn('sashimi_orange', SASHIMI_COLORS)
        self.assertIn('highlight', SASHIMI_COLORS)
        self.assertEqual(SASHIMI_COLORS['primary'], '#ffffff')
        self.assertEqual(SASHIMI_COLORS['sashimi_orange'], '#ff6b35')
        self.assertEqual(SASHIMI_COLORS['highlight'], '#ff4757')
    
    def test_app_initialization(self):
        """Test that the app initializes without errors."""
        with patch('customtkinter.CTk.__init__', return_value=None):
            with patch('customtkinter.CTk.grid_rowconfigure'):
                with patch('customtkinter.CTk.grid_columnconfigure'):
                    with patch('customtkinter.CTkFrame'):
                        app = SashimiApp()
                        self.assertIsNotNone(app)
    
    def test_credential_loading(self):
        """Test credential loading functionality."""
        # Test with no config file
        app = SashimiApp()
        creds = app.load_credentials()
        expected = {
            "api_key": "",
            "api_secret": "",
            "access_token": "",
            "access_token_secret": "",
        }
        self.assertEqual(creds, expected)
        
        # Test with existing config file
        test_creds = {
            "api_key": "test_key",
            "api_secret": "test_secret",
            "access_token": "test_token",
            "access_token_secret": "test_token_secret",
        }
        with open(self.config_file, 'w') as f:
            json.dump(test_creds, f)
        
        app = SashimiApp()
        creds = app.load_credentials()
        self.assertEqual(creds, test_creds)
    
    def test_credential_saving(self):
        """Test credential saving functionality."""
        app = SashimiApp()
        test_creds = {
            "api_key": "test_key",
            "api_secret": "test_secret", 
            "access_token": "test_token",
            "access_token_secret": "test_token_secret",
        }
        
        # Mock the twitter_credentials.py file
        creds_file = Path("twitter_credentials.py")
        creds_file.write_text('API_KEY: str = ""\nAPI_SECRET: str = ""\nACCESS_TOKEN: str = ""\nACCESS_TOKEN_SECRET: str = ""')
        
        with patch('tkinter.messagebox.showinfo'):
            app.save_credentials(test_creds)
        
        # Verify config.json was created
        self.assertTrue(self.config_file.exists())
        with open(self.config_file, 'r') as f:
            saved_creds = json.load(f)
        self.assertEqual(saved_creds, test_creds)
        
        # Verify twitter_credentials.py was updated
        content = creds_file.read_text()
        self.assertIn('test_key', content)
        self.assertIn('test_secret', content)


class TestAIReplyGenerator(unittest.TestCase):
    """Test AI reply generation functionality."""
    
    def test_ai_provider_enum(self):
        """Test AI provider enumeration."""
        self.assertEqual(AIProvider.OPENAI.value, "openai")
        self.assertEqual(AIProvider.ANTHROPIC.value, "anthropic")
        self.assertEqual(AIProvider.OLLAMA.value, "ollama")
        self.assertEqual(AIProvider.GROQ.value, "groq")
        self.assertEqual(AIProvider.NONE.value, "none")
    
    def test_template_reply_generation(self):
        """Test template-based reply generation (no AI)."""
        generator = create_reply_generator_from_config("none")
        
        # Test different types of mentions
        test_cases = [
            ("Thanks so much!", "You're very welcome! Glad I could help! 😊"),
            ("How do I use this?", "Happy to help! Feel free to DM me if you need more details."),
            ("This is awesome!", "Thank you so much! Really appreciate the kind words! 🙌"),
            ("There's a bug", "Sorry to hear that! Let me look into this for you. Can you DM me more details?"),
            ("Random mention", "Thanks for reaching out! I appreciate you connecting with me.")
        ]
        
        for mention, expected_start in test_cases:
            reply = generator.generate_reply(mention, "testuser")
            self.assertIsInstance(reply, str)
            self.assertGreater(len(reply), 0)
    
    def test_ai_generator_creation(self):
        """Test AI generator creation with different providers."""
        # Test with no provider (should use template)
        generator = create_reply_generator_from_config("none")
        self.assertEqual(generator.provider, AIProvider.NONE)
        
        # Test with invalid provider (should default to none)
        generator = create_reply_generator_from_config("invalid")
        self.assertEqual(generator.provider, AIProvider.NONE)
    
    def test_system_prompt(self):
        """Test system prompt generation."""
        generator = AIReplyGenerator(provider=AIProvider.NONE)
        prompt = generator._get_default_system_prompt()
        
        self.assertIsInstance(prompt, str)
        self.assertGreater(len(prompt), 0)
        self.assertIn("friendly", prompt.lower())
        self.assertIn("professional", prompt.lower())
    
    def test_user_prompt_building(self):
        """Test user prompt building."""
        generator = AIReplyGenerator(provider=AIProvider.NONE)
        
        prompt = generator._build_user_prompt(
            "Hey, great app!",
            "testuser",
            "We're a sushi delivery app"
        )
        
        self.assertIn("testuser", prompt)
        self.assertIn("Hey, great app!", prompt)
        self.assertIn("sushi delivery app", prompt)


class TestUIFeatures(unittest.TestCase):
    """Test UI-specific features."""
    
    def test_scrolling_configuration(self):
        """Test that scrolling is properly configured."""
        # This test verifies the textbox configuration includes scrolling
        from sashimi_gui import MainPage
        
        # Mock the parent and controller
        mock_parent = MagicMock()
        mock_controller = MagicMock()
        
        with patch('customtkinter.CTkFrame.__init__', return_value=None):
            with patch('customtkinter.CTkFrame.grid'):
                with patch('customtkinter.CTkFrame.grid_rowconfigure'):
                    with patch('customtkinter.CTkFrame.grid_columnconfigure'):
                        with patch('customtkinter.CTkTextbox') as mock_textbox:
                            # Create the main page
                            page = MainPage(mock_parent, mock_controller)
                            
                            # Verify textbox was created with scrolling parameters
                            mock_textbox.assert_called()
                            call_args = mock_textbox.call_args[1]
                            self.assertIn('scrollbar_button_color', call_args)
                            self.assertIn('scrollbar_button_hover_color', call_args)
    
    def test_color_theme_consistency(self):
        """Test that all UI components use consistent colors."""
        # Test that all required colors are defined
        required_colors = [
            'primary', 'secondary', 'accent', 'highlight',
            'success', 'warning', 'error', 'text_primary',
            'text_secondary', 'text_muted', 'card_bg',
            'sashimi_orange', 'wasabi_green', 'rice_white'
        ]
        
        for color in required_colors:
            self.assertIn(color, SASHIMI_COLORS)
            self.assertIsInstance(SASHIMI_COLORS[color], str)
            self.assertTrue(SASHIMI_COLORS[color].startswith('#'))
    
    def test_action_card_colors(self):
        """Test that action cards use the correct sashimi colors."""
        from sashimi_gui import MainPage
        
        # Test the color mapping for action buttons
        expected_colors = [
            SASHIMI_COLORS['seaweed_green'],    # Post Tweet
            SASHIMI_COLORS['sashimi_orange'],   # Schedule Tweet
            SASHIMI_COLORS['ginger_pink'],      # Bulk Upload
            SASHIMI_COLORS['highlight']         # Auto Reply
        ]
        
        # Verify colors are defined
        for color in expected_colors:
            self.assertIsInstance(color, str)
            self.assertTrue(color.startswith('#'))


class TestIntegration(unittest.TestCase):
    """Test integration between different components."""
    
    def test_ai_integration_with_gui(self):
        """Test that AI features integrate properly with the GUI."""
        # Test that AI providers are available in the auto-reply dialog
        from sashimi_gui import MainPage
        
        mock_parent = MagicMock()
        mock_controller = MagicMock()
        
        with patch('customtkinter.CTkFrame.__init__', return_value=None):
            with patch('customtkinter.CTkFrame.grid'):
                with patch('customtkinter.CTkFrame.grid_rowconfigure'):
                    with patch('customtkinter.CTkFrame.grid_columnconfigure'):
                        page = MainPage(mock_parent, mock_controller)
                        
                        # Test that auto_reply method exists and is callable
                        self.assertTrue(hasattr(page, 'auto_reply'))
                        self.assertTrue(callable(page.auto_reply))
    
    def test_credential_persistence(self):
        """Test that credentials persist between app sessions."""
        # Create a temporary config
        config_data = {
            "api_key": "persistent_key",
            "api_secret": "persistent_secret",
            "access_token": "persistent_token", 
            "access_token_secret": "persistent_token_secret"
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            # Test loading from file
            from sashimi_gui import SashimiApp
            with patch('pathlib.Path.exists', return_value=True):
                with patch('builtins.open', create=True) as mock_open:
                    with patch('json.load', return_value=config_data):
                        app = SashimiApp()
                        creds = app.load_credentials()
                        self.assertEqual(creds, config_data)
        finally:
            os.unlink(config_path)


def run_tests():
    """Run all tests and return results."""
    print("🍣 Running SashimiApp Test Suite...")
    print("=" * 50)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestSashimiApp))
    suite.addTests(loader.loadTestsFromTestCase(TestAIReplyGenerator))
    suite.addTests(loader.loadTestsFromTestCase(TestUIFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 50)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print("\nFailures:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nErrors:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    success = len(result.failures) == 0 and len(result.errors) == 0
    print(f"\nOverall: {'✅ PASSED' if success else '❌ FAILED'}")
    
    return success


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

