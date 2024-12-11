import tkinter as tk
from tkinter import messagebox

def show_popup(message):
    """
    Show a pop-up alert with the given message.
    """
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showwarning("Scam Alert", message)
    root.destroy()

if __name__ == "__main__":
    print("Testing pop-up functionality...")
    show_popup("This is a test scam alert!")
