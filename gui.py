"""
PizzaApp - Professional Twitter Automation GUI
Built with customtkinter (Dark Modern Design)
"""

import os, sys

# Ensure the app always loads the local gui.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

print("✅ Running launcher from:", BASE_DIR)
print("✅ sys.path[0]:", sys.path[0])

from gui import PizzaApp
print("✅ Imported PizzaApp from:", PizzaApp.__module__)

# Import backend functions from tweet.py
from tweet import post_tweet, schedule_tweet, bulk_post_from_file, auto_reply_to_mentions
from twitter_utils import read_tweets_from_file

CONFIG_FILE = Path("config.json")


class PizzaApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # App window
        self.title("🍕 PizzaApp - X Automation")
        self.geometry("900x600")
        self.resizable(False, False)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Root grid config (important!)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Load credentials if exist
        self.credentials = self.load_credentials()

        # Create container frame (using grid, not pack)
        self.container = ctk.CTkFrame(self, corner_radius=0)
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
    """Top navigation bar with app title and settings icon."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#1E2733", height=60)
        self.controller = controller
        
        # Configure grid
        self.grid_columnconfigure(1, weight=1)  # Title column expands
        
        # Logo
        self.logo_label = ctk.CTkLabel(self, text="🍕", font=("Helvetica", 26))
        self.logo_label.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        # App title
        self.title_label = ctk.CTkLabel(
            self, text="PizzaApp – X Automation", font=("Helvetica", 20, "bold")
        )
        self.title_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # Settings button
        self.settings_button = ctk.CTkButton(
            self,
            text="⚙️ Settings",
            width=100,
            height=30,
            fg_color="#2E3B4E",
            hover_color="#3E5069",
            command=lambda: controller.show_frame("SettingsPage"),
        )
        self.settings_button.grid(row=0, column=2, padx=20, pady=10, sticky="e")


class MainPage(ctk.CTkFrame):
    """Main dashboard page."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#19232D")
        self.controller = controller
        
        # Configure this frame to expand
        self.grid_rowconfigure(0, weight=0)  # navbar
        self.grid_rowconfigure(1, weight=1)  # content
        self.grid_columnconfigure(0, weight=1)

        # Navbar
        navbar = NavBar(self, controller)
        navbar.grid(row=0, column=0, sticky="ew")

        # Main layout
        main_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#22303C")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=40)
        
        # Configure main_frame grid
        main_frame.grid_columnconfigure(0, weight=1)
        for i in range(7):  # rows: title + 4 buttons + log label + log box
            main_frame.grid_rowconfigure(i, weight=0 if i < 6 else 1)

        # Title
        ctk.CTkLabel(
            main_frame,
            text="Twitter Automation Dashboard",
            font=("Helvetica", 22, "bold"),
        ).grid(row=0, column=0, pady=(20, 40), padx=20)

        # Action buttons
        buttons = [
            ("📝 Post a Tweet", self.post_tweet_action),
            ("🕒 Schedule Tweet", self.schedule_tweet_action),
            ("📁 Bulk Upload", self.bulk_upload),
            ("🤖 Auto Reply Mode", self.auto_reply),
        ]

        for idx, (text, command) in enumerate(buttons, start=1):
            btn = ctk.CTkButton(
                main_frame,
                text=text,
                font=("Helvetica", 15),
                width=300,
                height=50,
                corner_radius=8,
                command=command,
            )
            btn.grid(row=idx, column=0, pady=10, padx=20)

        # Log box
        self.log_box = ctk.CTkTextbox(main_frame, height=120, width=500)
        self.log_box.grid(row=5, column=0, pady=30, padx=20, sticky="ew")
        self.log_box.insert("end", "Welcome to PizzaApp! 🍕\n")

    # --- Backend integration with tweet.py ---
    def post_tweet_action(self):
        """Post a tweet immediately."""
        dialog = ctk.CTkInputDialog(
            text="Enter your tweet message:",
            title="Post Tweet"
        )
        message = dialog.get_input()
        
        if message:
            try:
                post_tweet(message)
                self.log_box.insert("end", f"✅ Tweet posted successfully!\n")
                messagebox.showinfo("Success", "Tweet posted!")
            except Exception as e:
                self.log_box.insert("end", f"❌ Error: {e}\n")
                messagebox.showerror("Error", f"Failed to post tweet:\n{e}")
        self.log_box.see("end")

    def schedule_tweet_action(self):
        """Schedule a tweet for later."""
        dialog = ctk.CTkInputDialog(
            text="Enter tweet message:",
            title="Schedule Tweet"
        )
        message = dialog.get_input()
        
        if message:
            delay_dialog = ctk.CTkInputDialog(
                text="Delay in minutes:",
                title="Schedule Tweet"
            )
            delay_str = delay_dialog.get_input()
            
            if delay_str:
                try:
                    delay_minutes = int(delay_str)
                    schedule_tweet(message, delay_minutes=delay_minutes)
                    self.log_box.insert("end", f"⏰ Tweet scheduled for {delay_minutes} min from now\n")
                    messagebox.showinfo("Success", f"Tweet scheduled for {delay_minutes} minutes from now!")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number of minutes")
                except Exception as e:
                    self.log_box.insert("end", f"❌ Error: {e}\n")
                    messagebox.showerror("Error", f"Failed to schedule tweet:\n{e}")
        self.log_box.see("end")

    def bulk_upload(self):
        """Bulk post tweets from a file."""
        filename = filedialog.askopenfilename(
            title="Select a file", filetypes=[("Text or CSV", "*.txt *.csv")]
        )
        if filename:
            delay_dialog = ctk.CTkInputDialog(
                text="Delay between posts (minutes):",
                title="Bulk Upload"
            )
            delay_str = delay_dialog.get_input()
            
            if delay_str:
                try:
                    delay = int(delay_str)
                    self.log_box.insert("end", f"📁 Loading file: {filename}\n")
                    
                    def run_bulk():
                        try:
                            bulk_post_from_file(filename, delay)
                            self.log_box.insert("end", "✅ Bulk posting completed!\n")
                            self.log_box.see("end")
                        except Exception as e:
                            self.log_box.insert("end", f"❌ Bulk error: {e}\n")
                            self.log_box.see("end")
                    
                    thread = threading.Thread(target=run_bulk, daemon=True)
                    thread.start()
                    messagebox.showinfo("Started", "Bulk posting started in background!")
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid number")
                except Exception as e:
                    messagebox.showerror("Error", f"Error: {e}")
        self.log_box.see("end")

    def auto_reply(self):
        """Start auto-reply mode with AI or fixed message options."""
        # Create custom dialog for AI configuration
        dialog = ctk.CTkToplevel(self)
        dialog.title("Auto Reply Configuration")
        dialog.geometry("500x600")
        dialog.resizable(False, False)

        # Make it modal
        dialog.grab_set()

        # Store result
        result = {"confirmed": False}

        # Title
        ctk.CTkLabel(
            dialog,
            text="Configure Auto-Reply",
            font=("Helvetica", 18, "bold")
        ).pack(pady=20)

        # Check interval
        ctk.CTkLabel(dialog, text="Check Interval (minutes):").pack(pady=(10, 5))
        interval_entry = ctk.CTkEntry(dialog, width=300, placeholder_text="e.g., 5")
        interval_entry.pack(pady=5)
        interval_entry.insert(0, "5")

        # AI Mode Toggle
        ctk.CTkLabel(dialog, text="Reply Mode:", font=("Helvetica", 14, "bold")).pack(pady=(20, 10))

        ai_mode_var = ctk.StringVar(value="fixed")

        ctk.CTkRadioButton(
            dialog,
            text="🤖 AI-Generated Replies (Smart & Contextual)",
            variable=ai_mode_var,
            value="ai"
        ).pack(pady=5)

        ctk.CTkRadioButton(
            dialog,
            text="💬 Fixed Message (Same reply every time)",
            variable=ai_mode_var,
            value="fixed"
        ).pack(pady=5)

        # AI Provider Selection
        ctk.CTkLabel(dialog, text="AI Provider (if using AI):", font=("Helvetica", 12)).pack(pady=(20, 5))

        provider_var = ctk.StringVar(value="anthropic")
        provider_menu = ctk.CTkOptionMenu(
            dialog,
            values=["anthropic", "openai", "groq", "ollama", "none"],
            variable=provider_var,
            width=300
        )
        provider_menu.pack(pady=5)

        # Optional: Brand context for AI
        ctk.CTkLabel(dialog, text="Brand Context (optional, for AI):", font=("Helvetica", 12)).pack(pady=(15, 5))
        context_entry = ctk.CTkEntry(
            dialog,
            width=400,
            placeholder_text="e.g., 'We're a pizza delivery app'"
        )
        context_entry.pack(pady=5)

        # Fixed message (for non-AI mode)
        ctk.CTkLabel(dialog, text="Fixed Reply Message (if not using AI):", font=("Helvetica", 12)).pack(pady=(15, 5))
        message_entry = ctk.CTkEntry(
            dialog,
            width=400,
            placeholder_text="e.g., 'Thanks for reaching out!'"
        )
        message_entry.pack(pady=5)

        # Buttons
        def on_start():
            result["confirmed"] = True
            result["interval"] = interval_entry.get()
            result["use_ai"] = ai_mode_var.get() == "ai"
            result["provider"] = provider_var.get()
            result["context"] = context_entry.get()
            result["message"] = message_entry.get()
            dialog.destroy()

        def on_cancel():
            dialog.destroy()

        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(pady=20)

        ctk.CTkButton(
            button_frame,
            text="Start Auto-Reply",
            command=on_start,
            width=150,
            fg_color="#3A9E5B",
            hover_color="#4BBF6B"
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            button_frame,
            text="Cancel",
            command=on_cancel,
            width=150,
            fg_color="#C84B4B",
            hover_color="#D65B5B"
        ).pack(side="left", padx=10)

        # Wait for dialog to close
        self.wait_window(dialog)

        # Process result
        if result.get("confirmed"):
            try:
                interval = int(result["interval"])
                use_ai = result["use_ai"]
                provider = result["provider"]
                context = result["context"] or None
                message = result["message"]

                if not use_ai and not message:
                    messagebox.showerror("Error", "Please provide a fixed message or enable AI mode")
                    return

                mode_desc = f"AI ({provider})" if use_ai else "Fixed message"
                self.log_box.insert("end", f"🤖 Starting auto-reply: {mode_desc} (every {interval} min)\n")

                def run_auto_reply():
                    try:
                        auto_reply_to_mentions(
                            interval_minutes=interval,
                            reply_message=message,
                            use_ai=use_ai,
                            ai_provider=provider,
                            ai_context=context,
                        )
                    except Exception as e:
                        self.log_box.insert("end", f"❌ Auto-reply error: {e}\n")
                        self.log_box.see("end")

                thread = threading.Thread(target=run_auto_reply, daemon=True)
                thread.start()
                messagebox.showinfo(
                    "Started",
                    f"Auto-reply mode started with {mode_desc}!\n\n"
                    f"Note: If using AI, ensure you've set the API key:\n"
                    f"export {provider.upper()}_API_KEY='your-key'"
                )
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid number for interval")
            except Exception as e:
                messagebox.showerror("Error", f"Error: {e}")

        self.log_box.see("end")


class SettingsPage(ctk.CTkFrame):
    """Settings page for credential management."""

    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="#19232D")
        self.controller = controller
        
        # Configure this frame to expand
        self.grid_rowconfigure(0, weight=0)  # navbar
        self.grid_rowconfigure(1, weight=1)  # content
        self.grid_columnconfigure(0, weight=1)

        # Navbar
        top = ctk.CTkFrame(self, fg_color="#1E2733", height=60)
        top.grid(row=0, column=0, sticky="ew")
        
        # Configure top navbar grid
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(
            top,
            text="← Back",
            width=80,
            height=30,
            fg_color="#2E3B4E",
            hover_color="#3E5069",
            command=lambda: controller.show_frame("MainPage"),
        ).grid(row=0, column=0, padx=15, pady=10, sticky="w")

        ctk.CTkLabel(
            top, text="Settings ⚙️", font=("Helvetica", 20, "bold")
        ).grid(row=0, column=1, padx=10, pady=10, sticky="w")

        # Settings content
        form_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#22303C")
        form_frame.grid(row=1, column=0, sticky="nsew", padx=40, pady=40)
        
        # Configure form_frame grid
        form_frame.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            form_frame,
            text="Manage Twitter API Credentials",
            font=("Helvetica", 22, "bold"),
        ).grid(row=0, column=0, pady=(20, 40), padx=60)

        self.entries = {}
        fields = [
            ("API Key", "api_key"),
            ("API Secret", "api_secret"),
            ("Access Token", "access_token"),
            ("Access Token Secret", "access_token_secret"),
        ]

        creds = controller.credentials
        row_idx = 1
        for label, key in fields:
            ctk.CTkLabel(form_frame, text=label, font=("Helvetica", 14)).grid(
                row=row_idx, column=0, sticky="w", padx=60, pady=(10, 0)
            )
            row_idx += 1
            
            entry = ctk.CTkEntry(
                form_frame,
                placeholder_text=f"Enter your {label.lower()}",
                show="*" if "secret" in key.lower() else "",
                width=500,
            )
            entry.grid(row=row_idx, column=0, padx=60, pady=(0, 10))
            entry.insert(0, creds.get(key, ""))
            self.entries[key] = entry
            row_idx += 1

        ctk.CTkButton(
            form_frame,
            text="💾 Save Credentials",
            font=("Helvetica", 15, "bold"),
            width=300,
            height=45,
            fg_color="#3A9E5B",
            hover_color="#4BBF6B",
            command=self.save,
        ).grid(row=row_idx, column=0, pady=30)

    def save(self):
        creds = {k: v.get().strip() for k, v in self.entries.items()}
        if not all(creds.values()):
            messagebox.showerror("Error", "All fields are required!")
            return
        self.controller.save_credentials(creds)
