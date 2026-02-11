#!/usr/bin/env python3
"""
Under Development Page for Sweatbox Creator
"""

import tkinter as tk
from tkinter import ttk

class UnderDevelopmentPage:
    def __init__(self, parent, controller_type, on_back_to_splash):
        self.parent = parent
        self.controller_type = controller_type
        self.on_back_to_splash = on_back_to_splash

        self.setup_ui()

    def setup_ui(self):
        # Main container with colorful background
        self.main_container = tk.Frame(self.parent, bg='#e3f2fd')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Header with orange warning color
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

        # Features list with white card
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

        # Back button with blue color
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

        # Chat button with teal color
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

    def open_chat(self):
        """Open a chat interface for user support"""
        chat_window = tk.Toplevel(self.parent)
        chat_window.title("Sweatbox Creator - Support Chat")
        chat_window.geometry("500x600")
        chat_window.transient(self.parent)
        chat_window.grab_set()

        # Chat display area
        chat_frame = tk.Frame(chat_window)
        chat_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        chat_text = tk.Text(chat_frame, wrap=tk.WORD, state=tk.DISABLED, font=('Segoe UI', 10), bg='#f8f9fa')
        chat_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        scrollbar = ttk.Scrollbar(chat_frame, command=chat_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        chat_text.config(yscrollcommand=scrollbar.set)

        # Input area
        input_frame = tk.Frame(chat_window)
        input_frame.pack(fill=tk.X, padx=10, pady=5)

        input_entry = tk.Entry(input_frame, font=('Segoe UI', 10))
        input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        def send_message():
            message = input_entry.get().strip()
            if message:
                chat_text.config(state=tk.NORMAL)
                chat_text.insert(tk.END, f"You: {message}\n")
                chat_text.config(state=tk.DISABLED)
                chat_text.see(tk.END)
                input_entry.delete(0, tk.END)
                chat_window.after(1000, lambda: show_bot_response(message))

        def show_bot_response(user_message):
            responses = {
                "help": "I'm here to help! You can ask me about:\n• Loading SCT/ESE files\n• Aircraft generation\n• Controller setup\n• Exporting scenarios",
                "sct": "SCT files contain sector data including airports, fixes, airways, and boundaries. Load them first to see the airspace structure.",
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

        send_btn = tk.Button(input_frame, text="Send", command=send_message, bg='#1976d2', fg='white', font=('Segoe UI', 9, 'bold'), padx=15)
        send_btn.pack(side=tk.RIGHT)

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
