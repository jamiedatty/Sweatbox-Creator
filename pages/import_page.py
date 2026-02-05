"""
Import Page Module
Placeholder page for future import functionality
"""
import tkinter as tk

class ImportPage:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root, bg='#f0f0f0')
        self.frame.pack(fill='both', expand=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        # Main container
        main_container = tk.Frame(self.frame, bg='#f0f0f0')
        main_container.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            main_container,
            text="Import",
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0',
            fg='#2c3e50'
        )
        title_label.pack(pady=50)
        
        # Unavailable message
        message_label = tk.Label(
            main_container,
            text="Import functionality is currently unavailable",
            font=('Arial', 14),
            bg='#f0f0f0',
            fg='#666666'
        )
        message_label.pack(pady=10)
        
        # Additional info
        info_label = tk.Label(
            main_container,
            text="This feature will be available in a future update",
            font=('Arial', 12),
            bg='#f0f0f0',
            fg='#888888'
        )
        info_label.pack(pady=5)
        
        # Back button
        back_button = tk.Button(
            main_container,
            text="← Back to Home",
            font=('Arial', 12),
            bg='#3498db',
            fg='white',
            padx=20,
            pady=10,
            cursor='hand2',
            command=self.go_back
        )
        back_button.pack(pady=30)
        
        # Placeholder for future features
        placeholder_frame = tk.Frame(main_container, bg='#f8f9fa', relief='solid', borderwidth=1)
        placeholder_frame.pack(pady=20, padx=40, fill='x')
        
        tk.Label(
            placeholder_frame,
            text="Planned Import Features:",
            font=('Arial', 11, 'bold'),
            bg='#f8f9fa'
        ).pack(pady=(10, 5))
        
        features = [
            "• Import multiple file formats (SCT, ESE, OpenAir, etc.)",
            "• Batch processing of sector files",
            "• Data conversion between formats",
            "• Merge multiple sector files",
            "• Import real-time data feeds"
        ]
        
        for feature in features:
            tk.Label(
                placeholder_frame,
                text=feature,
                font=('Arial', 10),
                bg='#f8f9fa',
                anchor='w',
                justify='left'
            ).pack(fill='x', padx=20, pady=2)
    
    def go_back(self):
        """Return to home page"""
        # Import here to avoid circular import
        from pages.home_page import HomePage
        self.frame.destroy()
        HomePage(self.root)