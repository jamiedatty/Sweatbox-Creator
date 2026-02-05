import tkinter as tk

class HomePage:
    def __init__(self, root):
        self.root = root
        self.frame = tk.Frame(root, bg='#f0f0f0')
        self.frame.pack(fill='both', expand=True)
        
        self.setup_ui()
    
    def setup_ui(self):
        title_label = tk.Label(
            self.frame, 
            text="ESE File Viewer", 
            font=('Arial', 24, 'bold'),
            bg='#f0f0f0'
        )
        title_label.pack(pady=50)
        
        button_frame = tk.Frame(self.frame, bg='#f0f0f0')
        button_frame.pack(expand=True)
        
        create_btn = tk.Button(
            button_frame,
            text="Create",
            font=('Arial', 16),
            width=15,
            height=2,
            bg='#4CAF50',
            fg='white',
            cursor='hand2',
            command=self.open_create_page
        )
        create_btn.pack(pady=10)
        
        import_btn = tk.Button(
            button_frame,
            text="Import",
            font=('Arial', 16),
            width=15,
            height=2,
            bg='#2196F3',
            fg='white',
            cursor='hand2',
            command=self.open_import_page
        )
        import_btn.pack(pady=10)
    
    def open_create_page(self):
        # Import here to avoid circular import
        from pages.create_page import CreatePage
        self.frame.destroy()
        CreatePage(self.root)
    
    def open_import_page(self):
        # Import here to avoid circular import
        from pages.import_page import ImportPage
        self.frame.destroy()
        ImportPage(self.root)