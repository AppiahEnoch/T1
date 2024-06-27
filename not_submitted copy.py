import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox, Canvas
import sqlite3
import os
import datetime
import re
# import inflect
from fpdf import FPDF
import os

from datetime import datetime
from GS import get_preferred_class


def get_formatted_datetime():
    now = datetime.now()
    day = now.day
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    formatted_date = now.strftime(f"{day}{suffix} %B, %Y %I:%M%p").lower()
    return formatted_date




HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def get_assessment_submission_status(year=None, semester=None, class_id=None):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = '''
    WITH expected_subjects AS (
        SELECT DISTINCT
            cps.class_id,
            cps.subject_id,
            cps.programme_id,
            c.class_name,
            s.subject_name,
            p.programme_name
        FROM class_programme_subject cps
        JOIN class_name c ON cps.class_id = c.id
        JOIN subject s ON cps.subject_id = s.id
        JOIN programme p ON cps.programme_id = p.id
    ),
    submitted_assessments AS (
        SELECT DISTINCT
            class_id,
            subject_id,
            programme_id,
            year,
            semester_id
        FROM assessment
    )
    SELECT 
        es.class_name,
        es.programme_name,
        es.subject_name,
        COALESCE(sa.year, ?) AS year,
        COALESCE(sa.semester_id, ?) AS semester_id,
        CASE 
            WHEN sa.subject_id IS NOT NULL THEN 'Submitted'
            ELSE 'Not Submitted'
        END AS submission_status
    FROM expected_subjects es
    LEFT JOIN submitted_assessments sa ON 
        es.class_id = sa.class_id AND
        es.subject_id = sa.subject_id AND
        es.programme_id = sa.programme_id AND
        (sa.year = ? OR ? IS NULL) AND
        (sa.semester_id = ? OR ? IS NULL)
    WHERE
        (es.class_id = ? OR ? IS NULL)
    ORDER BY 
        es.class_name,
        es.programme_name,
        year,
        semester_id,
        es.subject_name
    '''

    params = (year, semester, year, year, semester, semester, class_id, class_id)
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results




class PDF(FPDF):
    def header(self):
        formatted_datetime=get_formatted_datetime()


        
        self.set_font('Arial', 'B', 16)
        self.set_text_color(0, 0, 128)
        self.cell(0, 10, 'ASSESSMENT SUBMISSION REPORT ', 0, 1, 'C')
        self.set_font('Arial', 'I', 10)
        self.cell(0, 10, f"Generated on {formatted_datetime}", 0, 1, 'C')   
        
        
        
 
    
  
        self.ln(10)

    def chapter_title(self, programme_name):
        self.set_font('Arial', 'B', 14)
        self.set_text_color(0, 102, 204)
        self.cell(0, 10, programme_name, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, existing_subjects, not_existing_subjects):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(1, 135, 73)  # #018749
        self.set_text_color(255, 255, 255)  # White text color
        self.cell(95, 10, 'Submitted', 1, 0, 'C', fill=True)
        self.cell(95, 10, 'Not Submitted', 1, 1, 'C', fill=True)
        self.create_table(existing_subjects, not_existing_subjects)
        self.ln(5)

    def create_table(self, existing_subjects, not_existing_subjects):
        self.set_fill_color(200, 230, 201)  # Light green shade
        self.set_text_color(0, 0, 0)
        self.set_font('Arial', '', 12)
        max_len = max(len(existing_subjects), len(not_existing_subjects))
        for i in range(max_len):
            existing_subject = existing_subjects[i] if i < len(existing_subjects) else ''
            not_existing_subject = not_existing_subjects[i] if i < len(not_existing_subjects) else ''
            self.cell(95, 10, existing_subject, 1, 0, 'L', fill=True)
            self.cell(95, 10, not_existing_subject, 1, 1, 'L', fill=True)
        self.ln(2)

def createPDF(results):
    HOME_DIR = os.path.expanduser('~')
    DOCUMENTS_DIR = os.path.join(HOME_DIR, 'Documents')
    APP_DIR = os.path.join(DOCUMENTS_DIR, 'SHS-ASSESSMENT-SUBMISSION-REPORT')
    NOT_SUBMITTED_LIST_DIR = APP_DIR

    os.makedirs(APP_DIR, exist_ok=True)

    pdf = PDF()
    pdf.add_page()
    

    for result in results:
        pdf.chapter_title(result['programme_name'])
        pdf.chapter_body(result['existing_subjects'], result['not_existing_subjects'])
    report_path = os.path.join(NOT_SUBMITTED_LIST_DIR, 'ASSESSMENT_SUBMISSION_REPORT.pdf')
    pdf.output(report_path)
    os.startfile(NOT_SUBMITTED_LIST_DIR)


class NotSubmitted:
    def __init__(self, root):
        self.root = root
        self.root.title("Subject List")
        self.CURRENT_RESULTS = []

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 600
        window_height = 500
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

        ttk.Label(self.frame, text="Subjects with no assessment records", font=label_font).grid(row=0, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="Select Year:", font=label_font).grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.frame, textvariable=self.year_var, values=self.generate_years())
        self.year_select.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.year_select.config(justify="center")
        self.year_select.bind("<<ComboboxSelected>>", self.update_table)

        ttk.Label(self.frame, text="Select Class:", font=label_font).grid(row=1, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.class_var = ttk.StringVar()
        self.class_select = ttk.Combobox(self.frame, textvariable=self.class_var)
        self.class_select.grid(row=1, column=3, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.class_select.config(justify="center")
        self.class_select.bind("<<ComboboxSelected>>", self.update_table)
        self.populate_class_names()

        ttk.Label(self.frame, text="Select Semester:", font=label_font).grid(row=2, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.semester_var = ttk.StringVar()
        self.semester_select = ttk.Combobox(self.frame, textvariable=self.semester_var, values=["1", "2", "3"])
        self.semester_select.grid(row=2, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.semester_select.config(justify="center")
        self.semester_select.bind("<<ComboboxSelected>>", self.update_table)

        reset_button = ttk.Button(self.frame, text="Reset", command=self.reset_filters, bootstyle="secondary")
        reset_button.grid(row=2, column=2, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        
        print_button = ttk.Button(self.frame, text="Print", command=self.print_report, bootstyle="secondary")
        print_button.grid(row=2, column=3, padx=entry_padding_x, pady=entry_padding_y, sticky=W)

        self.tables_frame = ttk.Frame(self.frame)
        self.tables_frame.grid(row=3, column=0, columnspan=4, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        self.scrollbar_y = tkttk.Scrollbar(self.tables_frame, orient="vertical")
        self.scrollbar_y.pack(side="right", fill="y")

        self.canvas = Canvas(self.tables_frame, yscrollcommand=self.scrollbar_y.set)
        self.canvas.pack(side="left", fill="both", expand=True)

        self.scrollbar_y.config(command=self.canvas.yview)

        self.canvas_frame = ttk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.canvas_frame, anchor="nw")

        self.canvas_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind_all("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind_all("<Button-4>", self.on_mousewheel)
        self.canvas.bind_all("<Button-5>", self.on_mousewheel)

        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)
        self.frame.grid_columnconfigure(2, weight=1)
        self.frame.grid_columnconfigure(3, weight=1)

    def on_mousewheel(self, event):
        if event.delta:
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        elif event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")



    def generate_years(self):
        current_year = datetime.now().year
        start_year = 1991
        end_year = current_year + 1
        return [f"{year}/{year + 1}" for year in range(end_year, start_year - 1, -1)]


    def populate_class_names(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, class_name FROM class_name ORDER BY class_name ASC")
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

            
        

    def update_table(self, event=None):
        year = self.year_var.get()
        class_name = self.class_var.get()
        semester = self.semester_var.get()

        programmes_subjects = self.get_efficient_assessment_status(year, semester, class_name)
        self.CURRENT_RESULTS = programmes_subjects
        
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()

        if programmes_subjects:
            row = 0
            col = 0
            for programme in programmes_subjects:
                programme_frame = ttk.Labelframe(self.canvas_frame, text=programme["programme_name"], padding=10)
                programme_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

                table = tkttk.Treeview(programme_frame, columns=["subject"], show="headings")
                table.heading("subject", text="Subjects")
                table.column("subject", width=200, anchor=CENTER)
                table.pack(fill=BOTH, expand=True)

                for subject in programme["not_existing_subjects"]:
                    table.insert("", "end", values=(subject,))

                col += 1
                if col > 1:
                    col = 0
                    row += 1

    def reset_filters(self):
        self.year_var.set('')
        self.class_var.set('')
        self.semester_var.set('')
        for widget in self.canvas_frame.winfo_children():
            widget.destroy()
            
    def print_report(self):
        createPDF(self.CURRENT_RESULTS)
        messagebox.showinfo("Report", "Report printed successfully")
        



    def get_efficient_assessment_status(self, year=None, semester=None, class_name=None):
        # Get the class_id if class_name is provided
        class_id = None
        if class_name:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT id FROM class_name WHERE class_name = ?', (class_name,))
            result = cursor.fetchone()
            if result:
                class_id = result['id']
            conn.close()

        # Get assessment submission status
        submissions = get_assessment_submission_status(year, semester, class_id)

        # Process the results
        programmes = {}
        for submission in submissions:
            programme_name = submission['programme_name']
            subject_name = submission['subject_name']
            status = submission['submission_status']

            if programme_name not in programmes:
                programmes[programme_name] = {
                    "programme_name": programme_name,
                    "programme_id": None,  # This will be set later
                    "existing_subjects": set(),
                    "not_existing_subjects": set()
                }

            if status == 'Submitted':
                programmes[programme_name]["existing_subjects"].add(subject_name)
            else:
                programmes[programme_name]["not_existing_subjects"].add(subject_name)

        # Get programme IDs
        conn = get_db_connection()
        cursor = conn.cursor()
        for programme_name in programmes:
            cursor.execute('SELECT id FROM programme WHERE programme_name = ?', (programme_name,))
            result = cursor.fetchone()
            if result:
                programmes[programme_name]["programme_id"] = result['id']
        conn.close()

        # Convert sets to lists and create final output
        result = []
        for programme in programmes.values():
            programme["existing_subjects"] = list(programme["existing_subjects"])
            programme["not_existing_subjects"] = list(programme["not_existing_subjects"])
            result.append(programme)

        return result


if __name__ == "__main__":
    root = ttk.Window("Subject List", "darkly")
    app = NotSubmitted(root)
    root.mainloop()
