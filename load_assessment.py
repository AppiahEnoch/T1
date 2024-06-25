import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter import ttk as tkttk
from tkinter import messagebox
import datetime
import sqlite3
import os
import pandas as pd
import re
from ass import *
import LCS
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

class LoadAssessment:
    def __init__(self, root):
        self.root = root
        self.root.title("Load Assessment")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 700
        window_height = 600

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        frame_padding = (20, 20)
        label_font = ("Helvetica", 12)
        entry_padding_x = 10
        entry_padding_y = 5
        button_padding_x = 10
        button_padding_y = 5
        button_frame_padding_y = 10

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)

        ttk.Label(self.frame, text="Select Year:", font=label_font).grid(row=0, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.frame, textvariable=self.year_var, values=self.generate_years())
        self.year_select.grid(row=0, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.year_select.config(justify="center")
        self.year_select.bind("<<ComboboxSelected>>", self.on_combobox_select)
        
        # CREATE A CONTAINER TO HOLD 3 SMALLER COMBOS, NUM1, PROG

        ttk.Label(self.frame, text="Select Class:", font=label_font).grid(row=0, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(self.frame, textvariable=self.class_var)
        self.class_select.grid(row=0, column=3, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.class_select.config(justify="center")
        self.class_select.bind("<<ComboboxSelected>>", self.on_combobox_select)

        self.populate_class_names()

        ttk.Label(self.frame, text="Subject:", font=label_font).grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.subject_var = ttk.StringVar()
        self.subject_select = ttk.Combobox(self.frame, textvariable=self.subject_var)
        self.subject_select.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.subject_select.config(justify="center")
        self.subject_select.bind("<<ComboboxSelected>>", self.on_combobox_select)

        self.populate_subject_names()

        ttk.Label(self.frame, text="Term/Semester:", font=label_font).grid(row=1, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.semester_var = ttk.StringVar()
        self.semester_select = ttk.Combobox(self.frame, textvariable=self.semester_var, values=["1", "2", "3"])
        self.semester_select.grid(row=1, column=3, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.semester_select.config(justify="center")
        self.semester_select.bind("<<ComboboxSelected>>", self.on_combobox_select)

        ttk.Label(self.frame, text="Teacher Initials:", font=label_font).grid(row=2, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.teacher_initial_letters_var = ttk.StringVar()
        self.teacher_initial_letters_entry = ttk.Entry(self.frame, textvariable=self.teacher_initial_letters_var, font=("Helvetica", 10))
        self.teacher_initial_letters_entry.grid(row=2, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        #SET DEFAULT VALUE
        self.teacher_initial_letters_var.set("ST")

        ttk.Label(self.frame, text="Upload File:", font=label_font).grid(row=2, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.upload_button = ttk.Button(self.frame, text="Browse", command=self.upload_file, bootstyle="info")
        self.upload_button.grid(row=2, column=3, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.file_path = ttk.StringVar()
        self.file_label = ttk.Label(self.frame, textvariable=self.file_path, font=("Helvetica", 10), anchor="center")
        self.file_label.grid(row=3, column=3, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.file_path.set("No file selected")
        self.file_label.config(justify="center")

        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=4, column=0, columnspan=4, pady=button_frame_padding_y)

        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.pack(side=LEFT, padx=button_padding_x)
        
        #ADD CALCULATE BUTTON
        self.calculate_button = ttk.Button(button_frame, text="Calculate", command=self.calculate, bootstyle="success")
        self.calculate_button.pack(side=LEFT, padx=button_padding_x)
        
        
        
        # add reset button
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.clear_all_fields_data, bootstyle="success")
        self.reset_button.pack(side=LEFT, padx=button_padding_x)
        

        self.delete_button = ttk.Button(button_frame, text="Delete", command=self.delete_records, bootstyle="danger")
        self.delete_button.pack(side=LEFT, padx=button_padding_x)
        
        self.export_button = ttk.Button(button_frame, text="Export To Excel", command=self.export_to_excel, bootstyle="success")
        self.export_button.pack(side=LEFT, padx=button_padding_x)
        #button SET CLASS
        self.clear_button = ttk.Button(button_frame, text="Set Class", command=self.open_set_class_window, bootstyle="success")
        self.clear_button.pack(side=LEFT, padx=button_padding_x)
        

        columns = ("student_id", "name", "class", "subject", "class_score", "exam_score", "teacher_initial_letters")
        self.table = tkttk.Treeview(self.frame, columns=columns, show="headings")

        vsb = tkttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        hsb = tkttk.Scrollbar(self.frame, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.table.grid(row=5, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")
        vsb.grid(row=5, column=4, sticky="ns")
        hsb.grid(row=6, column=0, columnspan=4, sticky="ew")

        self.frame.grid_rowconfigure(5, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        
    def clear_all_fields_data(self):
        self.year_var.set('')
        self.class_var.set('')
        self.subject_var.set('')
        self.semester_var.set('')
        self.teacher_initial_letters_var.set('ST')
        self.file_path.set('No file selected')
        self.table_data = []
        self.populate_table_from_excel()
        
    def open_set_class_window(self):
        new_window = ttk.Toplevel(self.root)
        SetClass(new_window)
     
        
        
    def calculate(self):
        run_in_thread(compute_and_store_assessments())
        run_in_thread(LCS.update_student_programme())
        # show message box
        messagebox.showinfo("Success", "Assessment and other Records  Calculated Successfully")
        
        
    def getProgrammeIDFromClassName(self, class_name):
        conn = get_db_connection()
        cursor = conn.cursor()
        match = re.match(r"^\d+\s(.+)$", class_name)
        if match:
            matching_programme = match.group(1)
        else:
            matching_programme = ""
        
        cursor.execute('SELECT id FROM programme WHERE programme_name = ?', (matching_programme,))
        row = cursor.fetchone()
        conn.close()
        return row['id'] if row else None

    def generate_years(self):
        current_year = datetime.datetime.now().year
        start_year = 1991
        end_year = current_year + 1
        return [f"{year}/{year + 1}" for year in range(end_year, start_year - 1, -1)]

    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx;*.xls")])
        self.root.update_idletasks()
        if file_path:
            shortened_path = file_path
            if len(file_path) > 50:
                shortened_path = file_path[:10] + "..." + file_path[-20:]
            self.file_path.set(shortened_path)
            self.load_excel_data(file_path)

    def load_excel_data(self, file_path):
        try:
            df = pd.read_excel(file_path)
            required_columns = ["Name of Student", "Student ID", "Class Score", "Exam Score"]
            if not all(column in df.columns for column in required_columns):
                raise ValueError("Invalid file format. Please upload an Excel file with the correct format.")

            # Fill NaN values in scores with 0
            df["Class Score"] = df["Class Score"].fillna(0)
            df["Exam Score"] = df["Exam Score"].fillna(0)

            # Filter out rows where "Name of Student" or "Student ID" are NaN, null, or empty
            df = df.dropna(subset=["Name of Student", "Student ID"])
            df = df[df["Name of Student"].astype(bool) & df["Student ID"].astype(bool)]

            self.table_data = df.to_dict('records')
            self.populate_table_from_excel()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load Excel file: {e}")

   
    def export_to_excel(self):
        try:
            formatted_data = [
                {
                    'Name of Student': row[1],
                    'Student ID': row[0],
                    'Class Score': row[4],
                    'Exam Score': row[5]
                }
                for row in self.table_data
            ]
            
            df = pd.DataFrame(formatted_data)
            file_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])
            if file_path:
                with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')
                    
                    workbook = writer.book
                    worksheet = writer.sheets['Sheet1']
                    
                    header_format = workbook.add_format({'bold': True})
                    for col_num, value in enumerate(df.columns.values):
                        worksheet.write(0, col_num, value, header_format)
                    
                    worksheet.set_column(0, 0, 30)
                    worksheet.set_column(1, 1, 15)
                    worksheet.set_column(2, 2, 15)
                    worksheet.set_column(3, 3, 15)

                    messagebox.showinfo("Success", "Data exported successfully")
        except Exception as e:
            print(e)
            messagebox.showerror("Error", f"Failed to export data: {e}")

    def populate_table_from_excel(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for row in self.table_data:
            student_id = row["Student ID"]
            student_name = row["Name of Student"]
            class_name = row["Class"] if "Class" in row else self.class_var.get()
            subject_name = row["subject"] if "subject" in row else self.subject_var.get()
            class_score = row["Class Score"]
            exam_score = row["Exam Score"]
            teacher_initial_letters = self.teacher_initial_letters_var.get()

            self.table.insert("", "end", values=(
                student_id, 
                student_name, 
                class_name, 
                subject_name, 
                class_score, 
                exam_score,
                teacher_initial_letters
            ))

    def fetch_existing_data(self):
        #print(self.year_var.get())
        conditions = []
        params = []

        if self.year_var.get():
            conditions.append("a.year = ?")
            params.append(self.year_var.get())
        if self.class_var.get():
            conditions.append("a.class_id = ?")
            params.append(self.class_names[self.class_var.get()])
            self.update_subject_suggestions()
        if self.subject_var.get():
            conditions.append("a.subject_id = ?")
            params.append(self.subject_names[self.subject_var.get()])
            self.update_class_name_suggestions()
        if self.semester_var.get():
            conditions.append("a.semester_id = ?")
            params.append(self.semester_var.get())

        if conditions:
            query = f'''
                SELECT a.student_id, s.name AS student_name, c.class_name, p.subject_name, a.class_score, a.exam_score, a.teacher_initial_letters, a.programme_id
                FROM assessment a
                LEFT JOIN class_name c ON a.class_id = c.id
                LEFT JOIN subject p ON a.subject_id = p.id
                LEFT JOIN student s ON a.student_id = s.student_id
                WHERE {' AND '.join(conditions)}
            '''
            try:
                conn = get_db_connection()
                conn.execute('PRAGMA foreign_keys = ON')  # Ensure foreign keys are enabled
                conn.execute('PRAGMA synchronous = OFF')  # Speed up by not waiting for data to be written to disk
                conn.execute('PRAGMA journal_mode = MEMORY')  # Use memory for journal to speed up
                conn.execute('PRAGMA temp_store = MEMORY')  # Store temporary tables in memory
                conn.execute('PRAGMA optimize')  # Run PRAGMA optimize to optimize the database

                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                self.table_data = cursor.fetchall()
                conn.close()
                self.populate_table_from_db()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to fetch data: {e}")
        else:
            messagebox.showwarning("Input Error", "Please select at least one field.")
            self.table_data = []
            self.populate_table_from_db()

    
    def populate_table_from_db(self):
        for item in self.table.get_children():
            self.table.delete(item)

        for row in self.table_data:
            self.table.insert("", "end", values=(
                row["student_id"], 
                row["student_name"], 
                row["class_name"], 
                row["subject_name"], 
                row["class_score"], 
                row["exam_score"],
                row["teacher_initial_letters"]
            ))

    def delete_records(self):
        if not (self.year_var.get() and self.class_var.get() and self.subject_var.get() and self.semester_var.get()):
            messagebox.showwarning("Input Error", "Please select Year, Class, subject, and Semester to delete records.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete all records for the selected Year, Class, subject, and Semester?"):
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('''
                    DELETE FROM assessment
                    WHERE year = ? AND class_id = ? AND subject_id = ? AND semester_id = ?
                ''', (self.year_var.get(), self.class_names[self.class_var.get()], self.subject_names[self.subject_var.get()], self.semester_var.get()))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Records deleted successfully")
                self.fetch_existing_data()
            
                compute_and_store_assessments()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete records: {e}")

    def submit(self):
        try:
        
            conn = get_db_connection()
            cursor = conn.cursor()
                #CHECK  class_name, subject_name, semester_id, year, class_score, exam_score, teacher_initial_letters
            if not (self.year_var.get() and self.class_var.get() and self.subject_var.get() and self.semester_var.get() and self.teacher_initial_letters_var.get()):
                messagebox.showwarning("Input Error", "Please select Year, Class, subject, Semester, and Teacher Initials.")
                return
            
            for row in self.table_data:
                programme_id = self.getProgrammeIDFromClassName(self.class_var.get())
                cursor.execute('''
                    INSERT INTO assessment (student_id, semester_id, programme_id, subject_id, class_id, year, class_score, exam_score, teacher_initial_letters)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, semester_id, subject_id, class_id)
                    DO UPDATE SET class_score=excluded.class_score, exam_score=excluded.exam_score, teacher_initial_letters=excluded.teacher_initial_letters
                ''', (row["Student ID"], self.semester_var.get(), programme_id, self.subject_names[self.subject_var.get()], self.class_names[self.class_var.get()], self.year_var.get(), row["Class Score"], row["Exam Score"], self.teacher_initial_letters_var.get()))
            
            conn.commit()
            
            for row in self.table_data:
                student_id = row["Student ID"]
                name = row["Name of Student"]
                year = self.year_var.get()
                class_id = self.class_names[self.class_var.get()]
                
                cursor.execute('''
                    INSERT INTO student (student_id, name, year, class_id)
                    VALUES (?, ?, ?, ?)
                    ON CONFLICT(student_id) DO NOTHING
                ''', (student_id, name, year, class_id))
                
                # Check if student exists
                cursor.execute('SELECT student_id FROM student WHERE student_id = ?', (student_id,))
                existing_student = cursor.fetchone()
                
                if existing_student:
                    update_fields = []
                    update_values = []
                    
                    if name:
                        update_fields.append('name = ?')
                        update_values.append(name)
                    
                    if year:
                        update_fields.append('year = ?')
                        update_values.append(year)
                    
                    if class_id:
                        update_fields.append('class_id = ?')
                        update_values.append(class_id)
                    
                    if update_fields:
                        update_values.append(student_id)
                        cursor.execute(f'''
                            UPDATE student
                            SET {', '.join(update_fields)}
                            WHERE student_id = ?
                        ''', update_values)

            conn.commit()
          

            messagebox.showinfo("Success", "Data submitted successfully")
           
            
         
           
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to submit data: {e}")
        finally:
            conn.close()
            self.file_path.set("No file selected")

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


    def populate_subject_names(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject_name FROM subject")
        self.subject_names = {row["subject_name"]: row["id"] for row in cursor.fetchall()}
        conn.close()
        self.subject_select["values"] = list(self.subject_names.keys())
        
        
    def update_subject_suggestions(self):
        selected_class = self.class_select.get()
        #print(selected_class)
        if selected_class in self.class_names:
            class_id = self.class_names[selected_class]
            subjects = LCS.get_subjects_by_class_id(class_id)
            #clear subject suggestions
            self.subject_select["values"] = []
            
            subject_names = [subject[0] for subject in subjects]
            self.subject_select["values"] = subject_names
            
    def update_class_name_suggestions(self):
        selected_subject = self.subject_select.get()
        if selected_subject:
            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT id 
                FROM subject 
                WHERE subject_name = ?
            ''', (selected_subject,))

            row = cursor.fetchone()
            subject_id = row['id'] if row else None

            if subject_id:
                classes = LCS.get_classes_by_subject_id(subject_id)
                class_names = [class_item[0] for class_item in classes]
                
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

            conn.close()



    def on_combobox_select(self, event):
        self.fetch_existing_data()

if __name__ == "__main__":
    from create_table import initialize_database
    initialize_database()

    root = ttk.Window("Load Assessment", "darkly", resizable=(False, False))
    app = LoadAssessment(root)
    #always on top true
    root.attributes("-topmost", False)
    root.mainloop()
