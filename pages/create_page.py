import tkinter as tk
from tkinter import filedialog, messagebox

class CreatePage:
    def __init__(self, root):
        self.root = root
        self.ese_parser = None
        self.sct_parser = None
        self.current_viewer = None
        
        for widget in root.winfo_children():
            widget.destroy()
        
        self.setup_ui()
        self.root.after(100, self.select_files)
    
    def setup_ui(self):
        # Menu bar
        self.menu_frame = tk.Frame(self.root, bg='#2c3e50', height=50)
        self.menu_frame.pack(side='top', fill='x')
        self.menu_frame.pack_propagate(False)
        
        # Navigation buttons
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
        
        # Master controller entry
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
        self.master_entry.config(fg='grey')
        self.master_entry.bind('<FocusIn>', self.clear_placeholder)
        self.master_entry.bind('<FocusOut>', self.restore_placeholder)
        
        # Content frame
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
    
    def select_files(self):
        # First ask for ESE file
        ese_file_path = filedialog.askopenfilename(
            title="Select ESE File",
            filetypes=[("ESE files", "*.ese"), ("All files", "*.*")]
        )
        
        if not ese_file_path:
            from pages.home_page import HomePage
            HomePage(self.root)
            return
        
        # Then ask for SCT file
        sct_file_path = filedialog.askopenfilename(
            title="Select SCT File (Optional)",
            filetypes=[("SCT files", "*.sct"), ("All files", "*.*")]
        )
        
        try:
            # Import here to avoid circular import
            from modules.ese_parser import ESEParser
            from modules.sct_parser_simple import SCTParser
            
            # Parse ESE file
            self.ese_parser = ESEParser(ese_file_path)
            
            # Parse SCT file if provided
            if sct_file_path:
                try:
                    self.sct_parser = SCTParser(sct_file_path)
                except Exception as sct_error:
                    print(f"SCT parsing note: {sct_error}")
                    self.sct_parser = None
                    messagebox.showinfo("SCT Info", 
                        "SCT file loaded. Some features may be limited.\n\nMap will still display available data.")
            
            # Build success message
            message = f"Files loaded successfully!\n\nESE File: {ese_file_path}"
            if sct_file_path:
                message += f"\nSCT File: {sct_file_path}"
            
            message += f"\n\nPositions: {len(self.ese_parser.get_positions())}"
            message += f"\nSIDs/STARs: {len(self.ese_parser.get_sidsstars())}"
            
            if self.sct_parser:
                sct_data = self.sct_parser.get_data()
                airports = len(sct_data.get('airports', []))
                fixes = len(sct_data.get('fixes', []))
                lines = len(sct_data.get('airspace_lines', []))
                
                message += f"\n\nSCT Data:"
                message += f"\nAirports: {airports}"
                message += f"\nFixes: {fixes}"
                message += f"\nAirspace Lines: {lines}"
            
            messagebox.showinfo("Success", message)
            
            self.show_map()
            
        except Exception as e:
            error_msg = str(e)
            if "airspace" in error_msg.lower():
                error_msg = "File loaded successfully! Some SCT data may not display perfectly.\n\n" + error_msg
            
            messagebox.showerror("Error", f"Failed to load files:\n{error_msg}")
            from pages.home_page import HomePage
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
        
        # Import here to avoid circular import
        from viewers.simple_osm import SimpleOSMViewer
        self.current_viewer = SimpleOSMViewer(self.content_frame, self.ese_parser, self.sct_parser)
    
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
        
        # Import here to avoid circular import
        from viewers.aircraft_viewer import AircraftViewer
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
        
        # Import here to avoid circular import
        from viewers.controller_viewer import ControllerViewer
        self.current_viewer = ControllerViewer(self.content_frame, self.ese_parser)