import tkinter as tk
from pages.home_page import HomePage

def main():
    root = tk.Tk()
    root.title("ESE/SCT File Viewer")
    root.geometry("1200x800")
    root.minsize(1000, 700)
    
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    app = HomePage(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()