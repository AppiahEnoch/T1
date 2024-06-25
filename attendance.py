import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import sqlite3
import os
from datetime import datetime
import openpyxl
from tkinter import filedialog

import pandas as pd


# Constants for directory and database
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# def drop_table():
#     conn = get_db_connection()
#     cursor = conn.cursor()
#     cursor.execute('DROP TABLE IF EXISTS attendance')
#     conn.commit()
#     conn.close()

# drop_table()

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_id INTEGER NOT NULL,
            semester TEXT NOT NULL,
            year TEXT NOT NULL,
            attendance_value INTEGER NOT NULL,
            max_attendance_value INTEGER NOT NULL,
            UNIQUE(student_id, class_id, semester, year),
            FOREIGN KEY (student_id) REFERENCES student (student_id)
        )
    ''')

    conn.commit()
    conn.close()

# Create directories if they do not exist
os.makedirs(APP_DIR, exist_ok=True)

# Initialize the database
initialize_database()

class Attendance:
    def __init__(self, root):
        self.root = root
        self.root.title("Attendance Entry")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        frame_padding = (20, 20)
        label_font = ("Helvetica", 12)
        entry_padding_x = 10
        entry_padding_y = 5
        button_padding_x = 10
        button_padding_y = 5
        button_frame_padding_y = 10

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)

        # Search bar
        ttk.Label(self.frame, text="Search Student:", font=label_font).grid(row=0, column=0, padx=2, pady=entry_padding_y, sticky=W)
        self.search_var = ttk.StringVar()
        self.search_var.trace_add("write", self.search)
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var, width=50)
        self.search_entry.grid(row=0, column=1, padx=15, pady=entry_padding_y, sticky=W)

        # Year selection
        ttk.Label(self.frame, text="Select Year:", font=label_font).grid(row=1, column=0, padx=2, pady=entry_padding_y, sticky=W)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.frame, textvariable=self.year_var, values=self.generate_years())
        self.year_select.grid(row=1, column=1, padx=15, pady=entry_padding_y, sticky=W)
        self.year_select.config(justify="center")
        self.year_select.bind("<<ComboboxSelected>>", self.check_existing_record)

        # Class and Semester selection
        ttk.Label(self.frame, text="Select Class:", font=label_font).grid(row=2, column=0, padx=2, pady=entry_padding_y, sticky=W)
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(self.frame, textvariable=self.class_var)
        self.class_select.grid(row=2, column=1, padx=15, pady=entry_padding_y, sticky=W)
        self.class_select.config(justify="center")
        self.class_select.bind("<<ComboboxSelected>>", self.check_existing_record)
        self.populate_class_names()

        ttk.Label(self.frame, text="Select Semester:", font=label_font).grid(row=2, column=2, padx=2, pady=entry_padding_y, sticky=W)
        self.semester_var = ttk.StringVar()
        self.semester_select = ttk.Combobox(self.frame, textvariable=self.semester_var, values=["1", "2", "3"])
        self.semester_select.grid(row=2, column=3, padx=15, pady=entry_padding_y, sticky=W)
        self.semester_select.config(justify="center")
        self.semester_select.bind("<<ComboboxSelected>>", self.check_existing_record)

        # Attendance fields
        ttk.Label(self.frame, text="Enter Attendance Value:", font=label_font).grid(row=3, column=0, padx=2, pady=entry_padding_y, sticky=W)
        self.attendance_var = ttk.StringVar()
        self.attendance_entry = ttk.Entry(self.frame, textvariable=self.attendance_var, width=20)
        self.attendance_entry.grid(row=3, column=1, padx=15, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="Enter Max Attendance Value:", font=label_font).grid(row=3, column=2, padx=2, pady=entry_padding_y, sticky=W)
        self.max_attendance_var = ttk.StringVar()
        self.max_attendance_entry = ttk.Entry(self.frame, textvariable=self.max_attendance_var, width=20)
        self.max_attendance_entry.grid(row=3, column=3, padx=15, pady=entry_padding_y, sticky=W)

        # Submit and Reset buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=button_frame_padding_y)

        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.pack(side=LEFT, padx=button_padding_x)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset, bootstyle="secondary")
        self.reset_button.pack(side=LEFT, padx=button_padding_x)

        # Table for search results
        columns = ["student_id", "name", "programme", "attendance_value", "max_attendance_value"]
        self.table = tkttk.Treeview(self.frame, columns=columns, show="headings")
        
        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=150, anchor=CENTER)

        self.table.grid(row=5, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_y = tkttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        scrollbar_y.grid(row=5, column=4, sticky='ns')
        self.table.configure(yscroll=scrollbar_y.set)

        self.frame.grid_rowconfigure(5, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)

        self.populate_class_names()
        
        # add browse button to choose excel file
        
        ttk.Label(self.frame, text="Upload File:", font=label_font).grid(row=2, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.upload_button = ttk.Button(self.frame, text="Browse", bootstyle="info", command=self.upload_file)
        self.upload_button.grid(row=6, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.file_path = ttk.StringVar()
        self.file_label = ttk.Label(self.frame, textvariable=self.file_path, font=("Helvetica", 10), anchor="center")
        self.file_label.grid(row=6, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.file_path.set("No file selected")
        self.file_label.config(justify="center")
        
        self.export_button = ttk.Button(self.frame, text="Export To Excel", command=self.export_to_excel, bootstyle="warning")
        self.export_button.grid(row=6, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        
        
  
        
        
        
            
    def export_to_excel(self):
        try:
            # Collect data from the table
            table_data = []
            for row_id in self.table.get_children():
                row = self.table.item(row_id)['values']
                table_data.append({
                    'Student ID': row[0],
                    'Name': row[1],
                    'Programme': row[2],
                    'Attendance Value': row[3],
                    'Max Attendance Value': row[4]
                })

            df = pd.DataFrame(table_data)
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']
                    
                    header_format = workbook.add_format({'bold': True})
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    worksheet.set_column(0, 0, 15)
                    worksheet.set_column(1, 1, 30)
                    worksheet.set_column(2, 2, 20)
                    worksheet.set_column(3, 3, 20)
                    worksheet.set_column(4, 4, 20)

                messagebox.showinfo("Success", "Data exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data: {e}")

    def upload_file(self):
        class_name = self.class_var.get()
        semester = self.semester_var.get()
        year = self.year_var.get()

        if not class_name or not semester or not year:
            messagebox.showwarning("Input Error", "Please select Class, Semester, and Year before uploading.")
            return

        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        if file_path:
            shortened_path = file_path
            if len(file_path) > 10:
                shortened_path = file_path[:3] + "..." + file_path[-10:]
            self.file_path.set(shortened_path)
            self.load_excel_data(file_path, class_name, semester, year)

    def load_excel_data(self, file_path, class_name, semester, year):
        try:
            df = pd.read_excel(file_path)
            required_columns = ["Student ID", "Name", "Programme", "Attendance Value", "Max Attendance Value"]
            if not all(column in df.columns for column in required_columns):
                raise ValueError("Invalid file format. Please upload an Excel file with the correct format.")

            df["Attendance Value"] = df["Attendance Value"].fillna(0)
            df["Max Attendance Value"] = df["Max Attendance Value"].fillna(0)

            class_id = self.class_id_map.get(class_name)
            if not class_id:
                raise ValueError("Class name not found")

            conn = get_db_connection()
            cursor = conn.cursor()

            for _, row in df.iterrows():
                student_id = row["Student ID"]
                attendance_value = row["Attendance Value"]
                max_attendance_value = row["Max Attendance Value"]

                cursor.execute('''
                    INSERT INTO attendance (student_id, class_id, semester, year, attendance_value, max_attendance_value)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, class_id, semester, year)
                    DO UPDATE SET attendance_value = excluded.attendance_value, max_attendance_value = excluded.max_attendance_value
                ''', (student_id, class_id, semester, year, attendance_value, max_attendance_value))

            conn.commit()
            conn.close()

            self.table_data = df.to_dict('records')
            self.populate_table_from_excel()
            messagebox.showinfo("Success", "Excel data loaded and attendance records updated successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file: {e}")

    def populate_table_from_excel(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for row in self.table_data:
            self.table.insert("", "end", values=(
                row["Student ID"], row["Name"], row["Programme"],
                row["Attendance Value"], row["Max Attendance Value"]
            ))

  
        
        

    def generate_years(self):
        current_year = datetime.now().year
        start_year = 1991
        end_year = current_year + 1
        return [f"{year}/{year + 1}" for year in range(end_year, start_year - 1, -1)]

    def populate_class_names(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, class_name FROM class_name ORDER BY class_name ASC")
        classes = cursor.fetchall()
        conn.close()
        self.class_select['values'] = [cls['class_name'] for cls in classes]
        self.class_id_map = {cls['class_name']: cls['id'] for cls in classes}

    def search(self, *args):
        keyword = self.search_var.get()
        class_name = self.class_var.get()
        semester = self.semester_var.get()
        year = self.year_var.get()

        if keyword:
            class_id = self.class_id_map.get(class_name, None)
            conn = get_db_connection()
            cursor = conn.cursor()
            
            query = '''
                SELECT s.student_id, s.name, s.prog
                FROM student s
                WHERE s.student_id LIKE ? OR s.name LIKE ?
                ORDER BY s.name ASC
            '''
            cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
            student_results = cursor.fetchall()

            student_ids = [row['student_id'] for row in student_results]
            attendance_values = {}
            
            if student_ids:
                placeholders = ', '.join('?' for _ in student_ids)
                attendance_query = f'''
                    SELECT student_id, attendance_value, max_attendance_value
                    FROM attendance
                    WHERE student_id IN ({placeholders})
                '''
                params = student_ids
                if class_id:
                    attendance_query += ' AND class_id = ?'
                    params.append(class_id)
                if semester:
                    attendance_query += ' AND semester = ?'
                    params.append(semester)
                if year:
                    attendance_query += ' AND year = ?'
                    params.append(year)

                cursor.execute(attendance_query, params)
                attendance_results = cursor.fetchall()

                for row in attendance_results:
                    attendance_values[row['student_id']] = {
                        'attendance_value': row['attendance_value'],
                        'max_attendance_value': row['max_attendance_value']
                    }

            results = []
            for student in student_results:
                student_id = student['student_id']
                attendance_value = attendance_values.get(student_id, {}).get('attendance_value', 0)
                max_attendance_value = attendance_values.get(student_id, {}).get('max_attendance_value', 0)
                results.append({
                    'student_id': student_id,
                    'name': student['name'],
                    'prog': student['prog'],
                    'attendance_value': attendance_value,
                    'max_attendance_value': max_attendance_value
                })

            conn.close()
            self.update_table(results)
        else:
            self.update_table([])

    def update_table(self, results):
        for item in self.table.get_children():
            self.table.delete(item)

        for row in results:
            self.table.insert("", "end", values=(
                row["student_id"], row["name"], row["prog"], 
                row["attendance_value"], row["max_attendance_value"]
            ))

        self.table.bind('<ButtonRelease-1>', self.on_select)

    def on_select(self, event):
        selected_item = self.table.selection()[0]
        values = self.table.item(selected_item, "values")
        self.selected_student_id = values[0]
        self.attendance_var.set(values[3] if values[3] else "")
        self.max_attendance_var.set(values[4] if values[4] else "")

    def check_existing_record(self, event=None):
        if not hasattr(self, "selected_student_id"):
            return

        class_name = self.class_var.get()
        semester = self.semester_var.get()
        year = self.year_var.get()

        query = '''
            SELECT attendance_value, max_attendance_value
            FROM attendance
            WHERE student_id = ?
        '''
        params = [self.selected_student_id]

        if class_name:
            class_id = self.class_id_map.get(class_name)
            query += ' AND class_id = ?'
            params.append(class_id)
        if semester:
            query += ' AND semester = ?'
            params.append(semester)
        if year:
            query += ' AND year = ?'
            params.append(year)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(query, params)
        record = cursor.fetchone()
        conn.close()

        if record:
            self.attendance_var.set(record["attendance_value"])
            self.max_attendance_var.set(record["max_attendance_value"])
        else:
            self.attendance_var.set(0)
            self.max_attendance_var.set(0)

        self.search()



    def submit(self):
        if not hasattr(self, "selected_student_id"):
            messagebox.showwarning("Input Error", "Please select a student from the search results.")
            return

        class_name = self.class_var.get()
        semester = self.semester_var.get()
        year = self.year_var.get()
        attendance = self.attendance_var.get()
        max_attendance = self.max_attendance_var.get()
        #check max attendance is not less than attendance
        if int(max_attendance) < int(attendance):
            messagebox.showwarning("Input Error", "Max Attendance Value cannot be less than Attendance Value.")
            return

        if not class_name or not semester or not year or not attendance or not max_attendance:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        if class_name in self.class_id_map:
            class_id = self.class_id_map[class_name]
        else:
            messagebox.showerror("Error", "Class name not found")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO attendance (student_id, class_id, semester, year, attendance_value, max_attendance_value)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, class_id, semester, year)
                DO UPDATE SET attendance_value = excluded.attendance_value, max_attendance_value = excluded.max_attendance_value
            ''', (self.selected_student_id, class_id, semester, year, attendance, max_attendance))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Attendance entry added/updated successfully")
            self.search()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add/update attendance entry: {e}")

    def reset(self):
        self.search_var.set("")
        self.class_var.set("")
        self.semester_var.set("")
        self.year_var.set("")
        self.attendance_var.set("")
        self.max_attendance_var.set("")
        self.update_table([])

if __name__ == "__main__":
    root = ttk.Window("Attendance Entry", "superhero")
    app = Attendance(root)
    root.mainloop()
