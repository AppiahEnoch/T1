import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
from crud import *
import os
from datetime import datetime
import pandas as pd
from tkinter import filedialog
from dateutil.parser import parse
import sqlite3
import pandas as pd
import datetime
import GS
import student2
from dateutil.parser import parse

import os
import pandas as pd
import subprocess
from dateutil.parser import parse
import db
from GS import get_preferred_class
import multiprocessing
import LCS
class SafeMultiprocessingUpdate:
    def __init__(self):
        self.process = None
        self.lock = multiprocessing.Lock()

    def start_update_process(self):
        with self.lock:
            if self.process is None or not self.process.is_alive():
                self.process = multiprocessing.Process(target=self.update_student_house)
                self.process.start()
            else:
                print("Update process is already running.")

    def update_student_house(self):
        # This method should contain the original GS.update_student_house logic
        pass

# Assuming GS is a global instance of SafeMultiprocessingUpdate
GS1 = SafeMultiprocessingUpdate()


class Student:
    def __init__(self, root):
        GS1.update_student_house()
      
        self.root = root
        self.root.title("Student Management")
        root.attributes("-topmost", False)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 800
        window_height = 700
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
        self.year_select.bind("<<ComboboxSelected>>", self.on_combobox_select)

        # Select Class
        ttk.Label(self.frame, text="Select Class:", font=label_font).grid(
            row=2, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W
        )
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(self.frame, textvariable=self.class_var)
        self.class_select.grid(row=3, column=2, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)
        self.class_select.config(justify="center")
        self.class_select.bind("<<ComboboxSelected>>", self.on_combobox_select)

        self.populate_class_names()

        left_labels = [
            "Student ID", "Name", "Mobile", "Email", "Date of Birth"
        ]
        right_labels = [
            "House", "Guardian", "Programme", 
        ]

        self.entries = {}

        for idx, label in enumerate(left_labels, start=2):
            ttk.Label(self.frame, text=f"{label}:", font=label_font).grid(
                row=(idx-2) * 2 + 2, column=0, padx=2, pady=entry_padding_y, sticky=ttk.W, columnspan=2
            )
            if label == "Date of Birth":
                self.date_of_birth = ttk.DateEntry(self.frame, width=60, bootstyle="info")
                self.date_of_birth.grid(row=((idx-2) * 2) + 3, column=0, columnspan=2, padx=15, pady=entry_padding_y, sticky=ttk.W)
                self.entries[label] = self.date_of_birth
            else:
                var = ttk.StringVar()
                entry = ttk.Entry(self.frame, textvariable=var, width=60)
                entry.grid(row=((idx-2) * 2) + 3, column=0, columnspan=2, padx=15, pady=entry_padding_y, sticky=ttk.W)
                self.entries[label] = var

        for idx, label in enumerate(right_labels, start=2):
            ttk.Label(self.frame, text=f"{label}:", font=label_font).grid(
                row=(idx-2) * 2 + 4, column=2, padx=2, pady=entry_padding_y, sticky=ttk.W, columnspan=2
            )
            if label == "House":
                self.house_var = ttk.StringVar()
                self.house_combobox = ttk.Combobox(self.frame, textvariable=self.house_var, width=60)
                self.house_combobox.grid(row=((idx-2) * 2) + 5, column=2, columnspan=2, padx=15, pady=entry_padding_y, sticky=ttk.W)
                self.entries[label] = self.house_combobox
                self.load_houses()
            else:
                var = ttk.StringVar()
                entry = ttk.Entry(self.frame, textvariable=var, width=60)
                entry.grid(row=((idx-2) * 2) + 5, column=2, columnspan=2, padx=15, pady=entry_padding_y, sticky=ttk.W)
                self.entries[label] = var

        # Select Gender
        ttk.Label(self.frame, text="Select Gender:", font=label_font).grid(
            row=10, column=2, padx=2, pady=entry_padding_y, sticky=ttk.W, columnspan=2
        )
        self.gender_var = ttk.StringVar()
        self.gender_select = ttk.Combobox(self.frame, textvariable=self.gender_var, values=["Male", "Female"], width=60)
        self.gender_select.grid(row=11, column=2, columnspan=2, padx=15, pady=entry_padding_y, sticky=ttk.W)
        self.entries["Gender"] = self.gender_var

        # Buttons
        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=12, column=0, columnspan=6, pady=button_frame_padding_y, sticky=ttk.EW)

        self.submit_button = ttk.Button(button_frame, text="Update", command=self.submit, bootstyle="success")
        self.submit_button.pack(side=ttk.LEFT, padx=button_padding_x)

        self.export_button = ttk.Button(button_frame, text="Export Details", bootstyle="success", command=self.export_table)
        self.export_button.pack(side=ttk.LEFT, padx=button_padding_x)
        
        #export for assessemnt
        self.export_button = ttk.Button(button_frame, text="Export for Assessment", bootstyle="success", command=self.export_for_assessment)
        self.export_button.pack(side=ttk.LEFT, padx=button_padding_x)

        self.upload_button = ttk.Button(button_frame, text="Upload Excel File", bootstyle="success", command=self.upload_excel_file)
        self.upload_button.pack(side=ttk.LEFT, padx=button_padding_x)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_fields, bootstyle="secondary")
        self.reset_button.pack(side=ttk.LEFT, padx=button_padding_x)
        
        self.reset_button = ttk.Button(button_frame, text="More", command=self.openStudentDetails, bootstyle="secondary")
        self.reset_button.pack(side=ttk.LEFT, padx=button_padding_x)

        # Table
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25, font=("Helvetica", 10), bordercolor="gray", borderwidth=1)
        style.map('Custom.Treeview', background=[('selected', 'blue')])
        style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 12, "bold"), background="lightgray", foreground="black")

        columns = [
            "student_id", "name", "gender", "dateofbirth", "prog", "house", "guardian_name", 
            "mobile", "email", "guardian_title", "postal_address", "aggregate", "denomination", 
            "status", "year", "class"
        ]
        self.table = ttk.Treeview(self.frame, columns=columns, show="headings", style="Custom.Treeview")

        for col in columns:
            self.table.heading(col, text=col.replace("_", " ").title())
            self.table.column(col, width=100, anchor=ttk.CENTER)

        # Hide the email and guardian_title columns
        self.table.column("email", width=0, stretch=ttk.NO)
        self.table.column("guardian_title", width=0, stretch=ttk.NO)

        self.table.grid(row=14, column=0, columnspan=6, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_y = ttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        scrollbar_y.grid(row=14, column=6, sticky='ns')
        scrollbar_x = ttk.Scrollbar(self.frame, orient="horizontal", command=self.table.xview)
        scrollbar_x.grid(row=15, column=0, columnspan=6, sticky='ew')

        self.table.configure(yscroll=scrollbar_y.set, xscroll=scrollbar_x.set)

        self.frame.grid_rowconfigure(14, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_columnconfigure(4, weight=1)
        self.frame.grid_columnconfigure(5, weight=1)

        self.update_table()

    def on_combobox_select(self, event):
        #reset all values 
        self.reset_fields2()
        
        self.fetch_existing_data()
        
    def fetch_existing_data(self):
        conditions = []
        params = []

        if self.year_var.get():
            conditions.append("s.year = ?")
            params.append(self.year_var.get())
        if self.class_var.get():
            conditions.append("s.class_id = ?")
            params.append(self.class_names[self.class_var.get()])
        if self.gender_var.get():
            conditions.append("s.gender = ?")
            params.append(self.gender_var.get())

        query = f'''
            SELECT 
                s.student_id, 
                s.name, 
                s.gender,
                s.dateofbirth, 
                s.prog, 
                h.house_name AS house, 
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
            LEFT JOIN house h ON s.house_id = h.id
          
            WHERE {' AND '.join(conditions)} 
        ''' if conditions else '''
            SELECT 
                s.student_id, 
                s.name, 
                s.gender,
                s.dateofbirth, 
                s.prog, 
                h.house_name AS house, 
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
            LEFT JOIN house h ON s.house_id = h.id
           
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


    def load_houses(self):
        """Load house names into the combobox."""
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, house_name FROM house ORDER BY house_name ASC")
        houses = cursor.fetchall()
        conn.close()
        self.house_combobox['values'] = [house['house_name']
                                         for house in houses]
        self.house_id_map = {house['house_name']: house['id'] for house in houses}

    def search(self, *args):
        keyword = self.search_var.get()
        self.update_table(keyword)
        
        
    def update_table(self, keyword=""):
        # Clear the table
        for item in self.table.get_children():
            self.table.delete(item)

        # Insert new data from database based on search keyword
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
            SELECT 
                s.student_id, s.name, s.gender, s.dateofbirth, s.prog, 
                h.house_name, s.guardian_name, s.mobile, s.email, s.guardian_title, 
                s.postal_address, s.aggregate, s.denomination, s.status, s.year, 
                c.class_name as class_name
            FROM student s
            LEFT JOIN class_name c ON s.class_id = c.id
            LEFT JOIN house h ON s.house_id = h.id
            WHERE s.student_id LIKE ? OR s.name LIKE ?
            ORDER BY s.name ASC
        """
        cursor.execute(query, (f"%{keyword}%", f"%{keyword}%"))
        for row in cursor.fetchall():
            self.table.insert("", "end", values=(
                row["student_id"], row["name"], row["gender"], row["dateofbirth"], row["prog"], row["house_name"], 
                row["guardian_name"], row["mobile"], row["email"], row["guardian_title"], row["postal_address"], 
                row["aggregate"], row["denomination"], row["status"], row["year"], row["class_name"]
            ))
        conn.close()

        # Add selection functionality
        self.table.bind('<ButtonRelease-1>', self.on_select)



    def submit(self):
        student_id = self.entries["Student ID"].get()

        if student_id:
            house_name = self.house_var.get()
            if house_name in self.house_id_map:
                house_id = self.house_id_map[house_name]
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE student
                    SET name = ?, mobile = ?, email = ?, dateofbirth = ?, house_id = ?, guardian_name = ?, prog = ?, gender = ?
                    WHERE student_id = ?
                """, (
                    self.entries["Name"].get(), self.entries["Mobile"].get(),
                    self.entries["Email"].get(), self.date_of_birth.entry.get(), house_id,
                    self.entries["Guardian"].get(), self.entries["Programme"].get(),
                    self.gender_var.get(), student_id
                ))
                conn.commit()
                conn.close()
                self.update_table()
                LCS.update_student_boarding_and_house()
                
                messagebox.showinfo("Success", "Student details updated successfully")
            else:
                messagebox.showerror("Error", "House name not found")
        else:
            messagebox.showerror("Error", "Student ID is required")


    def on_select(self, event):
            item = self.table.selection()[0]
            values = self.table.item(item, "values")
            labels = ["Student ID", "Name", "Gender", "Date of Birth", "Programme", "House", "Guardian", "Mobile"]
            
            for label, value in zip(labels, values):
                if label == "Date of Birth":
                    print(value)
                else:
                    entry_widget = self.entries.get(label)
                    if entry_widget:
                        if label == "House":
                            # Check if the house value is None or not in the house_id_map
                            if value is None or value not in self.house_id_map:
                                # Set to the first house option if not valid
                                first_house = next(iter(self.house_id_map))
                                value = first_house
                                house_id = self.house_id_map[first_house]
                            else:
                                house_id = self.house_id_map[value]
                            
                            self.house_combobox.set(value)
                            continue
                        entry_widget.set(value)
            
            student_id = values[0]
            GS.saveValues(student_id=student_id)

            house_name = values[5]  # Assuming house is the 6th value in the tuple
            if house_name is None or house_name not in self.house_id_map:
                first_house = next(iter(self.house_id_map))
                house_name = first_house
            self.house_var.set(house_name)
            

    def reset_fields(self):
        self.year_var.set('')
        self.class_var.set('')

        for entry in self.entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, ttk.END)
            elif isinstance(entry, ttk.StringVar):
                entry.set('')
            elif isinstance(entry, ttk.Combobox):
                entry.set('')
            elif isinstance(entry, ttk.Text):
                entry.delete('1.0', ttk.END)
            elif isinstance(entry, ttk.DateEntry):
                entry.entry.delete(0, ttk.END)
                
                #load all student data to table
        self.update_table()
        
    def reset_fields2(self):
        # Only reset the fields in self.entries, skipping year and class select fields
        for entry in self.entries.values():
            if isinstance(entry, ttk.Entry):
                entry.delete(0, ttk.END)
            elif isinstance(entry, ttk.StringVar):
                entry.set('')
            elif isinstance(entry, ttk.Text):
                entry.delete('1.0', ttk.END)
            elif isinstance(entry, ttk.DateEntry):
                entry.entry.delete(0, ttk.END)
        
        # Load all student data to table
        self.update_table()
                
  
    def openStudentDetails(self):
        ps_view_window = ttk.Toplevel(self.root)
        ps_view_window.title("EDIT STUDENT DATA")
        ps_view_window.geometry("400x600")
        
        # Center the window on the screen
        screen_width = ps_view_window.winfo_screenwidth()
        screen_height = ps_view_window.winfo_screenheight()
        window_width = 400
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        ps_view_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        student2.Student2(ps_view_window)

     
        
        
    def export_table(self):
        try:
            # Fetch data currently displayed in the table
            table_data = [self.table.item(item, 'values') for item in self.table.get_children()]

            columns = [
                'Id', 'Name', 'Gender', 'Dateofbirth', 'Programme', 'House', 'Guardian', 'Mobile', 'Email', 
                'GuardianTitle', 'PostalAddress', 'Aggregate', 'Denomination', 'Status', 'Year', 'ClassName'
            ]

            # Create a DataFrame with the current table data or an empty DataFrame with the specified columns
            if table_data:
                # Adjust column names to match the DataFrame columns
                adjusted_data = []
                for item in table_data:
                    adjusted_data.append(dict(zip(columns, item)))
                df = pd.DataFrame(adjusted_data)
            else:
                df = pd.DataFrame(columns=columns)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

            # Validate the file path
            if not file_path:
                messagebox.showerror("Error", "No file path selected")
                return

            # Ensure file path has the correct extension
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'

            # Additional debug information
            print(f"Saving file to: {file_path}")

            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                worksheet.set_column('A:A', 20)  # id
                worksheet.set_column('B:B', 40)  # name
                worksheet.set_column('C:C', 10)  # gender
                worksheet.set_column('D:D', 20)  # dateofbirth
                worksheet.set_column('E:E', 30)  # prog
                worksheet.set_column('F:F', 10)  # house
                worksheet.set_column('G:G', 30)  # guardian
                worksheet.set_column('H:H', 10)  # mobile
                worksheet.set_column('I:I', 30)  # email
                worksheet.set_column('J:J', 30)  # guardian_title
                worksheet.set_column('K:K', 30)  # postal_address
                worksheet.set_column('L:L', 10)  # aggregate
                worksheet.set_column('M:M', 20)  # denomination
                worksheet.set_column('N:N', 10)  # status
                worksheet.set_column('O:O', 10)  # year
                worksheet.set_column('P:P', 30)  # class_name

            messagebox.showinfo("Success", "Data exported to Excel successfully")

        except Exception as e:
            # Additional debug information
            print(f"Failed to export data: {e}")
            messagebox.showerror("Error", f"Failed to export data: {e}")
            



    def export_for_assessment(self):
        try:
            # Fetch data currently displayed in the table
            table_data = [self.table.item(item, 'values') for item in self.table.get_children()]

            # Define the required columns
            columns = ['Student ID', 'Name of Student', 'Class Score', 'Exam Score']

            # Create a DataFrame with the current table data or an empty DataFrame with the specified columns
            if table_data:
                # Adjust column names to match the required columns
                adjusted_data = []
                for item in table_data:
                    adjusted_data.append({
                        'Student ID': item[0],
                        'Name of Student': item[1],
                        'Class Score': '',
                        'Exam Score': ''
                    })
                df = pd.DataFrame(adjusted_data)
            else:
                df = pd.DataFrame(columns=columns)

            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")])

            # Validate the file path
            if not file_path:
                messagebox.showerror("Error", "No file path selected")
                return

            # Ensure file path has the correct extension
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'

            # Additional debug information
            print(f"Saving file to: {file_path}")

            with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
                workbook = writer.book
                worksheet = writer.sheets['Sheet1']
                worksheet.set_column('A:A', 20)  # Student ID
                worksheet.set_column('B:B', 40)  # Name of Student
                worksheet.set_column('C:C', 20)  # Class Score
                worksheet.set_column('D:D', 20)  # Exam Score

            messagebox.showinfo("Success", "Data exported to Excel successfully")

        except Exception as e:
            # Additional debug information
            print(f"Failed to export data: {e}")
            messagebox.showerror("Error", f"Failed to export data: {e}")





    def parse_date(self, date_str):
        """Parse and format the date string to 'YYYY-MM-DD'."""
        try:
            date_obj = parse(date_str, fuzzy=True)
            year = date_obj.year
            month = f"{date_obj.month:02d}"
            day = f"{date_obj.day:02d}"
            return f"{year}-{month}-{day}"
        except (ValueError, TypeError):
            return None

            
    def save_error_data(self, error_data):
        HOME_DIR = os.path.expanduser('~')
        DOCUMENTS_DIR = os.path.join(HOME_DIR, 'Documents')
        APP_DIR = os.path.join(DOCUMENTS_DIR, 'ERROR_DATA')
        NOT_SUBMITTED_LIST_DIR = APP_DIR

        os.makedirs(APP_DIR, exist_ok=True)
        error_df = pd.DataFrame(error_data)
        error_file_path = os.path.join(NOT_SUBMITTED_LIST_DIR, 'error_data.xlsx')
        error_df.to_excel(error_file_path, index=False)
        messagebox.showinfo("Error", f"Some rows were not processed due to errors. Check the file at {error_file_path}")

        # Open the folder containing the error file
        if os.name == 'nt':  # Windows
            os.startfile(APP_DIR)
        elif os.name == 'posix':  # macOS or Linux
            subprocess.Popen(['open', APP_DIR])
        elif os.name == 'mac':  # older macOS
            subprocess.Popen(['open', APP_DIR])
        else:
            messagebox.showerror("Error", "Unable to open the folder automatically. Please check manually.")
            


    def upload_excel_file(self):
        # Check if year and class are selected
        if not self.year_var.get():
            messagebox.showerror("Error", "Please select a year")
            return
        if not self.class_var.get():
            messagebox.showerror("Error", "Please select a class")
            return

        file_path = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
        if file_path:
            df = pd.read_excel(file_path)

            # Define expected columns, ensuring they match the exact case as in the DataFrame
            expected_columns = [
                'Id', 'Name', 'Gender', 'Dateofbirth', 'Programme', 'House', 'Guardian', 'Mobile', 'Email',
                'GuardianTitle', 'PostalAddress', 'Aggregate', 'Denomination', 'Status'
            ]
            expected_columns = [col.upper() for col in expected_columns]

            # Convert DataFrame columns to upper case to match the expected columns
            df.columns = [col.upper() for col in df.columns]

            # Check if all expected columns are present in the DataFrame
            missing_columns = [col for col in expected_columns if col not in df.columns]
            if missing_columns:
                messagebox.showerror("Error", f"File format incorrect. Missing columns: {', '.join(missing_columns)}. Please check the column headings.")
                return  # Exit the function if the headers are wrong

            # Get year and class_id from the UI
            year = self.year_var.get()
            class_id = self.class_names[self.class_var.get()]

            # Connection to the database
            conn = get_db_connection()
            cursor = conn.cursor()

            # Fetch all house IDs and names
            cursor.execute("SELECT id, house_name FROM house")
            house_data = cursor.fetchall()
            house_dict = {house["house_name"].upper(): house["id"] for house in house_data}

            error_data = []

            # Process each row in the DataFrame
            for _, row in df.iterrows():
                student_id = str(row['ID']).strip()  # Trim whitespace

                # Handle date of birth
                date_of_birth = self.parse_date(str(row['DATEOFBIRTH']).strip())
                if not date_of_birth:
                    error_data.append(row)
                    continue  # Skip to the next row

                # Handle mobile number
                mobile = str(row['MOBILE']).strip()
                if '.' in mobile:
                    mobile = mobile.split('.')[0]  # Remove decimal part
                if not mobile.startswith(('0', '+')):
                    mobile = '0' + mobile

                # Get house ID
                house_name = str(row['HOUSE']).strip().upper()
                house_id = house_dict.get(house_name)
                
                # Check status and convert to title case
                status = str(row['STATUS']).strip().title()
                
                # Check if the student already exists
                cursor.execute("SELECT student_id FROM student WHERE student_id = ?", (student_id,))
                exists = cursor.fetchone()

                if exists:
                    # Update existing student if they exist
                    update_data = []
                    update_query = "UPDATE student SET "
                    db_columns = {
                        'ID': 'student_id',
                        'NAME': 'name',
                        'MOBILE': 'mobile',
                        'EMAIL': 'email',
                        'DATEOFBIRTH': 'dateofbirth',
                        'HOUSE': 'house_id',
                        'GUARDIAN': 'guardian_name',
                        'PROGRAMME': 'prog',
                        'GENDER': 'gender',
                        'GUARDIANTITLE': 'guardian_title',
                        'POSTALADDRESS': 'postal_address',
                        'AGGREGATE': 'aggregate',
                        'DENOMINATION': 'denomination',
                        'STATUS': 'status',
                        'YEAR': 'year',
                        'CLASSNAME': 'class_id'
                    }

                    for col in expected_columns:
                        if col in row:
                            db_col = db_columns[col]
                            value = None if str(row[col]) == 'None' else row[col]
                            if pd.notna(value) and value != '':
                                # Ensure no Timestamp values are used
                                if isinstance(value, pd.Timestamp):
                                    value = value.strftime('%Y-%m-%d')
                                if col == 'MOBILE':
                                    value = mobile  # Use the formatted mobile number
                                if col == 'HOUSE':
                                    value = house_id  # Use the house_id
                                if col == 'STATUS':
                                    value = status  # Use the title case status
                                update_data.append(value)
                                update_query += f"{db_col} = ?, "

                    if update_data:
                        update_query = update_query.rstrip(', ') + " WHERE student_id = ?"
                        update_data.append(student_id)
                        cursor.execute(update_query, update_data)
                else:
                    # Insert new student if they do not exist
                    values = (
                        student_id, row.get('NAME'), mobile, row.get('EMAIL'), date_of_birth,
                        house_id, row.get('GUARDIANTITLE'), row.get('GUARDIAN'), row.get('PROGRAMME'), row.get('GENDER'),
                        row.get('POSTALADDRESS'), row.get('AGGREGATE'), row.get('DENOMINATION'), status,
                        year, class_id
                    )
                    cursor.execute("""
                        INSERT INTO student (student_id, name, mobile, email, dateofbirth, house_id, guardian_title, guardian_name, prog, gender, postal_address, aggregate, denomination, status, year, class_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, values)

                # Commit after each row to save changes
                conn.commit()

            # Close database connection
            conn.close()
            self.update_table()
            messagebox.showinfo("Success", "Data uploaded successfully")
            
            GS1.start_update_process()
    

            # Save error-prone rows to a separate Excel file
            if error_data:
                self.save_error_data(error_data)
        else:
            messagebox.showerror("Error", "No file selected")


if __name__ == "__main__":
 
    root = ttk.Window(themename="darkly")
    app = Student(root)
    root.mainloop()
