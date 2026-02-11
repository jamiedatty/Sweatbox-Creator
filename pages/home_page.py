import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import sys

def get_macos_colors():
    """Get macOS-compatible color palette"""
    return {
        # Background colors
        'background': '#F5F5F7',       # macOS system gray
        'surface': '#FFFFFF',           # Pure white for cards
        'surface_alternate': '#F0F0F2', # Alternate surface
        
        # Primary colors
        'primary': '#007AFF',           # macOS blue
        'primary_dark': '#0056B3',      # Darker blue
        'primary_light': '#5AC8FA',     # Light blue
        
        # Status colors
        'success': '#34C759',           # macOS green
        'success_dark': '#248A3D',      # Dark green
        'warning': '#FF9500',          # macOS orange
        'danger': '#FF3B30',           # macOS red
        'info': '#00C7BE',             # macOS teal
        
        # Text colors
        'text': '#1D1D1F',             # macOS text primary
        'text_secondary': '#86868B',    # macOS text secondary
        'text_hint': '#AEAEB2',         # macOS text tertiary
        
        # UI element colors
        'border': '#D2D2D7',            # macOS separator
        'divider': '#E5E5EA',           # Lighter divider
        'shadow': '#00000020',           # Soft shadow
        
        # Gradient colors
        'gradient_start': '#007AFF',
        'gradient_end': '#5AC8FA',
        
        # Special colors
        'accent': '#007AFF',
        'highlight': '#34C759',
        
        # Status bar colors
        'status_background': '#2C2C2E',
        'status_text': '#FFFFFF',
        'status_indicator': '#30D158',
        
        # Card colors
        'card_background': '#FFFFFF',
        'card_border': '#D2D2D7',
        
        # White
        'white': '#FFFFFF',
    }

def get_windows_colors():
    """Get Windows-compatible color palette"""
    return {
        # Background colors
        'background': '#e3f2fd',        # Very light blue
        'surface': '#ffffff',            # Pure white
        'surface_alternate': '#ffffff',
        
        # Primary colors
        'primary': '#1976d2',           # Deep blue
        'primary_dark': '#1565c0',      # Darker blue
        'primary_light': '#42a5f5',     # Light blue
        
        # Status colors
        'success': '#4caf50',           # Green
        'success_dark': '#388e3c',      # Dark green
        'warning': '#ff9800',           # Orange
        'danger': '#f44336',            # Red
        'info': '#03dac6',             # Teal
        
        # Text colors
        'text': '#0d47a1',             # Dark blue text
        'text_secondary': '#455a64',    # Blue-gray
        'text_hint': '#78909c',         # Light blue-gray
        
        # UI element colors
        'border': '#bbdefb',            # Light blue border
        'divider': '#e3f2fd',          # Light blue dividers
        'shadow': '#00000015',          # Soft shadow
        
        # Gradient colors
        'gradient_start': '#1976d2',
        'gradient_end': '#42a5f5',
        
        # Special colors
        'accent': '#2196f3',
        'highlight': '#64b5f6',
        
        # Status bar colors
        'status_background': '#34495e',
        'status_text': '#ecf0f1',
        'status_indicator': '#27ae60',
        
        # Card colors
        'card_background': '#ffffff',
        'card_border': '#bbdefb',
        
        # White
        'white': '#ffffff',
    }

def get_platform_colors():
    """Get colors appropriate for the current platform"""
    if sys.platform == 'darwin':
        return get_macos_colors()
    else:
        return get_windows_colors()

def get_platform_font():
    """Get appropriate font for the current platform"""
    if sys.platform == 'darwin':
        return 'SF Pro Text'
    else:
        return 'Segoe UI'

class HomePage:
    def __init__(self, parent):
        self.parent = parent
        self.ese_parser = None
        self.sct_parser = None
        self.rwy_parser = None
        self.map_viewer = None
        self.master_controller = "SYS"
        self.aircraft_details_tree = None
        self.controller_tree = None
        
        # Get platform-specific colors and font
        self.colors = get_platform_colors()
        self.font_name = get_platform_font()
        
        # Add project root to path for imports
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        # Now try to import modules
        try:
            from modules.parsers.ese_parser import ESEParser
            from modules.parsers.sct_parser_simple import SCTParser
            from modules.parsers.rwy_parser import RWYParser
            from modules.generators.random_generator import RandomScenarioGenerator
            from modules.exporters.sweatbox_exporter import SweatboxExporter
            from modules.ui.viewers.sweatbox_map import SweatboxMapViewer
            
            self.ESEParser = ESEParser
            self.SCTParser = SCTParser
            self.RWYParser = RWYParser
            self.RandomScenarioGenerator = RandomScenarioGenerator
            self.SweatboxExporter = SweatboxExporter
            self.SweatboxMapViewer = SweatboxMapViewer
            
        except ImportError as e:
            print(f"Import error: {e}")
            print("Creating fallback classes...")
            
            # Create fallback classes
            class FallbackESEParser:
                def __init__(self, *args): 
                    self.positions = []
                def get_positions(self): 
                    return []
            
            class FallbackSCTParser:
                def __init__(self, *args): 
                    self.data = {}
                def parse(self): 
                    pass
                def get_data(self): 
                    return {}
            
            class FallbackRWYParser:
                def __init__(self, *args): 
                    self.runways = []
                    self.ils_data = []
                def parse(self): 
                    pass
                def get_data(self): 
                    return {'runways': [], 'ils_data': []}
            
            class FallbackRandomScenarioGenerator:
                def __init__(self, creator): 
                    self.creator = creator
                def generate_random_scenario(self): 
                    messagebox.showinfo("Info", "Random generator not available")
            
            class FallbackSweatboxExporter:
                def __init__(self, creator): 
                    self.creator = creator
                def export(self, file_path): 
                    return (False, "Exporter not available")
            
            class FallbackSweatboxMapViewer:
                def __init__(self, parent, ese=None, sct=None, rwy=None):
                    self.parent = parent
                    self.aircraft_points = []
                    self.entry_fixes = []
                    self.selected_airport = None
                def load_data(self): 
                    pass
                def redraw_all(self): 
                    pass
                def clear_aircraft(self): 
                    pass
                def add_aircraft(self, aircraft_data): 
                    pass
                def get_entry_fixes(self): 
                    return self.entry_fixes
                def get_selected_airport(self): 
                    return self.selected_airport
                def select_aircraft(self, callsign):
                    return False
                def setup_ui(self): 
                    # Create a simple frame
                    frame = tk.Frame(self.parent, bg='white')
                    frame.pack(fill='both', expand=True)
                    label = tk.Label(frame, text="Map viewer not available", bg='white')
                    label.pack(pady=50)
            
            self.ESEParser = FallbackESEParser
            self.SCTParser = FallbackSCTParser
            self.RWYParser = FallbackRWYParser
            self.RandomScenarioGenerator = FallbackRandomScenarioGenerator
            self.SweatboxExporter = FallbackSweatboxExporter
            self.SweatboxMapViewer = FallbackSweatboxMapViewer
        
        self.setup_ui()
    
    def setup_styles(self):
        """Configure modern styling with platform-compatible colors"""
        style = ttk.Style()

        # Use platform-specific colors (already initialized in __init__)
        # self.colors is already set from get_platform_colors()

        # Configure modern button styles with proper hover effects
        style.configure('Action.TButton',
                       font=(self.font_name, 10, 'bold'),
                       padding=[16, 8],
                       relief='flat',
                       borderwidth=0,
                       background=self.colors['primary'],
                       foreground=self.colors['white'])

        style.configure('Primary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=(self.font_name, 10, 'bold'),
                       padding=[16, 8],
                       relief='flat',
                       borderwidth=0)

        style.configure('Success.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['white'],
                       font=(self.font_name, 10, 'bold'),
                       padding=[16, 8],
                       relief='flat',
                       borderwidth=0)

        style.configure('Warning.TButton',
                       background=self.colors['warning'],
                       foreground=self.colors['white'],
                       font=(self.font_name, 10, 'bold'),
                       padding=[16, 8],
                       relief='flat',
                       borderwidth=0)

        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground=self.colors['white'],
                       font=(self.font_name, 10, 'bold'),
                       padding=[16, 8],
                       relief='flat',
                       borderwidth=0)

        style.configure('Secondary.TButton',
                       background=self.colors['primary'],
                       foreground=self.colors['white'],
                       font=(self.font_name, 10, 'bold'),
                       padding=[16, 8],
                       relief='flat',
                       borderwidth=0)

        style.configure('Outline.TButton',
                       background=self.colors['surface'],
                       foreground=self.colors['primary'],
                       font=(self.font_name, 10, 'bold'),
                       padding=[14, 6],
                       relief='solid',
                       borderwidth=2,
                       bordercolor=self.colors['primary'])

        # Configure modern card frames
        style.configure('Card.TLabelframe',
                       background=self.colors['surface'],
                       borderwidth=1,
                       relief='solid',
                       bordercolor=self.colors['border'])

        style.configure('Card.TLabelframe.Label',
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       font=(self.font_name, 12, 'bold'))

        # Configure modern treeview with alternating rows
        style.configure('Modern.Treeview',
                       font=(self.font_name, 9),
                       rowheight=32,
                       background=self.colors['surface'],
                       fieldbackground=self.colors['surface'],
                       borderwidth=0,
                       relief='flat')

        style.configure('Modern.Treeview.Heading',
                       font=(self.font_name, 10, 'bold'),
                       background=self.colors['surface'],
                       foreground=self.colors['text'],
                       borderwidth=0,
                       relief='flat')

        # Configure modern notebook with tabs
        style.configure('Modern.TNotebook',
                       background=self.colors['background'],
                       borderwidth=0,
                       relief='flat')

        style.configure('Modern.TNotebook.Tab',
                       background=self.colors['surface'],
                       foreground=self.colors['text_secondary'],
                       font=(self.font_name, 10, 'bold'),
                       padding=[24, 12],
                       borderwidth=0,
                       relief='flat')

        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['surface'])],
                 foreground=[('selected', self.colors['primary'])])

        # Configure modern entry fields
        style.configure('Modern.TEntry',
                       font=(self.font_name, 10),
                       padding=10,
                       relief='flat',
                       borderwidth=1,
                       bordercolor=self.colors['border'],
                       fieldbackground=self.colors['surface'])

        # Configure modern labels
        style.configure('Modern.TLabel',
                       font=(self.font_name, 10),
                       background=self.colors['surface'],
                       foreground=self.colors['text'])

        style.configure('Header.TLabel',
                       font=(self.font_name, 16, 'bold'),
                       background=self.colors['surface'],
                       foreground=self.colors['text'])

        style.configure('Subheader.TLabel',
                       font=(self.font_name, 12, 'bold'),
                       background=self.colors['surface'],
                       foreground=self.colors['text'])

        style.configure('Caption.TLabel',
                       font=(self.font_name, 9),
                       background=self.colors['surface'],
                       foreground=self.colors['text_secondary'])

        # Configure modern progress bars
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['surface'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])

    def setup_ui(self):
        # Configure modern style
        self.setup_styles()

        # Main container with platform-compatible background
        self.main_container = tk.Frame(
            self.parent, 
            bg=self.colors['background'],
            highlightthickness=0,
            relief='flat'
        )
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Top header bar
        self.setup_header_bar()

        # Main content area
        content_frame = tk.Frame(
            self.main_container, 
            bg=self.colors['background'],
            highlightthickness=0,
            relief='flat'
        )
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=15)

        # Main paned window for three-panel layout
        main_paned = tk.PanedWindow(
            content_frame, 
            orient=tk.HORIZONTAL,
            sashrelief=tk.FLAT, 
            sashwidth=8,
            bg=self.colors['divider'],
            highlightthickness=0,
            relief='flat'
        )
        main_paned.pack(fill=tk.BOTH, expand=True)

        # Left panel - controls
        left_panel = tk.Frame(
            main_paned, 
            bg=self.colors['surface'], 
            relief='raised', 
            borderwidth=2,
            highlightthickness=0
        )
        main_paned.add(left_panel, minsize=360)

        # Center panel - map
        center_panel = tk.Frame(
            main_paned, 
            bg=self.colors['surface'], 
            relief='raised', 
            borderwidth=2,
            highlightthickness=0
        )
        main_paned.add(center_panel, minsize=780)

        # Right panel - details
        right_panel = tk.Frame(
            main_paned, 
            bg=self.colors['surface'], 
            relief='raised', 
            borderwidth=2,
            highlightthickness=0
        )
        main_paned.add(right_panel, minsize=360)

        self.setup_left_panel(left_panel)
        self.setup_center_panel(center_panel)
        self.setup_right_panel(right_panel)

        # Bottom status bar
        self.setup_status_bar()





    def setup_header_bar(self):
        """Create header bar with platform-compatible styling"""
        # Create gradient effect using frames
        header_frame = tk.Frame(self.main_container, height=70, bg=self.colors['gradient_start'])
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False)

        gradient_frame = tk.Frame(header_frame, bg=self.colors['gradient_end'], highlightthickness=0, relief='flat')
        gradient_frame.pack(fill=tk.X, padx=2, pady=2)
        gradient_frame.pack_propagate(False)

        # Logo/title area
        title_frame = tk.Frame(gradient_frame, bg=self.colors['gradient_end'], highlightthickness=0, relief='flat')
        title_frame.pack(side=tk.LEFT, padx=25, pady=12)

        # Title with platform-compatible font
        title_label = tk.Label(
            title_frame, 
            text="✈️ SWEATBOX CREATOR",
            font=(self.font_name, 20, 'bold'),
            fg='#ffffff', 
            bg=self.colors['gradient_end'],
            highlightthickness=0,
            relief='flat'
        )
        title_label.pack(side=tk.TOP, anchor=tk.W)

        subtitle_label = tk.Label(
            title_frame, 
            text="✨ Professional ATC Scenario Builder ✨",
            font=(self.font_name, 10, 'bold'),
            fg='#e8f4f8', 
            bg=self.colors['gradient_end'],
            highlightthickness=0,
            relief='flat'
        )
        subtitle_label.pack(side=tk.TOP, anchor=tk.W, pady=(2, 0))

        # Quick actions area
        actions_frame = tk.Frame(gradient_frame, bg=self.colors['gradient_end'], highlightthickness=0, relief='flat')
        actions_frame.pack(side=tk.RIGHT, padx=25, pady=12)

        # Buttons with platform-compatible styling
        button_font = (self.font_name, 9, 'bold')
        
        save_btn = tk.Button(
            actions_frame, 
            text="💾 SAVE SCENARIO",
            font=button_font,
            bg=self.colors['success'], 
            fg='white',
            relief='flat', 
            padx=18, 
            pady=10, 
            borderwidth=0,
            highlightthickness=0,
            activebackground=self.colors['success_dark'],
            command=self.export_sweatbox
        )
        save_btn.pack(side=tk.LEFT, padx=3)

        load_btn = tk.Button(
            actions_frame, 
            text="📁 LOAD FILE",
            font=button_font,
            bg=self.colors['primary'], 
            fg='white',
            relief='flat', 
            padx=18, 
            pady=10, 
            borderwidth=0,
            highlightthickness=0,
            activebackground=self.colors['primary_dark'],
            command=self.load_sweatbox_file
        )
        load_btn.pack(side=tk.LEFT, padx=3)

        help_btn = tk.Button(
            actions_frame, 
            text="❓ HELP & TIPS",
            font=button_font,
            bg=self.colors['info'], 
            fg='white',
            relief='flat', 
            padx=18, 
            pady=10, 
            borderwidth=0,
            highlightthickness=0,
            activebackground='#81d4fa',
            command=self.show_help
        )
        help_btn.pack(side=tk.LEFT, padx=3)

    def setup_status_bar(self):
        """Create modern status bar at bottom"""
        status_frame = tk.Frame(
            self.main_container, 
            bg=self.colors['status_background'], 
            height=35,
            highlightthickness=0,
            relief='flat'
        )
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        status_frame.pack_propagate(False)

        # Status indicator
        status_indicator = tk.Frame(
            status_frame, 
            bg=self.colors['status_indicator'], 
            width=8, 
            height=8,
            highlightthickness=0,
            relief='flat'
        )
        status_indicator.pack(side=tk.LEFT, padx=15, pady=13)
        status_indicator.pack_propagate(False)

        # Status text
        self.status_label = tk.Label(
            status_frame, 
            text="Ready - Load SCT/ESE files to begin",
            font=(self.font_name, 9),
            fg=self.colors['status_text'], 
            bg=self.colors['status_background'],
            highlightthickness=0,
            relief='flat'
        )
        self.status_label.pack(side=tk.LEFT, pady=8)

        # Chat button in status bar
        chat_btn = tk.Button(
            status_frame, 
            text="💬 CHAT",
            font=(self.font_name, 8, 'bold'),
            bg=self.colors['info'], 
            fg='white',
            relief='flat', 
            padx=8, 
            pady=4, 
            borderwidth=0,
            highlightthickness=0,
            activebackground='#00bfa5',
            command=self.open_chat
        )
        chat_btn.pack(side=tk.RIGHT, padx=5, pady=6)

        # Progress info
        self.progress_label = tk.Label(
            status_frame, 
            text="",
            font=(self.font_name, 9),
            fg='#bdc3c7', 
            bg=self.colors['status_background'],
            highlightthickness=0,
            relief='flat'
        )
        self.progress_label.pack(side=tk.RIGHT, padx=15, pady=8)
    
    def setup_left_panel(self, parent):
        """Setup left panel with platform-compatible styling"""
        # Gradient background for left panel
        gradient_canvas = tk.Canvas(parent, height=8, highlightthickness=0)
        gradient_canvas.pack(fill=tk.X, side=tk.TOP)
        gradient_canvas.create_rectangle(0, 0, 1000, 8, fill=self.colors['gradient_start'], outline='')
        gradient_canvas.create_rectangle(0, 4, 1000, 8, fill=self.colors['gradient_end'], outline='')

        # Define fonts
        frame_font = (self.font_name, 11, 'bold')
        button_font = (self.font_name, 9, 'bold')
        label_font = (self.font_name, 9, 'bold')
        entry_font = (self.font_name, 9)
        
        # File controls frame
        file_frame = tk.LabelFrame(
            parent, 
            text="📁 FILE CONTROLS", 
            padx=15, 
            pady=12,
            bg=self.colors['surface'], 
            fg=self.colors['text'], 
            font=frame_font,
            relief='solid', 
            borderwidth=2,
            highlightthickness=0
        )
        file_frame.pack(fill=tk.X, padx=12, pady=8)

        # File control buttons
        ese_btn = tk.Button(
            file_frame, 
            text="📡 LOAD ESE FILE", 
            command=self.load_ese_file,
            bg=self.colors['primary'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground=self.colors['primary_dark']
        )
        ese_btn.pack(fill=tk.X, pady=4)

        sct_btn = tk.Button(
            file_frame, 
            text="🗺️ LOAD SCT FILE", 
            command=self.load_sct_file,
            bg=self.colors['success'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground=self.colors['success_dark']
        )
        sct_btn.pack(fill=tk.X, pady=4)

        load_btn = tk.Button(
            file_frame, 
            text="📂 LOAD SWEATBOX FILE", 
            command=self.load_sweatbox_file,
            bg=self.colors['info'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground='#81d4fa'
        )
        load_btn.pack(fill=tk.X, pady=4)

        create_btn = tk.Button(
            file_frame, 
            text="⚡ CREATE SWEATBOX", 
            command=self.create_sweatbox,
            bg=self.colors['warning'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground='#ff8f00'
        )
        create_btn.pack(fill=tk.X, pady=4)

        # Master controller input
        tk.Label(
            file_frame, 
            text="🎯 Master Controller:", 
            bg=self.colors['surface'], 
            fg=self.colors['text'],
            font=label_font,
            highlightthickness=0,
            relief='flat'
        ).pack(anchor=tk.W, pady=(12, 4))
        
        self.master_controller_entry = tk.Entry(
            file_frame, 
            font=entry_font,
            relief='flat', 
            borderwidth=1, 
            bg='#f8f9fa',
            highlightthickness=0
        )
        self.master_controller_entry.pack(fill=tk.X, pady=2)
        self.master_controller_entry.insert(0, "SYS")

        # Export button
        export_btn = tk.Button(
            file_frame, 
            text="💾 EXPORT SWEATBOX", 
            command=self.export_sweatbox,
            bg=self.colors['primary'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground=self.colors['primary_dark']
        )
        export_btn.pack(fill=tk.X, pady=(12, 4))

        # Refresh map button
        refresh_btn = tk.Button(
            file_frame, 
            text="🔄 REFRESH MAP", 
            command=self.refresh_map,
            bg=self.colors['accent'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground='#e91e63'
        )
        refresh_btn.pack(fill=tk.X, pady=4)

        # Web map toggle button
        web_map_btn = tk.Button(
            file_frame, 
            text="🌐 TOGGLE WEB MAP", 
            command=self.toggle_web_map,
            bg=self.colors['info'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground='#81d4fa'
        )
        web_map_btn.pack(fill=tk.X, pady=4)

        # Scenario generation frame
        scenario_frame = tk.LabelFrame(
            parent, 
            text="✈️ SCENARIO GENERATION", 
            padx=15, 
            pady=12,
            bg=self.colors['surface'], 
            fg=self.colors['text'], 
            font=frame_font,
            relief='solid', 
            borderwidth=2,
            highlightthickness=0
        )
        scenario_frame.pack(fill=tk.X, padx=12, pady=8)

        random_btn = tk.Button(
            scenario_frame, 
            text="🎲 GENERATE RANDOM SCENARIO",
            command=self.generate_random_scenario,
            bg=self.colors['success'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground=self.colors['success_dark']
        )
        random_btn.pack(fill=tk.X, pady=4)

        entry_btn = tk.Button(
            scenario_frame, 
            text="📍 GENERATE AT ENTRY FIXES",
            command=self.generate_aircraft_at_entry,
            bg=self.colors['info'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground='#81d4fa'
        )
        entry_btn.pack(fill=tk.X, pady=4)

        clear_btn = tk.Button(
            scenario_frame, 
            text="🗑️ CLEAR ALL AIRCRAFT",
            command=self.clear_all_aircraft,
            bg=self.colors['danger'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground='#d32f2f'
        )
        clear_btn.pack(fill=tk.X, pady=4)

        # Aircraft management frame
        aircraft_frame = tk.LabelFrame(
            parent, 
            text="⚙️ AIRCRAFT MANAGEMENT", 
            padx=15, 
            pady=12,
            bg=self.colors['surface'], 
            fg=self.colors['text'], 
            font=frame_font,
            relief='solid', 
            borderwidth=2,
            highlightthickness=0
        )
        aircraft_frame.pack(fill=tk.X, padx=12, pady=8)

        add_btn = tk.Button(
            aircraft_frame, 
            text="➕ ADD AIRCRAFT",
            command=self.add_aircraft,
            bg=self.colors['primary'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground=self.colors['primary_dark']
        )
        add_btn.pack(fill=tk.X, pady=4)

        edit_btn = tk.Button(
            aircraft_frame, 
            text="✏️ EDIT SELECTED",
            command=self.edit_aircraft,
            bg=self.colors['primary'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground=self.colors['primary_dark']
        )
        edit_btn.pack(fill=tk.X, pady=4)

        delete_btn = tk.Button(
            aircraft_frame, 
            text="🗑️ DELETE SELECTED",
            command=self.delete_aircraft,
            bg=self.colors['danger'], 
            fg='white', 
            font=button_font,
            relief='flat', 
            borderwidth=0,
            highlightthickness=0,
            padx=12, 
            pady=8,
            activebackground='#d32f2f'
        )
        delete_btn.pack(fill=tk.X, pady=4)

        # Status label
        self.status_label = tk.Label(
            parent, 
            text="Ready - Load SCT/ESE files to begin",
            bg=self.colors['surface'], 
            fg=self.colors['text'],
            font=label_font, 
            anchor='w',
            highlightthickness=0,
            relief='flat'
        )
        self.status_label.pack(fill=tk.X, side=tk.BOTTOM, padx=12, pady=8)
    
    def setup_center_panel(self, parent):
        # Store reference to center panel for map recreation
        self.center_panel = parent
        # Create initial map viewer (empty, with no data)
        self.map_viewer = self.SweatboxMapViewer(parent, self.ese_parser, self.sct_parser, self.rwy_parser)
        
        # Enable verbose debug output
        try:
            if hasattr(self.map_viewer, 'debug'):
                self.map_viewer.debug = True
        except Exception:
            pass
    
    def recreate_map(self):
        """Recreate map with current parsers - used when loading new files"""
        try:
            # Save current aircraft data and selection before recreating
            saved_aircraft = self.map_viewer.aircraft_data.copy() if self.map_viewer and hasattr(self.map_viewer, 'aircraft_data') else []
            saved_selected = self.map_viewer.selected_aircraft if self.map_viewer and hasattr(self.map_viewer, 'selected_aircraft') else None
            saved_airport = self.map_viewer.selected_airport if self.map_viewer and hasattr(self.map_viewer, 'selected_airport') else None
            saved_loaded_airports = self.map_viewer.loaded_airports.copy() if self.map_viewer and hasattr(self.map_viewer, 'loaded_airports') else []

            # Destroy ALL child widgets in center_panel to start fresh
            for widget in list(self.center_panel.winfo_children()):
                try:
                    widget.destroy()
                except Exception as e:
                    print(f"Error destroying widget: {e}")
                    try:
                        widget.pack_forget()
                    except Exception as e2:
                        print(f"Error packing forget widget: {e2}")

            # Create new map viewer with updated parser
            self.map_viewer = self.SweatboxMapViewer(self.center_panel, self.ese_parser,
                                                     self.sct_parser, self.rwy_parser)
            if hasattr(self.map_viewer, 'debug'):
                self.map_viewer.debug = True

            # Restore saved data
            self.map_viewer.aircraft_data = saved_aircraft
            self.map_viewer.selected_aircraft = saved_selected
            self.map_viewer.selected_airport = saved_airport
            self.map_viewer.loaded_airports = saved_loaded_airports

            print("[RECREATE] ✓ Map recreated with fresh widgets")
        except Exception as e:
            print(f"[ERROR] Failed to recreate map: {e}")
            import traceback
            traceback.print_exc()
    
    def setup_right_panel(self, parent):
        # Notebook for tabs
        notebook = ttk.Notebook(parent)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Aircraft tab
        aircraft_frame = tk.Frame(notebook)
        notebook.add(aircraft_frame, text="Aircraft")
        self.setup_aircraft_tab(aircraft_frame)
        
        # Controllers tab
        controller_frame = tk.Frame(notebook)
        notebook.add(controller_frame, text="Controllers")
        self.setup_controller_tab(controller_frame)
        
        # Entry fixes tab
        fixes_frame = tk.Frame(notebook)
        notebook.add(fixes_frame, text="Entry Fixes")
        self.setup_fixes_tab(fixes_frame)
        
        # Route editor tab
        route_frame = tk.Frame(notebook)
        notebook.add(route_frame, text="Route Editor")
        self.setup_route_tab(route_frame)
    
    def setup_aircraft_tab(self, parent):
        # Frame for tree and buttons
        main_frame = tk.Frame(parent)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Treeview for aircraft
        columns = ("Callsign", "Type", "Altitude", "Position", "Route", "Speed", "Heading")
        self.aircraft_details_tree = ttk.Treeview(main_frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.aircraft_details_tree.heading(col, text=col)
            self.aircraft_details_tree.column(col, width=100)
        
        # Bind selection event
        self.aircraft_details_tree.bind('<<TreeviewSelect>>', self.on_aircraft_tree_select)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.aircraft_details_tree.yview)
        x_scrollbar = ttk.Scrollbar(main_frame, orient=tk.HORIZONTAL, command=self.aircraft_details_tree.xview)
        self.aircraft_details_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Grid layout
        self.aircraft_details_tree.grid(row=0, column=0, sticky='nsew')
        y_scrollbar.grid(row=0, column=1, sticky='ns')
        x_scrollbar.grid(row=1, column=0, sticky='ew')
        
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Buttons frame
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Add Aircraft", command=self.add_aircraft).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Edit Selected", command=self.edit_aircraft).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_aircraft).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Update Map", command=self.update_aircraft_on_map).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Select on Map", command=self.select_selected_on_map).pack(side=tk.LEFT, padx=5)
    
    def setup_controller_tab(self, parent):
        # Create treeview for controllers
        columns = ("Callsign", "Frequency", "Type", "Simulated")
        self.controller_tree = ttk.Treeview(parent, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.controller_tree.heading(col, text=col)
            self.controller_tree.column(col, width=100)
        
        # Scrollbars
        y_scrollbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.controller_tree.yview)
        self.controller_tree.configure(yscrollcommand=y_scrollbar.set)
        
        self.controller_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 5), pady=5)

        # Bind double-click on controller to toggle simulated state
        try:
            self.controller_tree.bind('<Double-1>', lambda e: self.toggle_controller_sim())
        except Exception:
            pass
        
        # Buttons frame
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Toggle Simulated", command=self.toggle_controller_sim).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Clear All", command=self.clear_controllers).pack(side=tk.LEFT, padx=5)
    
    def setup_fixes_tab(self, parent):
        self.fixes_text = tk.Text(parent, wrap=tk.WORD, height=20)
        self.fixes_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(parent, command=self.fixes_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.fixes_text.config(yscrollcommand=scrollbar.set)
        
        self.fixes_text.insert(tk.END, "Entry fixes will appear here after selecting an airport.")
        self.fixes_text.config(state=tk.DISABLED)
    
    def setup_route_tab(self, parent):
        self.route_text = tk.Text(parent, wrap=tk.WORD, height=20)
        self.route_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(parent, command=self.route_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.route_text.config(yscrollcommand=scrollbar.set)
        
        self.route_text.insert(tk.END, "Route editor will appear here.")
        self.route_text.config(state=tk.NORMAL)
        
        btn_frame = tk.Frame(parent)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)
        
        tk.Button(btn_frame, text="Apply Route to Selected Aircraft", 
                 command=self.apply_route_to_selected).pack(side=tk.LEFT, padx=5)
    
    def extract_airports_from_controllers(self, positions):
        """Extract unique airport ICAOs from controller positions.

        Rules applied:
        - Skip any controller that ends with FSS or CTR (case-insensitive)
        - Split callsign on '_' and look for the first 4-letter alphabetic token
        - Return a sorted list of unique ICAOs
        
        Examples:
        - OMAA_APP -> OMAA (valid)
        - OMAA_CTR -> skip (CTR is not an airport)
        - OMAA_FSS -> skip (FSS is not an airport)
        - OMDB_TWR -> OMDB (valid)
        """
        airports = set()
        for pos in positions:
            raw = (pos.get('callsign') or '').strip().upper()
            if not raw:
                continue

            # Skip any callsigns that end with FSS or CTR (these are not airports)
            if raw.endswith('_FSS') or raw.endswith('_CTR'):
                if self.debug if hasattr(self, 'debug') else False:
                    print(f"[EXTRACT] Skipping {raw} - ends with FSS or CTR")
                continue

            parts = [p for p in raw.split('_') if p]
            if not parts:
                continue
            
            # Extract first token (should be 4-letter ICAO)
            first_token = parts[0]
            if len(first_token) == 4 and first_token.isalpha():
                airports.add(first_token)
                # Uncomment for debugging:
                # print(f"[EXTRACT] Valid airport: {first_token} from {raw}")

        return sorted(list(airports))
    
    def load_ese_file(self):
        file_path = filedialog.askopenfilename(
            title="Select ESE File",
            filetypes=[("ESE files", "*.ese"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.ese_parser = self.ESEParser(file_path)
                
                # CRITICAL: Update map viewer with the ESE parser so it can use the fallback logic
                if self.map_viewer and hasattr(self.map_viewer, 'ese_parser'):
                    self.map_viewer.ese_parser = self.ese_parser
                    print(f"[ESE] Updated map viewer with ESE parser")
                
                # Extract airports from controller positions
                positions = []
                if hasattr(self.ese_parser, 'get_positions'):
                    positions = self.ese_parser.get_positions()
                    print(f"[ESE] Loaded {len(positions)} controller positions from ESE")
                
                # Extract airports (everything before underscore)
                airports = self.extract_airports_from_controllers(positions)
                
                # Update map viewer with extracted airports
                if self.map_viewer and hasattr(self.map_viewer, 'update_airports'):
                    self.map_viewer.update_airports(airports)

                    # Also highlight those airports on the map (look up coordinates from SCT if available)
                    try:
                        if hasattr(self.map_viewer, 'highlight_airports'):
                            # If there is no SCT parser loaded, we cannot resolve ICAOs to coords
                            if not self.sct_parser:
                                print("[ESE] No SCT loaded - cannot highlight airports. Load SCT file first to enable highlighting.")
                                messagebox.showinfo("Notice", "ESE loaded but no SCT data present.\nLoad an SCT file first to highlight airports on the map.")
                            else:
                                drawn = self.map_viewer.highlight_airports(airports)
                                print(f"[ESE] Highlighted {drawn} airports on map")
                                if drawn == 0:
                                    # No matching airports from ESE. Try displaying all SCT airports instead.
                                    print(f"[ESE] No matching airports found for extracted: {', '.join(airports)}")
                                    try:
                                        sct_data = self.sct_parser.get_data()
                                        sct_airports = [a.get('icao') for a in sct_data.get('airports', []) if a.get('icao')]
                                        if sct_airports:
                                            print(f"[ESE] Falling back to displaying SCT airports: {sct_airports}")
                                            # Highlight SCT airports instead
                                            drawn_sct = self.map_viewer.highlight_airports(sct_airports)
                                            print(f"[ESE] Highlighted {drawn_sct} SCT airports on map")
                                            messagebox.showinfo("Note", 
                                                f"ESE controllers did not match SCT airports.\n"
                                                f"Displaying SCT airports instead: {', '.join(sct_airports)}\n\n"
                                                f"ESE extracted: {', '.join(airports[:5])}{'...' if len(airports) > 5 else ''}")
                                        else:
                                            messagebox.showinfo("ESE Notice", 
                                                f"No airports extracted from ESE.\n"
                                                f"No airports in SCT either.")
                                    except Exception as e:
                                        print(f"[ESE] Error falling back to SCT airports: {e}")
                                        messagebox.showinfo("ESE Notice", 
                                            f"No matching airports found in loaded SCT for: {', '.join(airports[:10])}")
                    except Exception as e:
                        print(f"[ESE] Error highlighting airports: {e}")
                
                # Clear existing controllers
                if self.controller_tree:
                    for item in self.controller_tree.get_children():
                        self.controller_tree.delete(item)
                
                # Add controllers to tree - DEFAULT TO ✗ (OFF)
                for pos in positions:
                    callsign = (pos.get('callsign') or '').strip().upper()
                    # Skip FSS and CTR types entirely from the list
                    if 'FSS' in callsign or callsign.endswith('_CTR') or '_CTR' in callsign:
                        continue

                    self.controller_tree.insert('', 'end', values=(
                        pos.get('callsign', ''),
                        pos.get('frequency', ''),
                        pos.get('type', ''),
                        '✗'  # DEFAULT TO OFF (not simulated)
                    ))
                
                messagebox.showinfo("Success", 
                    f"Loaded ESE file: {file_path}\n"
                    f"Positions found: {len(positions)}\n"
                    f"Airports extracted: {len(airports)}\n"
                    f"Airports: {', '.join(airports[:10])}{'...' if len(airports) > 10 else ''}"
                )
                self.status_label.config(text=f"Loaded ESE: {os.path.basename(file_path)} - {len(positions)} positions, {len(airports)} airports")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load ESE file: {str(e)}")
    
    def load_sct_file(self):
        file_path = filedialog.askopenfilename(
            title="Select SCT File",
            filetypes=[("SCT files", "*.sct"), ("All files", "*.*")]
        )
        if file_path:
            try:
                print(f"\n[LOAD] Loading SCT file: {os.path.basename(file_path)}")
                self.sct_parser = self.SCTParser(file_path)
                data = self.sct_parser.parse()
                
                # Show detailed info about what was loaded
                airports_count = len(data.get('airports', []))
                fixes_count = len(data.get('fixes', []))
                runways_count = len(data.get('runways', []))
                vor_count = len(data.get('VOR', []))
                ndb_count = len(data.get('NDB', []))
                artcc_high_count = len(data.get('ARTCC_HIGH', []))
                artcc_low_count = len(data.get('ARTCC_LOW', []))
                
                print(f"[LOAD] ✓ Parsed: {airports_count} airports, {fixes_count} fixes, {runways_count} runways")
                
                messagebox.showinfo("Success", 
                    f"Loaded SCT file: {os.path.basename(file_path)}\n"
                    f"Airports: {airports_count}\n"
                    f"Fixes: {fixes_count}\n"
                    f"Runways: {runways_count}\n"
                    f"VORs: {vor_count}\n"
                    f"NDBs: {ndb_count}\n"
                    f"ARTCC High: {artcc_high_count} boundaries\n"
                    f"ARTCC Low: {artcc_low_count} boundaries"
                )
                
                # Recreate map with new parser and load data
                print("[LOAD] Recreating map with new data...")
                self.recreate_map()
                self.map_viewer.load_data()
                print("[LOAD] ✓ Map displayed")
                
                # Highlight all SCT airports on the map
                try:
                    sct_airports = [a.get('icao') for a in data.get('airports', []) if a.get('icao')]
                    if sct_airports and hasattr(self.map_viewer, 'highlight_airports'):
                        drawn = self.map_viewer.highlight_airports(sct_airports)
                        print(f"[LOAD] ✓ Highlighted {drawn} airports on map")
                except Exception as e:
                    print(f"[LOAD] Could not highlight airports: {e}")
                
                self.status_label.config(text=f"✓ Loaded {os.path.basename(file_path)}\n{airports_count} airports, {fixes_count} fixes")
                
            except Exception as e:
                print(f"[ERROR] {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Error", f"Failed to load SCT file: {str(e)}")
    
    def load_rwy_file(self):
        file_path = filedialog.askopenfilename(
            title="Select RWY File",
            filetypes=[("RWY files", "*.rwy"), ("All files", "*.*")]
        )
        if file_path:
            try:
                self.rwy_parser = self.RWYParser(file_path)
                data = self.rwy_parser.parse()
                
                # Check if data was parsed
                runways_count = len(data.get('runways', []))
                ils_count = len(data.get('ils_data', []))
                centerlines_count = len(data.get('centerlines', []))
                
                messagebox.showinfo("Success", 
                    f"Loaded RWY file: {file_path}\n"
                    f"Runways: {runways_count}\n"
                    f"ILS Data: {ils_count}\n"
                    f"Centerlines: {centerlines_count}"
                )
                
                # Update map viewer - LOAD DATA IMMEDIATELY
                if self.map_viewer:
                    self.map_viewer.rwy_parser = self.rwy_parser
                    self.map_viewer.load_data()  # This should draw data to map
                
                self.status_label.config(text=f"Loaded RWY: {os.path.basename(file_path)} - {runways_count} runways, {ils_count} ILS")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load RWY file: {str(e)}")

    def load_sweatbox_file(self):
        """Load an existing sweatbox-like file and import controllers and aircraft into the UI"""
        file_path = filedialog.askopenfilename(
            title="Select Sweatbox File",
            filetypes=[("Text files", "*.txt;*.sweatbox;*.sbx"), ("All files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = [l.strip() for l in f.readlines()]

            # Clear existing trees
            for item in self.controller_tree.get_children():
                self.controller_tree.delete(item)
            for item in self.aircraft_details_tree.get_children():
                self.aircraft_details_tree.delete(item)

            aircraft_cache = {}
            current_callsign = None
            current_index = 0

            for line in lines:
                if not line:
                    continue
                # Controllers
                if line.startswith('CONTROLLER:'):
                    # Format: CONTROLLER:CALLSIGN:FREQUENCY
                    parts = line.split(':')
                    if len(parts) >= 3:
                        callsign = parts[1].strip()
                        freq = parts[2].strip()
                        self.controller_tree.insert('', 'end', values=(callsign, freq, '', '✓'))

                # Aircraft start
                if line.startswith('@N:'):
                    # Example: @N:CALLSIGN:7367:1:-25.4403997:27.0490802:19000:0:1456:0
                    parts = line.split(':')
                    if len(parts) >= 7:
                        callsign = parts[1].strip()
                        lat = parts[4].strip()
                        lon = parts[5].strip()
                        alt = parts[6].strip()
                        current_callsign = callsign
                        aircraft_cache[current_callsign] = {
                            'callsign': current_callsign,
                            'position': f"{lat}, {lon}",
                            'altitude': f"{alt}ft",
                            'type': '',
                            'route': ''
                        }
                        current_index += 1

                # Flight plan lines ($FP...)
                if line.startswith('$FP') or line.startswith('$FP'):
                    # try to extract aircraft type after the colon
                    try:
                        parts = line.split(':')
                        if len(parts) >= 4:
                            callsign_fp = parts[0][3:]
                            ac_type = parts[3].split('/')[0].strip()
                            # if FP line belongs to last parsed callsign, set type
                            if current_callsign and current_callsign in aircraft_cache:
                                aircraft_cache[current_callsign]['type'] = ac_type
                    except Exception:
                        pass

                # Route
                if line.startswith('$ROUTE:'):
                    route = line[len('$ROUTE:'):].strip()
                    if current_callsign and current_callsign in aircraft_cache:
                        aircraft_cache[current_callsign]['route'] = route

            # Populate aircraft tree and map
            for callsign, ad in aircraft_cache.items():
                vals = (
                    ad.get('callsign', 'N/A'),
                    ad.get('type', 'N/A'),
                    ad.get('altitude', 'N/A'),
                    ad.get('position', 'N/A'),
                    ad.get('route', ''),
                    '250',
                    '000'
                )
                self.aircraft_details_tree.insert('', 'end', values=vals)
                # also add to map
                if self.map_viewer and hasattr(self.map_viewer, 'add_aircraft'):
                    self.map_viewer.add_aircraft({
                        'callsign': ad.get('callsign'),
                        'type': ad.get('type'),
                        'altitude': ad.get('altitude'),
                        'position': ad.get('position'),
                        'route': ad.get('route'),
                        'speed': '250',
                        'heading': '000'
                    })

            # Redraw map
            if self.map_viewer and hasattr(self.map_viewer, 'redraw_all'):
                self.map_viewer.redraw_all()

            messagebox.showinfo('Loaded', f'Imported sweatbox-like file: {os.path.basename(file_path)}')
            self.status_label.config(text=f'Imported sweatbox: {os.path.basename(file_path)}')

        except Exception as e:
            messagebox.showerror('Error', f'Failed to load sweatbox file: {e}')

    def create_sweatbox(self):
        """Guided create flow: ensure SCT/ESE/RWY loaded, choose airports, optionally import existing sweatbox, then allow edits and export."""
        # If ESE not loaded, prompt
        if not self.ese_parser:
            if messagebox.askyesno('Missing ESE', 'No ESE file loaded. Do you want to load one now?'):
                self.load_ese_file()
        # If SCT not loaded, prompt
        if not self.sct_parser:
            if messagebox.askyesno('Missing SCT', 'No SCT file loaded. Do you want to load one now?'):
                self.load_sct_file()
        # If RWY not loaded, prompt
        if not self.rwy_parser:
            if messagebox.askyesno('Missing RWY', 'No RWY file loaded. Do you want to load one now?'):
                self.load_rwy_file()

        # Extract available airports
        airports = []
        try:
            if self.map_viewer and hasattr(self.map_viewer, 'loaded_airports') and self.map_viewer.loaded_airports:
                airports = list(self.map_viewer.loaded_airports)
            elif self.sct_parser and hasattr(self.sct_parser, 'get_data'):
                data = self.sct_parser.get_data()
                if 'airports' in data:
                    airports = [a.get('icao') for a in data['airports'] if a.get('icao')]
        except Exception:
            airports = []

        if not airports:
            messagebox.showwarning('No Airports', 'No airports found in loaded data. Please load an SCT file containing airports.')
            return

        # Ask user which airports to include (multi-select)
        sel = tk.Toplevel(self.parent)
        sel.title('Select Airports to Include')
        sel.geometry('300x400')
        sel.transient(self.parent)
        listbox = tk.Listbox(sel, selectmode=tk.MULTIPLE)
        listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        for a in airports:
            listbox.insert(tk.END, a)

        def on_select_done():
            chosen = [listbox.get(i) for i in listbox.curselection()]
            if not chosen:
                messagebox.showwarning('Select', 'Please select at least one airport')
                return
            # Update map viewer airports and center on first
            if self.map_viewer and hasattr(self.map_viewer, 'update_airports'):
                self.map_viewer.update_airports(chosen)
                # Select first
                try:
                    self.map_viewer.airport_combo.set(chosen[0])
                    self.map_viewer.on_airport_selected(None)
                except Exception:
                    pass

            sel.destroy()

            # Optionally import an existing sweatbox file to pre-populate aircraft/controllers
            if messagebox.askyesno('Import', 'Do you want to import an existing sweatbox file to edit?'):
                self.load_sweatbox_file()

            messagebox.showinfo('Create', 'You can now edit aircraft/controllers and export the sweatbox when ready.')

        btn = tk.Button(sel, text='Done', command=on_select_done, bg='#2ecc71', fg='white')
        btn.pack(pady=6)
    
    def generate_random_scenario(self):
        if not self.map_viewer:
            messagebox.showwarning("Warning", "Map viewer not available.")
            return
        
        selected_airport = self.map_viewer.get_selected_airport()
        generator = self.RandomScenarioGenerator(self)
        generator.generate_random_scenario(selected_airport=selected_airport)
    
    def generate_aircraft_at_entry(self):
        if not self.map_viewer:
            messagebox.showwarning("Warning", "Map viewer not available.")
            return
        
        entry_fixes = self.map_viewer.get_entry_fixes()
        airport = self.map_viewer.get_selected_airport()
        
        if not entry_fixes or not airport:
            messagebox.showwarning("Warning", "No entry fixes found. Please select an airport first.")
            return
        
        generator = self.RandomScenarioGenerator(self)
        if hasattr(generator, 'generate_aircraft_at_entry_fixes'):
            aircraft_list = generator.generate_aircraft_at_entry_fixes(entry_fixes, airport)
            
            # Add aircraft to tree and map
            for aircraft in aircraft_list:
                self.add_aircraft_from_dict(aircraft)
            
            # Update map
            self.update_aircraft_on_map()
            
            messagebox.showinfo("Success", f"Generated {len(aircraft_list)} aircraft at entry fixes")
            self.status_label.config(text=f"Generated {len(aircraft_list)} aircraft at entry fixes")
        else:
            messagebox.showinfo("Info", "Aircraft generation at entry fixes not available")
    
    def add_aircraft_from_dict(self, aircraft_dict):
        # Add to tree
        values = (
            aircraft_dict.get('callsign', 'N/A'),
            aircraft_dict.get('type', 'N/A'),
            aircraft_dict.get('altitude', 'N/A'),
            aircraft_dict.get('position', 'N/A'),
            aircraft_dict.get('route', ''),
            aircraft_dict.get('speed', '250'),
            aircraft_dict.get('heading', '000')
        )
        self.aircraft_details_tree.insert('', 'end', values=values)
        
        # Add to map
        if self.map_viewer and hasattr(self.map_viewer, 'add_aircraft'):
            self.map_viewer.add_aircraft(aircraft_dict)
    
    def add_aircraft(self):
        # Simple dialog to add aircraft
        dialog = tk.Toplevel(self.parent)
        dialog.title("Add Aircraft")
        dialog.geometry("400x350")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Callsign:").pack(pady=(10, 0))
        callsign_entry = tk.Entry(dialog, width=30)
        callsign_entry.pack(pady=5)
        callsign_entry.insert(0, "SAA123")
        
        tk.Label(dialog, text="Aircraft Type:").pack(pady=(10, 0))
        type_entry = tk.Entry(dialog, width=30)
        type_entry.pack(pady=5)
        type_entry.insert(0, "A320")
        
        tk.Label(dialog, text="Altitude (ft):").pack(pady=(10, 0))
        alt_entry = tk.Entry(dialog, width=30)
        alt_entry.pack(pady=5)
        alt_entry.insert(0, "35000")
        
        tk.Label(dialog, text="Position (lat,lon):").pack(pady=(10, 0))
        pos_entry = tk.Entry(dialog, width=30)
        pos_entry.pack(pady=5)
        pos_entry.insert(0, "-26.145, 28.234")
        
        tk.Label(dialog, text="Route:").pack(pady=(10, 0))
        route_entry = tk.Entry(dialog, width=30)
        route_entry.pack(pady=5)
        route_entry.insert(0, "DCT FAOR")
        
        tk.Label(dialog, text="Speed (kts):").pack(pady=(10, 0))
        speed_entry = tk.Entry(dialog, width=30)
        speed_entry.pack(pady=5)
        speed_entry.insert(0, "250")
        
        tk.Label(dialog, text="Heading (deg):").pack(pady=(10, 0))
        heading_entry = tk.Entry(dialog, width=30)
        heading_entry.pack(pady=5)
        heading_entry.insert(0, "000")
        
        def save_aircraft():
            values = (
                callsign_entry.get(),
                type_entry.get(),
                f"{alt_entry.get()}ft",
                pos_entry.get(),
                route_entry.get(),
                speed_entry.get(),
                heading_entry.get()
            )
            self.aircraft_details_tree.insert('', 'end', values=values)
            dialog.destroy()
            self.update_aircraft_on_map()
        
        tk.Button(dialog, text="Add", command=save_aircraft, bg='#2ecc71', fg='white').pack(pady=20)
    
    def edit_aircraft(self):
        selected = self.aircraft_details_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an aircraft to edit.")
            return
        
        item = selected[0]
        values = self.aircraft_details_tree.item(item, 'values')
        
        dialog = tk.Toplevel(self.parent)
        dialog.title("Edit Aircraft")
        dialog.geometry("400x350")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        tk.Label(dialog, text="Callsign:").pack(pady=(10, 0))
        callsign_entry = tk.Entry(dialog, width=30)
        callsign_entry.pack(pady=5)
        callsign_entry.insert(0, values[0])
        
        tk.Label(dialog, text="Aircraft Type:").pack(pady=(10, 0))
        type_entry = tk.Entry(dialog, width=30)
        type_entry.pack(pady=5)
        type_entry.insert(0, values[1])
        
        tk.Label(dialog, text="Altitude (ft):").pack(pady=(10, 0))
        alt_entry = tk.Entry(dialog, width=30)
        alt_entry.pack(pady=5)
        alt_entry.insert(0, values[2].replace('ft', ''))
        
        tk.Label(dialog, text="Position (lat,lon):").pack(pady=(10, 0))
        pos_entry = tk.Entry(dialog, width=30)
        pos_entry.pack(pady=5)
        pos_entry.insert(0, values[3])
        
        tk.Label(dialog, text="Route:").pack(pady=(10, 0))
        route_entry = tk.Entry(dialog, width=30)
        route_entry.pack(pady=5)
        route_entry.insert(0, values[4])
        
        tk.Label(dialog, text="Speed:").pack(pady=(10, 0))
        speed_entry = tk.Entry(dialog, width=30)
        speed_entry.pack(pady=5)
        speed_entry.insert(0, values[5] if len(values) > 5 else "250")
        
        tk.Label(dialog, text="Heading:").pack(pady=(10, 0))
        heading_entry = tk.Entry(dialog, width=30)
        heading_entry.pack(pady=5)
        heading_entry.insert(0, values[6] if len(values) > 6 else "000")
        
        def save_changes():
            new_values = (
                callsign_entry.get(),
                type_entry.get(),
                f"{alt_entry.get()}ft",
                pos_entry.get(),
                route_entry.get(),
                speed_entry.get(),
                heading_entry.get()
            )
            self.aircraft_details_tree.item(item, values=new_values)
            dialog.destroy()
            self.update_aircraft_on_map()
        
        tk.Button(dialog, text="Save", command=save_changes, bg='#2ecc71', fg='white').pack(pady=20)
    
    def delete_aircraft(self):
        selected = self.aircraft_details_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an aircraft to delete.")
            return
        
        for item in selected:
            self.aircraft_details_tree.delete(item)
        
        self.update_aircraft_on_map()
        self.status_label.config(text=f"Deleted {len(selected)} aircraft")
    
    def clear_all_aircraft(self):
        for item in self.aircraft_details_tree.get_children():
            self.aircraft_details_tree.delete(item)
        
        if self.map_viewer and hasattr(self.map_viewer, 'clear_aircraft'):
            self.map_viewer.clear_aircraft()
        
        self.status_label.config(text="Cleared all aircraft")
    
    def toggle_controller_sim(self):
        selected = self.controller_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a controller to toggle.")
            return
        
        for item in selected:
            values = list(self.controller_tree.item(item, 'values'))
            if values[3] == '✓':
                values[3] = '✗'
            else:
                values[3] = '✓'
            self.controller_tree.item(item, values=values)
    
    def clear_controllers(self):
        for item in self.controller_tree.get_children():
            self.controller_tree.delete(item)
    
    def apply_route_to_selected(self):
        selected = self.aircraft_details_tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select an aircraft to apply route to.")
            return
        
        route = self.route_text.get("1.0", tk.END).strip()
        if not route:
            messagebox.showwarning("Warning", "Please enter a route in the Route Editor tab.")
            return
        
        for item in selected:
            values = list(self.aircraft_details_tree.item(item, 'values'))
            if len(values) >= 5:
                values[4] = route
                self.aircraft_details_tree.item(item, values=values)
        
        self.update_aircraft_on_map()
        messagebox.showinfo("Success", f"Applied route to {len(selected)} aircraft")
    
    def export_sweatbox(self):
        if not self.aircraft_details_tree.get_children():
            messagebox.showwarning("Warning", "No aircraft to export.")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Export Sweatbox File",
            defaultextension=".txt",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                self.master_controller = self.master_controller_entry.get()
                exporter = self.SweatboxExporter(self)
                success, message = exporter.export(file_path)
                
                if success:
                    messagebox.showinfo("Success", message)
                    self.status_label.config(text=f"Exported to {os.path.basename(file_path)}")
                else:
                    messagebox.showerror("Error", message)
            except Exception as e:
                messagebox.showerror("Error", f"Export failed: {str(e)}")
    
    def refresh_map(self):
        if self.map_viewer and hasattr(self.map_viewer, 'redraw_all'):
            self.map_viewer.redraw_all()
            self.status_label.config(text="Map refreshed")

    def toggle_web_map(self):
        """Toggle between app map and web map"""
        if self.map_viewer and hasattr(self.map_viewer, 'toggle_web_map'):
            self.map_viewer.toggle_web_map()
        else:
            messagebox.showwarning("Warning", "Web map feature not available. Please install Flask and Folium.")
    
    def update_aircraft_on_map(self):
        """Update aircraft on map from tree data"""
        if not self.map_viewer or not hasattr(self.map_viewer, 'clear_aircraft'):
            return
        
        # Clear existing aircraft from map
        self.map_viewer.clear_aircraft()
        
        # Add all aircraft from tree
        for item in self.aircraft_details_tree.get_children():
            values = self.aircraft_details_tree.item(item, 'values')
            if values and len(values) >= 5:
                callsign, ac_type, altitude, position, route = values[:5]
                
                # Get speed and heading if available
                speed = "250"
                heading = "000"
                if len(values) >= 7:
                    speed = values[5] if values[5] else "250"
                    heading = values[6] if values[6] else "000"
                
                # Create aircraft data dict
                aircraft_data = {
                    'callsign': callsign,
                    'type': ac_type,
                    'altitude': altitude,
                    'position': position,
                    'route': route,
                    'speed': speed,
                    'heading': heading
                }
                
                # Add to map
                if hasattr(self.map_viewer, 'add_aircraft'):
                    self.map_viewer.add_aircraft(aircraft_data)
        
        # Fit to data to show all aircraft
        if hasattr(self.map_viewer, 'fit_to_data'):
            try:
                self.map_viewer.fit_to_data()
            except:
                pass

        # Force canvas update to ensure markers are visible
        try:
            self.map_viewer.map_widget.canvas.update()
        except:
            pass
        self.status_label.config(text="Updated aircraft on map")
    
    def on_aircraft_position_update(self, callsign, new_position):
        """Handle aircraft position update from map"""
        print(f"DEBUG: Updating position for {callsign} to {new_position}")
        
        # Update in aircraft tree
        for item in self.aircraft_details_tree.get_children():
            values = self.aircraft_details_tree.item(item, 'values')
            if values and values[0] == callsign:
                new_values = list(values)
                new_values[3] = new_position  # Update position field
                self.aircraft_details_tree.item(item, values=tuple(new_values))
                print(f"✓ Updated {callsign} position in tree")
                break
        
        # Update map
        if self.map_viewer:
            self.map_viewer.redraw_all()
        
        self.status_label.config(text=f"Updated position for {callsign}")
    
    def on_aircraft_tree_select(self, event):
        """Handle aircraft selection in tree"""
        selected = self.aircraft_details_tree.selection()
        if selected:
            item = selected[0]
            values = self.aircraft_details_tree.item(item, 'values')
            if values:
                callsign = values[0]
                self.select_aircraft_on_map(callsign)
    
    def select_aircraft_on_map(self, callsign):
        """Select aircraft on map from tree selection"""
        if self.map_viewer and hasattr(self.map_viewer, 'select_aircraft'):
            success = self.map_viewer.select_aircraft(callsign)
            if success:
                self.status_label.config(text=f"Selected {callsign} on map")
            else:
                self.status_label.config(text=f"Aircraft {callsign} not found on map")
    
    def select_selected_on_map(self):
        """Select currently selected aircraft on map"""
        selected = self.aircraft_details_tree.selection()
        if selected:
            item = selected[0]
            values = self.aircraft_details_tree.item(item, 'values')
            if values:
                callsign = values[0]
                self.select_aircraft_on_map(callsign)
        else:
            messagebox.showwarning("Warning", "Please select an aircraft first.")
    
    def get_simulated_controllers(self):
        """Get controllers marked for simulation"""
        controllers = []
        if self.controller_tree:
            for item in self.controller_tree.get_children():
                values = self.controller_tree.item(item, 'values')
                if values and values[3] == '✓':  # Only simulated controllers
                    controllers.append({
                        'callsign': values[0],
                        'frequency': values[1],
                        'type': values[2]
                    })
        return controllers
    
    def show_help(self):
        """Show comprehensive help dialog"""
        help_window = tk.Toplevel(self.parent)
        help_window.title("Sweatbox Creator - Help & Quick Start")
        help_window.geometry("700x600")
        help_window.transient(self.parent)
        help_window.grab_set()

        # Create notebook for different help sections
        notebook = ttk.Notebook(help_window)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Quick Start tab
        quick_frame = tk.Frame(notebook)
        notebook.add(quick_frame, text="🚀 Quick Start")

        quick_text = tk.Text(quick_frame, wrap=tk.WORD, padx=10, pady=10, font=(self.font_name, 10))
        quick_text.pack(fill=tk.BOTH, expand=True)

        quick_content = """
SWEATBOX CREATOR - QUICK START GUIDE

1. LOAD YOUR DATA FILES:
   • Click "Load SCT File" to load sector data (airports, fixes, airways)
   • Click "Load ESE File" to load controller positions
   • Optional: Load RWY file for detailed runway information

2. CONFIGURE YOUR SCENARIO:
   • Select an airport from the dropdown to center the map
   • Use the checkboxes to show/hide different map elements
   • Enable "RWY Extensions" to see 20NM centerline extensions

3. ADD AIRCRAFT:
   • Click "Add Aircraft" to manually add aircraft
   • Or use "Generate Random Scenario" for automatic aircraft placement
   • Edit aircraft details by selecting them and clicking "Edit Selected"

4. MANAGE CONTROLLERS:
   • Controllers are automatically loaded from ESE files
   • Double-click controllers to toggle simulation on/off
   • Use "Toggle Simulated" button for batch operations

5. EXPORT YOUR SCENARIO:
   • Click "Export Sweatbox" to save your scenario
   • The file can be used with ATC simulation software

TIPS:
• Use the map controls (+/-) to zoom in/out
• Click "Fit Data" to center all loaded elements
• Drag aircraft on the map to reposition them
• Double-click the map to move selected aircraft
        """
        quick_text.insert(tk.END, quick_content)
        quick_text.config(state=tk.DISABLED)

        # Features tab
        features_frame = tk.Frame(notebook)
        notebook.add(features_frame, text="✨ Features")

        features_text = tk.Text(features_frame, wrap=tk.WORD, padx=10, pady=10, font=(self.font_name, 10))
        features_text.pack(fill=tk.BOTH, expand=True)

        features_content = """
PROFESSIONAL FEATURES

MAP VISUALIZATION:
• Interactive map with pan, zoom, and fit-to-data
• Airport markers with ICAO codes
• Runway centerlines and 20NM extensions
• Aircraft positions with heading indicators
• Navigation aids (VOR, NDB) and fixes
• Airway boundaries and sector divisions

AIRCRAFT MANAGEMENT:
• Manual aircraft addition and editing
• Bulk aircraft generation at entry fixes
• Real-time position updates via map interaction
• Route assignment and modification
• Aircraft type and performance data

CONTROLLER SIMULATION:
• Automatic controller loading from ESE files
• Simulation toggle for each controller position
• Frequency and type information
• Bulk controller management

DATA SUPPORT:
• SCT (Sector) files for airspace data
• ESE (EuroScope) files for controller positions
• RWY files for detailed runway information
• Export to Sweatbox-compatible format

USER INTERFACE:
• Modern Material Design-inspired interface
• Intuitive three-panel layout
• Professional color scheme
• Tooltips and contextual help
• Responsive design with adjustable panels
        """
        features_text.insert(tk.END, features_content)
        features_text.config(state=tk.DISABLED)

        # Keyboard Shortcuts tab
        shortcuts_frame = tk.Frame(notebook)
        notebook.add(shortcuts_frame, text="⌨️ Shortcuts")

        shortcuts_text = tk.Text(shortcuts_frame, wrap=tk.WORD, padx=10, pady=10, font=(self.font_name, 10))
        shortcuts_text.pack(fill=tk.BOTH, expand=True)

        shortcuts_content = """
KEYBOARD SHORTCUTS & MOUSE CONTROLS

MAP CONTROLS:
• Left Click + Drag: Pan the map
• Mouse Wheel: Zoom in/out
• Double Left Click: Move selected aircraft to position

AIRCRAFT MANAGEMENT:
• Double-click aircraft in list: Select on map
• Right-click aircraft on map: Show context menu

DATA MANAGEMENT:
• Ctrl+S: Quick save/export
• Ctrl+O: Load sweatbox file
• F5: Refresh map display

WINDOW MANAGEMENT:
• Ctrl+W: Close current dialog
• Alt+F4: Exit application

MOUSE CONTROLS:
• Hover over buttons: Show tooltips
• Drag panel borders: Resize panels
• Click airport markers: Center map on airport
• Click aircraft markers: Select aircraft
        """
        shortcuts_text.insert(tk.END, shortcuts_content)
        shortcuts_text.config(state=tk.DISABLED)

        # About tab
        about_frame = tk.Frame(notebook)
        notebook.add(about_frame, text="ℹ️ About")

        about_text = tk.Text(about_frame, wrap=tk.WORD, padx=10, pady=10, font=(self.font_name, 10))
        about_text.pack(fill=tk.BOTH, expand=True)

        about_content = """
SWEATBOX CREATOR
Professional ATC Scenario Builder

VERSION: 2.0
PLATFORM: Cross-platform (Windows, macOS, Linux)

DESCRIPTION:
Sweatbox Creator is a professional tool for creating realistic
Air Traffic Control training scenarios. It provides an intuitive
interface for loading airspace data, positioning aircraft, and
configuring controller positions for simulation training.

SUPPORTED FORMATS:
• SCT (Sector) files - Airspace and navigation data
• ESE (EuroScope) files - Controller position data
• RWY files - Detailed runway information
• Sweatbox export format - Compatible with ATC simulators

SYSTEM REQUIREMENTS:
• Python 3.8 or higher
• tkinter (included with Python)
• tkintermapview library
• Pillow (PIL) for enhanced graphics

CONTACT & SUPPORT:
For support, feature requests, or bug reports, please refer to
the project documentation or contact the development team.

© 2024 Sweatbox Creator Development Team
Licensed under MIT License
        """
        about_text.insert(tk.END, about_content)
        about_text.config(state=tk.DISABLED)

        # Close button
        close_btn = tk.Button(help_window, text="Close", command=help_window.destroy,
                            bg=self.colors['primary'], fg='white',
                            font=(self.font_name, 10, 'bold'), padx=20, pady=8)
        close_btn.pack(pady=10)

    def test_aircraft_features(self):
        """Test aircraft features with sample data"""
        # Add some test aircraft with different headings
        test_aircraft = [
            {
                'callsign': 'SAA101',
                'type': 'A320',
                'altitude': '35000ft',
                'position': '-26.145, 28.234',
                'route': 'DCT FAOR',
                'speed': '480',
                'heading': '045'  # Northeast
            },
            {
                'callsign': 'SAA202',
                'type': 'B738',
                'altitude': '28000ft',
                'position': '-26.100, 28.300',
                'route': 'DCT FACT',
                'speed': '420',
                'heading': '180'  # South
            },
            {
                'callsign': 'SAA303',
                'type': 'A333',
                'altitude': '38000ft',
                'position': '-26.200, 28.150',
                'route': 'DCT FALE',
                'speed': '520',
                'heading': '270'  # West
            }
        ]

        for aircraft in test_aircraft:
            self.add_aircraft_from_dict(aircraft)

        self.update_aircraft_on_map()
        messagebox.showinfo("Test", "Added 3 test aircraft with different headings")
        self.status_label.config(text="Added test aircraft with heading indicators")

    def open_chat(self):
        """Open a chat interface for user support"""
        chat_window = tk.Toplevel(self.parent)
        chat_window.title("Sweatbox Creator - Support Chat")
        chat_window.geometry("500x600")
        chat_window.transient(self.parent)
        chat_window.grab_set()

        # Chat display area
        chat_frame = tk.Frame(chat_window, bg='white')
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        chat_text = tk.Text(chat_frame, wrap=tk.WORD, state=tk.DISABLED,
                          font=(self.font_name, 10), bg='#f8f9fa')
        chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = tk.Scrollbar(chat_frame, command=chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        chat_text.config(yscrollcommand=scrollbar.set)

        # Input area
        input_frame = tk.Frame(chat_window, bg='white')
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        input_entry = tk.Entry(input_frame, font=(self.font_name, 10))
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def send_message():
            message = input_entry.get().strip()
            if message:
                chat_text.config(state=tk.NORMAL)
                chat_text.insert(tk.END, f"You: {message}\n")
                chat_text.config(state=tk.DISABLED)
                chat_text.see(tk.END)
                input_entry.delete(0, tk.END)

                # Simulate bot response
                import time
                chat_window.after(1000, lambda: show_bot_response(message))

        def show_bot_response(user_message):
            responses = {
                "help": "I'm here to help! You can ask me about:\n• Loading SCT/ESE files\n• Aircraft generation\n• Controller setup\n• Exporting scenarios",
                "sct": "SCT files contain sector data including airports, runways, fixes, and airways. Load them first to see the airspace structure.",
                "ese": "ESE files contain controller positions and frequencies. They're needed for realistic ATC simulation.",
                "aircraft": "You can add aircraft manually or generate them randomly. Each aircraft needs a callsign, type, position, and route.",
                "export": "Once you have aircraft and controllers set up, use 'Export Sweatbox' to save your scenario for ATC simulation.",
            }

            response = "I'm a simple chat bot. Please check the Help & Tips section for detailed guidance, or visit our documentation for more information."

            for keyword, resp in responses.items():
                if keyword.lower() in user_message.lower():
                    response = resp
                    break

            chat_text.config(state=tk.NORMAL)
            chat_text.insert(tk.END, f"Support Bot: {response}\n\n")
            chat_text.config(state=tk.DISABLED)
            chat_text.see(tk.END)

        send_btn = tk.Button(input_frame, text="Send", command=send_message,
                           bg=self.colors['primary'], fg='white',
                           font=(self.font_name, 9, 'bold'), padx=15)
        send_btn.pack(side=tk.RIGHT)

        # Bind Enter key to send
        input_entry.bind('<Return>', lambda e: send_message())

        # Initial welcome message
        chat_text.config(state=tk.NORMAL)
        chat_text.insert(tk.END, "Support Bot: Welcome to Sweatbox Creator support!\n\n")
        chat_text.insert(tk.END, "How can I help you today? You can ask about:\n")
        chat_text.insert(tk.END, "• Loading data files (SCT, ESE, RWY)\n")
        chat_text.insert(tk.END, "• Aircraft management\n")
        chat_text.insert(tk.END, "• Controller setup\n")
        chat_text.insert(tk.END, "• Exporting scenarios\n\n")
        chat_text.config(state=tk.DISABLED)

    def prompt_startup_controller_type(self):
        """Prompt user for controller type selection on startup"""
        import tkinter as tk
        from tkinter import simpledialog

        root = tk.Tk()
        root.withdraw()  # Hide the root window
        root.attributes('-topmost', True)  # Bring to front

        try:
            result = simpledialog.askstring(
                "Controller Type Selection",
                "Welcome to Sweatbox Creator!\n\nSelect your controller type:\n\nGND/DEL = Ground/Delivery\nTWR = Tower\nAPP/DEP = Approach/Departure\nCTR = Center\n\nEnter: GND/DEL, TWR, APP/DEP, or CTR",
                parent=root
            )
        finally:
            root.destroy()

        if result:
            result = result.upper().strip()
            if result in ['GND/DEL', 'TWR', 'APP/DEP', 'CTR']:
                messagebox.showinfo("Controller Type Selected",
                    f"You selected: {result}\n\n"
                    f"{'Note: ESE file will be loaded automatically for Approach/Departure controllers.' if result == 'APP/DEP' else ''}")

                # If APP/DEP selected, automatically load ESE file
                if result == 'APP/DEP':
                    self.load_ese_file()

                return result
            else:
                messagebox.showerror("Invalid Selection",
                    "Please enter GND/DEL, TWR, APP/DEP, or CTR")
                # Recursively prompt again
                return self.prompt_startup_controller_type()
        else:
            # User cancelled, default to GND/DEL
            messagebox.showinfo("Default Selection",
                "No selection made. Defaulting to Ground/Delivery (GND/DEL) controller.")
            return 'GND/DEL'

# For backward compatibility
SweatboxCreatorPage = HomePage
