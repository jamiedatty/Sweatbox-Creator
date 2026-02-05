import tkinter as tk
from home_page import HomePage

def main():
    root = tk.Tk()
    root.title("ESE File Viewer")
    root.geometry("800x600")
    
    app = HomePage(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()