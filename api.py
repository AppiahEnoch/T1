import sqlite3
import os
import ttkbootstrap as ttk

from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import tkinter as tk

# Use os.path.expanduser to get the path to the user's home directory
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Enable access by column name
    return conn

def create_api_key_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create api_key table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS api_key (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key_name VARCHAR(255) UNIQUE,
            api_key TEXT,
            recdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    

class AddApiKey:
    def __init__(self, root):
        self.root = root
        self.root.title("Add API Key")
        root.attributes("-topmost", False)

        # Calculate screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate window position to center it on the screen
        window_width = 700
        window_height = 400
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2

        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        
        # Resize the window false
        self.root.resizable(False, False)

        # Padding and font size variables
        frame_padding = (20, 20)
        label_font = ("Helvetica", 12)
        entry_padding_x = 10
        entry_padding_y = 5
        button_padding_x = 10
        button_padding_y = 5
        button_frame_padding_y = 10

        # Frame setup
        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=ttk.BOTH, expand=ttk.TRUE)

        # Inner frame for centering
        self.inner_frame = ttk.Frame(self.frame)
        self.inner_frame.pack(expand=True)

        # Add label at the top
        self.title_label = ttk.Label(self.inner_frame, text="Add New API Key", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Key name entry
        ttk.Label(self.inner_frame, text="Enter Key Name:", font=label_font).grid(row=1, column=0, padx=2, pady=entry_padding_y, sticky=ttk.E)
        self.key_name_var = ttk.StringVar()
        self.key_name_entry = ttk.Entry(self.inner_frame, textvariable=self.key_name_var, width=60)
        self.key_name_entry.grid(row=1, column=1, padx=15, pady=entry_padding_y)

        # API key entry
        ttk.Label(self.inner_frame, text="Enter API Key:", font=label_font).grid(row=2, column=0, padx=2, pady=entry_padding_y, sticky=ttk.E)
        self.api_key_var = ttk.StringVar()
        self.api_key_entry = ttk.Entry(self.inner_frame, textvariable=self.api_key_var, width=60)
        self.api_key_entry.grid(row=2, column=1, padx=15, pady=entry_padding_y)

        # Submit button
        self.submit_button = ttk.Button(self.inner_frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.grid(row=3, column=0, columnspan=2, pady=button_frame_padding_y)

        # Table style
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25, font=("Helvetica", 10), bordercolor="gray", borderwidth=1)
        style.map('Custom.Treeview', background=[('selected', 'blue')])
        style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 12, "bold"), background="lightgray", foreground="black")

        # Table setup
        columns = ("key_name", "api_key", "delete")
        self.table_frame = ttk.Frame(self.frame)
        self.table_frame.pack(fill=ttk.BOTH, expand=ttk.TRUE, pady=10)
        
        table_container = ttk.Frame(self.table_frame)
        table_container.pack(fill=ttk.BOTH, expand=ttk.TRUE)
        
        self.table = tkttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
        self.table.heading("key_name", text="Key Name")
        self.table.heading("api_key", text="API Key")
        self.table.heading("delete", text="")

        self.table.column("key_name", width=200, anchor=ttk.CENTER)
        self.table.column("api_key", width=300, anchor=ttk.CENTER)
        self.table.column("delete", width=50, anchor=ttk.CENTER)

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE, padx=entry_padding_x, pady=entry_padding_y)

        # Scrollbar for the table
        scrollbar = tkttk.Scrollbar(table_container, orient="vertical", command=self.table.yview, bootstyle="primary")
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initial data
        self.update_table()
        
    

    def submit(self):
        key_name = self.key_name_var.get()
        api_key = self.api_key_var.get()
        if key_name == "" or api_key == "":
            messagebox.showerror("Error", "Please enter both key name and API key!")
            return
      
        if key_name and api_key:
            self.insert_update_table('api_key', 'key_name', ['key_name', 'api_key'], [key_name, api_key])
            self.update_table()
            messagebox.showinfo("Success", "API key added successfully!")

    def update_table(self):
        # Clear the table
        for item in self.table.get_children():
            self.table.delete(item)

        # Insert new data from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM api_key ORDER BY recdate DESC")
        for row in cursor.fetchall():
            self.table.insert("", "end", values=(row["key_name"], row["api_key"], "Delete"))
        conn.close()

        # Add delete button functionality
        self.table.bind('<ButtonRelease-1>', self.on_delete)

    def on_delete(self, event):
        item = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        if item and column == '#3':  # The 'delete' column is at index 2 (3rd column)
            key_name = self.table.item(item, "values")[0]
            if messagebox.askyesno("Delete", f"Are you sure you want to delete the API key for '{key_name}'?"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM api_key WHERE key_name = ?", (key_name,))
                conn.commit()
                conn.close()
                self.update_table()

    def insert_update_table(self, table, unique_col, cols, values):
        conn = get_db_connection()
        cursor = conn.cursor()
        
        placeholders = ', '.join(['?'] * len(values))
        update_placeholders = ', '.join([f"{col}=excluded.{col}" for col in cols])
        
        cursor.execute(f'''
            INSERT INTO {table} ({', '.join(cols)})
            VALUES ({placeholders})
            ON CONFLICT({unique_col}) DO UPDATE SET {update_placeholders}
        ''', values)
        
        conn.commit()
        conn.close()

if __name__ == "__main__":
    create_api_key_table()
    
    root = ttk.Window(themename="darkly")
    app = AddApiKey(root)
    root.mainloop()
