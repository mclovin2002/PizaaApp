"""Test GUI with debug output"""
import customtkinter as ctk

print("Creating app...")
app = ctk.CTk()
app.title("Test Window")
app.geometry("900x600")

print("Setting appearance...")
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

print("Creating frame...")
frame = ctk.CTkFrame(app, fg_color="#19232D")
frame.pack(fill="both", expand=True)

print("Creating label...")
label = ctk.CTkLabel(frame, text="Hello World!", font=("Helvetica", 30))
label.pack(pady=50)

print("Creating button...")
button = ctk.CTkButton(frame, text="Click Me", width=200, height=50)
button.pack(pady=20)

print("Starting mainloop...")
app.mainloop()
