#!/usr/bin/env python3
"""
Splash Page for Sweatbox Creator
"""

import tkinter as tk
from tkinter import ttk

class SplashPage:
    def __init__(self, parent, on_controller_selected):
        self.parent = parent
        self.on_controller_selected = on_controller_selected
        
        self.setup_ui()

    def setup_ui(self):
        # Main container with colorful background
        self.main_container = tk.Frame(self.parent, bg='#e3f2fd')
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Splash text with blue color
        splash_label = tk.Label(
            self.main_container,
            text="✈️ WELCOME TO SWEATBOX CREATOR\n\nProfessional ATC Scenario Builder",
            font=('Segoe UI', 24, 'bold'),
            fg='#0d47a1',
            bg='#e3f2fd',
            justify='center'
        )
        splash_label.pack(pady=(50, 30))

        subtitle_label = tk.Label(
            self.main_container,
            text="Select your controller type to get started:",
            font=('Segoe UI', 14),
            fg='#455a64',
            bg='#e3f2fd'
        )
        subtitle_label.pack(pady=(0, 40))

        # Button frame
        button_frame = tk.Frame(self.main_container, bg='#e3f2fd')
        button_frame.pack(pady=20)

        # Controller type buttons with blue styling
        button_configs = [
            ("GND/DEL", "Ground/Delivery Control"),
            ("TWR", "Tower Control"),
            ("APP/DEP", "Approach/Departure Control"),
            ("CTR", "Center Control")
        ]

        for controller_type, description in button_configs:
            btn = tk.Button(
                button_frame,
                text=f"{controller_type}\n{description}",
                font=('Segoe UI', 12, 'bold'),
                bg='#1976d2',
                fg='white',
                relief='flat',
                padx=20,
                pady=15,
                command=lambda ct=controller_type: self.on_controller_selected(ct)
            )
            btn.pack(side=tk.LEFT, padx=10)

        # Chat button and footer
        bottom_frame = tk.Frame(self.main_container, bg='#e3f2fd')
        bottom_frame.pack(side=tk.BOTTOM, pady=20)

        # Chat button with teal color
        chat_btn = tk.Button(
            bottom_frame,
            text="💬 Support Chat",
            command=self.open_chat,
            font=('Segoe UI', 10, 'bold'),
            bg='#03dac6',
            fg='white',
            relief='flat',
            padx=15,
            pady=8,
            activebackground='#00bfa5'
        )
        chat_btn.pack(side=tk.LEFT, padx=10)

        # Footer text
        footer_label = tk.Label(
            bottom_frame,
            text="Note: Only Approach/Departure control is fully implemented.\nOther controller types are under development.",
            font=('Segoe UI', 10),
            fg='#78909c',
            bg='#e3f2fd',
            justify='center'
        )
        footer_label.pack(side=tk.RIGHT, padx=10)

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
