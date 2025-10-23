"""
Test script to verify scrolling functionality in SashimiApp
"""

import customtkinter as ctk
from datetime import datetime

def test_scrolling():
    """Test scrolling functionality with a simple textbox."""
    print("📜 Testing scrolling functionality...")
    
    # Create a simple test window
    root = ctk.CTk()
    root.title("Scrolling Test")
    root.geometry("400x300")
    
    # Create a textbox with scrolling
    textbox = ctk.CTkTextbox(
        root,
        height=250,
        font=("Consolas", 12),
        wrap="word"
    )
    textbox.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Add lots of content to test scrolling
    for i in range(50):
        textbox.insert("end", f"Line {i+1}: This is test content to verify scrolling functionality. You should be able to scroll up and down to see all lines.\n")
    
    textbox.insert("end", "\n✅ If you can scroll up and down to see all lines, scrolling is working!\n")
    
    # Auto-scroll to bottom
    textbox.see("end")
    
    print("  📜 Test window opened. Try scrolling with mouse wheel or scrollbar.")
    print("  📜 If you can scroll up and down, the scrolling is working!")
    
    # Run the test for 5 seconds
    root.after(5000, root.destroy)
    root.mainloop()
    
    print("  ✅ Scrolling test completed!")

if __name__ == "__main__":
    test_scrolling()
