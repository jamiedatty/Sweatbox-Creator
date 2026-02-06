import tkinter as tk
from pages.home_page import HomePage

def main():
    root = tk.Tk()
    root.title("ESE/SCT File Viewer & Sweatbox Creator")
    root.geometry("1400x900")
    root.minsize(1200, 800)
    
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    # Test for tkintermapview
    try:
        from tkintermapview import TkinterMapView
    except ImportError:
        tk.messagebox.showerror(
            "Missing Dependency",
            "tkintermapview is not installed!\n\n"
            "Please install it using:\n"
            "pip install tkintermapview"
        )
        return
    
    app = HomePage(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()