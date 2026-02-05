"""
Controller Viewer Module
Displays controller positions and information
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
        main_frame.pack(fill='both', expand=True)
        
        title_frame = tk.Frame(main_frame, bg='white')
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text=f"Controller Positions ({len(self.positions)} total)",
            font=('Arial', 14, 'bold'),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=10)
        
        filter_frame = tk.Frame(main_frame, bg='white')
        filter_frame.pack(fill='x', pady=5, padx=10)
        
        tk.Label(
            filter_frame,
            text="Filter by type:",
            font=('Arial', 10),
            bg='white'
        ).pack(side='left', padx=5)
        
        self.filter_var = tk.StringVar(value='ALL')
        
        types = ['ALL', 'TWR', 'GND', 'APP', 'CTR', 'ATIS', 'DEL']
        for ptype in types:
            tk.Radiobutton(
                filter_frame,
                text=ptype,
                variable=self.filter_var,
                value=ptype,
                bg='white',
                font=('Arial', 9),
                command=self.apply_filter
            ).pack(side='left', padx=5)
        
        tree_frame = tk.Frame(main_frame)
        tree_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        vsb = ttk.Scrollbar(tree_frame, orient="vertical")
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal")
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('callsign', 'name', 'frequency', 'type', 'identifier'),
            show='headings',
            yscrollcommand=vsb.set,
            xscrollcommand=hsb.set
        )
        
        vsb.config(command=self.tree.yview)
        hsb.config(command=self.tree.xview)
        
        self.tree.heading('callsign', text='Callsign')
        self.tree.heading('name', text='Name')
        self.tree.heading('frequency', text='Frequency')
        self.tree.heading('type', text='Type')
        self.tree.heading('identifier', text='ID')
        
        self.tree.column('callsign', width=150)
        self.tree.column('name', width=250)
        self.tree.column('frequency', width=100)
        self.tree.column('type', width=80)
        self.tree.column('identifier', width=80)
        
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        self.populate_tree()
        
        stats_frame = tk.Frame(main_frame, bg='
        stats_frame.pack(fill='x', pady=5)
        stats_frame.pack_propagate(False)
        
        self.stats_label = tk.Label(
            stats_frame,
            text=self.get_stats_text(),
            font=('Arial', 9),
            bg='
            fg='
        )
        self.stats_label.pack(pady=10)
    
    def populate_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        filter_type = self.filter_var.get()
        
        for position in self.positions:
            if filter_type != 'ALL' and position['type'] != filter_type:
                continue
            
            self.tree.insert('', 'end', values=(
                position['callsign'],
                position['name'],
                position['frequency'],
                position['type'],
                position['identifier']
            ))
    
    def apply_filter(self):
        self.populate_tree()
        self.stats_label.config(text=self.get_stats_text())
    
    def get_stats_text(self):
        filter_type = self.filter_var.get()
        
        if filter_type == 'ALL':
            type_counts = {}
            for pos in self.positions:
                ptype = pos['type']
                type_counts[ptype] = type_counts.get(ptype, 0) + 1
            
            stats = []
            for ptype, count in sorted(type_counts.items()):
                if ptype:
                    stats.append(f"{ptype}: {count}")
            
            return "  |  ".join(stats) if stats else "No positions"
        else:
            count = sum(1 for pos in self.positions if pos['type'] == filter_type)
            return f"Showing {count} {filter_type} position(s)"