import sqlite3
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import tkinter as tk
import datetime

import AE
from THREAD import *
from set_class import SetClass
from GS import get_preferred_class


HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def delete_all_from_computed_assessment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM computed_assessment')
    conn.commit()
    conn.close()


class DeleteAllClassRecord:
    def __init__(self, root):
        self.root = root
        self.root.title("Delete All Class Record")
        root.attributes("-topmost", False)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 600
        window_height = 450
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        self.root.resizable(False, False)

        # Frame setup
        self.frame = ttk.Frame(self.root, padding=(20, 20))
        self.frame.pack(fill=ttk.BOTH, expand=ttk.TRUE)

        # Inner frame for centering
        self.inner_frame = ttk.Frame(self.frame)
        self.inner_frame.pack(expand=True)

        # Add title label
        self.title_label = ttk.Label(self.inner_frame, text="Delete All Class Records", font=("Helvetica", 16, "bold"))
        self.title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Year selection
        ttk.Label(self.inner_frame, text="Select Year:", font=("Helvetica", 12)).grid(row=1, column=0, padx=2, pady=5, sticky=ttk.E)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.inner_frame, textvariable=self.year_var, values=AE.generate_years(), width=28)
        self.year_select.grid(row=1, column=1, padx=15, pady=5, sticky=ttk.W)
        self.year_select.bind("<<ComboboxSelected>>", self.update_class_options)

        # Class selection
        ttk.Label(self.inner_frame, text="Select Class:", font=("Helvetica", 12)).grid(row=2, column=0, padx=2, pady=5, sticky=ttk.E)
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(self.inner_frame, textvariable=self.class_var, width=28)
        self.class_select.grid(row=2, column=1, padx=15, pady=5, sticky=ttk.W)
        self.populate_class_names()

        # Delete button
        self.delete_button = ttk.Button(self.inner_frame, text="Delete Records", command=self.delete_records, bootstyle="danger")
        self.delete_button.grid(row=3, column=0, columnspan=2, pady=20)

        # Status label
        self.status_label = ttk.Label(self.inner_frame, text="", font=("Helvetica", 10))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=10)



    def populate_class_names(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, class_name FROM class_name")
        self.class_names = {row["class_name"]: row["id"] for row in cursor.fetchall()}
        conn.close()
        
        class_names = list(self.class_names.keys())

        preferred_class = get_preferred_class()

        if preferred_class:
            filtered_class_names = [
                class_name for class_name in class_names 
                if preferred_class.lower() in class_name.lower()
            ]
            self.class_select["values"] = filtered_class_names
        else:
            self.class_select["values"] = class_names

    def update_class_options(self, event=None):
        selected_year = self.year_var.get()
        if selected_year:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT cn.class_name 
                FROM assessment a 
                JOIN class_name cn ON a.class_id = cn.id 
                WHERE a.year = ?
            """, (selected_year,))
            available_classes = [row["class_name"] for row in cursor.fetchall()]
            conn.close()
            self.class_select["values"] = available_classes
        else:
            self.class_select["values"] = list(self.class_names.keys())

    def delete_records(self):
        selected_year = self.year_var.get()
        selected_class = self.class_var.get()
        if not selected_year or not selected_class:
            messagebox.showerror("Error", "Please select both a year and a class!")
            return

        if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete all records for '{selected_class}' in {selected_year}?\nThis action cannot be undone!"):
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                # Get the class_id for the selected class
                class_id = self.class_names[selected_class]

                # Delete records from the assessment table
                cursor.execute("DELETE FROM assessment WHERE class_id = ? AND year = ?", (class_id, selected_year))
                deleted_count = cursor.rowcount

                conn.commit()
                self.status_label.config(text=f"Successfully deleted {deleted_count} records for {selected_class} in {selected_year}.")
            except sqlite3.Error as e:
                conn.rollback()
                self.status_label.config(text=f"Error: {str(e)}")
            finally:
                delete_all_from_computed_assessment()
                conn.close()

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = DeleteAllClassRecord(root)
    root.mainloop()