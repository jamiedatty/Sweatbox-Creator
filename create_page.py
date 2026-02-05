import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from ese_parser import ESEParser
from map_viewer import MapViewer
from aircraft_viewer import AircraftViewer
from controller_viewer import ControllerViewer

class CreatePage:
    def __init__(self, root):
        self.root = root
        self.ese_parser = None
        self.current_viewer = None
        
        for widget in root.winfo_children():
            widget.destroy()
        
        self.setup_ui()
        
        self.root.after(100, self.select_file)
    
    def setup_ui(self):
        self.menu_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        self.menu_frame.pack(side='top', fill='x')
        self.menu_frame.pack_propagate(False)
        
        self.map_btn = tk.Button(
            self.menu_frame,
            text="Map",
            font=('Arial', 12, 'bold'),
            bg='#3498db',
            fg='white',
            width=12,
            height=2,
            cursor='hand2',
            command=self.show_map
        )
        self.map_btn.pack(side='left', padx=5, pady=5)
        
        self.aircraft_btn = tk.Button(
            self.menu_frame,
            text="Aircraft",
            font=('Arial', 12),
            bg='#34495e',
            fg='white',
            width=12,
            height=2,
            cursor='hand2',
            command=self.show_aircraft
        )
        self.aircraft_btn.pack(side='left', padx=5, pady=5)
        
        self.controllers_btn = tk.Button(
            self.menu_frame,
            text="Controllers",
            font=('Arial', 12),
            bg='#34495e',
            fg='white',
            width=12,
            height=2,
            cursor='hand2',
            command=self.show_controllers
        )
        self.controllers_btn.pack(side='left', padx=5, pady=5)
        
        tk.Label(
            self.menu_frame,
            text="Master Pseudo-controller:",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='white'
        ).pack(side='left', padx=(20, 5), pady=5)
        
        self.master_entry = tk.Entry(
            self.menu_frame,
            font=('Arial', 11),
            width=20
        )
        self.master_entry.pack(side='left', padx=5, pady=5)
        self.master_entry.insert(0, "Enter the 'master' pseudocontroller")
        self.master_entry.bind('<FocusIn>', self.clear_placeholder)
        self.master_entry.bind('<FocusOut>', self.restore_placeholder)
        
        self.content_frame = tk.Frame(self.root, bg='white')
        self.content_frame.pack(fill='both', expand=True)
    
    def clear_placeholder(self, event):
        if self.master_entry.get() == "Enter the 'master' pseudocontroller":
            self.master_entry.delete(0, tk.END)
            self.master_entry.config(fg='black')
    
    def restore_placeholder(self, event):
        if not self.master_entry.get():
            self.master_entry.insert(0, "Enter the 'master' pseudocontroller")
            self.master_entry.config(fg='grey')
    
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select ESE File",
            filetypes=[("ESE files", "*.ese"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.ese_parser = ESEParser(file_path)
                
                messagebox.showinfo(
                    "Success", 
                    f"ESE file loaded successfully!\n\nPositions: {len(self.ese_parser.get_positions())}\nSIDs/STARs: {len(self.ese_parser.get_sidsstars())}"
                )
                
                self.show_map()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load ESE file:\n{str(e)}")
                self.root.destroy()
        else:
            from home_page import HomePage
            HomePage(self.root)
    
    def show_map(self):
        if not self.ese_parser:
            messagebox.showwarning("Warning", "No ESE file loaded")
            return
        
        self.map_btn.config(bg='#3498db', font=('Arial', 12, 'bold'))
        self.aircraft_btn.config(bg='#34495e', font=('Arial', 12))
        self.controllers_btn.config(bg='#34495e', font=('Arial', 12))
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if self.current_viewer:
            self.current_viewer = None
        
        self.current_viewer = MapViewer(self.content_frame, self.ese_parser)
    
    def show_aircraft(self):
        if not self.ese_parser:
            messagebox.showwarning("Warning", "No ESE file loaded")
            return
        
        self.map_btn.config(bg='#34495e', font=('Arial', 12))
        self.aircraft_btn.config(bg='#3498db', font=('Arial', 12, 'bold'))
        self.controllers_btn.config(bg='#34495e', font=('Arial', 12))
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if self.current_viewer:
            self.current_viewer = None
        
        self.current_viewer = AircraftViewer(self.content_frame, self.ese_parser)
    
    def show_controllers(self):
        if not self.ese_parser:
            messagebox.showwarning("Warning", "No ESE file loaded")
            return
        
        self.map_btn.config(bg='#34495e', font=('Arial', 12))
        self.aircraft_btn.config(bg='#34495e', font=('Arial', 12))
        self.controllers_btn.config(bg='#3498db', font=('Arial', 12, 'bold'))
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if self.current_viewer:
            self.current_viewer = None
        
        self.current_viewer = ControllerViewer(self.content_frame, self.ese_parser)