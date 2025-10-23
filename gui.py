"""
PizzaApp - Professional Twitter Automation GUI
Built with customtkinter (Modern Dark Design with Enhanced UI)
"""

import os, sys

# Ensure the app always loads the local gui.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print("✅ Running launcher from:", BASE_DIR)
print("✅ sys.path[0]:", sys.path[0])
# Required local imports for this module
from pathlib import Path
import json
import re
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog
from datetime import datetime
import time

# backend helpers
from tweet import (
    schedule_tweet,
    schedule_tweet_in_month,
    bulk_schedule_from_file,
    auto_reply_ai,
)
from token_manager import get_tokens

# Import backend functions from tweet.py
from tweet import post_tweet, schedule_tweet, bulk_post_from_file, auto_reply_to_mentions
from twitter_utils import read_tweets_from_file

CONFIG_FILE = Path("config.json")

# Modern Color Palette
COLORS = {
    'primary': '#1a1a2e',
    'secondary': '#16213e', 
    'accent': '#0f3460',
    'highlight': '#e94560',
    'success': '#2ecc71',
    'warning': '#f39c12',
    'error': '#e74c3c',
    'text_primary': '#ffffff',
    'text_secondary': '#bdc3c7',
    'text_muted': '#7f8c8d',
    'card_bg': '#2c3e50',
    'card_hover': '#34495e',
    'border': '#3498db',
    'gradient_start': '#667eea',
    'gradient_end': '#764ba2'
}


class PizzaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App window with enhanced styling
        self.title("🍕 PizzaApp - X Automation")
        self.geometry("1200x800")
        self.minsize(1000, 700)
        self.resizable(True, True)
        
        # Set modern dark theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Configure window styling
        self.configure(fg_color=COLORS['primary'])

        # Root grid config (important!)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Load credentials if exist
        self.credentials = self.load_credentials()

        # Create container frame with enhanced styling
        self.container = ctk.CTkFrame(
            self, 
            corner_radius=0,
            fg_color=COLORS['primary'],
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
        print(f"Switching to: {page_name}")
        frame.tkraise()
        frame.update_idletasks()


    def load_credentials(self):
        """Load saved credentials or return default structure."""
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
            
            messagebox.showinfo("Success", "✅ Credentials saved successfully!")
            self.credentials = creds
            self.show_frame("MainPage")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials:\n{e}")


class NavBar(ctk.CTkFrame):
    """Enhanced top navigation bar with modern styling."""

    def __init__(self, parent, controller):
        super().__init__(
            parent, 
            fg_color=COLORS['secondary'], 
            height=80,
            corner_radius=0,
            border_width=0
        )
        self.controller = controller
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Title column expands
        
        # Enhanced logo with better styling
        self.logo_label = ctk.CTkLabel(
            self, 
            text="🍕", 
            font=("Helvetica", 32),
            text_color=COLORS['highlight']
        )
        self.logo_label.grid(row=0, column=0, padx=25, pady=15, sticky="w")

        # Enhanced app title with gradient effect
        self.title_label = ctk.CTkLabel(
            self, 
            text="PizzaApp – X Automation", 
            font=("Helvetica", 24, "bold"),
            text_color=COLORS['text_primary']
        )
        self.title_label.grid(row=0, column=1, padx=10, pady=15, sticky="w")

        # Status indicator
        self.status_label = ctk.CTkLabel(
            self,
            text="● Ready",
            font=("Helvetica", 12),
            text_color=COLORS['success']
        )
        self.status_label.grid(row=0, column=2, padx=10, pady=15, sticky="e")
        
    def update_status(self, status, color=None):
        """Update the status indicator."""
        if color is None:
            color = COLORS['success']
        self.status_label.configure(text=f"● {status}", text_color=color)

        # Enhanced settings button with modern styling
        self.settings_button = ctk.CTkButton(
            self,
            text="⚙️ Settings",
            width=120,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=COLORS['accent'],
            hover_color=COLORS['highlight'],
            corner_radius=20,
            border_width=0,
            command=lambda: controller.show_frame("SettingsPage"),
        )
        self.settings_button.grid(row=0, column=3, padx=25, pady=15, sticky="e")


class MainPage(ctk.CTkFrame):
    """Enhanced main dashboard page with modern card layout."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLORS['primary'])
        self.controller = controller
        
        # Configure this frame to expand
        self.grid_rowconfigure(0, weight=0)  # navbar
        self.grid_rowconfigure(1, weight=1)  # content
        self.grid_columnconfigure(0, weight=1)

        # Enhanced navbar
        self.navbar = NavBar(self, controller)
        self.navbar.grid(row=0, column=0, sticky="ew")

        # Main content area with padding
        content_frame = ctk.CTkFrame(self, fg_color=COLORS['primary'])
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(1, weight=1)

        # Welcome header
        header_frame = ctk.CTkFrame(
            content_frame, 
            fg_color=COLORS['card_bg'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border']
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        # Welcome title with enhanced styling
        welcome_label = ctk.CTkLabel(
            header_frame,
            text="🚀 Twitter Automation Dashboard",
            font=("Helvetica", 28, "bold"),
            text_color=COLORS['text_primary']
        )
        welcome_label.grid(row=0, column=0, pady=25, padx=30)

        # Subtitle
        subtitle_label = ctk.CTkLabel(
            header_frame,
            text="Manage your Twitter presence with powerful automation tools",
            font=("Helvetica", 16),
            text_color=COLORS['text_secondary']
        )
        subtitle_label.grid(row=1, column=0, pady=(0, 25), padx=30)

        # Main content area with cards
        main_content = ctk.CTkFrame(content_frame, fg_color=COLORS['primary'])
        main_content.grid(row=1, column=0, sticky="nsew")
        main_content.grid_columnconfigure((0, 1), weight=1)
        main_content.grid_rowconfigure(0, weight=1)

        # Left column - Action cards
        left_column = ctk.CTkFrame(main_content, fg_color=COLORS['primary'])
        left_column.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        left_column.grid_columnconfigure(0, weight=1)

        # Action buttons with enhanced styling
        action_buttons = [
            ("📝", "Post a Tweet", "Post immediately to your timeline", self.post_tweet_action, COLORS['success']),
            ("🕒", "Schedule Tweet", "Schedule tweets for later", self.schedule_tweet_action, COLORS['warning']),
            ("📁", "Bulk Upload", "Upload multiple tweets at once", self.bulk_upload, COLORS['accent']),
            ("🤖", "Auto Reply", "AI-powered automatic replies", self.auto_reply, COLORS['highlight']),
        ]

        for idx, (icon, title, description, command, color) in enumerate(action_buttons):
            self.create_action_card(left_column, icon, title, description, command, color, idx)

        # Right column - Activity log
        right_column = ctk.CTkFrame(main_content, fg_color=COLORS['primary'])
        right_column.grid(row=0, column=1, sticky="nsew", padx=(15, 0))
        right_column.grid_columnconfigure(0, weight=1)
        right_column.grid_rowconfigure(1, weight=1)

        # Activity log header
        log_header = ctk.CTkFrame(right_column, fg_color=COLORS['card_bg'], corner_radius=10)
        log_header.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        log_title = ctk.CTkLabel(
            log_header,
            text="📊 Activity Log",
            font=("Helvetica", 18, "bold"),
            text_color=COLORS['text_primary']
        )
        log_title.grid(row=0, column=0, pady=15, padx=20)

        # Enhanced log box
        self.log_box = ctk.CTkTextbox(
            right_column, 
            height=400,
            font=("Consolas", 12),
            fg_color=COLORS['card_bg'],
            text_color=COLORS['text_primary'],
            corner_radius=10,
            border_width=1,
            border_color=COLORS['border']
        )
        self.log_box.grid(row=1, column=0, sticky="nsew")
        self.log_box.insert("end", f"🍕 [{datetime.now().strftime('%H:%M:%S')}] Welcome to PizzaApp! Ready to automate your Twitter presence.\n")
        self.log_box.insert("end", f"💡 [{datetime.now().strftime('%H:%M:%S')}] Tip: Use the cards on the left to get started with automation.\n")
        self.log_box.insert("end", f"🔧 [{datetime.now().strftime('%H:%M:%S')}] Make sure to configure your Twitter API credentials in Settings.\n\n")

    def create_action_card(self, parent, icon, title, description, command, color, row):
        """Create a modern action card with enhanced styling."""
        card = ctk.CTkFrame(
            parent,
            fg_color=COLORS['card_bg'],
            corner_radius=15,
            border_width=1,
            border_color=COLORS['border']
        )
        card.grid(row=row, column=0, sticky="ew", pady=10, padx=10)
        card.grid_columnconfigure(0, weight=1)

        # Card content
        content_frame = ctk.CTkFrame(card, fg_color="transparent")
        content_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        content_frame.grid_columnconfigure(1, weight=1)

        # Icon
        icon_label = ctk.CTkLabel(
            content_frame,
            text=icon,
            font=("Helvetica", 24),
            text_color=color
        )
        icon_label.grid(row=0, column=0, padx=(0, 15), pady=5, sticky="nw")

        # Text content
        text_frame = ctk.CTkFrame(content_frame, fg_color="transparent")
        text_frame.grid(row=0, column=1, sticky="ew")
        text_frame.grid_columnconfigure(0, weight=1)

        # Title
        title_label = ctk.CTkLabel(
            text_frame,
            text=title,
            font=("Helvetica", 16, "bold"),
            text_color=COLORS['text_primary'],
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="ew", pady=(0, 5))

        # Description
        desc_label = ctk.CTkLabel(
            text_frame,
            text=description,
            font=("Helvetica", 12),
            text_color=COLORS['text_secondary'],
            anchor="w"
        )
        desc_label.grid(row=1, column=0, sticky="ew")

        # Action button
        action_btn = ctk.CTkButton(
            card,
            text="Go",
            width=80,
            height=35,
            font=("Helvetica", 12, "bold"),
            fg_color=color,
            hover_color=self.darken_color(color),
            corner_radius=18,
            command=command
        )
        action_btn.grid(row=1, column=0, pady=(0, 20), padx=20, sticky="e")

    def darken_color(self, color):
        """Helper to darken a color for hover effects."""
        color_map = {
            COLORS['success']: '#27ae60',
            COLORS['warning']: '#e67e22', 
            COLORS['accent']: '#0d2847',
            COLORS['highlight']: '#c0392b'
        }
        return color_map.get(color, color)

    # --- Backend integration with tweet.py ---
    def post_tweet_action(self):
        """Post a tweet immediately with enhanced UI."""
        # Create custom dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("📝 Post a Tweet")
        dialog.geometry("500x300")
        dialog.configure(fg_color=COLORS['card_bg'])
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"500x300+{x}+{y}")
        
        # Header
        header_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=20)
        
        title_label = ctk.CTkLabel(
            header_frame,
            text="📝 Post a Tweet",
            font=("Helvetica", 20, "bold"),
            text_color=COLORS['text_primary']
        )
        title_label.pack(pady=(0, 10))
        
        # Tweet input
        tweet_frame = ctk.CTkFrame(dialog, fg_color=COLORS['secondary'], corner_radius=10)
        tweet_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        text_area = ctk.CTkTextbox(
            tweet_frame,
            height=120,
            font=("Helvetica", 14),
            fg_color=COLORS['primary'],
            text_color=COLORS['text_primary'],
            corner_radius=8
        )
        text_area.pack(fill="both", expand=True, padx=15, pady=15)
        
        # Character counter
        char_label = ctk.CTkLabel(
            tweet_frame,
            text="0/280 characters",
            font=("Helvetica", 12),
            text_color=COLORS['text_secondary']
        )
        char_label.pack(pady=(0, 10))
        
        # Buttons
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        def update_char_count(event=None):
            char_count = len(text_area.get("1.0", "end-1c"))
            char_label.configure(text=f"{char_count}/280 characters")
            if char_count > 280:
                char_label.configure(text_color=COLORS['error'])
            else:
                char_label.configure(text_color=COLORS['text_secondary'])
        
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
                self.navbar.update_status("Posting...", COLORS['warning'])
                post_tweet(message)
                self.log_box.insert("end", f"✅ [{datetime.now().strftime('%H:%M:%S')}] Tweet posted successfully!\n")
                self.log_box.insert("end", f"   📝 Content: {message[:50]}{'...' if len(message) > 50 else ''}\n\n")
                self.log_box.see("end")
                self.navbar.update_status("Ready", COLORS['success'])
                messagebox.showinfo("Success", "Tweet posted successfully!")
                dialog.destroy()
            except Exception as e:
                self.log_box.insert("end", f"❌ [{datetime.now().strftime('%H:%M:%S')}] Error posting tweet: {e}\n\n")
                self.log_box.see("end")
                self.navbar.update_status("Error", COLORS['error'])
                messagebox.showerror("Error", f"Failed to post tweet:\n{e}")
        
        ctk.CTkButton(
            button_frame,
            text="🚀 Post Tweet",
            font=("Helvetica", 14, "bold"),
            width=120,
            height=40,
            fg_color=COLORS['success'],
            hover_color='#27ae60',
            corner_radius=20,
            command=post_tweet_click
        ).pack(side="right", padx=(10, 0))
        
        ctk.CTkButton(
            button_frame,
            text="Cancel",
            font=("Helvetica", 14),
            width=100,
            height=40,
            fg_color=COLORS['text_muted'],
            hover_color=COLORS['error'],
            corner_radius=20,
            command=dialog.destroy
        ).pack(side="right")

    def schedule_tweet_action(self):
        """Schedule a tweet for a specific date/time via simple date/time selectors.

        Uses schedule_tweet_in_month if the date is within the current month, else falls
        back to schedule_tweet with computed delay.
        """
        # Ask for message first
        dialog = ctk.CTkInputDialog(text="Enter tweet message:", title="Schedule Tweet")
        message = dialog.get_input()
        if not message:
            return

        # Simple date/time dialog: day, month, year, hour, minute
        top = ctk.CTkToplevel(self)
        top.title("Pick date & time")
        top.geometry("380x220")

        now = datetime.now()
        years = [now.year, now.year + 1]
        months = list(range(1, 13))
        days = list(range(1, 32))
        hours = list(range(0, 24))
        minutes = [0, 15, 30, 45]

        vars = {}
        vars['year'] = ctk.StringVar(value=str(now.year))
        vars['month'] = ctk.StringVar(value=str(now.month))
        vars['day'] = ctk.StringVar(value=str(now.day))
        vars['hour'] = ctk.StringVar(value=str(now.hour))
        vars['minute'] = ctk.StringVar(value=str(0))

        r = 0
        ctk.CTkLabel(top, text="Year:").grid(row=r, column=0, padx=12, pady=6, sticky='w')
        ctk.CTkOptionMenu(top, values=[str(y) for y in years], variable=vars['year']).grid(row=r, column=1)
        r += 1
        ctk.CTkLabel(top, text="Month:").grid(row=r, column=0, padx=12, pady=6, sticky='w')
        ctk.CTkOptionMenu(top, values=[str(m) for m in months], variable=vars['month']).grid(row=r, column=1)
        r += 1
        ctk.CTkLabel(top, text="Day:").grid(row=r, column=0, padx=12, pady=6, sticky='w')
        ctk.CTkOptionMenu(top, values=[str(d) for d in days], variable=vars['day']).grid(row=r, column=1)
        r += 1
        ctk.CTkLabel(top, text="Hour (24h):").grid(row=r, column=0, padx=12, pady=6, sticky='w')
        ctk.CTkOptionMenu(top, values=[str(h) for h in hours], variable=vars['hour']).grid(row=r, column=1)
        r += 1
        ctk.CTkLabel(top, text="Minute:").grid(row=r, column=0, padx=12, pady=6, sticky='w')
        ctk.CTkOptionMenu(top, values=[str(m) for m in minutes], variable=vars['minute']).grid(row=r, column=1)
        r += 1

        def on_ok():
            y = int(vars['year'].get())
            mo = int(vars['month'].get())
            d = int(vars['day'].get())
            hh = int(vars['hour'].get())
            mm = int(vars['minute'].get())
            top.destroy()

            try:
                # If the scheduled date is in the current month and year, use schedule_tweet_in_month
                now = datetime.now()
                if y == now.year and mo == now.month:
                    schedule_tweet_in_month(message, y, mo, d, f"{hh:02d}:{mm:02d}")
                    self.log_box.insert("end", f"⏰ Tweet scheduled for {y}-{mo:02d}-{d:02d} {hh:02d}:{mm:02d}\n")
                else:
                    # Compute minutes until the datetime and use schedule_tweet
                    then = datetime(y, mo, d, hh, mm)
                    delta = then - now
                    minutes = int(max(0, delta.total_seconds() // 60))
                    schedule_tweet(message, delay_minutes=minutes)
                    self.log_box.insert("end", f"⏰ Tweet scheduled for {then.strftime('%Y-%m-%d %H:%M')}\n")
                messagebox.showinfo("Success", "Tweet scheduled!")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to schedule tweet:\n{e}")
            self.log_box.see("end")

        ctk.CTkButton(top, text="OK", command=on_ok).grid(row=r, column=0, pady=12)
        ctk.CTkButton(top, text="Cancel", command=top.destroy).grid(row=r, column=1, pady=12)


    def bulk_upload(self):
        """Bulk post tweets from a file."""
        filename = filedialog.askopenfilename(title="Select a file", filetypes=[("Text or CSV", "*.txt *.csv")])
        if not filename:
            return

        # Ask frequency with preset options
        freq_top = ctk.CTkToplevel(self)
        freq_top.title("Bulk frequency")
        freq_top.geometry("360x160")

        freq_var = ctk.StringVar(value="60")
        options = [("Every 30 minutes", "30"), ("Every hour", "60"), ("Every 4 hours", "240"), ("Every 8 hours", "480"), ("Every day", "1440")]
        r = 0
        ctk.CTkLabel(freq_top, text=f"Selected file: {filename}").grid(row=r, column=0, columnspan=2, pady=6, padx=12, sticky='w')
        r += 1
        for label, val in options:
            ctk.CTkRadioButton(freq_top, text=label, variable=freq_var, value=val).grid(row=r, column=0, sticky='w', padx=12)
            r += 1

        def on_start_bulk():
            freq_min = int(freq_var.get())
            self.log_box.insert("end", f"📁 Scheduling {filename} every {freq_min} minutes\n")

            def run_sched():
                try:
                    bulk_schedule_from_file(filename, freq_min)
                    self.log_box.insert("end", "✅ Bulk scheduling started!\n")
                except Exception as e:
                    self.log_box.insert("end", f"❌ Bulk scheduling error: {e}\n")
                self.log_box.see("end")

            thread = threading.Thread(target=run_sched, daemon=True)
            thread.start()
            messagebox.showinfo("Started", "Bulk scheduling started in background!")
            freq_top.destroy()

        ctk.CTkButton(freq_top, text="Start", command=on_start_bulk).grid(row=r, column=0, pady=8)
        ctk.CTkButton(freq_top, text="Cancel", command=freq_top.destroy).grid(row=r, column=1, pady=8)

        self.log_box.see("end")

    def auto_reply(self):
        """Start AI-powered auto-reply mode with token accounting."""
        # Ask for who to reply to (user spec) and interval
        spec_dialog = ctk.CTkInputDialog(text="Reply to which type of people? (e.g., people mentioning product X)", title="AI Auto Reply")
        user_spec = spec_dialog.get_input()
        if not user_spec:
            return

        interval_dialog = ctk.CTkInputDialog(text="Check interval (minutes):", title="Auto Reply")
        interval_str = interval_dialog.get_input()
        if not interval_str:
            return

        try:
            interval = int(interval_str)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid number")
            return

        # Start AI auto-reply thread
        def run_ai():
            try:
                auto_reply_ai(interval, user_spec)
            except Exception as e:
                self.log_box.insert("end", f"❌ AI Auto-reply error: {e}\n")
                self.log_box.see("end")

        thread = threading.Thread(target=run_ai, daemon=True)
        thread.start()
        left, limit = get_tokens()
        self.log_box.insert("end", f"🤖 AI Auto-reply started (interval {interval} min). Tokens left: {left}/{limit}\n")
        messagebox.showinfo("Started", "AI Auto-reply started!\nPress Ctrl+C in terminal to stop.")
        self.log_box.see("end")


class SettingsPage(ctk.CTkFrame):
    """Enhanced settings page with modern credential management."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color=COLORS['primary'])
        self.controller = controller
        
        # Configure this frame to expand
        self.grid_rowconfigure(0, weight=0)  # navbar
        self.grid_rowconfigure(1, weight=1)  # content
        self.grid_columnconfigure(0, weight=1)

        # Enhanced navbar
        top = ctk.CTkFrame(self, fg_color=COLORS['secondary'], height=80, corner_radius=0)
        top.grid(row=0, column=0, sticky="ew")
        
        # Configure top navbar grid
        top.grid_columnconfigure(1, weight=1)

        # Back button with enhanced styling
        back_btn = ctk.CTkButton(
            top,
            text="← Back to Dashboard",
            width=150,
            height=40,
            font=("Helvetica", 14, "bold"),
            fg_color=COLORS['accent'],
            hover_color=COLORS['highlight'],
            corner_radius=20,
            command=lambda: controller.show_frame("MainPage"),
        )
        back_btn.grid(row=0, column=0, padx=25, pady=15, sticky="w")

        # Enhanced title
        title_label = ctk.CTkLabel(
            top, 
            text="⚙️ Settings & Configuration", 
            font=("Helvetica", 24, "bold"),
            text_color=COLORS['text_primary']
        )
        title_label.grid(row=0, column=1, padx=20, pady=15, sticky="w")

        # Main content area
        content_frame = ctk.CTkFrame(self, fg_color=COLORS['primary'])
        content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        content_frame.grid_columnconfigure(0, weight=1)
        content_frame.grid_rowconfigure(0, weight=1)

        # Settings form with enhanced styling
        form_frame = ctk.CTkFrame(
            content_frame, 
            corner_radius=20, 
            fg_color=COLORS['card_bg'],
            border_width=1,
            border_color=COLORS['border']
        )
        form_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        form_frame.grid_columnconfigure(0, weight=1)

        # Header section
        header_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", padx=40, pady=(30, 20))
        header_frame.grid_columnconfigure(0, weight=1)

        # Title with icon
        title_section = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_section.grid(row=0, column=0, sticky="ew")
        title_section.grid_columnconfigure(1, weight=1)

        icon_label = ctk.CTkLabel(
            title_section,
            text="🔐",
            font=("Helvetica", 32),
            text_color=COLORS['highlight']
        )
        icon_label.grid(row=0, column=0, padx=(0, 15), pady=5)

        title_text = ctk.CTkLabel(
            title_section,
            text="Twitter API Credentials",
            font=("Helvetica", 26, "bold"),
            text_color=COLORS['text_primary']
        )
        title_text.grid(row=0, column=1, sticky="w", pady=5)

        # Subtitle
        subtitle = ctk.CTkLabel(
            header_frame,
            text="Configure your Twitter API credentials to enable automation features",
            font=("Helvetica", 16),
            text_color=COLORS['text_secondary']
        )
        subtitle.grid(row=1, column=0, sticky="ew", pady=(10, 0))

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
        form_content.grid(row=1, column=0, sticky="ew", padx=40, pady=20)
        form_content.grid_columnconfigure(0, weight=1)

        for idx, (label, key, placeholder) in enumerate(fields):
            # Field container
            field_frame = ctk.CTkFrame(
                form_content,
                fg_color=COLORS['secondary'],
                corner_radius=12,
                border_width=1,
                border_color=COLORS['border']
            )
            field_frame.grid(row=idx, column=0, sticky="ew", pady=15)
            field_frame.grid_columnconfigure(1, weight=1)

            # Field label
            label_widget = ctk.CTkLabel(
                field_frame,
                text=label,
                font=("Helvetica", 16, "bold"),
                text_color=COLORS['text_primary']
            )
            label_widget.grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

            # Input field
            entry = ctk.CTkEntry(
                field_frame,
                placeholder_text=placeholder,
                show="*" if "secret" in key.lower() else "",
                width=400,
                height=45,
                font=("Helvetica", 14),
                fg_color=COLORS['primary'],
                border_color=COLORS['border'],
                text_color=COLORS['text_primary'],
                corner_radius=8
            )
            entry.grid(row=1, column=0, padx=20, pady=(0, 15), sticky="ew")
            entry.insert(0, creds.get(key, ""))
            self.entries[key] = entry

        # Save button with enhanced styling
        save_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        save_frame.grid(row=2, column=0, sticky="ew", padx=40, pady=(20, 40))
        save_frame.grid_columnconfigure(0, weight=1)

        save_btn = ctk.CTkButton(
            save_frame,
            text="💾 Save Credentials",
            font=("Helvetica", 18, "bold"),
            width=300,
            height=50,
            fg_color=COLORS['success'],
            hover_color='#27ae60',
            corner_radius=25,
            command=self.save,
        )
        save_btn.grid(row=0, column=0, pady=20)

    def save(self):
        creds = {k: v.get().strip() for k, v in self.entries.items()}
        if not all(creds.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
        self.controller.save_credentials(creds)
