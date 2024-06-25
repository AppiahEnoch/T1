import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
from crud import get_db_connection
import pandas as pd
from tkinter import filedialog
import datetime
import subprocess
import json
import sqlite3
from fpdf import FPDF
import os
import sys
from terminal_report import generate_student_report, getStudentProgram
from ass import *
from GS import get_preferred_class

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)
REPORT_DIR = os.path.join(HOME_DIR, 'Documents', 'STUDENT_REPORT')

# Ensure the report directory exists
os.makedirs(REPORT_DIR, exist_ok=True)




def open_student_report_folder():
    if os.name == 'nt':  # For Windows
        os.startfile(REPORT_DIR)
    elif os.name == 'posix':  # For macOS and Linux
        subprocess.call(['open', REPORT_DIR]) if sys.platform == 'darwin' else subprocess.call(['xdg-open', REPORT_DIR])

def saveValues(**kwargs):
    HOME_DIR = os.path.expanduser('~')
    APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
    DATABASE_FILENAME = 'shs.db'
    DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)
    REPORT_DIR = APP_DIR
    
    # Ensure the report directory exists
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # Save JSON file to the report directory
    filename = os.path.join(REPORT_DIR, 'student_data.json')
    
    with open(filename, 'w') as json_file:
        json.dump(kwargs, json_file)

def getValues(key):
    HOME_DIR = os.path.expanduser('~')
    APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
    filename = os.path.join(APP_DIR, 'student_data.json')
    
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            return data.get(key, None)
    else:
        return None


def getStudentIds(year, semester_id, class_id, search_term=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT student_id 
        FROM assessment 
        WHERE year = ? AND semester_id = ? AND class_id = ?
    '''
    params = [year, semester_id, class_id]
    if search_term:
        query += ' AND (student_id LIKE ? OR name LIKE ?)'
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    cursor.execute(query, tuple(params))
    records = cursor.fetchall()
    conn.close()
    return [record["student_id"] for record in records]

class Report:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Report")
        root.attributes("-topmost", False)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 800
        window_height = 600
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
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

        ttk.Label(self.frame, text="Search Student:", font=label_font).grid(row=0, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        
        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", self.update_table_by_filters)
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var, width=50)
        self.search_entry.grid(row=0, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)

        ttk.Label(self.frame, text="Select Year:", font=label_font).grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.frame, textvariable=self.year_var, values=self.generate_years())
        self.year_select.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.year_select.bind("<<ComboboxSelected>>", self.update_table_by_filters)

        ttk.Label(self.frame, text="Select Class:", font=label_font).grid(row=2, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(self.frame, textvariable=self.class_var)
        self.class_select.grid(row=2, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.class_select.bind("<<ComboboxSelected>>", self.update_table_by_filters)
        self.populate_class_names()

        ttk.Label(self.frame, text="Select Semester:", font=label_font).grid(row=3, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.semester_var = ttk.StringVar()
        self.semester_select = ttk.Combobox(self.frame, textvariable=self.semester_var, values=["1", "2", "3"])
        self.semester_select.grid(row=3, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.semester_select.bind("<<ComboboxSelected>>", self.update_table_by_filters)

        self.terminal_button = ttk.Button(self.frame, text="Report", command=self.print_terminal_report, bootstyle="success")
        self.terminal_button.grid(row=4, column=0, padx=button_padding_x, pady=button_padding_y, sticky=ttk.W)

        self.button_frame = ttk.Frame(self.frame)
        self.button_frame.grid(row=4, column=1, padx=button_padding_x, pady=button_padding_y, sticky=ttk.W)

        self.transcript_button = ttk.Button(self.button_frame, text="Transcript", command=self.print_transcript, bootstyle="success")
        self.transcript_button.grid(row=0, column=0, padx=(0, 5))

        self.reset_button = ttk.Button(self.button_frame, text="Reset", command=self.reset_all_fields, bootstyle="success")
        self.reset_button.grid(row=0, column=1, padx=(5, 0))

        self.bulk_report_button = ttk.Button(self.frame, text="Bulk R", command=self.prepareBulkPrintTerminalData, bootstyle="success")
        self.bulk_report_button.grid(row=4, column=2, padx=button_padding_x, pady=button_padding_y, sticky=ttk.W)
        
        self.bulk_transcript_button = ttk.Button(self.frame, text="Bulk T", command=self.print_transcript, bootstyle="success")
        self.bulk_transcript_button.grid(row=4, column=3, padx=button_padding_x, pady=button_padding_y, sticky=ttk.W)

        columns = ["student_id", "name", "prog"]
        self.table = tkttk.Treeview(self.frame, columns=columns, show="headings")
        
        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=100, anchor=ttk.CENTER)

        self.table.grid(row=5, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_y = tkttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        scrollbar_y.grid(row=5, column=4, sticky='ns')
        scrollbar_x = tkttk.Scrollbar(self.frame, orient="horizontal", command=self.table.xview)
        scrollbar_x.grid(row=6, column=0, columnspan=4, sticky='ew')

        self.table.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        self.frame.grid_rowconfigure(5, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)

        self.table.bind('<ButtonRelease-1>', self.on_select)

        self.selected_student_id = None

        self.selected_student_label = ttk.Label(self.frame, text="", font=("Helvetica", 10), wraplength=400, justify=LEFT)
        self.selected_student_label.grid(row=1, column=2, padx=10, pady=5, sticky=ttk.W)

    def fetch_existing_data(self):
        conditions = []
        params = []

        if self.year_var.get():
            conditions.append("s.year = ?")
            params.append(self.year_var.get())
        if self.class_var.get():
            conditions.append("s.class_id = ?")
            params.append(self.class_names[self.class_var.get()])
        if self.semester_var.get():
            conditions.append("s.semester = ?")
            params.append(self.semester_var.get())
        if self.search_var.get():
            conditions.append("(s.student_id LIKE ? OR s.name LIKE ?)")
            params.extend([f'%{self.search_var.get()}%', f'%{self.search_var.get()}%'])

        query = f'''
            SELECT 
                s.student_id, 
                s.name, 
                s.gender,
                s.dateofbirth, 
                s.prog, 
                h.class_name AS house, 
                s.guardian_name, 
                s.mobile,
                s.email,
                s.guardian_title,
                s.postal_address,
                s.aggregate,
                s.denomination,
                s.status,
                s.year,
                c.class_name AS class_name
            FROM student s
            LEFT JOIN class_name c ON s.class_id = c.id
            LEFT JOIN class_name h ON s.house_id = h.id
            WHERE {' AND '.join(conditions)} 
        ''' if conditions else '''
            SELECT 
                s.student_id, 
                s.name, 
                s.gender,
                s.dateofbirth, 
                s.prog, 
                h.class_name AS house, 
                s.guardian_name, 
                s.mobile,
                s.email,
                s.guardian_title,
                s.postal_address,
                s.aggregate,
                s.denomination,
                s.status,
                s.year,
                c.class_name AS class_name
            FROM student s
            LEFT JOIN class_name c ON s.class_id = c.id
            LEFT JOIN class_name h ON s.house_id = h.id
        '''

        try:
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            self.table_data = cursor.fetchall()
            conn.close()

            for row in self.table.get_children():
                self.table.delete(row)

            for row in self.table_data:
                self.table.insert('', 'end', values=[
                    row['student_id'],
                    row['name'],
                    row['gender'] if row['gender'] is not None else 'None',
                    row['dateofbirth'] if row['dateofbirth'] is not None else 'None',
                    row['prog'] if row['prog'] is not None else 'None',
                    row['house'] if row['house'] is not None else 'None',
                    row['guardian_name'] if row['guardian_name'] is not None else 'None',
                    row['mobile'] if row['mobile'] is not None else 'None',
                    row['email'] if row['email'] is not None else 'None',
                    row['guardian_title'] if row['guardian_title'] is not None else 'None',
                    row['postal_address'] if row['postal_address'] is not None else 'None',
                    row['aggregate'] if row['aggregate'] is not None else 'None',
                    row['denomination'] if row['denomination'] is not None else 'None',
                    row['status'] if row['status'] is not None else 'None',
                    row['year'] if row['year'] is not None else 'None',
                    row['class_name'] if row['class_name'] is not None else 'None'
                ])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")


    def update_table_by_filters(self, *args):
        conditions = []
        params = []

        if self.year_var.get():
            conditions.append("a.year = ?")
            params.append(self.year_var.get())

        if self.class_var.get():
            conditions.append("a.class_id = ?")
            params.append(self.class_names[self.class_var.get()])

        if self.semester_var.get():
            conditions.append("a.semester_id = ?")
            params.append(int(self.semester_var.get()))

        if self.search_var.get():
            conditions.append("(s.student_id LIKE ? OR s.name LIKE ?)")
            params.extend([f'%{self.search_var.get()}%', f'%{self.search_var.get()}%'])

        query = f'''
            SELECT DISTINCT
                s.student_id, 
                s.name, 
                s.prog
            FROM assessment a
            JOIN student s ON a.student_id = s.student_id
            {f"WHERE {' AND '.join(conditions)}" if conditions else ""}
            ORDER BY s.student_id
        '''

        try:
            conn = get_db_connection()
            conn.row_factory = sqlite3.Row  # This enables column access by name: row['column_name']
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            self.table_data = cursor.fetchall()
            conn.close()

            for row in self.table.get_children():
                self.table.delete(row)

            for row in self.table_data:
                self.table.insert('', 'end', values=[
                    row['student_id'],
                    row['name'],
                    row['prog']
                ])

        except Exception as e:
            messagebox.showerror("Error", f"Failed to fetch data: {e}")
            




    def prepareBulkPrintTerminalData(self):
        if not self.year_var.get() or not self.semester_var.get() or not self.class_var.get():
            messagebox.showerror("Error", "Please select all fields.")
            return
        year = self.year_var.get()
        semester_id = self.semester_var.get()
        class_id = self.class_names[self.class_var.get()]
        search_term = self.search_var.get()

        student_ids = getStudentIds(year, semester_id, class_id, search_term)
        
        for student_id in student_ids:
            session_data = {
                'class_id': class_id,
                'semester_id': semester_id,
                'subject': getStudentProgram(student_id),
                'year': year,
                'student_id': student_id
            }
            saveValues(**session_data)
       
            generate_student_report(student_id)
            open_student_report_folder()
        
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
        self.update_table_by_filters()

    def update_table(self, keyword=""):
        for item in self.table.get_children():
            self.table.delete(item)

        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT student_id, name, prog FROM student WHERE (student_id LIKE ? OR name LIKE ?)"
        params = [f"%{keyword}%", f"%{keyword}%"]

        query += " ORDER BY name ASC"
        cursor.execute(query, tuple(params))
        for row in cursor.fetchall():
            self.table.insert("", "end", values=(row["student_id"], row["name"], row["prog"]))
        conn.close()

    def on_select(self, event):
        try:
            selected_items = self.table.selection()
            if not selected_items:
                raise IndexError("No item selected")
            
            item = selected_items[0]
            values = self.table.item(item, "values")
            self.selected_student_id = values[0]
            selected_student = f"Selected Student:\nName: {values[1]}\nID: {values[0]}\nSubject: {values[2]}"
            self.selected_student_label.config(text=selected_student)
        except IndexError as e:
            print(f"Error: {e}")
            self.selected_student_label.config(text="No student selected")

    def print_terminal_report(self):
        if not self.year_var.get() or not self.semester_var.get() or not self.class_var.get():
            messagebox.showerror("Error", "Please all fields are required.")
            return
        if self.selected_student_id:
            student_id = self.selected_student_id
            year = self.year_var.get()
            semester_id = self.semester_var.get()
            class_id = self.class_names[self.class_var.get()]
            subject = getStudentProgram(student_id)
            
            session_data = {
                'class_id': class_id,
                'semester_id': semester_id,
                'subject': subject,
                'year': year,
                'student_id': student_id
            }

            saveValues(**session_data)
            
            generate_student_report(student_id)
            open_student_report_folder()
        else:
            messagebox.showerror("Error", "No student selected.")

    def print_transcript(self):
        if self.selected_student_id:
            messagebox.showinfo("Transcript", f"Printing Transcript for Student ID: {self.selected_student_id}")
        else:
            messagebox.showerror("Error", "No student selected.")
                
    def reset_all_fields(self):
        self.search_var.set("")
        self.year_var.set("")
        self.semester_var.set("")
        self.class_var.set("")
        self.selected_student_id = None
        self.selected_student_label.config(text="")
        self.update_table()

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = Report(root)
    root.mainloop()
