import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import sqlite3
import os
import datetime
from tkinter import *
from sms_util import send_sms, get_db_connection
import requests

class SendSMSToParents:
    def __init__(self, root):
        self.root = root
        self.root.title("Send SMS to Parents")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 700
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

        ttk.Label(self.frame, text="Send SMS to Parents", font=label_font).grid(row=0, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="Select Year:", font=label_font).grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.frame, textvariable=self.year_var, values=self.generate_years())
        self.year_select.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.year_select.config(justify="center")
        self.year_select.bind("<<ComboboxSelected>>", self.update_suggested_table)

        ttk.Label(self.frame, text="Select Class:", font=label_font).grid(row=1, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(self.frame, textvariable=self.class_var)
        self.class_select.grid(row=1, column=3, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.class_select.config(justify="center")
        self.class_select.bind("<<ComboboxSelected>>", self.update_suggested_table)
        self.populate_class_names()

        ttk.Label(self.frame, text="Search Student:", font=label_font).grid(row=2, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.student_var = ttk.StringVar()
        self.student_var.trace("w", self.update_suggested_table)
        self.student_search = ttk.Entry(self.frame, textvariable=self.student_var, width=30)
        self.student_search.grid(row=2, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="Message:", font=label_font).grid(row=3, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.message_text = Text(self.frame, height=6, width=40)
        self.message_text.grid(row=3, column=1, columnspan=3, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        send_sms_button = ttk.Button(self.frame, text="Send SMS", command=self.send_sms, bootstyle="success")
        send_sms_button.grid(row=4, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        reset_button = ttk.Button(self.frame, text="Reset", command=self.reset_fields, bootstyle="secondary")
        reset_button.grid(row=4, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        # Suggested students table
        suggested_columns = ["student_id", "name", "mobile"]
        self.suggested_table = tkttk.Treeview(self.frame, columns=suggested_columns, show="headings")
        
        for col in suggested_columns:
            self.suggested_table.heading(col, text=col.replace("_", " ").title())
            self.suggested_table.column(col, width=150, anchor=CENTER)

        self.suggested_table.grid(row=5, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_suggested_y = tkttk.Scrollbar(self.frame, orient="vertical", command=self.suggested_table.yview)
        scrollbar_suggested_y.grid(row=5, column=4, sticky='ns')
        self.suggested_table.configure(yscroll=scrollbar_suggested_y.set)

        # SMS history table
        columns = ["student_id", "name", "time_sent"]
        self.sms_table = tkttk.Treeview(self.frame, columns=columns, show="headings")
        
        for col in columns:
            self.sms_table.heading(col, text=col.replace("_", " ").title())
            self.sms_table.column(col, width=150, anchor=CENTER)

        self.sms_table.grid(row=6, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_y = tkttk.Scrollbar(self.frame, orient="vertical", command=self.sms_table.yview)
        scrollbar_y.grid(row=6, column=4, sticky='ns')
        self.sms_table.configure(yscroll=scrollbar_y.set)

        self.frame.grid_rowconfigure(5, weight=1)
        self.frame.grid_rowconfigure(6, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)

        self.loading_label = ttk.Label(self.frame, text="", font=label_font)
        self.loading_label.grid(row=7, column=0, columnspan=4, pady=entry_padding_y)

        self.progress_bar = ttk.Progressbar(self.frame, mode='determinate')
        self.progress_bar.grid(row=8, column=0, columnspan=4, pady=entry_padding_y)

        self.populate_students()

    def generate_years(self):
        current_year = datetime.datetime.now().year
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

    def populate_students(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name FROM student ORDER BY name ASC")
        students = cursor.fetchall()
        conn.close()
        self.all_students = {f"{student['name']} ({student['student_id']})": student['student_id'] for student in students}

    def update_student_list(self, event):
        search_term = self.student_var.get().lower()
        filtered_students = [student for student in self.all_students.keys() if search_term in student.lower()]
        self.student_search['values'] = filtered_students

    def reset_fields(self):
        self.year_var.set('')
        self.class_var.set('')
        self.student_var.set('')
        self.message_text.delete('1.0', END)
        self.progress_bar['value'] = 0
        self.loading_label['text'] = ""
        self.update_suggested_table()

    def send_sms(self):
        class_name = self.class_var.get()
        year = self.year_var.get()
        student_selection = self.student_var.get()
        student_id = self.all_students.get(student_selection)
        message = self.message_text.get("1.0", "end-1c")
        
        if not message:
            messagebox.showerror("Error", "Message cannot be empty.")
            return

        class_id = self.class_id_map.get(class_name, None)

        conn = get_db_connection()
        cursor = conn.cursor()

        query = '''
            SELECT DISTINCT student_id
            FROM assessment
            WHERE 1=1
        '''
        params = []

        if class_id:
            query += ' AND class_id = ?'
            params.append(class_id)
        if year:
            query += ' AND year = ?'
            params.append(year)
        if student_id:
            query += ' AND student_id = ?'
            params.append(student_id)

        cursor.execute(query, params)
        student_ids = cursor.fetchall()

        self.progress_bar['value'] = 0
        self.progress_bar['maximum'] = len(student_ids)
        self.loading_label['text'] = "Sending messages..."

        for index, student in enumerate(student_ids):
            student_id = student['student_id']
            cursor.execute('''
                SELECT name, mobile
                FROM student
                WHERE student_id = ?
            ''', (student_id,))
            student_info = cursor.fetchone()

            if student_info:
                student_name = student_info['name']
                student_mobile = student_info['mobile']

                if not student_mobile or len(student_mobile) <= 5:
                    continue

                isSent = send_sms(message, student_mobile)

                if isSent == 1:
                    cursor.execute('''
                        INSERT OR REPLACE INTO sms (student_id, class_id, year, message, delivered)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (student_id, class_id, year, message, 1))
                    conn.commit()

                    self.sms_table.insert("", "end", values=(student_id, student_name, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                    self.sms_table.update_idletasks()

            self.progress_bar['value'] = index + 1
            self.frame.update_idletasks()

        self.loading_label['text'] = "Finished sending messages."
        conn.close()

    def update_suggested_table(self, *args):
        self.suggested_table.delete(*self.suggested_table.get_children())

        class_name = self.class_var.get()
        year = self.year_var.get()
        search_term = self.student_var.get().lower()

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
        if year:
            query += ' AND a.year = ?'
            params.append(year)

        cursor.execute(query, params)
        students = cursor.fetchall()

        if not students:
            query = '''
                SELECT student_id, name, mobile
                FROM student
                WHERE 1=1
            '''
            params = []
            if class_name:
                query += ' AND class_id = (SELECT id FROM class_name WHERE class_name = ?)'
                params.append(class_name)
            if year:
                query += ' AND year = ?'
                params.append(year)

            cursor.execute(query, params)
            students = cursor.fetchall()

        conn.close()

        for student in students:
            if any(search_term in str(value).lower() for value in student):
                self.suggested_table.insert("", "end", values=(student['student_id'], student['name'], student['mobile']))

if __name__ == "__main__":
    root = ttk.Window("Send SMS to Parents", "darkly")
    # SET ALWAYS ON TOP TRUE
    root.wm_attributes("-topmost", 1)
    app = SendSMSToParents(root)
    root.mainloop()
