import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import sqlite3
import os
import datetime
from tkinter import *
from fpdf import FPDF
from ttkbootstrap.widgets import DateEntry
from crud import get_db_connection

HOME_DIR = os.path.expanduser('~')
DOCUMENTS_DIR = os.path.join(HOME_DIR, 'Documents')
APP_DIR = os.path.join(DOCUMENTS_DIR, 'SHS-SMS-REPORT')
NOT_SUBMITTED_LIST_DIR = APP_DIR

os.makedirs(APP_DIR, exist_ok=True)

def get_formatted_datetime():
    now = datetime.datetime.now()
    day = now.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    formatted_date = now.strftime(f"{day}{suffix} %B, %Y %I:%M%p").lower()
    return formatted_date

current_datetime = get_formatted_datetime()
print(current_datetime)

class PDF(FPDF):
    def header(self):
        formatted_datetime=get_formatted_datetime()

        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, 'SMS SUBMISSION REPORT ', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Generated on {formatted_datetime}", 0, 1, 'C')  

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def add_sms_records(self, records):
        self.set_font('Arial', '', 10)
        for record in records:
            self.cell(0, 10, f"Student ID: {record['student_id']}, Name: {record['name']}, Message: {record['message']}, Time: {record['recdate']}", 0, 1)
        self.ln()

class ViewSMSReport:
    def __init__(self, root):
        self.root = root
        self.root.title("View SMS Report")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 820
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

        ttk.Label(self.frame, text="SMS Report", font=label_font).grid(row=0, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="From Date:", font=label_font).grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.from_date = DateEntry(self.frame, width=20, dateformat='%Y-%m-%d')
        self.from_date.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="To Date:", font=label_font).grid(row=1, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.to_date = DateEntry(self.frame, width=20, dateformat='%Y-%m-%d')
        self.to_date.grid(row=1, column=3, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        filter_button = ttk.Button(self.frame, text="Filter", command=self.filter_records, bootstyle="primary")
        filter_button.grid(row=1, column=4, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        columns = ["student_id", "name", "message", "recdate"]
        self.sms_table = tkttk.Treeview(self.frame, columns=columns, show="headings")
        
        for col in columns:
            self.sms_table.heading(col, text=col.replace("_", " ").title())
            self.sms_table.column(col, width=150, anchor=CENTER)

        self.sms_table.grid(row=2, column=0, columnspan=5, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        scrollbar_y = tkttk.Scrollbar(self.frame, orient="vertical", command=self.sms_table.yview)
        scrollbar_y.grid(row=2, column=5, sticky='ns')
        self.sms_table.configure(yscroll=scrollbar_y.set)

        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)
        self.frame.grid_columnconfigure(4, weight=1)

        delete_button = ttk.Button(self.frame, text="Delete All", command=self.delete_all_sms, bootstyle="danger")
        delete_button.grid(row=3, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        print_button = ttk.Button(self.frame, text="Print to PDF", command=self.print_to_pdf, bootstyle="info")
        print_button.grid(row=3, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        self.load_sms_data()

    def load_sms_data(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, sms.message, sms.recdate
            FROM sms
            JOIN student s ON s.student_id = sms.student_id
        ''')
        sms_records = cursor.fetchall()
        conn.close()

        for record in sms_records:
            self.sms_table.insert("", "end", values=(record['student_id'], record['name'], record['message'], record['recdate']))

    def delete_all_sms(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM sms')
        conn.commit()
        conn.close()
        self.sms_table.delete(*self.sms_table.get_children())
        messagebox.showinfo("Info", "All SMS records have been deleted.")
        
    def print_to_pdf(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, s.mobile, sms.message, sms.recdate
            FROM sms
            JOIN student s ON s.student_id = sms.student_id order by sms.recdate desc
        ''')
        sms_records = cursor.fetchall()
        conn.close()

        pdf = PDF()
        pdf.add_page()
        pdf.chapter_title("SMS Report")

        pdf.set_fill_color(23, 177, 105)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(25, 10, 'Student ID', 1, 0, 'C', True)
        pdf.cell(35, 10, 'Name', 1, 0, 'C', True)
        pdf.cell(35, 10, 'Mobile', 1, 0, 'C', True)
        pdf.cell(40, 10, 'Message', 1, 0, 'C', True)
        pdf.cell(40, 10, 'Time', 1, 0, 'C', True)
        pdf.ln()

        pdf.set_text_color(0, 0, 0)
        pdf.set_font('Arial', '', 10)
        for i, record in enumerate(sms_records):
            student_id = record['student_id']
            name = (record['name'][:7] + '...') if len(record['name']) > 10 else record['name']
            mobile = record['mobile']
            message = (record['message'][:17] + '...') if len(record['message']) > 20 else record['message']
            recdate = datetime.datetime.strptime(record['recdate'], '%Y-%m-%d %H:%M:%S').strftime('%d %b, %Y %I:%M %p')

            fill = i % 2 == 0  # Alternate row colors
            pdf.set_fill_color(217, 237, 247) if fill else pdf.set_fill_color(255, 255, 255)
            pdf.cell(25, 10, student_id, 1, 0, 'C', fill)
            pdf.cell(35, 10, name, 1, 0, 'C', fill)
            pdf.cell(35, 10, mobile, 1, 0, 'C', fill)
            pdf.cell(40, 10, message, 1, 0, 'C', fill)
            pdf.cell(40, 10, recdate, 1, 0, 'C', fill)
            pdf.ln()

        pdf_output_path = os.path.join(APP_DIR, 'sms_report.pdf')
        pdf.output(pdf_output_path)

        os.startfile(APP_DIR)  # Automatically open the folder after saving

    def filter_records(self):
        from_date = self.from_date.entry.get() + " 00:00:00"
        to_date = self.to_date.entry.get() + " 23:59:59"

        self.sms_table.delete(*self.sms_table.get_children())

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT s.student_id, s.name, sms.message, sms.recdate
            FROM sms
            JOIN student s ON s.student_id = sms.student_id
            WHERE sms.recdate BETWEEN ? AND ?
        ''', (from_date, to_date))
        sms_records = cursor.fetchall()
        conn.close()

        for record in sms_records:
            self.sms_table.insert("", "end", values=(record['student_id'], record['name'], record['message'], record['recdate']))

if __name__ == "__main__":
    root = ttk.Window("View SMS Report", "darkly")
    #-topmost', True
   
    app = ViewSMSReport(root)
 
    
    root.mainloop()
