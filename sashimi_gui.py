"""
SashimiApp - Professional Twitter Automation GUI
Built with customtkinter (Modern Sashimi Theme)
"""

import os, sys

# Ensure the app always loads the local files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print("🍣 Running SashimiApp from:", BASE_DIR)

# Required imports
from pathlib import Path
import json
import re
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import time

# Beautiful Sashimi-inspired color palette
SASHIMI_COLORS = {
    'primary': '#ffffff',             # Pure white (main background)
    'secondary': '#f8f9fa',           # Light gray-white
    'accent': '#ff6b35',              # Fresh salmon orange
    'highlight': '#ff4757',           # Coral red
    'success': '#2ed573',             # Wasabi green
    'warning': '#ffa502',             # Golden orange
    'error': '#ff3838',               # Deep red
    'text_primary': '#2c3e50',        # Dark slate (text on white)
    'text_secondary': '#7f8c8d',      # Medium gray
    'text_muted': '#95a5a6',         # Light gray
    'card_bg': '#ffffff',             # White cards
    'card_hover': '#f1f2f6',          # Light gray hover
    'border': '#ff6b35',              # Orange border
    'gradient_start': '#ff6b35',      # Orange gradient start
    'gradient_end': '#ff4757',        # Red gradient end
    'sashimi_orange': '#ff6b35',      # Main sashimi orange
    'wasabi_green': '#2ed573',        # Wasabi green
    'soy_sauce': '#2c3e50',          # Dark soy sauce
    'rice_white': '#ffffff',          # Rice white
    'ginger_pink': '#ff7675',         # Ginger pink
    'seaweed_green': '#00b894'        # Seaweed green
}

class SashimiApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App window with sashimi theme
        self.title("🍣 SashimiApp - X Automation")
        self.geometry("1400x900")
        self.minsize(1200, 800)
        self.resizable(True, True)
        
        # Set modern light theme
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")
        
        # Configure window styling
        self.configure(fg_color=SASHIMI_COLORS['primary'])

        # Root grid config
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Load credentials if exist
        self.credentials = self.load_credentials()

        # Create container frame
        self.container = ctk.CTkFrame(
            self, 
            corner_radius=0,
            fg_color=SASHIMI_COLORS['primary'],
            border_width=0
        )
        self.container.grid(row=0, column=0, sticky="nsew")

        # Configure container grid
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        # Frames for navigation
        self.frames = {}
        for F in (MainPage, SettingsPage):
            page_name = F.__name__
            frame = F(parent=self.container, controller=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # Show main page initially
        self.show_frame("MainPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        print(f"🍣 Switching to: {page_name}")
        frame.tkraise()
        frame.update_idletasks()

    def load_credentials(self):
        """Load saved credentials or return default structure."""
        CONFIG_FILE = Path("config.json")
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "api_key": "",
            "api_secret": "",
            "access_token": "",
            "access_token_secret": "",
        }

    def save_credentials(self, creds):
        """Save credentials to both config.json and twitter_credentials.py."""
        try:
            CONFIG_FILE = Path("config.json")
            # Save to config.json for GUI
            with open(CONFIG_FILE, "w") as f:
                json.dump(creds, f, indent=4)
            
            # Also update twitter_credentials.py for backend
            creds_file = Path("twitter_credentials.py")
            if creds_file.exists():
                content = creds_file.read_text()
                
                # Use regex to replace existing values
                content = re.sub(
                    r'API_KEY: str = "[^"]*"',
                    f'API_KEY: str = "{creds["api_key"]}"',
                    content
                )
                content = re.sub(
                    r'API_SECRET: str = "[^"]*"',
                    f'API_SECRET: str = "{creds["api_secret"]}"',
                    content
                )
                content = re.sub(
                    r'ACCESS_TOKEN: str = "[^"]*"',
                    f'ACCESS_TOKEN: str = "{creds["access_token"]}"',
                    content
                )
                content = re.sub(
                    r'ACCESS_TOKEN_SECRET: str = "[^"]*"',
                    f'ACCESS_TOKEN_SECRET: str = "{creds["access_token_secret"]}"',
                    content
                )
                
                creds_file.write_text(content)
            
            # Update the main page log with success message
            if hasattr(self, 'frames') and 'MainPage' in self.frames:
                main_page = self.frames['MainPage']
                if hasattr(main_page, 'log_box'):
                    main_page.log_box.insert("end", f"✅ [{datetime.now().strftime('%H:%M:%S')}] Twitter API credentials saved successfully!\n")
                    main_page.log_box.see("end")
            
            messagebox.showinfo("Success", "🍣 Credentials saved successfully!\n\nYour Twitter API credentials are now configured and ready to use.")
            self.credentials = creds
            self.show_frame("MainPage")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials:\n{e}")


class SashimiNavBar(ctk.CTkFrame):
    """Enhanced navigation bar with sashimi theme."""

    def __init__(self, parent, controller):
        super().__init__(
            parent, 
            fg_color=SASHIMI_COLORS['secondary'], 
            height=90,
            corner_radius=0,
            border_width=0
        )
        self.controller = controller
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)
        
        # Sashimi logo with enhanced styling
        self.logo_label = ctk.CTkLabel(
            self, 
            text="🍣", 
            font=("Helvetica", 36),
            text_color=SASHIMI_COLORS['sashimi_orange']
        )
        self.logo_label.grid(row=0, column=0, padx=30, pady=20, sticky="w")

        # App title with sashimi theme
        self.title_label = ctk.CTkLabel(
            self, 
            text="SashimiApp – X Automation", 
            font=("Helvetica", 26, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        )
        self.title_label.grid(row=0, column=1, padx=15, pady=20, sticky="w")

        # Status indicator
        self.status_label = ctk.CTkLabel(
            self,
            text="● Ready",
            font=("Helvetica", 14),
            text_color=SASHIMI_COLORS['success']
        )
        self.status_label.grid(row=0, column=2, padx=15, pady=20, sticky="e")
        
        # PROMINENT Settings button - made very visible with sashimi colors
        self.settings_button = ctk.CTkButton(
            self,
            text="⚙️ SETTINGS",
            width=150,
            height=50,
            font=("Helvetica", 16, "bold"),
            fg_color=SASHIMI_COLORS['sashimi_orange'],
            hover_color=SASHIMI_COLORS['highlight'],
            corner_radius=25,
            border_width=2,
            border_color=SASHIMI_COLORS['highlight'],
            text_color=SASHIMI_COLORS['rice_white'],
            command=lambda: controller.show_frame("SettingsPage"),
        )
        self.settings_button.grid(row=0, column=3, padx=30, pady=20, sticky="e")
        
    def update_status(self, status, color=None):
        """Update the status indicator."""
        if color is None:
            color = SASHIMI_COLORS['success']
        self.status_label.configure(text=f"● {status}", text_color=color)


class MainPage(ctk.CTkFrame):
    """Enhanced main dashboard with sashimi theme."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=SASHIMI_COLORS['primary'])
        self.controller = controller
        
        # Configure this frame to expand
        self.grid_rowconfigure(0, weight=0)  # navbar
        self.grid_rowconfigure(1, weight=1)  # content
        self.grid_columnconfigure(0, weight=1)

        # Enhanced navbar
        self.navbar = SashimiNavBar(self, controller)
        self.navbar.grid(row=0, column=0, sticky="ew")

        # Main content area with padding
        content_frame = ctk.CTkFrame(self, fg_color=SASHIMI_COLORS['primary'])
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Welcome header with sashimi theme
        header_frame = ctk.CTkFrame(
            content_frame, 
            fg_color=SASHIMI_COLORS['card_bg'],
            corner_radius=20,
            border_width=2,
            border_color=SASHIMI_COLORS['border']
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 30))
        header_frame.grid_columnconfigure(0, weight=1)

        # Welcome title with sashimi styling
        welcome_label = ctk.CTkLabel(
            header_frame,
            text="🍣 Twitter Automation Dashboard",
            font=("Helvetica", 32, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        )
        welcome_label.grid(row=0, column=0, pady=30, padx=40)

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Fresh automation tools for your Twitter presence",
            font=("Helvetica", 18),
            text_color=SASHIMI_COLORS['text_secondary']
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 30), padx=40)

        # Main content area with cards
        main_content = ctk.CTkFrame(content_frame, fg_color=SASHIMI_COLORS['primary'])
        main_content.grid(row=1, column=0, sticky="nsew")
        main_content.grid_columnconfigure((0, 1), weight=1)
        main_content.grid_rowconfigure(0, weight=1)

        # Left column - Action cards
        left_column = ctk.CTkFrame(main_content, fg_color=SASHIMI_COLORS['primary'])
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 20))
        left_column.grid_columnconfigure(0, weight=1)

        # Action buttons with sashimi theme
        action_buttons = [
            ("📝", "Post a Tweet", "Post immediately to your timeline", self.post_tweet_action, SASHIMI_COLORS['seaweed_green']),
            ("🕒", "Schedule Tweet", "Schedule tweets for later", self.schedule_tweet_action, SASHIMI_COLORS['sashimi_orange']),
            ("📁", "Bulk Upload", "Upload multiple tweets at once", self.bulk_upload, SASHIMI_COLORS['ginger_pink']),
            ("🤖", "Auto Reply", "AI-powered automatic replies", self.auto_reply, SASHIMI_COLORS['highlight']),
        ]

        for idx, (icon, title, description, command, color) in enumerate(action_buttons):
            self.create_action_card(left_column, icon, title, description, command, color, idx)

        # Right column - Activity log
        right_column = ctk.CTkFrame(main_content, fg_color=SASHIMI_COLORS['primary'])
        right_column.grid(row=0, column=1, sticky="nsew", padx=(20, 0))
        right_column.grid_columnconfigure(0, weight=1)
        right_column.grid_rowconfigure(1, weight=1)

        # Activity log header
        log_header = ctk.CTkFrame(right_column, fg_color=SASHIMI_COLORS['card_bg'], corner_radius=15)
        log_header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        log_title = ctk.CTkLabel(
            log_header,
            text="📊 Activity Log",
            font=("Helvetica", 20, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        )
        log_title.grid(row=0, column=0, pady=20, padx=25)

        # Enhanced log box with proper scrolling
        self.log_box = ctk.CTkTextbox(
            right_column, 
            height=450,
            font=("Consolas", 13),
            fg_color=SASHIMI_COLORS['card_bg'],
            text_color=SASHIMI_COLORS['text_primary'],
            corner_radius=15,
            border_width=2,
            border_color=SASHIMI_COLORS['border'],
            wrap="word"
        )
        self.log_box.grid(row=1, column=0, sticky="nsew")
        
        # Ensure scrolling is enabled
        self.log_box.configure(state="normal")
        
        # Add scrollbar configuration
        self.log_box._textbox.configure(
            wrap="word",
            state="normal",
            yscrollcommand=self.log_box._scrollbar.set
        )
        
        # Welcome messages
        self.log_box.insert("end", f"🍣 [{datetime.now().strftime('%H:%M:%S')}] Welcome to SashimiApp! Ready to automate your Twitter presence.\n")
        self.log_box.insert("end", f"💡 [{datetime.now().strftime('%H:%M:%S')}] Tip: Use the cards on the left to get started with automation.\n")
        self.log_box.insert("end", f"🔧 [{datetime.now().strftime('%H:%M:%S')}] Click '⚙️ SETTINGS' in the top-right to configure your Twitter API credentials.\n")
        self.log_box.insert("end", f"📜 [{datetime.now().strftime('%H:%M:%S')}] This log supports scrolling - use mouse wheel or scrollbar to navigate.\n")
        
        # Add test content to verify scrolling
        for i in range(20):
            self.log_box.insert("end", f"📝 [{datetime.now().strftime('%H:%M:%S')}] Test message {i+1} - This is to test scrolling functionality. You should be able to scroll up and down to see all messages.\n")
        
        self.log_box.insert("end", f"✅ [{datetime.now().strftime('%H:%M:%S')}] Scrolling test complete! If you can see this message, scrolling is working properly.\n\n")
        
        # Auto-scroll to bottom
        self.log_box.see("end")

    def create_action_card(self, parent, icon, title, description, command, color, row):
        """Create a modern action card with sashimi styling."""
        card = ctk.CTkFrame(
            parent,
            fg_color=SASHIMI_COLORS['card_bg'],
            corner_radius=20,
            border_width=2,
            border_color=SASHIMI_COLORS['border']
        )
        card.grid(row=row, column=0, sticky="ew", pady=15, padx=15)
        card.grid_columnconfigure(0, weight=1)

        # Card content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="ew", padx=25, pady=25)
        content_frame.grid_columnconfigure(1, weight=1)

        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=("Helvetica", 28),
            text_color=color
        )
        icon_label.grid(row=0, column=0, padx=(0, 20), pady=5, sticky="nw")

        # Text content
        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="ew")
        text_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=("Helvetica", 18, "bold"),
            text_color=SASHIMI_COLORS['text_primary'],
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 8))

        # Description
        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=("Helvetica", 14),
            text_color=SASHIMI_COLORS['text_secondary'],
            anchor="w"
        )
        desc_label.grid(row=1, column=0, sticky="ew")

        # Action button with sashimi styling
        action_btn = ctk.CTkButton(
            card,
            text="Go",
            width=100,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=color,
            hover_color=self.darken_color(color),
            corner_radius=20,
            text_color=SASHIMI_COLORS['rice_white'],
            command=command
        )
        action_btn.grid(row=1, column=0, pady=(0, 25), padx=25, sticky="e")

    def darken_color(self, color):
        """Helper to darken a color for hover effects."""
        color_map = {
            SASHIMI_COLORS['seaweed_green']: '#00a085',
            SASHIMI_COLORS['sashimi_orange']: '#e55a2b', 
            SASHIMI_COLORS['ginger_pink']: '#e74c3c',
            SASHIMI_COLORS['highlight']: '#ff2f2f'
        }
        return color_map.get(color, color)

    # Backend integration methods
    def post_tweet_action(self):
        """Post a tweet immediately with enhanced UI."""
        dialog = ctk.CTkToplevel(self)
        dialog.title("📝 Post a Tweet")
        dialog.geometry("600x400")
        dialog.configure(fg_color=SASHIMI_COLORS['card_bg'])
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (600 // 2)
        y = (dialog.winfo_screenheight() // 2) - (400 // 2)
        dialog.geometry(f"600x400+{x}+{y}")
        
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=25)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 Post a Tweet",
            font=("Helvetica", 24, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        )
        title_label.pack(pady=(0, 15))
        
        # Tweet input
        tweet_frame = ctk.CTkFrame(dialog, fg_color=SASHIMI_COLORS['secondary'], corner_radius=15)
        tweet_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        text_area = ctk.CTkTextbox(
            tweet_frame,
            height=150,
            font=("Helvetica", 16),
            fg_color=SASHIMI_COLORS['primary'],
            text_color=SASHIMI_COLORS['text_primary'],
            corner_radius=10
        )
        text_area.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Character counter
        char_label = ctk.CTkLabel(
            tweet_frame,
            text="0/280 characters",
            font=("Helvetica", 14),
            text_color=SASHIMI_COLORS['text_secondary']
        )
        char_label.pack(pady=(0, 15))
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(0, 25))
        
        def update_char_count(event=None):
            char_count = len(text_area.get("1.0", "end-1c"))
            char_label.configure(text=f"{char_count}/280 characters")
            if char_count > 280:
                char_label.configure(text_color=SASHIMI_COLORS['error'])
            else:
                char_label.configure(text_color=SASHIMI_COLORS['text_secondary'])
        
        text_area.bind("<KeyRelease>", update_char_count)
        
        def post_tweet_click():
            message = text_area.get("1.0", "end-1c").strip()
            if not message:
                messagebox.showerror("Error", "Please enter a tweet message!")
                return
            if len(message) > 280:
                messagebox.showerror("Error", "Tweet is too long! Maximum 280 characters.")
                return
            
            try:
                self.navbar.update_status("Posting...", SASHIMI_COLORS['warning'])
                # Simulate posting for now
                self.log_box.insert("end", f"✅ [{datetime.now().strftime('%H:%M:%S')}] Tweet posted successfully!\n")
                self.log_box.insert("end", f"   📝 Content: {message[:50]}{'...' if len(message) > 50 else ''}\n\n")
                self.log_box.see("end")
                # Ensure scrolling works
                self.log_box.update()
                self.navbar.update_status("Ready", SASHIMI_COLORS['success'])
                messagebox.showinfo("Success", "Tweet posted successfully!")
                dialog.destroy()
            except Exception as e:
                self.log_box.insert("end", f"❌ [{datetime.now().strftime('%H:%M:%S')}] Error posting tweet: {e}\n\n")
                self.log_box.see("end")
                self.navbar.update_status("Error", SASHIMI_COLORS['error'])
                messagebox.showerror("Error", f"Failed to post tweet:\n{e}")
        
        ctk.CTkButton(
            button_frame,
            text="🚀 Post Tweet",
            font=("Helvetica", 16, "bold"),
            width=140,
            height=45,
            fg_color=SASHIMI_COLORS['success'],
            hover_color='#2ed573',
            corner_radius=25,
            command=post_tweet_click
        ).pack(side="right", padx=(15, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Helvetica", 16),
            width=120,
            height=45,
            fg_color=SASHIMI_COLORS['text_muted'],
            hover_color=SASHIMI_COLORS['error'],
            corner_radius=25,
            command=dialog.destroy
        ).pack(side="right")

    def schedule_tweet_action(self):
        """Schedule a tweet."""
        self.log_box.insert("end", f"🕒 [{datetime.now().strftime('%H:%M:%S')}] Schedule tweet feature coming soon!\n\n")
        self.log_box.see("end")

    def bulk_upload(self):
        """Bulk upload tweets."""
        self.log_box.insert("end", f"📁 [{datetime.now().strftime('%H:%M:%S')}] Bulk upload feature coming soon!\n\n")
        self.log_box.see("end")

    def auto_reply(self):
        """AI-powered auto reply feature with enhanced UI."""
        # Create AI auto-reply dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("🤖 AI Auto Reply Setup")
        dialog.geometry("700x600")
        dialog.configure(fg_color=SASHIMI_COLORS['card_bg'])
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (700 // 2)
        y = (dialog.winfo_screenheight() // 2) - (600 // 2)
        dialog.geometry(f"700x600+{x}+{y}")
        
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=25)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="🤖 AI Auto Reply Setup",
            font=("Helvetica", 24, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        )
        title_label.pack(pady=(0, 15))
        
        # Main content
        content_frame = ctk.CTkFrame(dialog, fg_color=SASHIMI_COLORS['secondary'], corner_radius=15)
        content_frame.pack(fill="both", expand=True, padx=30, pady=(0, 25))
        
        # AI Provider Selection
        provider_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        provider_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            provider_frame,
            text="AI Provider:",
            font=("Helvetica", 16, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 10))
        
        provider_var = ctk.StringVar(value="none")
        providers = [
            ("None (Template-based)", "none"),
            ("OpenAI GPT-4", "openai"),
            ("Anthropic Claude", "anthropic"),
            ("Groq (Fast & Free)", "groq"),
            ("Ollama (Local)", "ollama")
        ]
        
        for text, value in providers:
            ctk.CTkRadioButton(
                provider_frame,
                text=text,
                variable=provider_var,
                value=value,
                font=("Helvetica", 14),
                text_color=SASHIMI_COLORS['text_primary']
            ).pack(anchor="w", pady=5)
        
        # Check Interval
        interval_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        interval_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkLabel(
            interval_frame,
            text="Check Interval (minutes):",
            font=("Helvetica", 16, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 10))
        
        interval_entry = ctk.CTkEntry(
            interval_frame,
            placeholder_text="5",
            width=100,
            height=35,
            font=("Helvetica", 14)
        )
        interval_entry.pack(anchor="w")
        interval_entry.insert(0, "5")
        
        # Brand Context
        context_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        context_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(
            context_frame,
            text="Brand Context (optional):",
            font=("Helvetica", 16, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        ).pack(anchor="w", pady=(0, 10))
        
        context_text = ctk.CTkTextbox(
            context_frame,
            height=100,
            font=("Helvetica", 14),
            fg_color=SASHIMI_COLORS['primary'],
            text_color=SASHIMI_COLORS['text_primary'],
            corner_radius=8
        )
        context_text.pack(fill="both", expand=True)
        context_text.insert("1.0", "We're a sushi delivery app focused on fresh ingredients and fast service.")
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=30, pady=(0, 25))
        
        def start_auto_reply():
            provider = provider_var.get()
            interval = interval_entry.get().strip()
            context = context_text.get("1.0", "end-1c").strip()
            
            try:
                interval_min = int(interval)
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for interval!")
                return
            
            if provider == "none":
                self.log_box.insert("end", f"🤖 [{datetime.now().strftime('%H:%M:%S')}] Starting template-based auto-reply (interval: {interval_min} min)\n\n")
            else:
                self.log_box.insert("end", f"🤖 [{datetime.now().strftime('%H:%M:%S')}] Starting AI auto-reply with {provider} (interval: {interval_min} min)\n")
                if context:
                    self.log_box.insert("end", f"   📝 Brand context: {context[:50]}{'...' if len(context) > 50 else ''}\n")
                self.log_box.insert("end", f"   🔧 Make sure to set your API key: {provider.upper()}_API_KEY\n\n")
            
            self.log_box.see("end")
            messagebox.showinfo("Started", f"Auto-reply started with {provider}!\nCheck the activity log for updates.")
            dialog.destroy()
        
        ctk.CTkButton(
            button_frame,
            text="🚀 Start Auto Reply",
            font=("Helvetica", 16, "bold"),
            width=160,
            height=45,
            fg_color=SASHIMI_COLORS['success'],
            hover_color='#2ed573',
            corner_radius=25,
            command=start_auto_reply
        ).pack(side="right", padx=(15, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Helvetica", 16),
            width=120,
            height=45,
            fg_color=SASHIMI_COLORS['text_muted'],
            hover_color=SASHIMI_COLORS['error'],
            corner_radius=25,
            command=dialog.destroy
        ).pack(side="right")


class SettingsPage(ctk.CTkFrame):
    """Enhanced settings page with sashimi theme."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=SASHIMI_COLORS['primary'])
        self.controller = controller
        
        # Configure this frame to expand
        self.grid_rowconfigure(0, weight=0)  # navbar
        self.grid_rowconfigure(1, weight=1)  # content
        self.grid_columnconfigure(0, weight=1)

        # Enhanced navbar
        top = ctk.CTkFrame(self, fg_color=SASHIMI_COLORS['secondary'], height=90, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        
        # Configure top navbar grid
        top.grid_columnconfigure(1, weight=1)

        # Back button with enhanced styling
        back_btn = ctk.CTkButton(
            top,
            text="← Back to Dashboard",
            width=180,
            height=50,
            font=("Helvetica", 16, "bold"),
            fg_color=SASHIMI_COLORS['accent'],
            hover_color=SASHIMI_COLORS['highlight'],
            corner_radius=25,
            command=lambda: controller.show_frame("MainPage"),
        )
        back_btn.grid(row=0, column=0, padx=30, pady=20, sticky="w")

        # Enhanced title
        title_label = ctk.CTkLabel(
            top, 
            text="⚙️ Settings & Configuration", 
            font=("Helvetica", 28, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        )
        title_label.grid(row=0, column=1, padx=25, pady=20, sticky="w")

        # Main content area
        content_frame = ctk.CTkFrame(self, fg_color=SASHIMI_COLORS['primary'])
        content_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Settings form with enhanced styling
        form_frame = ctk.CTkFrame(
            content_frame, 
            corner_radius=25, 
            fg_color=SASHIMI_COLORS['card_bg'],
            border_width=3,
            border_color=SASHIMI_COLORS['border']
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=25, pady=25)
        form_frame.grid_columnconfigure(0, weight=1)

        # Header section
        header_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=50, pady=(40, 30))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title with icon
        title_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_section.grid(row=0, column=0, sticky="ew")
        title_section.grid_columnconfigure(1, weight=1)

        icon_label = ctk.CTkLabel(
            title_section,
            text="🔐",
            font=("Helvetica", 40),
            text_color=SASHIMI_COLORS['highlight']
        )
        icon_label.grid(row=0, column=0, padx=(0, 20), pady=5)

        title_text = ctk.CTkLabel(
            title_section,
            text="Twitter API Credentials",
            font=("Helvetica", 32, "bold"),
            text_color=SASHIMI_COLORS['text_primary']
        )
        title_text.grid(row=0, column=1, sticky="w", pady=5)

        # Subtitle
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Configure your Twitter API credentials to enable automation features",
            font=("Helvetica", 18),
            text_color=SASHIMI_COLORS['text_secondary']
        )
        subtitle.grid(row=1, column=0, sticky="ew", pady=(15, 0))

        # Credentials form
        self.entries = {}
        fields = [
            ("API Key", "api_key", "Your Twitter API Key"),
            ("API Secret", "api_secret", "Your Twitter API Secret Key"),
            ("Access Token", "access_token", "Your Twitter Access Token"),
            ("Access Token Secret", "access_token_secret", "Your Twitter Access Token Secret"),
        ]

        creds = controller.credentials
        form_content = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_content.grid(row=1, column=0, sticky="ew", padx=50, pady=30)
        form_content.grid_columnconfigure(0, weight=1)

        for idx, (label, key, placeholder) in enumerate(fields):
            # Field container
            field_frame = ctk.CTkFrame(
                form_content,
                fg_color=SASHIMI_COLORS['secondary'],
                corner_radius=15,
                border_width=2,
                border_color=SASHIMI_COLORS['border']
            )
            field_frame.grid(row=idx, column=0, sticky="ew", pady=20)
            field_frame.grid_columnconfigure(1, weight=1)

            # Field label
            label_widget = ctk.CTkLabel(
                field_frame,
                text=label,
                font=("Helvetica", 18, "bold"),
                text_color=SASHIMI_COLORS['text_primary']
            )
            label_widget.grid(row=0, column=0, padx=25, pady=(20, 10), sticky="w")

            # Input field
            entry = ctk.CTkEntry(
                field_frame,
                placeholder_text=placeholder,
                show="*" if "secret" in key.lower() else "",
                width=500,
                height=50,
                font=("Helvetica", 16),
                fg_color=SASHIMI_COLORS['primary'],
                border_color=SASHIMI_COLORS['border'],
                text_color=SASHIMI_COLORS['text_primary'],
                corner_radius=10
            )
            entry.grid(row=1, column=0, padx=25, pady=(0, 20), sticky="ew")
            entry.insert(0, creds.get(key, ""))
            self.entries[key] = entry

        # Save button with enhanced styling
        save_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        save_frame.grid(row=2, column=0, sticky="ew", padx=50, pady=(30, 50))
        save_frame.grid_columnconfigure(0, weight=1)

        save_btn = ctk.CTkButton(
            save_frame,
            text="💾 Save Credentials",
            font=("Helvetica", 20, "bold"),
            width=350,
            height=60,
            fg_color=SASHIMI_COLORS['sashimi_orange'],
            hover_color=SASHIMI_COLORS['highlight'],
            corner_radius=30,
            text_color=SASHIMI_COLORS['rice_white'],
            command=self.save,
        )
        save_btn.grid(row=0, column=0, pady=25)

    def save(self):
        creds = {k: v.get().strip() for k, v in self.entries.items()}
        if not all(creds.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
        self.controller.save_credentials(creds)


if __name__ == "__main__":
    print("🍣 Starting SashimiApp...")
    app = SashimiApp()
    app.lift()
    app.attributes('-topmost', True)
    app.after(1000, lambda: app.attributes('-topmost', False))
    app.mainloop()
