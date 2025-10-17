"""
PizzaApp GUI - Professional Twitter Posting Application

A sleek, minimalistic GUI for posting, scheduling, and managing tweets.
Features:
- Credential management
- Instant posting
- Time-based scheduling
- Monthly calendar scheduling
- Bulk operations
- Auto-reply mode
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import calendar
import os
from datetime import datetime, timedelta
from pathlib import Path

# Import backend modules
from twitter_credentials import load_credentials
from twitter_utils import (
    get_api,
    compute_delay_seconds,
    read_tweets_from_file,
    compute_delay_to_month_day_time,
)
from tweet import (
    post_tweet,
    schedule_tweet,
    schedule_tweet_in_month,
    bulk_post_from_file,
    auto_reply_to_mentions,
)


class PizzaAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PizzaApp - Twitter Posting Suite")
        self.root.geometry("700x850")
        self.root.resizable(False, False)
        
        # Dark, modern color scheme like the reference
        self.bg_color = "#1a2332"  # Dark blue-gray background
        self.card_color = "#243447"  # Lighter card background
        self.accent_color = "#FF6B35"  # Pizza orange
        self.button_color = "#2d3e50"  # Dark button background
        self.button_hover = "#3a4f63"  # Button hover state
        self.text_color = "#FFFFFF"  # White text
        self.subtitle_color = "#8892a6"  # Muted text
        
        self.root.configure(bg=self.bg_color)
        
        # Check if credentials exist
        self.credentials_valid = self._check_credentials()
        
        if not self.credentials_valid:
            self._show_credential_setup()
        else:
            self._build_main_interface()
    
    def _check_credentials(self):
        """Check if valid credentials are configured."""
        try:
            load_credentials()
            return True
        except Exception:
            return False
    
    def _show_credential_setup(self):
        """Show credential input form with dark theme."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Card container for form
        card = tk.Frame(main_container, bg=self.card_color, relief="flat")
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with logo
        header = tk.Frame(card, bg=self.card_color)
        header.pack(pady=(40, 20))
        
        # Try to load logo
        try:
            from PIL import Image, ImageTk
            if os.path.exists("logo.png"):
                logo_img = Image.open("logo.png")
                logo_img = logo_img.resize((100, 100), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header, image=logo_photo, bg=self.card_color)
                logo_label.image = logo_photo
                logo_label.pack(pady=(0, 20))
        except Exception:
            pass
        
        title = tk.Label(
            header,
            text="PizzaApp Setup",
            font=("Helvetica", 32, "bold"),
            bg=self.card_color,
            fg=self.text_color,
        )
        title.pack()
        
        subtitle = tk.Label(
            header,
            text="Enter your Twitter API credentials",
            font=("Helvetica", 13),
            bg=self.card_color,
            fg=self.subtitle_color,
        )
        subtitle.pack(pady=(5, 0))
        
        # Credential form
        form_frame = tk.Frame(card, bg=self.card_color)
        form_frame.pack(pady=30, padx=60, fill="both")
        
        # Info text
        info_text = tk.Label(
            form_frame,
            text="Get your credentials from https://developer.x.com/\nCreate an app with Read and Write permissions.",
            font=("Helvetica", 11),
            bg=self.card_color,
            fg=self.subtitle_color,
            justify="center",
        )
        info_text.pack(pady=(0, 30))
        
        # Input fields
        fields = [
            ("API Key", "api_key"),
            ("API Secret", "api_secret"),
            ("Access Token", "access_token"),
            ("Access Token Secret", "access_token_secret"),
        ]
        
        self.cred_entries = {}
        
        for label_text, field_name in fields:
            field_container = tk.Frame(form_frame, bg=self.card_color)
            field_container.pack(fill="x", pady=8)
            
            label = tk.Label(
                field_container,
                text=label_text,
                font=("Helvetica", 11),
                bg=self.card_color,
                fg=self.text_color,
                anchor="w",
            )
            label.pack(anchor="w", pady=(0, 5))
            
            entry = tk.Entry(
                field_container,
                font=("Helvetica", 12),
                bg=self.button_color,
                fg=self.text_color,
                insertbackground=self.text_color,
                relief="flat",
                show="*" if "secret" in field_name.lower() else "",
                bd=0,
            )
            entry.pack(fill="x", ipady=10, ipadx=10)
            self.cred_entries[field_name] = entry
        
        # Save button
        save_btn = tk.Button(
            form_frame,
            text="Save and Continue",
            font=("Helvetica", 13, "bold"),
            bg=self.accent_color,
            fg="white",
            activebackground="#E85A2B",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self._save_credentials,
            bd=0,
        )
        save_btn.pack(fill="x", pady=(30, 20), ipady=12)
    
    def _save_credentials(self):
        """Save credentials to twitter_credentials.py."""
        api_key = self.cred_entries["api_key"].get().strip()
        api_secret = self.cred_entries["api_secret"].get().strip()
        access_token = self.cred_entries["access_token"].get().strip()
        access_token_secret = self.cred_entries["access_token_secret"].get().strip()
        
        if not all([api_key, api_secret, access_token, access_token_secret]):
            messagebox.showerror("Error", "All fields are required!")
            return
        
        # Write to twitter_credentials.py
        creds_file = Path("twitter_credentials.py")
        try:
            content = creds_file.read_text()
            # Replace placeholder values
            content = content.replace('API_KEY: str = "YOUR_API_KEY"', f'API_KEY: str = "{api_key}"')
            content = content.replace('API_SECRET: str = "YOUR_API_SECRET"', f'API_SECRET: str = "{api_secret}"')
            content = content.replace('ACCESS_TOKEN: str = "YOUR_ACCESS_TOKEN"', f'ACCESS_TOKEN: str = "{access_token}"')
            content = content.replace('ACCESS_TOKEN_SECRET: str = "YOUR_ACCESS_TOKEN_SECRET"', f'ACCESS_TOKEN_SECRET: str = "{access_token_secret}"')
            creds_file.write_text(content)
            
            messagebox.showinfo("Success", "Credentials saved successfully!")
            self.credentials_valid = True
            self._build_main_interface()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save credentials: {e}")
    
    def _build_main_interface(self):
        """Build the main menu interface with dark theme."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True)
        
        # Card container (centered dialog box)
        card_container = tk.Frame(main_container, bg=self.bg_color)
        card_container.place(relx=0.5, rely=0.5, anchor="center")
        
        card = tk.Frame(card_container, bg=self.card_color, relief="flat")
        card.pack(padx=80, pady=60)
        
        # Header with logo and close button
        header = tk.Frame(card, bg=self.card_color)
        header.pack(fill="x", padx=30, pady=(30, 20))
        
        # Try to load logo (small version for header)
        try:
            from PIL import Image, ImageTk
            if os.path.exists("logo.png"):
                logo_img = Image.open("logo.png")
                logo_img = logo_img.resize((60, 60), Image.Resampling.LANCZOS)
                logo_photo = ImageTk.PhotoImage(logo_img)
                logo_label = tk.Label(header, image=logo_photo, bg=self.card_color)
                logo_label.image = logo_photo
                logo_label.pack(side="left", padx=(0, 15))
        except Exception:
            pass
        
        # Title
        title_frame = tk.Frame(header, bg=self.card_color)
        title_frame.pack(side="left", fill="both", expand=True)
        
        title = tk.Label(
            title_frame,
            text="Twitter Manager",
            font=("Helvetica", 28, "bold"),
            bg=self.card_color,
            fg=self.text_color,
            anchor="w",
        )
        title.pack(anchor="w")
        
        # Close button (X)
        close_btn = tk.Label(
            header,
            text="✕",
            font=("Helvetica", 20),
            bg=self.card_color,
            fg=self.subtitle_color,
            cursor="hand2",
        )
        close_btn.pack(side="right")
        close_btn.bind("<Button-1>", lambda e: self.root.quit())
        
        # Menu buttons container
        menu_frame = tk.Frame(card, bg=self.card_color)
        menu_frame.pack(padx=30, pady=(20, 30), fill="both")
        
        # Menu buttons
        buttons = [
            ("Post a Tweet", self._show_post_interface),
            ("Schedule a Tweet", self._show_schedule_interface),
            ("Bulk Post from File", self._show_bulk_interface),
            ("Enable Auto-Reply Mode", self._show_auto_reply_interface),
            ("Exit", self.root.quit),
        ]
        
        for btn_text, btn_command in buttons:
            if btn_text == "Exit":
                # Special styling for exit button
                btn = tk.Button(
                    menu_frame,
                    text=btn_text,
                    font=("Helvetica", 15),
                    bg=self.button_color,
                    fg=self.text_color,
                    activebackground=self.button_hover,
                    activeforeground=self.text_color,
                    relief="flat",
                    cursor="hand2",
                    command=btn_command,
                    bd=0,
                )
                btn.pack(fill="x", pady=(30, 0), ipady=15)
            else:
                btn = tk.Button(
                    menu_frame,
                    text=btn_text,
                    font=("Helvetica", 15),
                    bg=self.button_color,
                    fg=self.text_color,
                    activebackground=self.button_hover,
                    activeforeground=self.text_color,
                    relief="flat",
                    cursor="hand2",
                    command=btn_command,
                    bd=0,
                )
                btn.pack(fill="x", pady=(0, 12), ipady=15)
    
    def _show_post_interface(self):
        """Show the post tweet interface."""
        self._show_operation_screen(
            title="Post a Tweet",
            inputs=[
                {"label": "Tweet message", "type": "text", "key": "message", "height": 6}
            ],
            button_text="Post Tweet",
            action=self._execute_post
        )
    
    def _show_schedule_interface(self):
        """Show the schedule tweet interface."""
        self._show_operation_screen(
            title="Schedule a Tweet",
            inputs=[
                {"label": "Tweet message", "type": "text", "key": "message", "height": 5},
                {"label": "Schedule type", "type": "choice", "key": "sched_type", 
                 "options": ["Minutes from now", "Today at time (HH:MM)", "Day of month"]},
                {"label": "Value (minutes/HH:MM/day+time)", "type": "entry", "key": "sched_value"}
            ],
            button_text="Schedule Tweet",
            action=self._execute_schedule
        )
    
    def _show_bulk_interface(self):
        """Show the bulk operations interface."""
        self._show_operation_screen(
            title="Bulk Post from File",
            inputs=[
                {"label": "File path (.txt or .csv)", "type": "file", "key": "file_path"},
                {"label": "Delay between posts (minutes)", "type": "entry", "key": "delay"}
            ],
            button_text="Execute Bulk Post",
            action=self._execute_bulk
        )
    
    def _show_auto_reply_interface(self):
        """Show the auto-reply interface."""
        self._show_operation_screen(
            title="Enable Auto-Reply Mode",
            inputs=[
                {"label": "Check interval (minutes)", "type": "entry", "key": "interval"},
                {"label": "Reply message", "type": "text", "key": "reply", "height": 4}
            ],
            button_text="Start Auto-Reply",
            action=self._execute_auto_reply
        )
    
    def _show_operation_screen(self, title, inputs, button_text, action):
        """Generic operation screen builder."""
        # Clear window
        for widget in self.root.winfo_children():
            widget.destroy()
        
        # Main container
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill="both", expand=True, padx=40, pady=40)
        
        # Card
        card = tk.Frame(main_container, bg=self.card_color, relief="flat")
        card.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        header = tk.Frame(card, bg=self.card_color)
        header.pack(fill="x", padx=30, pady=30)
        
        # Back button
        back_btn = tk.Label(
            header,
            text="← Back",
            font=("Helvetica", 13),
            bg=self.card_color,
            fg=self.subtitle_color,
            cursor="hand2",
        )
        back_btn.pack(anchor="w")
        back_btn.bind("<Button-1>", lambda e: self._build_main_interface())
        
        # Title
        title_label = tk.Label(
            card,
            text=title,
            font=("Helvetica", 24, "bold"),
            bg=self.card_color,
            fg=self.text_color,
        )
        title_label.pack(padx=30, pady=(0, 20))
        
        # Form frame
        form_frame = tk.Frame(card, bg=self.card_color)
        form_frame.pack(padx=40, pady=20, fill="both", expand=True)
        
        # Store widget references
        self.operation_widgets = {}
        
        for inp in inputs:
            field_container = tk.Frame(form_frame, bg=self.card_color)
            field_container.pack(fill="x", pady=10)
            
            label = tk.Label(
                field_container,
                text=inp["label"],
                font=("Helvetica", 12),
                bg=self.card_color,
                fg=self.text_color,
                anchor="w",
            )
            label.pack(anchor="w", pady=(0, 8))
            
            if inp["type"] == "text":
                widget = scrolledtext.ScrolledText(
                    field_container,
                    height=inp.get("height", 5),
                    font=("Helvetica", 12),
                    bg=self.button_color,
                    fg=self.text_color,
                    insertbackground=self.text_color,
                    relief="flat",
                    wrap="word",
                    bd=0,
                )
                widget.pack(fill="both", padx=2, pady=2)
            elif inp["type"] == "entry":
                widget = tk.Entry(
                    field_container,
                    font=("Helvetica", 12),
                    bg=self.button_color,
                    fg=self.text_color,
                    insertbackground=self.text_color,
                    relief="flat",
                    bd=0,
                )
                widget.pack(fill="x", ipady=10, ipadx=10)
            elif inp["type"] == "file":
                file_frame = tk.Frame(field_container, bg=self.card_color)
                file_frame.pack(fill="x")
                
                widget = tk.Entry(
                    file_frame,
                    font=("Helvetica", 11),
                    bg=self.button_color,
                    fg=self.text_color,
                    insertbackground=self.text_color,
                    relief="flat",
                    state="readonly",
                    bd=0,
                )
                widget.pack(side="left", fill="x", expand=True, ipady=8, ipadx=10)
                
                browse_btn = tk.Button(
                    file_frame,
                    text="Browse",
                    font=("Helvetica", 11),
                    bg=self.button_hover,
                    fg=self.text_color,
                    activebackground=self.accent_color,
                    activeforeground="white",
                    relief="flat",
                    cursor="hand2",
                    command=lambda w=widget: self._browse_file_for_widget(w),
                    bd=0,
                )
                browse_btn.pack(side="left", padx=(10, 0), ipady=8, ipadx=15)
            elif inp["type"] == "choice":
                widget = ttk.Combobox(
                    field_container,
                    values=inp["options"],
                    font=("Helvetica", 11),
                    state="readonly",
                )
                widget.set(inp["options"][0])
                widget.pack(fill="x", ipady=5)
            
            self.operation_widgets[inp["key"]] = widget
        
        # Action button
        action_btn = tk.Button(
            card,
            text=button_text,
            font=("Helvetica", 14, "bold"),
            bg=self.accent_color,
            fg="white",
            activebackground="#E85A2B",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=action,
            bd=0,
        )
        action_btn.pack(fill="x", padx=40, pady=(20, 30), ipady=12)
    
    def _browse_file_for_widget(self, widget):
        """Browse for file and update widget."""
        filename = filedialog.askopenfilename(
            title="Select file",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filename:
            widget.config(state="normal")
            widget.delete(0, "end")
            widget.insert(0, filename)
            widget.config(state="readonly")
    
    def _execute_post(self):
        """Execute instant post."""
        message = self.operation_widgets["message"].get("1.0", "end-1c").strip()
        if not message:
            messagebox.showerror("Error", "Tweet message cannot be empty!")
            return
        
        try:
            post_tweet(message)
            messagebox.showinfo("Success", "Tweet posted successfully!")
            self._build_main_interface()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to post tweet:\n{e}")
    
    def _execute_schedule(self):
        """Execute scheduled tweet."""
        message = self.operation_widgets["message"].get("1.0", "end-1c").strip()
        sched_type = self.operation_widgets["sched_type"].get()
        value = self.operation_widgets["sched_value"].get().strip()
        
        if not message:
            messagebox.showerror("Error", "Tweet message cannot be empty!")
            return
        if not value:
            messagebox.showerror("Error", "Schedule value is required!")
            return
        
        try:
            if "Minutes" in sched_type:
                minutes = int(value)
                schedule_tweet(message, delay_minutes=minutes)
                messagebox.showinfo("Success", f"Tweet scheduled for {minutes} minutes from now!")
            elif "time" in sched_type:
                schedule_tweet(message, time_hhmm=value)
                messagebox.showinfo("Success", f"Tweet scheduled for today at {value}!")
            else:  # Day of month
                parts = value.split()
                if len(parts) != 2:
                    messagebox.showerror("Error", "Format: <day> <HH:MM> (e.g., 25 14:30)")
                    return
                day = int(parts[0])
                time_str = parts[1]
                now = datetime.now()
                schedule_tweet_in_month(message, now.year, now.month, day, time_str)
                messagebox.showinfo("Success", f"Tweet scheduled for day {day} at {time_str}!")
            
            self._build_main_interface()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule tweet:\n{e}")
    
    def _execute_bulk(self):
        """Execute bulk posting."""
        file_path = self.operation_widgets["file_path"].get()
        delay_str = self.operation_widgets["delay"].get().strip()
        
        if not file_path:
            messagebox.showerror("Error", "Please select a file!")
            return
        if not delay_str:
            messagebox.showerror("Error", "Delay is required!")
            return
        
        try:
            delay = int(delay_str)
            
            def run():
                try:
                    bulk_post_from_file(file_path, delay)
                    messagebox.showinfo("Success", "Bulk posting completed!")
                except Exception as e:
                    messagebox.showerror("Error", f"Bulk posting failed:\n{e}")
            
            threading.Thread(target=run, daemon=True).start()
            messagebox.showinfo("Started", "Bulk posting started in background!")
            self._build_main_interface()
        except ValueError:
            messagebox.showerror("Error", "Delay must be a number!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start bulk posting:\n{e}")
    
    def _execute_auto_reply(self):
        """Execute auto-reply mode."""
        interval_str = self.operation_widgets["interval"].get().strip()
        reply = self.operation_widgets["reply"].get("1.0", "end-1c").strip()
        
        if not interval_str:
            messagebox.showerror("Error", "Interval is required!")
            return
        if not reply:
            messagebox.showerror("Error", "Reply message cannot be empty!")
            return
        
        try:
            interval = int(interval_str)
            
            def run():
                try:
                    auto_reply_to_mentions(interval, reply)
                except Exception as e:
                    messagebox.showerror("Error", f"Auto-reply error:\n{e}")
            
            threading.Thread(target=run, daemon=True).start()
            messagebox.showinfo("Started", "Auto-reply mode started! Press Ctrl+C in terminal to stop.")
            self._build_main_interface()
        except ValueError:
            messagebox.showerror("Error", "Interval must be a number!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start auto-reply:\n{e}")
    

    
    def _create_schedule_tab(self):
        """Create scheduling tab."""
        frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="⏰ Schedule")
        
        content = tk.Frame(frame, bg=self.bg_color)
        content.pack(expand=True, fill="both", padx=40, pady=40)
        
        label = tk.Label(
            content,
            text="Schedule a Tweet",
            font=("Helvetica", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        )
        label.pack(anchor="w", pady=(0, 20))
        
        tk.Label(
            content,
            text="Tweet message:",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(anchor="w")
        
        self.schedule_text = scrolledtext.ScrolledText(
            content,
            height=6,
            font=("Helvetica", 11),
            wrap="word",
            relief="solid",
            borderwidth=1,
        )
        self.schedule_text.pack(fill="both", pady=(5, 20))
        
        # Schedule type
        sched_frame = tk.Frame(content, bg=self.bg_color)
        sched_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            sched_frame,
            text="Schedule by:",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=(0, 10))
        
        self.schedule_type = tk.StringVar(value="minutes")
        tk.Radiobutton(
            sched_frame,
            text="Minutes from now",
            variable=self.schedule_type,
            value="minutes",
            font=("Helvetica", 10),
            bg=self.bg_color,
            activebackground=self.bg_color,
            command=self._toggle_schedule_inputs,
        ).pack(side="left", padx=5)
        
        tk.Radiobutton(
            sched_frame,
            text="Today at time (HH:MM)",
            variable=self.schedule_type,
            value="time",
            font=("Helvetica", 10),
            bg=self.bg_color,
            activebackground=self.bg_color,
            command=self._toggle_schedule_inputs,
        ).pack(side="left", padx=5)
        
        tk.Radiobutton(
            sched_frame,
            text="Day of month",
            variable=self.schedule_type,
            value="monthly",
            font=("Helvetica", 10),
            bg=self.bg_color,
            activebackground=self.bg_color,
            command=self._toggle_schedule_inputs,
        ).pack(side="left", padx=5)
        
        # Input fields
        input_frame = tk.Frame(content, bg=self.bg_color)
        input_frame.pack(fill="x", pady=(10, 20))
        
        # Minutes input
        self.minutes_frame = tk.Frame(input_frame, bg=self.bg_color)
        tk.Label(
            self.minutes_frame,
            text="Delay (minutes):",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=(0, 10))
        self.schedule_minutes = tk.Entry(self.minutes_frame, font=("Helvetica", 11), width=10)
        self.schedule_minutes.pack(side="left")
        self.minutes_frame.pack(anchor="w")
        
        # Time input
        self.time_frame = tk.Frame(input_frame, bg=self.bg_color)
        tk.Label(
            self.time_frame,
            text="Time (HH:MM):",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=(0, 10))
        self.schedule_time = tk.Entry(self.time_frame, font=("Helvetica", 11), width=10)
        self.schedule_time.pack(side="left")
        
        # Monthly input
        self.monthly_frame = tk.Frame(input_frame, bg=self.bg_color)
        tk.Label(
            self.monthly_frame,
            text="Day:",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=(0, 10))
        self.schedule_day = tk.Entry(self.monthly_frame, font=("Helvetica", 11), width=5)
        self.schedule_day.pack(side="left", padx=(0, 20))
        tk.Label(
            self.monthly_frame,
            text="Time (HH:MM):",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=(0, 10))
        self.schedule_month_time = tk.Entry(self.monthly_frame, font=("Helvetica", 11), width=10)
        self.schedule_month_time.pack(side="left")
        
        self._toggle_schedule_inputs()
        
        schedule_btn = tk.Button(
            content,
            text="Schedule Tweet",
            font=("Helvetica", 12, "bold"),
            bg=self.button_color,
            fg="white",
            activebackground="#E85A2B",
            relief="flat",
            cursor="hand2",
            command=self._schedule_tweet,
            padx=30,
            pady=12,
        )
        schedule_btn.pack()
    
    def _toggle_schedule_inputs(self):
        """Show/hide schedule input fields based on selection."""
        self.minutes_frame.pack_forget()
        self.time_frame.pack_forget()
        self.monthly_frame.pack_forget()
        
        if self.schedule_type.get() == "minutes":
            self.minutes_frame.pack(anchor="w")
        elif self.schedule_type.get() == "time":
            self.time_frame.pack(anchor="w")
        else:
            self.monthly_frame.pack(anchor="w")
    
    def _schedule_tweet(self):
        """Schedule a tweet based on user input."""
        message = self.schedule_text.get("1.0", "end-1c").strip()
        if not message:
            messagebox.showerror("Error", "Tweet message cannot be empty!")
            return
        
        try:
            sched_type = self.schedule_type.get()
            
            if sched_type == "minutes":
                minutes = int(self.schedule_minutes.get())
                schedule_tweet(message, delay_minutes=minutes)
                messagebox.showinfo("Success", f"Tweet scheduled for {minutes} minutes from now!")
            elif sched_type == "time":
                time_str = self.schedule_time.get().strip()
                schedule_tweet(message, time_hhmm=time_str)
                messagebox.showinfo("Success", f"Tweet scheduled for today at {time_str}!")
            else:  # monthly
                day = int(self.schedule_day.get())
                time_str = self.schedule_month_time.get().strip()
                now = datetime.now()
                schedule_tweet_in_month(message, now.year, now.month, day, time_str)
                messagebox.showinfo("Success", f"Tweet scheduled for day {day} at {time_str}!")
            
            self.schedule_text.delete("1.0", "end")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to schedule tweet:\n{e}")
    
    def _create_bulk_tab(self):
        """Create bulk operations tab."""
        frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="📦 Bulk")
        
        content = tk.Frame(frame, bg=self.bg_color)
        content.pack(expand=True, fill="both", padx=40, pady=40)
        
        label = tk.Label(
            content,
            text="Bulk Tweet Operations",
            font=("Helvetica", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        )
        label.pack(anchor="w", pady=(0, 20))
        
        # File selection
        file_frame = tk.Frame(content, bg=self.bg_color)
        file_frame.pack(fill="x", pady=(0, 20))
        
        tk.Label(
            file_frame,
            text="Select file (.txt or .csv):",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=(0, 10))
        
        self.bulk_file_path = tk.StringVar()
        self.bulk_file_entry = tk.Entry(
            file_frame,
            textvariable=self.bulk_file_path,
            font=("Helvetica", 11),
            width=40,
            state="readonly",
        )
        self.bulk_file_entry.pack(side="left", padx=(0, 10))
        
        browse_btn = tk.Button(
            file_frame,
            text="Browse",
            font=("Helvetica", 10),
            bg=self.secondary_color,
            relief="flat",
            cursor="hand2",
            command=self._browse_file,
            padx=15,
            pady=5,
        )
        browse_btn.pack(side="left")
        
        # Operation type
        op_frame = tk.Frame(content, bg=self.bg_color)
        op_frame.pack(fill="x", pady=(0, 10))
        
        tk.Label(
            op_frame,
            text="Operation:",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=(0, 10))
        
        self.bulk_operation = tk.StringVar(value="immediate")
        tk.Radiobutton(
            op_frame,
            text="Post immediately (with delay)",
            variable=self.bulk_operation,
            value="immediate",
            font=("Helvetica", 10),
            bg=self.bg_color,
            activebackground=self.bg_color,
        ).pack(side="left", padx=5)
        
        tk.Radiobutton(
            op_frame,
            text="Schedule with frequency",
            variable=self.bulk_operation,
            value="schedule",
            font=("Helvetica", 10),
            bg=self.bg_color,
            activebackground=self.bg_color,
        ).pack(side="left", padx=5)
        
        # Delay/Frequency input
        delay_frame = tk.Frame(content, bg=self.bg_color)
        delay_frame.pack(fill="x", pady=(10, 20))
        
        tk.Label(
            delay_frame,
            text="Delay/Frequency (minutes):",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(side="left", padx=(0, 10))
        
        self.bulk_delay = tk.Entry(delay_frame, font=("Helvetica", 11), width=10)
        self.bulk_delay.insert(0, "1")
        self.bulk_delay.pack(side="left")
        
        # Execute button
        execute_btn = tk.Button(
            content,
            text="Execute Bulk Operation",
            font=("Helvetica", 12, "bold"),
            bg=self.button_color,
            fg="white",
            activebackground="#E85A2B",
            relief="flat",
            cursor="hand2",
            command=self._execute_bulk,
            padx=30,
            pady=12,
        )
        execute_btn.pack()
    
    def _browse_file(self):
        """Open file browser for bulk file selection."""
        filename = filedialog.askopenfilename(
            title="Select tweets file",
            filetypes=[("Text files", "*.txt"), ("CSV files", "*.csv"), ("All files", "*.*")],
        )
        if filename:
            self.bulk_file_path.set(filename)
    
    def _execute_bulk(self):
        """Execute bulk operation."""
        file_path = self.bulk_file_path.get()
        if not file_path:
            messagebox.showerror("Error", "Please select a file!")
            return
        
        try:
            delay = int(self.bulk_delay.get())
        except ValueError:
            messagebox.showerror("Error", "Delay must be a number!")
            return
        
        operation = self.bulk_operation.get()
        
        def run_bulk():
            try:
                if operation == "immediate":
                    bulk_post_from_file(file_path, delay)
                    messagebox.showinfo("Success", "Bulk posting completed!")
                else:
                    # Schedule all tweets with frequency
                    tweets = read_tweets_from_file(file_path)
                    for i, msg in enumerate(tweets):
                        seconds = i * delay * 60
                        threading.Timer(seconds, lambda m=msg: post_tweet(m)).start()
                    messagebox.showinfo(
                        "Success",
                        f"Scheduled {len(tweets)} tweets with {delay} min frequency!",
                    )
            except Exception as e:
                messagebox.showerror("Error", f"Bulk operation failed:\n{e}")
        
        threading.Thread(target=run_bulk, daemon=True).start()
    
    def _create_auto_reply_tab(self):
        """Create auto-reply tab."""
        frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="🔄 Auto-Reply")
        
        content = tk.Frame(frame, bg=self.bg_color)
        content.pack(expand=True, fill="both", padx=40, pady=40)
        
        label = tk.Label(
            content,
            text="Auto-Reply to Mentions",
            font=("Helvetica", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        )
        label.pack(anchor="w", pady=(0, 20))
        
        tk.Label(
            content,
            text="Check interval (minutes):",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(anchor="w")
        
        self.reply_interval = tk.Entry(content, font=("Helvetica", 11), width=10)
        self.reply_interval.insert(0, "5")
        self.reply_interval.pack(anchor="w", pady=(5, 20))
        
        tk.Label(
            content,
            text="Reply message:",
            font=("Helvetica", 11),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(anchor="w")
        
        self.reply_message = scrolledtext.ScrolledText(
            content,
            height=5,
            font=("Helvetica", 11),
            wrap="word",
            relief="solid",
            borderwidth=1,
        )
        self.reply_message.pack(fill="both", pady=(5, 20))
        
        self.reply_active = False
        self.reply_thread = None
        
        self.reply_btn = tk.Button(
            content,
            text="Start Auto-Reply",
            font=("Helvetica", 12, "bold"),
            bg=self.button_color,
            fg="white",
            activebackground="#E85A2B",
            relief="flat",
            cursor="hand2",
            command=self._toggle_auto_reply,
            padx=30,
            pady=12,
        )
        self.reply_btn.pack()
        
        self.reply_status = tk.Label(
            content,
            text="Status: Inactive",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg="#666666",
        )
        self.reply_status.pack(pady=(10, 0))
    
    def _toggle_auto_reply(self):
        """Start or stop auto-reply mode."""
        if not self.reply_active:
            try:
                interval = int(self.reply_interval.get())
                message = self.reply_message.get("1.0", "end-1c").strip()
                
                if not message:
                    messagebox.showerror("Error", "Reply message cannot be empty!")
                    return
                
                self.reply_active = True
                self.reply_btn.config(text="Stop Auto-Reply", bg="#DC3545")
                self.reply_status.config(text="Status: Active", fg="#28A745")
                
                def run_auto_reply():
                    try:
                        auto_reply_to_mentions(interval, message)
                    except Exception as e:
                        messagebox.showerror("Error", f"Auto-reply error:\n{e}")
                        self.reply_active = False
                        self.reply_btn.config(text="Start Auto-Reply", bg=self.button_color)
                        self.reply_status.config(text="Status: Inactive", fg="#666666")
                
                self.reply_thread = threading.Thread(target=run_auto_reply, daemon=True)
                self.reply_thread.start()
            except ValueError:
                messagebox.showerror("Error", "Interval must be a number!")
        else:
            self.reply_active = False
            self.reply_btn.config(text="Start Auto-Reply", bg=self.button_color)
            self.reply_status.config(text="Status: Inactive", fg="#666666")
            messagebox.showinfo("Info", "Auto-reply will stop after current cycle")
    
    def _create_settings_tab(self):
        """Create settings tab."""
        frame = tk.Frame(self.notebook, bg=self.bg_color)
        self.notebook.add(frame, text="⚙️ Settings")
        
        content = tk.Frame(frame, bg=self.bg_color)
        content.pack(expand=True, fill="both", padx=40, pady=40)
        
        label = tk.Label(
            content,
            text="Settings",
            font=("Helvetica", 18, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        )
        label.pack(anchor="w", pady=(0, 30))
        
        # Reconfigure credentials button
        reconfig_btn = tk.Button(
            content,
            text="Reconfigure Credentials",
            font=("Helvetica", 11),
            bg=self.secondary_color,
            relief="flat",
            cursor="hand2",
            command=self._reconfigure_credentials,
            padx=20,
            pady=10,
        )
        reconfig_btn.pack(anchor="w")
        
        # About section
        about_frame = tk.Frame(content, bg=self.bg_color)
        about_frame.pack(anchor="w", pady=(40, 0))
        
        tk.Label(
            about_frame,
            text="About PizzaApp",
            font=("Helvetica", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_color,
        ).pack(anchor="w")
        
        tk.Label(
            about_frame,
            text="Professional Twitter posting and scheduling suite\nVersion 1.0\n\nFeatures:\n• Instant posting\n• Flexible scheduling\n• Bulk operations\n• Auto-reply to mentions",
            font=("Helvetica", 10),
            bg=self.bg_color,
            fg="#666666",
            justify="left",
        ).pack(anchor="w", pady=(10, 0))
    
    def _reconfigure_credentials(self):
        """Allow user to reconfigure credentials."""
        if messagebox.askyesno(
            "Confirm",
            "This will reset your credentials. Continue?",
        ):
            self.credentials_valid = False
            self._show_credential_setup()


def main():
    """Launch the GUI application."""
    # Generate logo if it doesn't exist
    if not os.path.exists("logo.png"):
        try:
            from generate_logo import create_pizza_logo
            create_pizza_logo()
        except Exception as e:
            print(f"Could not generate logo: {e}")
    
    root = tk.Tk()
    app = PizzaAppGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
