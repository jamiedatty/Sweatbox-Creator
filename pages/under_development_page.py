import tkinter as tk
from tkinter import ttk

class UnderDevelopmentPage:
    def __init__(self, parent, controller_type, on_back_to_splash):
        self.parent = parent
        self.controller_type = controller_type
        self.on_back_to_splash = on_back_to_splash

        self.setup_ui()

    def setup_ui(self):
        # Main container
        self.main_container = tk.Frame(self.parent, bg='#e3f2fd')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header
        header_label = tk.Label(
            self.main_container,
            text=f"⚠️ {self.controller_type} Controller - Under Development",
            font=('Segoe UI', 24, 'bold'),
            fg='#f57c00',
            bg='#e3f2fd',
            justify='center'
        )
        header_label.pack(pady=(50, 20))

        # Description
        desc_label = tk.Label(
            self.main_container,
            text=f"The {self.controller_type} controller interface is currently under development.\n\n"
                 "This feature will be available in a future update. For now, you can use the\n"
                 "Approach/Departure (APP/DEP) controller which is fully functional.",
            font=('Segoe UI', 14),
            fg='#455a64',
            bg='#e3f2fd',
            justify='center'
        )
        desc_label.pack(pady=(0, 40))

        # Features list
        features_frame = tk.Frame(self.main_container, bg='#ffffff', relief='solid', borderwidth=1)
        features_frame.pack(pady=20, padx=40)

        features_title = tk.Label(
            features_frame,
            text="🚀 Coming Soon:",
            font=('Segoe UI', 16, 'bold'),
            fg='#1976d2',
            bg='#ffffff'
        )
        features_title.pack(pady=(20, 10))

        features = [
            "• Specialized interface for Ground/Delivery operations",
            "• Tower control position management",
            "• Center controller airspace visualization",
            "• Custom scenario templates",
            "• Advanced traffic management tools"
        ]

        for feature in features:
            feature_label = tk.Label(
                features_frame,
                text=feature,
                font=('Segoe UI', 12),
                fg='#455a64',
                bg='#ffffff',
                anchor='w'
            )
            feature_label.pack(fill=tk.X, padx=30, pady=2)

        # Buttons frame
        buttons_frame = tk.Frame(self.main_container, bg='#e3f2fd')
        buttons_frame.pack(pady=40)

        # Back button
        back_btn = tk.Button(
            buttons_frame,
            text="⬅️ Back to Controller Selection",
            command=self.on_back_to_splash,
            font=('Segoe UI', 12, 'bold'),
            bg='#1976d2',
            fg='white',
            relief='flat',
            padx=20,
            pady=12,
            activebackground='#1565c0'
        )
        back_btn.pack(side=tk.LEFT, padx=(0, 20))

        # Chat button
        chat_btn = tk.Button(
            buttons_frame,
            text="💬 Get Help & Support",
            command=self.open_chat,
            font=('Segoe UI', 12, 'bold'),
            bg='#03dac6',
            fg='white',
            relief='flat',
            padx=20,
            pady=12,
            activebackground='#00bfa5'
        )
        chat_btn.pack(side=tk.LEFT)

        # Footer
        footer_label = tk.Label(
            self.main_container,
            text="Thank you for your patience! Stay tuned for updates.",
            font=('Segoe UI', 10),
            fg='#78909c',
            bg='#e3f2fd'
        )
        footer_label.pack(side=tk.BOTTOM, pady=20)
