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

def fetch_programmes_subjects():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ps.id AS programme_subject_id, p.id AS programme_id, p.programme_name, s.id AS subject_id, s.subject_name 
        FROM programme_subject ps 
        JOIN programme p ON ps.programme_id = p.id 
        JOIN subject s ON ps.subject_id = s.id
    ''')
    data = cursor.fetchall()
    conn.close()
    return data

class ProgrammeSubjectApp(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill=tk.BOTH, expand=tk.TRUE)
        self.create_widgets()

    def create_widgets(self):
        self.canvas = tk.Canvas(self)
        self.scrollbar = tkttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = ttk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            )
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)  # Bind mouse wheel for Windows
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)    # Bind mouse wheel for Linux
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)    # Bind mouse wheel for Linux

        self.populate_tables()

    def populate_tables(self):
        data = fetch_programmes_subjects()
        programmes = {}

        for row in data:
            programme = row["programme_name"]
            programme_id = row["programme_id"]
            subject = row["subject_name"]
            subject_id = row["subject_id"]
            programme_subject_id = row["programme_subject_id"]

            if programme not in programmes:
                frame = ttk.LabelFrame(self.scrollable_frame, text=programme, padding=(10, 5))
                frame.pack(fill="x", expand=True, padx=10, pady=5)
                tree = tkttk.Treeview(frame, columns=("Subject", "Action"), show="headings")
                tree.heading("Subject", text="Subject")
                tree.heading("Action", text="Action")
                tree.column("Action", width=100, anchor="center")  # Set Action column width and center alignment
                tree.pack(fill=tk.BOTH, expand=tk.TRUE, padx=20, pady=10)  # Centering the table by padding
                programmes[programme] = (tree, programme_id)

            tree, programme_id = programmes[programme]
            tree.insert("", "end", values=(subject, "Delete"), tags=(programme_subject_id, programme_id, subject_id))

        for programme, (tree, programme_id) in programmes.items():
            tree.bind("<Button-1>", self.on_tree_click)

    def on_tree_click(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if item:
            column = tree.identify_column(event.x)
            if column == "#2":  # Action column
                self.delete_subject(tree, item)

    def delete_subject(self, tree, item):
        row = tree.item(item, "values")
        programme_subject_id = tree.item(item, "tags")[0]
        subject = row[0]
        programme_id = tree.item(item, "tags")[1]
        subject_id = tree.item(item, "tags")[2]

        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{subject}'?"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM programme_subject 
                WHERE id = ?
            ''', (programme_subject_id,))
            conn.commit()
            conn.close()
            tree.delete(item)

    def on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    window_width = 400
    window_height = 600
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    position_top = int(screen_height/2 - window_height/2)
    position_right = int(screen_width/2 - window_width/2)
    root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")  # Set the initial window size and center it
    ProgrammeSubjectApp(root).pack(fill=tk.BOTH, expand=tk.TRUE)
    root.mainloop()