"""
Controller Viewer Module
Displays controller positions and information in a filterable table
"""
import tkinter as tk
from tkinter import ttk

class ControllerViewer:
    def __init__(self, parent, ese_parser):
        self.parent = parent
        self.ese_parser = ese_parser
        self.positions = ese_parser.get_positions()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Title frame
        title_frame = tk.Frame(main_frame, bg='white')
        title_frame.pack(fill='x', pady=(0, 10))
        
        title_label = tk.Label(
            title_frame,
            text=f"Controller Positions ({len(self.positions)} total)",
            font=('Arial', 16, 'bold'),
            bg='white',
            fg='#2c3e50'
        )
        title_label.pack(side='left')
        
        # Export button
        export_btn = tk.Button(
            title_frame,
            text="Export to CSV",
            font=('Arial', 10),
            bg='#3498db',
            fg='white',
            padx=10,
            command=self.export_to_csv
        )
        export_btn.pack(side='right', padx=5)
        
        # Filter frame
        filter_frame = tk.Frame(main_frame, bg='white')
        filter_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            filter_frame,
            text="Filter by type:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(side='left', padx=(0, 10))
        
        self.filter_var = tk.StringVar(value='ALL')
        
        # Position type buttons
        types = ['ALL', 'TWR', 'GND', 'APP', 'DEP', 'CTR', 'ATIS', 'DEL', 'FSS']
        for ptype in types:
            btn = tk.Radiobutton(
                filter_frame,
                text=ptype,
                variable=self.filter_var,
                value=ptype,
                bg='white',
                font=('Arial', 9),
                command=self.apply_filter
            )
            btn.pack(side='left', padx=5)
            
            # Color code the radio buttons
            if ptype == 'TWR':
                btn.config(fg='red')
            elif ptype == 'GND':
                btn.config(fg='darkorange')
            elif ptype in ['APP', 'DEP']:
                btn.config(fg='blue')
            elif ptype == 'CTR':
                btn.config(fg='green')
            elif ptype == 'ATIS':
                btn.config(fg='purple')
            elif ptype == 'DEL':
                btn.config(fg='brown')
        
        # Search frame
        search_frame = tk.Frame(main_frame, bg='white')
        search_frame.pack(fill='x', pady=(0, 10))
        
        tk.Label(
            search_frame,
            text="Search:",
            font=('Arial', 10, 'bold'),
            bg='white'
        ).pack(side='left', padx=(0, 10))
        
        self.search_var = tk.StringVar()
        self.search_var.trace('w', self.apply_search)
        
        search_entry = tk.Entry(
            search_frame,
            textvariable=self.search_var,
            font=('Arial', 10),
            width=30
        )
        search_entry.pack(side='left', padx=(0, 10))
        
        # Clear search button
        clear_btn = tk.Button(
            search_frame,
            text="Clear",
            font=('Arial', 9),
            command=self.clear_search
        )
        clear_btn.pack(side='left')
        
        # Treeview frame with scrollbars
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True)
        
        # Configure grid
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Create scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        # Create Treeview
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('callsign', 'name', 'frequency', 'type', 'identifier', 'coords'),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set,
            height=20
        )
        
        # Configure scrollbars
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        # Define columns
        self.tree.heading('callsign', text='Callsign')
        self.tree.heading('name', text='Name')
        self.tree.heading('frequency', text='Frequency')
        self.tree.heading('type', text='Type')
        self.tree.heading('identifier', text='ID')
        self.tree.heading('coords', text='Coordinates')
        
        # Set column widths
        self.tree.column('callsign', width=150, minwidth=100)
        self.tree.column('name', width=250, minwidth=150)
        self.tree.column('frequency', width=100, minwidth=80)
        self.tree.column('type', width=80, minwidth=60)
        self.tree.column('identifier', width=80, minwidth=60)
        self.tree.column('coords', width=200, minwidth=150)
        
        # Configure tags for color coding
        self.tree.tag_configure('TWR', background='#ffe6e6')
        self.tree.tag_configure('GND', background='#fff0e6')
        self.tree.tag_configure('APP', background='#e6f3ff')
        self.tree.tag_configure('DEP', background='#e6f3ff')
        self.tree.tag_configure('CTR', background='#e6ffe6')
        self.tree.tag_configure('ATIS', background='#f0e6ff')
        self.tree.tag_configure('DEL', background='#f5e6d9')
        self.tree.tag_configure('FSS', background='#e6f5ff')
        self.tree.tag_configure('OTHER', background='#f0f0f0')
        
        # Grid the tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Bind double-click event
        self.tree.bind('<Double-Button-1>', self.on_item_double_click)
        
        # Statistics frame
        stats_frame = tk.Frame(main_frame, bg='#f8f9fa', height=30)
        stats_frame.pack(fill='x', pady=(10, 0))
        stats_frame.pack_propagate(False)
        
        self.stats_label = tk.Label(
            stats_frame,
            text=self.get_stats_text(),
            font=('Arial', 9),
            bg='#f8f9fa',
            fg='#2c3e50'
        )
        self.stats_label.pack(pady=5)
        
        # Populate the tree
        self.populate_tree()
    
    def populate_tree(self, search_text=None):
        """Populate the treeview with filtered data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filter_type = self.filter_var.get()
        search_text = search_text.lower() if search_text else ""
        
        for position in self.positions:
            # Apply type filter
            if filter_type != 'ALL' and position['type'] != filter_type:
                continue
            
            # Apply search filter
            if search_text:
                search_fields = [
                    position['callsign'].lower(),
                    position['name'].lower(),
                    position['frequency'].lower(),
                    position['type'].lower(),
                    position['identifier'].lower()
                ]
                if not any(search_text in field for field in search_fields):
                    continue
            
            # Format coordinates for display
            coords_display = ""
            if 'coordinates' in position and position['coordinates']:
                coords = position['coordinates']
                if len(coords) >= 2:
                    # Take first two coordinates (usually lat and lon)
                    coords_display = f"{coords[0]}, {coords[1]}"
                    if len(coords) > 2:
                        coords_display += f" (+{len(coords)-2} more)"
            
            # Insert item with appropriate tag
            item_tag = position['type'] if position['type'] in ['TWR', 'GND', 'APP', 'DEP', 'CTR', 'ATIS', 'DEL', 'FSS'] else 'OTHER'
            
            self.tree.insert('', 'end', values=(
                position['callsign'],
                position['name'],
                position['frequency'],
                position['type'],
                position['identifier'],
                coords_display
            ), tags=(item_tag,))
    
    def apply_filter(self):
        """Apply the selected filter"""
        self.populate_tree(self.search_var.get())
        self.stats_label.config(text=self.get_stats_text())
    
    def apply_search(self, *args):
        """Apply search filter"""
        search_text = self.search_var.get().strip().lower()
        self.populate_tree(search_text)
        self.stats_label.config(text=self.get_stats_text())
    
    def clear_search(self):
        """Clear search field"""
        self.search_var.set("")
    
    def get_stats_text(self):
        """Generate statistics text"""
        filter_type = self.filter_var.get()
        search_text = self.search_var.get().strip().lower()
        
        if filter_type == 'ALL':
            # Count by type
            type_counts = {}
            for pos in self.positions:
                if search_text:
                    search_fields = [
                        pos['callsign'].lower(),
                        pos['name'].lower(),
                        pos['frequency'].lower(),
                        pos['type'].lower(),
                        pos['identifier'].lower()
                    ]
                    if not any(search_text in field for field in search_fields):
                        continue
                
                ptype = pos['type']
                type_counts[ptype] = type_counts.get(ptype, 0) + 1
            
            stats = []
            for ptype, count in sorted(type_counts.items()):
                if ptype and count > 0:
                    stats.append(f"{ptype}: {count}")
            
            if stats:
                return f"Showing {sum(type_counts.values())} positions | " + " | ".join(stats)
            else:
                return "No positions match the search criteria"
        else:
            # Count specific type
            count = 0
            for pos in self.positions:
                if pos['type'] == filter_type:
                    if search_text:
                        search_fields = [
                            pos['callsign'].lower(),
                            pos['name'].lower(),
                            pos['frequency'].lower(),
                            pos['type'].lower(),
                            pos['identifier'].lower()
                        ]
                        if not any(search_text in field for field in search_fields):
                            continue
                    count += 1
            
            if search_text:
                return f"Showing {count} {filter_type} position(s) matching '{search_text}'"
            else:
                return f"Showing {count} {filter_type} position(s)"
    
    def on_item_double_click(self, event):
        """Handle double-click on tree item"""
        item = self.tree.selection()[0]
        values = self.tree.item(item, 'values')
        
        if values:
            callsign, name, frequency, ptype, identifier, coords = values
            
            # Create detail window
            detail_window = tk.Toplevel(self.parent)
            detail_window.title(f"Controller Details - {callsign}")
            detail_window.geometry("500x300")
            detail_window.resizable(False, False)
            
            # Center the window
            detail_window.transient(self.parent)
            detail_window.grab_set()
            
            # Detail frame
            detail_frame = tk.Frame(detail_window, padx=20, pady=20)
            detail_frame.pack(fill='both', expand=True)
            
            # Display details
            details = [
                ("Callsign:", callsign),
                ("Name:", name),
                ("Frequency:", frequency),
                ("Type:", ptype),
                ("Identifier:", identifier),
                ("Coordinates:", coords)
            ]
            
            for i, (label, value) in enumerate(details):
                tk.Label(
                    detail_frame,
                    text=label,
                    font=('Arial', 10, 'bold'),
                    anchor='e',
                    width=15
                ).grid(row=i, column=0, sticky='e', pady=5)
                
                tk.Label(
                    detail_frame,
                    text=value,
                    font=('Arial', 10),
                    anchor='w',
                    wraplength=300
                ).grid(row=i, column=1, sticky='w', pady=5, padx=(10, 0))
            
            # Close button
            close_btn = tk.Button(
                detail_window,
                text="Close",
                font=('Arial', 10),
                width=10,
                command=detail_window.destroy
            )
            close_btn.pack(pady=10)
    
    def export_to_csv(self):
        """Export controller data to CSV file"""
        import csv
        from tkinter import filedialog
        
        # Ask for save location
        filename = filedialog.asksaveasfilename(
            title="Export Controllers to CSV",
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Write header
                writer.writerow(['Callsign', 'Name', 'Frequency', 'Type', 'Identifier', 'Coordinates'])
                
                # Write data
                for position in self.positions:
                    coords_display = ""
                    if 'coordinates' in position and position['coordinates']:
                        coords = position['coordinates']
                        if len(coords) >= 2:
                            coords_display = f"{coords[0]}, {coords[1]}"
                    
                    writer.writerow([
                        position['callsign'],
                        position['name'],
                        position['frequency'],
                        position['type'],
                        position['identifier'],
                        coords_display
                    ])
            
            # Show success message
            from tkinter import messagebox
            messagebox.showinfo("Export Successful", f"Controller data exported to:\n{filename}")
            
        except Exception as e:
            from tkinter import messagebox
            messagebox.showerror("Export Failed", f"Failed to export data:\n{str(e)}")