import tkinter as tk
from tkinter import ttk

class AircraftViewer:
    def __init__(self, parent, ese_parser):
        self.parent = parent
        self.ese_parser = ese_parser
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = tk.Frame(self.parent, bg='white')
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            main_frame,
            text="Aircraft Information",
            font=('Arial', 18, 'bold'),
            bg='white',
            fg='black'
        )
        title_label.pack(pady=20)
        
        info_text = tk.Text(
            main_frame,
            font=('Arial', 11),
            wrap='word',
            bg='#f0f0f0',
            relief='flat',
            height=20
        )
        info_text.pack(fill='both', expand=True, pady=10)
        
        scrollbar = ttk.Scrollbar(info_text, command=info_text.yview)
        scrollbar.pack(side='right', fill='y')
        info_text.config(yscrollcommand=scrollbar.set)
        
        info_text.insert('1.0', "Aircraft Management Panel\n\n")
        info_text.insert('end', "This section will display:\n\n")
        info_text.insert('end', "• Active aircraft in the airspace\n")
        info_text.insert('end', "• Flight plans and routes\n")
        info_text.insert('end', "• Aircraft types and performance data\n")
        info_text.insert('end', "• Departure and arrival information\n")
        info_text.insert('end', "• Altitude and speed restrictions\n\n")
        info_text.insert('end', "Currently parsing ESE file for:\n\n")
        
        sidsstars = self.ese_parser.get_sidsstars()
        
        if sidsstars:
            info_text.insert('end', f"SIDs/STARs: {len(sidsstars)} procedures found\n\n")
            
            airports = {}
            for proc in sidsstars:
                airport = proc['airport']
                if airport not in airports:
                    airports[airport] = {'SID': [], 'STAR': []}
                airports[airport][proc['type']].append(proc)
            
            for airport, procs in sorted(airports.items()):
                info_text.insert('end', f"\n{airport}:\n", 'airport')
                
                if procs['SID']:
                    info_text.insert('end', f"  SIDs ({len(procs['SID'])}): ")
                    sids = list(set([p['name'] for p in procs['SID']]))[:5]
                    info_text.insert('end', ', '.join(sids))
                    if len(procs['SID']) > 5:
                        info_text.insert('end', f" ... and {len(procs['SID']) - 5} more")
                    info_text.insert('end', '\n')
                
                if procs['STAR']:
                    info_text.insert('end', f"  STARs ({len(procs['STAR'])}): ")
                    stars = list(set([p['name'] for p in procs['STAR']]))[:5]
                    info_text.insert('end', ', '.join(stars))
                    if len(procs['STAR']) > 5:
                        info_text.insert('end', f" ... and {len(procs['STAR']) - 5} more")
                    info_text.insert('end', '\n')
        else:
            info_text.insert('end', "No SID/STAR data found in ESE file\n")
        
        info_text.tag_config('airport', font=('Arial', 11, 'bold'), foreground='darkblue')
        
        info_text.config(state='disabled')