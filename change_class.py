import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from crud import *
import os
import pandas as pd
import sqlite3
import student2
from dateutil.parser import parse
from GS import get_preferred_class
import datetime

class ChangeStudentClass:
    def __init__(self, root):
        self.root = root
        self.root.title("Change Student Class")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        frame_padding = (20, 20)
        label_font = ("Helvetica", 12)
        entry_padding_x = 10
        entry_padding_y = 5
        button_padding_x = 10
        button_padding_y = 5
        button_frame_padding_y = 10

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=ttk.BOTH, expand=ttk.TRUE)

        # Search Student
        ttk.Label(self.frame, text="Search Student:", font=label_font).grid(
            row=0, column=0, padx=2, pady=entry_padding_y, sticky=ttk.W
        )
        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", self.search)
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var, width=40)
        self.search_entry.grid(row=1, column=0, columnspan=2, padx=15, pady=entry_padding_y, sticky=ttk.W)

        # Select Year
        ttk.Label(self.frame, text="Select Year:", font=label_font).grid(
            row=0, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W
        )
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.frame, textvariable=self.year_var, values=self.generate_years())
        self.year_select.grid(row=1, column=2, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.year_select.config(justify="center")

        # Select Semester
        ttk.Label(self.frame, text="Select Semester:", font=label_font).grid(
            row=2, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W
        )
        self.semester_var = ttk.StringVar()
        self.semester_select = ttk.Combobox(self.frame, textvariable=self.semester_var, values=["1", "2"])
        self.semester_select.grid(row=3, column=0, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.semester_select.config(justify="center")

        # Select Class
        ttk.Label(self.frame, text="Select Class:", font=label_font).grid(
            row=2, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W
        )
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(self.frame, textvariable=self.class_var)
        self.class_select.grid(row=3, column=2, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.class_select.config(justify="center")
        self.populate_class_names()

        # Student ID and Name
        ttk.Label(self.frame, text="Student ID:", font=label_font).grid(
            row=4, column=0, padx=2, pady=entry_padding_y, sticky=ttk.W
        )
        self.student_id_var = ttk.StringVar()
        self.student_id_entry = ttk.Entry(self.frame, textvariable=self.student_id_var, width=40)
        self.student_id_entry.grid(row=5, column=0, columnspan=2, padx=15, pady=entry_padding_y, sticky=ttk.W)

        ttk.Label(self.frame, text="Name:", font=label_font).grid(
            row=4, column=2, padx=2, pady=entry_padding_y, sticky=ttk.W
        )
        self.name_var = ttk.StringVar()
        self.name_label = ttk.Label(self.frame, textvariable=self.name_var, font=label_font)
        self.name_label.grid(row=5, column=2, columnspan=2, padx=15, pady=entry_padding_y, sticky=ttk.W)

        # Table
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25, font=("Helvetica", 10), bordercolor="gray", borderwidth=1)
        style.map('Custom.Treeview', background=[('selected', 'blue')])
        style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 12, "bold"), background="lightgray", foreground="black")

        self.table = ttk.Treeview(self.frame, columns=["student_id", "name"], show="headings", style="Custom.Treeview")
        self.table.heading("student_id", text="Student ID")
        self.table.heading("name", text="Name")
        self.table.column("student_id", width=200, anchor=ttk.CENTER)
        self.table.column("name", width=400, anchor=ttk.CENTER)
        self.table.grid(row=6, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        scrollbar_y.grid(row=6, column=4, sticky='ns')
        self.table.configure(yscroll=scrollbar_y.set)

        self.table.bind('<ButtonRelease-1>', self.on_select)

        # Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=7, column=0, columnspan=4, pady=button_frame_padding_y, sticky=ttk.EW)

        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.pack(side=ttk.LEFT, padx=button_padding_x)

    def generate_years(self):
        current_year = datetime.datetime.now().year
        start_year = 1991
        end_year = current_year + 1
        return [f"{year}/{year + 1}" for year in range(end_year, start_year - 1, -1)]

    def populate_class_names(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, class_name FROM class_name")
        self.class_names = {row["class_name"]: row["id"] for row in cursor.fetchall()}
        conn.close()
        
        class_names = list(self.class_names.keys())

        # Get the preferred class filter
        preferred_class = get_preferred_class()

        if preferred_class:
            # Filter class names that match the preferred class pattern
            filtered_class_names = [
                class_name for class_name in class_names 
                if preferred_class.lower() in class_name.lower()
            ]
            self.class_select["values"] = filtered_class_names
        else:
            self.class_select["values"] = class_names

    def search(self, *args):
        keyword = self.search_var.get()
        self.update_table(keyword)

    def update_table(self, keyword=""):
        for item in self.table.get_children():
            self.table.delete(item)

        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT student_id, name FROM student 
            WHERE student_id LIKE ? OR name LIKE ?
            ORDER BY name ASC
        """
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
        for row in cursor.fetchall():
            self.table.insert("", "end", values=(row["student_id"], row["name"]))
        conn.close()

    def on_select(self, event):
        item = self.table.selection()[0]
        values = self.table.item(item, "values")
        self.student_id_var.set(values[0])
        self.name_var.set(values[1])

    def submit(self):
        student_id = self.student_id_var.get()
        class_name = self.class_var.get()
        year = self.year_var.get()
        semester = self.semester_var.get()

        if student_id and class_name and year and semester:
            new_class_id = self.class_names[class_name]
            conn = get_db_connection()
            cursor = conn.cursor()
            print("student_id", student_id)
            print("new_class_id", new_class_id)
            print("year", year)
            print("semester", semester)
            print("class_name", class_name)
       
            
            try:
                # Get the current class_id for the student
                cursor.execute("SELECT class_id FROM student WHERE student_id = ?", (student_id,))
                current_class_id = cursor.fetchone()["class_id"]

                # Update student's class_id
                cursor.execute("UPDATE student SET class_id = ? WHERE student_id = ?", (new_class_id, student_id))
                
                # Delete records from assessment table only if the new class_id is different
                if new_class_id != current_class_id:
                    # cursor.execute("""
                    #     DELETE FROM assessment 
                    #     WHERE student_id = ? AND class_id = ? AND semester_id = ? AND year = ?
                    # """, (student_id, current_class_id, semester, year))
                    

                    
                    message = "Class updated and assessment records deleted successfully"
                else:
                    message = "Class updated successfully (no assessment records deleted)"
                
                conn.commit()
                messagebox.showinfo("Success", message)
            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("Error", f"An error occurred: {str(e)}")
            finally:
                conn.close()
        else:
            messagebox.showerror("Error", "Please fill in all fields")

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = ChangeStudentClass(root)
    root.mainloop()