import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import sqlite3
import os
import datetime
from tkinter import *
from SMS import generate_student_message
from ass import *
import SendSMSToParents
import sms_report
import GS
import threading
import AE

from GS import get_preferred_class

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

import requests

def check_internet_connection():
    url = "http://www.google.com"
    timeout = 5
    try:
        request = requests.get(url, timeout=timeout)
        return True
    except (requests.ConnectionError, requests.Timeout) as exception:
        messagebox.showerror("No Internet Connection", "Please check your internet connection and try again. THE SMS SERVICE REQUIRES ACTIVE INTERNET CONNECTION")
        return False

def send_sms(message, mobile):
    apiKey = GS.get_api_key()
    print(apiKey)
    GS.saveValues(sms="1")
    can_send = GS.getValues("sms")
    print("SENDSMSVALUE:", can_send)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT short_name FROM school_details WHERE id = 1")
    record = cursor.fetchone()
    conn.close()

    if record:
        sender_id = record['short_name']
        if len(sender_id) > 8:
            sender_id = sender_id[:8]
    else:
        sender_id = 'SHS-REP'

    if mobile.startswith('0'):
        recipient = '233' + mobile[1:]
    elif not mobile.startswith('+'):
        recipient = '+' + mobile
    else:
        recipient = mobile

    if len(recipient) < 6:
        return False

    url = 'https://sms.arkesel.com/sms/api?action=send-sms'
    encoded_message = requests.utils.quote(message)
    final_url = f"{url}&api_key={apiKey}&to={recipient}&from={sender_id}&sms={encoded_message}"
    response = requests.get(final_url)

    if response.status_code == 200:
        return 1
    else:
        return 0

def create_sms_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sms (
            student_id TEXT,
            class_id INTEGER,
            semester_id INTEGER,
            year TEXT,
            message TEXT,
            delivered INTEGER DEFAULT 0,
            recdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (student_id, class_id, semester_id, year)
        )
    ''')
    conn.commit()
    conn.close()

class SMS:
    def __init__(self, root):
        self.root = root
        self.root.title("Send Student Report as SMS")
        self.STUDID = "0"

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

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)

        # Left column inputs
        left_column = ttk.Frame(self.frame)
        left_column.grid(row=0, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")
        self.search_var = ttk.StringVar()
        self.search_var.trace("w", self.update_treeview)
        self.search_entry = ttk.Entry(left_column, textvariable=self.search_var, width=50, state='normal')
        self.search_entry.grid(row=0, column=0, columnspan=2, padx=entry_padding_x, pady=entry_padding_y)

        ttk.Label(left_column, text="Year:", font=label_font).grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(left_column, textvariable=self.year_var, values=AE.generate_years())
        self.year_select.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.year_select.config(justify="center")
        self.year_select.bind("<<ComboboxSelected>>", self.update_suggested_table)

        ttk.Label(left_column, text="Class:", font=label_font).grid(row=2, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(left_column, textvariable=self.class_var)
        self.class_select.grid(row=2, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.class_select.config(justify="center")
        self.class_select.bind("<<ComboboxSelected>>", self.update_suggested_table)
        self.populate_class_names()

        ttk.Label(left_column, text="Semester:", font=label_font).grid(row=3, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.semester_var = ttk.StringVar()
        self.semester_select = ttk.Combobox(left_column, textvariable=self.semester_var, values=["1", "2", "3"])
        self.semester_select.grid(row=3, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.semester_select.config(justify="center")
        self.semester_select.bind("<<ComboboxSelected>>", self.update_suggested_table)

        # Right column buttons in a grid
        right_column = ttk.Frame(self.frame)
        right_column.grid(row=0, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        send_sms_button = ttk.Button(right_column, text="Send", width=10, command=self.start_sending_sms, bootstyle="success")
        send_sms_button.grid(row=0, column=0, padx=entry_padding_x, pady=entry_padding_y)

        stop_sms_button = ttk.Button(right_column, text="Stop", width=10, command=self.stop_sending_sms, bootstyle="danger")
        stop_sms_button.grid(row=0, column=1, padx=entry_padding_x, pady=entry_padding_y)

        reset_button = ttk.Button(right_column, text="Reset", command=self.reset_fields, bootstyle="secondary")
        reset_button.grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y)

        view_report_button = ttk.Button(right_column, text="View", bootstyle="info", width=10, command=self.open_view_report)
        view_report_button.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y)

        pta_sms_button = ttk.Button(right_column, text="PTA", width=10, bootstyle="success", command=self.open_sms_pta_window)
        pta_sms_button.grid(row=2, column=0, padx=entry_padding_x, pady=entry_padding_y)

        suggested_columns = ["student_id", "name", "mobile"]
        self.suggested_table = tkttk.Treeview(self.frame, columns=suggested_columns, show="headings")
        
        for col in suggested_columns:
            self.suggested_table.heading(col, text=col.replace("_", " ").title())
            self.suggested_table.column(col, width=150, anchor=CENTER)

        self.suggested_table.grid(row=3, column=0, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_suggested_y = tkttk.Scrollbar(self.frame, orient="vertical", command=self.suggested_table.yview)
        scrollbar_suggested_y.grid(row=3, column=2, sticky='ns')
        self.suggested_table.configure(yscroll=scrollbar_suggested_y.set)

        self.suggested_table.bind("<ButtonRelease-1>", self.on_row_select)

        columns = ["student_id", "name", "time_sent"]
        self.sms_table = tkttk.Treeview(self.frame, columns=columns, show="headings")
        
        for col in columns:
            self.sms_table.heading(col, text=col.replace("_", " ").title())
            self.sms_table.column(col, width=150, anchor=CENTER)

        self.sms_table.grid(row=4, column=0, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_y = tkttk.Scrollbar(self.frame, orient="vertical", command=self.sms_table.yview)
        scrollbar_y.grid(row=4, column=2, sticky='ns')
        self.sms_table.configure(yscroll=scrollbar_y.set)

        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_rowconfigure(4, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        self.loading_label = ttk.Label(self.frame, text="", font=label_font)
        self.loading_label.grid(row=5, column=0, columnspan=2, pady=entry_padding_y)

        self.progress_bar = ttk.Progressbar(self.frame, mode='determinate')
        self.progress_bar.grid(row=6, column=0, columnspan=2, pady=entry_padding_y)
        self.update_suggested_table()

        self.stop_flag = threading.Event()
        
        
        
                # Set default values based on preferred year and semester
        preferred_values = AE.get_preferred_year_semester()
        if "year" in preferred_values:
            self.year_var.set(preferred_values["year"])
        else:
            self.year_var.set(AE.generate_years()[0])  # Set to the most recent year if no preference

        if "semester" in preferred_values:
            self.semester_var.set(preferred_values["semester"])
        else:
            self.semester_var.set("1")  # Set to "1" if no preference
       
    def generate_years(self):
        current_year = datetime.datetime.now().year
        start_year = 1991
        end_year = current_year + 1
        return [f"{year}/{year + 1}" for year in range(end_year, start_year - 1, -1)]
    
    def open_sms_pta_window(self):
        ptaView = ttk.Toplevel(self.root)
        ptaView.title("SEND MESSAGE TO PTA MEMBERS")
        ptaView.geometry("400x600")
        
        screen_width = ptaView.winfo_screenwidth()
        screen_height = ptaView.winfo_screenheight()
        window_width = 400
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height -     window_height) // 2
        ptaView.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Schedule the initialization of the SMS sending UI on the main thread
        #SET ON TOP OF ALL WINDOWS
     
        self.root.after(0, SendSMSToParents.SendSMSToParents, ptaView)
        print(23)

    
    def open_view_report(self):
        reportView = Toplevel(self.root)
        reportView.title("View SMS Report")
        reportView.geometry("800x600")

        screen_width = reportView.winfo_screenwidth()
        screen_height = reportView.winfo_screenheight()
        window_width = 800
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        reportView.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Schedule the initialization of the SMS report view on the main thread
        self.root.after(0, sms_report.ViewSMSReport, reportView)
        self.root.attributes('-topmost', True)
        



    def populate_class_names(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, class_name FROM class_name ORDER BY class_name ASC")
        classes = cursor.fetchall()
        conn.close()
        
        class_names = [cls['class_name'] for cls in classes]
        self.class_id_map = {cls['class_name']: cls['id'] for cls in classes}

        # Get the preferred class filter
        preferred_class = get_preferred_class()

        if preferred_class:
            # Filter class names that match the preferred class pattern
            filtered_class_names = [
                class_name for class_name in class_names 
                if preferred_class.lower() in class_name.lower()
            ]
            self.class_select['values'] = filtered_class_names
        else:
            self.class_select['values'] = class_names


    def reset_fields(self):
        self.year_var.set('')
        self.class_var.set('')
        self.semester_var.set('')
        self.progress_bar['value'] = 0
        self.loading_label['text'] = ""
        self.search_var.set('')
        self.STUDID="0"
        self.update_suggested_table()

    def start_sending_sms(self):
        self.stop_flag.clear()
        threading.Thread(target=self.send_sms_thread).start()

    def stop_sending_sms(self):
        self.stop_flag.set()
    
    def on_row_select(self, event):
        selected_item = self.suggested_table.selection()
        if selected_item:
            student_id = self.suggested_table.item(selected_item, 'values')[0]
            self.search_var.set(student_id)
            self.STUDID = student_id

    def send_sms_thread(self):
        class_name = self.class_var.get()
        semester = self.semester_var.get()
        year = self.year_var.get()
     
        #print("single_id:", self.STUDID)

        if not class_name or not semester or not year:
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        class_id = self.class_id_map[class_name]

        if not check_internet_connection():
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT DISTINCT student_id, name, mobile 
            FROM student
            WHERE 1=1
        '''
        params = []
        if class_id:
            query += ' AND student_id IN (SELECT student_id FROM assessment WHERE class_id = ? AND semester_id = ? AND year = ?)'
            params.extend([class_id, semester, year])
            if self.STUDID and len(self.STUDID) > 3:
                query += ' AND student_id = ?'
                params.append(self.STUDID)

        cursor.execute(query, params)
        students = cursor.fetchall()
    

        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(students)
        self.loading_label['text'] = "Sending messages..."

        if not students:
            messagebox.showinfo("Info", "No students found for the given criteria.")
            self.loading_label['text'] = "No students found."
            return

        for index, student in enumerate(students):
            if self.stop_flag.is_set():
                self.loading_label['text'] = "Sending messages stopped."
                break

            student_id = student['student_id']
            student_name = student['name']
            student_mobile = student['mobile']

            if not student_mobile or len(student_mobile) <= 5:
                continue

            message = generate_student_message(student_id, class_id, year, semester) if student_name else None
            print(message)
            if not message:
                continue

            isSent = send_sms(message, student_mobile)
            print("sent:", isSent)

            if isSent == 1:
                cursor.execute('''
                    INSERT OR REPLACE INTO sms (student_id, class_id, semester_id, year, message, delivered)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (student_id, class_id, int(semester), year, message, 1))
                conn.commit()

                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.sms_table.insert("", "end", values=(student_id, student_name, current_time))
                self.sms_table.update_idletasks()
                print(f"Message sent to: {student_id}, {student_name}, {current_time}")

            self.progress_bar['value'] = index + 1
            self.frame.update_idletasks()

        if not self.stop_flag.is_set():
            self.loading_label['text'] = "Finished sending messages."
        conn.close()



    def update_suggested_table(self, *args):
        self.suggested_table.delete(*self.suggested_table.get_children())

        class_name = self.class_var.get()
        semester = self.semester_var.get()
        year = self.year_var.get()
        search_term = self.search_var.get().lower()
        
        # Clear the search field if the class or year or semester is changed
        self.search_var.set('')
        
        # RETURN IF NO CLASS SELECTED OR YEAR OR SEMESTER
        if not class_name or not semester or not year:
            return

        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT DISTINCT a.student_id, s.name, s.mobile
            FROM assessment a
            JOIN student s ON a.student_id = s.student_id
            WHERE 1=1
        '''
        params = []
        if class_name:
            query += ' AND a.class_id = (SELECT id FROM class_name WHERE class_name = ?)'
            params.append(class_name)
        if semester:
            query += ' AND a.semester_id = ?'
            params.append(semester)
        if year:
            query += ' AND a.year = ?'
            params.append(year)

        cursor.execute(query, params)
        students = cursor.fetchall()

        conn.close()

        def is_valid_mobile(mobile):
            return mobile and len(mobile) >= 8

        for student in students:
            if is_valid_mobile(student['mobile']) and any(search_term in str(value).lower() for value in student):
                self.suggested_table.insert("", "end", values=(student['student_id'], student['name'], student['mobile']))
    
    def update_treeview(self, *args):
        self.update_suggested_table()

if __name__ == "__main__":
    check_internet_connection()
    create_sms_table()
    root = ttk.Window("Send Student Report as SMS", "darkly")
    root.attributes('-topmost', True)
    app = SMS(root)
    root.mainloop()
