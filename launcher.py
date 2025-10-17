"""
PizzaApp Launcher – Main entry point for the modern GUI.
This launches the customtkinter GUI while keeping tweet.py as backend.

Usage:
    python3 launcher.py
"""
import os, sys
print("=== DEBUG START ===")
print("Current working dir:", os.getcwd())
print("Launcher file path:", __file__)
print("sys.path BEFORE:", sys.path[:3])
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)
print("sys.path AFTER:", sys.path[:3])
print("Looking for gui.py in:", os.path.join(BASE_DIR, "gui.py"))
print("Exists:", os.path.exists(os.path.join(BASE_DIR, "gui.py")))
print("=== DEBUG END ===")

import sys
from gui import PizzaApp
print("✅ launcher running from:", __file__)
print("✅ gui module location:", PizzaApp.__module__)



def main():
    """Launch the PizzaApp GUI."""
    try:
        app = PizzaApp()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n👋 PizzaApp closed by user.")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Error launching PizzaApp: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

