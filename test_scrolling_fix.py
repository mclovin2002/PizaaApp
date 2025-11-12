"""
Test script to verify scrolling fix in SashimiApp
"""

import customtkinter as ctk
from datetime import datetime
import time

def test_sashimi_scrolling():
    """Test scrolling with the same configuration as SashimiApp."""
    print("🍣 Testing SashimiApp scrolling fix...")
    
    # Create test window
    root = ctk.CTk()
    root.title("SashimiApp Scrolling Test")
    root.geometry("600x500")
    root.configure(fg_color='#ffffff')
    
    # Create frame like in SashimiApp
    right_column = ctk.CTkFrame(root, fg_color='#ffffff')
    right_column.pack(fill="both", expand=True, padx=20, pady=20)
    right_column.grid_columnconfigure(0, weight=1)
    right_column.grid_rowconfigure(1, weight=1)
    
    # Log header
    log_header = ctk.CTkFrame(right_column, fg_color='#2c3e50', corner_radius=15)
    log_header.grid(row=0, column=0, sticky="ew", pady=(0, 15))
    
    log_title = ctk.CTkLabel(
        log_header,
        text="📊 Activity Log",
        font=("Helvetica", 20, "bold"),
        text_color='#ffffff'
    )
    log_title.grid(row=0, column=0, pady=20, padx=25)
    
    # Create textbox with same config as SashimiApp
    log_box = ctk.CTkTextbox(
        right_column, 
        height=400,
        font=("Consolas", 13),
        fg_color='#ffffff',
        text_color='#2c3e50',
        corner_radius=15,
        border_width=2,
        border_color='#ff6b35',
        wrap="word",
        scrollbar_button_color='#ff6b35',
        scrollbar_button_hover_color='#ff4757'
    )
    log_box.grid(row=1, column=0, sticky="nsew")
    
    # Configure scrolling like in SashimiApp
    log_box.configure(state="normal")
    
    try:
        text_widget = log_box._textbox
        text_widget.configure(
            wrap="word",
            state="normal",
            yscrollcommand=log_box._scrollbar.set
        )
        
        log_box._scrollbar.configure(command=text_widget.yview)
        
        # Mouse wheel support
        def on_mousewheel(event):
            text_widget.yview_scroll(int(-1*(event.delta/120)), "units")
            return "break"
        
        text_widget.bind("<MouseWheel>", on_mousewheel)
        
    except Exception as e:
        print(f"Scrollbar config warning: {e}")
    
    # Add lots of content to test scrolling
    log_box.insert("end", f"🍣 [{datetime.now().strftime('%H:%M:%S')}] Welcome to SashimiApp scrolling test!\n")
    log_box.insert("end", f"📜 [{datetime.now().strftime('%H:%M:%S')}] This test verifies scrolling functionality.\n")
    
    for i in range(30):
        log_box.insert("end", f"📝 [{datetime.now().strftime('%H:%M:%S')}] Test message {i+1} - This is to test scrolling functionality. You should be able to scroll up and down to see all messages. Line {i+1} of many test lines.\n")
    
    log_box.insert("end", f"✅ [{datetime.now().strftime('%H:%M:%S')}] Scrolling test complete! Try scrolling with mouse wheel or scrollbar.\n\n")
    
    # Auto-scroll to bottom
    log_box.see("end")
    
    # Ensure scrolling
    def ensure_scrolling():
        try:
            log_box.update()
            text_widget = log_box._textbox
            content_height = int(text_widget.index("end-1c").split('.')[0])
            visible_lines = int(text_widget.winfo_height() / 20)
            
            if content_height > visible_lines:
                log_box._scrollbar.configure(command=text_widget.yview)
                text_widget.configure(yscrollcommand=log_box._scrollbar.set)
                print(f"📜 Scrolling enabled: {content_height} lines, {visible_lines} visible")
            else:
                print("📜 Content fits in visible area")
        except Exception as e:
            print(f"📜 Scrolling: {e}")
    
    ensure_scrolling()
    
    print("📜 Test window opened. Try scrolling with mouse wheel or scrollbar.")
    print("📜 If you can scroll up and down, the fix is working!")
    
    # Auto-close after 10 seconds
    root.after(10000, root.destroy)
    root.mainloop()
    
    print("✅ Scrolling test completed!")

if __name__ == "__main__":
    test_sashimi_scrolling()
