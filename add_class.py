import sqlite3
import os
import ttkbootstrap as ttk
import CPS

from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import tkinter as tk  # Import the base tkinter module

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

def create_programme_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create programme table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS programme (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            programme_name VARCHAR(255) UNIQUE
        )
    ''')
    
    conn.commit()
    conn.close()

def insert_programme_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    programme_names = [
        "General Science",
        "Business",
        "General Arts",
        "Visual Arts",
        "Home Economics",
        "Agricultural Science",
        "Technical"
    ]
    
    for name in programme_names:
        cursor.execute('''
            INSERT OR IGNORE INTO programme (programme_name)
            VALUES (?)
        ''', (name,))
    
    conn.commit()
    conn.close()

def update_programme_column():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, class_name FROM class_name')
    rows = cursor.fetchall()
    for row in rows:
        class_name = row[1]
        parts = class_name.split(' ')
        if len(parts) > 2:
            programme = ' '.join(parts[1:])
            cursor.execute('UPDATE class_name SET programme = ? WHERE id = ?', (programme, row[0]))
        elif len(parts) == 2:
            programme = parts[1]
            cursor.execute('UPDATE class_name SET programme = ? WHERE id = ?', (programme, row[0]))
    conn.commit()
    conn.close()

class AddClass:
    def __init__(self, root):
        self.root = root
        self.root.title("Add Class")
        root.attributes("-topmost", False)

        # Calculate screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate window position to center it on the screen
        window_width = 600
        window_height = 600
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
        self.title_label = ttk.Label(self.inner_frame, text="Add New Class", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Year number selection
        ttk.Label(self.inner_frame, text="Select Year Number:", font=label_font).grid(row=1, column=0, padx=2, pady=entry_padding_y, sticky=ttk.E)
        self.year_var = ttk.StringVar()
        self.year_combobox = ttk.Combobox(self.inner_frame, textvariable=self.year_var, values=[1, 2, 3, 4, 5], width=28)
        self.year_combobox.grid(row=1, column=1, padx=15, pady=entry_padding_y)

        # Programme selection
        ttk.Label(self.inner_frame, text="Select Programme:", font=label_font).grid(row=2, column=0, padx=2, pady=entry_padding_y, sticky=ttk.E)
        self.programme_var = ttk.StringVar()
        self.programme_combobox = ttk.Combobox(self.inner_frame, textvariable=self.programme_var, width=28)
        self.programme_combobox.grid(row=2, column=1, padx=15, pady=entry_padding_y)
        self.load_programme_options()

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
        columns = ("class_name", "delete")
        self.table_frame = ttk.Frame(self.frame)
        self.table_frame.pack(fill=ttk.BOTH, expand=ttk.TRUE, pady=10)
        
        table_container = ttk.Frame(self.table_frame)
        table_container.pack(fill=ttk.BOTH, expand=ttk.TRUE)
        
        self.table = tkttk.Treeview(table_container, columns=columns, show="headings", style="Custom.Treeview")
        self.table.heading("class_name", text="Classes Available")
        self.table.heading("delete", text="")

        self.table.column("class_name", width=300, anchor=ttk.CENTER)
        self.table.column("delete", width=50, anchor=ttk.CENTER)

        self.table.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.TRUE, padx=entry_padding_x, pady=entry_padding_y)

        # Scrollbar for the table
        scrollbar = tkttk.Scrollbar(table_container, orient="vertical", command=self.table.yview, bootstyle="primary")
        self.table.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Initial data
        self.update_table()

    def load_programme_options(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT programme_name FROM programme ORDER BY programme_name ASC")
        programmes = [row["programme_name"] for row in cursor.fetchall()]
        self.programme_combobox['values'] = programmes
        conn.close()

    def submit(self):
        year_number = self.year_var.get()
        programme_name = self.programme_var.get()
        #CHECK YEAR AND PROGRAMME NAME ARE NOT EMPTY
        if year_number == "" or programme_name == "":
            messagebox.showerror("Error", "Please select a year number and programme name!")
            return
      
        if year_number and programme_name:
            class_name = f"{year_number} {programme_name}"
            self.insert_update_table('class_name', 'class_name', ['class_name'], [class_name])
            self.update_table()
            #self.class_number_var.set("")
            CPS.insert_class_programme_subject()

    def update_table(self):
        # Clear the table
        for item in self.table.get_children():
            self.table.delete(item)

        # Insert new data from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM class_name ORDER BY programme DESC")
        for row in cursor.fetchall():
            self.table.insert("", "end", values=(row["class_name"], "Delete"))
        conn.close()

        # Add delete button functionality
        self.table.bind('<ButtonRelease-1>', self.on_delete)

    def on_delete(self, event):
        item = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        if item and column == '#2':  # The 'delete' column is at index 1 (2nd column)
            class_name = self.table.item(item, "values")[0]
            if messagebox.askyesno("Delete", f"Are you sure you want to delete '{class_name}'?"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM class_name WHERE class_name = ?", (class_name,))
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
        update_programme_column()
        messagebox.showinfo("Success", "Class added successfully!")

if __name__ == "__main__":
    create_programme_table()
    insert_programme_names()
    
    root = ttk.Window(themename="darkly")
    app = AddClass(root)
    root.mainloop()
