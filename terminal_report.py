import sqlite3
from fpdf import FPDF
import os
import sys
import json
import subprocess
import re
from R import *


from ass import *
# Constants for directory and database
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)
REPORT_DIR = os.path.join(HOME_DIR, 'Documents', 'STUDENT_REPORT')

# Ensure the report directory exists
os.makedirs(REPORT_DIR, exist_ok=True)


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

def get_student_guardian(student_id, column_name):
    conn = get_db_connection()
    query = f"SELECT {column_name} FROM student WHERE student_id = '{student_id}'"
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result is None or result[0] is None or len(result[0].strip()) < 4:
        return ""
    
    return result[0].strip()



def get_number_on_roll(class_id, semester_id, year):
    """
    Returns the number of students on roll for a specific class, semester, and year.

    Parameters:
    class_id (int): The ID of the class.
    semester_id (str): The ID of the semester.
    year (str): The year.

    Returns:
    int: The number of students on roll.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(DISTINCT student_id) as number_on_roll
        FROM computed_assessment
        WHERE class_id = ? AND semester_id = ? AND year = ?
    ''', (class_id, semester_id, year))
    record = cursor.fetchone()
    conn.close()
    return record['number_on_roll'] if record else 0




def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def open_student_report_folder():
    if os.name == 'nt':  # For Windows
        os.startfile(REPORT_DIR)
    elif os.name == 'posix':  # For macOS and Linux
        subprocess.call(['open', REPORT_DIR]) if sys.platform == 'darwin' else subprocess.call(['xdg-open', REPORT_DIR])



def get_guardian_name(student_id):
    conn = get_db_connection()
    query = f"SELECT * FROM student WHERE student_id = '{student_id}'"
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchone()
    cursor.close()

    if result is None or result[0] is None or result[0].strip() == "" or len(result[0]) < 3:
        return "P.O. Box..."
    
    return result[0]


def getSignature():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT img_url FROM signature WHERE id = 1")
    record = cursor.fetchone()
    conn.close()
    return record["img_url"] if record else None


def create_tables():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS class_name (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS house (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house_name TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS next_term (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            year TEXT,
            semester TEXT,
            next_term TEXT,
            UNIQUE(year, semester)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            prog TEXT,
            class_id INTEGER,
            house_id INTEGER,
            guardian_name TEXT,
            guardian_title TEXT,
            mobile TEXT,
            email TEXT,
            dateofbirth TEXT,
            FOREIGN KEY (class_id) REFERENCES class_name(id),
            FOREIGN KEY (house_id) REFERENCES house(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS computed_assessment (
            student_id TEXT,
            subject_id TEXT,
            class_score REAL,
            exam_score REAL,
            total_score REAL,
            grade TEXT,
            number_equivalence TEXT,
            remarks TEXT,
            isCore INTEGER,
            teacher_initial_letters TEXT,
            rank INTEGER,
            FOREIGN KEY (student_id) REFERENCES student(student_id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS remark (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mark_range TEXT NOT NULL,
            remark TEXT NOT NULL
        )
    ''')
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

def get_school_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM school_details WHERE id = 1")
    record = cursor.fetchone()
    conn.close()
    return record

def get_student_assessment(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT  ca.subject_id, ca.class_score, ca.exam_score, ca.total_score, ca.grade, ca.number_equivalence, ca.remarks, ca.isCore, ca.teacher_initial_letters, ca.rank, p.subject_name
        FROM computed_assessment ca
        LEFT JOIN subject p ON ca.subject_id = p.id
        WHERE ca.student_id = ? AND ca.total_score > 0
    ''', (student_id,))
    records = cursor.fetchall()
    conn.close()
    return records

def get_student_details(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.student_id, s.name, s.prog,  h.house_name, 
               s.guardian_name, s.guardian_title, s.mobile, s.email, s.dateofbirth,s.status
        FROM student s
        LEFT JOIN house h ON s.house_id = h.id
        WHERE s.student_id = ?
    ''', (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def get_student_image(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT img_url FROM student_img WHERE student_id = ?", (student_id,))
    student_img_record = cursor.fetchone()
    conn.close()
    return student_img_record["img_url"] if student_img_record else None

def get_next_term(year, semester):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT next_term
        FROM next_term
        WHERE year = ? AND semester = ?
    ''', (year, semester))
    record = cursor.fetchone()
    conn.close()
    return record["next_term"] if record else "No Date Set"

def get_class_name(class_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT class_name
        FROM class_name
        WHERE id = ?
    ''', (class_id,))
    record = cursor.fetchone()
    conn.close()
    return record["class_name"] if record else "No Record"

def get_attendance(student_id, class_id, semester, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT attendance_value, max_attendance_value
        FROM attendance
        WHERE student_id = ? AND class_id = ? AND semester = ? AND year = ?
    ''', (student_id, class_id, semester, year))
    record = cursor.fetchone()
    conn.close()
    if record:
        return f"{record['attendance_value']} Out Of: {record['max_attendance_value']}"
    else:
        return "63 Out Of: 65"



def get_student_position(student_id, class_id, semester_id, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT student_id, total_score, RANK() OVER (ORDER BY total_score DESC) as position
        FROM (
            SELECT student_id, SUM(total_score) as total_score
            FROM computed_assessment
            WHERE class_id = ? AND semester_id = ? AND year = ?
            GROUP BY student_id
        )
    ''', (class_id, semester_id, year))
    records = cursor.fetchall()
    conn.close()
    
    position_suffix = lambda n: "%d%s" % (n, {1: "st", 2: "nd", 3: "rd"}.get(n if n < 20 else n % 10, "th"))

    for record in records:
        if record["student_id"] == student_id:
            return position_suffix(record["position"])
    return None


def get_average_mark(student_id, class_id, semester_id, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT AVG(total_score) as avg_mark
        FROM computed_assessment
        WHERE student_id = ? AND class_id = ? AND semester_id = ? AND year = ?
    ''', (student_id, class_id, semester_id, year))
    record = cursor.fetchone()
    conn.close()
    return record["avg_mark"] if record else 0

def get_remark(average_mark):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT remark
        FROM remark
        WHERE ? BETWEEN 
              CAST(SUBSTR(mark_range, 1, INSTR(mark_range, '-') - 1) AS REAL)
              AND 
              CAST(SUBSTR(mark_range, INSTR(mark_range, '-') + 1) AS REAL)
        ORDER BY RANDOM()
        LIMIT 1
    ''', (average_mark,))
    record = cursor.fetchone()
    conn.close()
    return record["remark"] if record else "No Remark"





class PDF(FPDF):
    
    def header(self):
        school_details = get_school_details()
        if not school_details:
            self.error_message("School details not found")
            return

        self.set_font('Arial', 'B', 12)
        self.add_school_logo(school_details)
        self.add_school_info(school_details)
        self.add_report_title()

    def add_school_logo(self, school_details):
        logo_url = school_details["logo_url"]
        if logo_url and os.path.exists(logo_url):
            self.image(logo_url, 20, 8, 30, 30)
        else:
            default_logo = get_default_logo_image()
            if default_logo and os.path.exists(default_logo):
                self.image(default_logo, 20, 8, 30, 30)

    def add_school_info(self, school_details):
        self.cell(0, 10, school_details["school_name"], 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.ln(-6)
        contact_info = f'Tel: {school_details["tel"]} | Email: {school_details["email"]}'
        self.cell(0, 10, contact_info, 0, 1, 'C')

    def add_report_title(self):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, 'TERMINAL REPORT', 0, 1, 'C')
        self.ln(10)

    def error_message(self, message):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, f"Error: {message}", 0, 1, 'C')
        self.ln(5)
        
        
        
            
    def footer(self):
        # default height of a4 paper is 297mm
        # UP +   DOWN -
        image_height = 70  # Height of the signature image and text
        
        page_total_height = 297
        margin_bottom = 10  # 10mm above the bottom margin
        signature_position = page_total_height - margin_bottom - image_height  # Position for the signature image
        text_position = signature_position + 14  # Position for the text below the image
        guardian_name_position = text_position + 25  # Position for the guardian name below the signature text
        postal_address_position = guardian_name_position + 6  # Position for the postal address below the guardian name

        print("signatureP:", signature_position)
        print("textP:", text_position)
        print("guardianNameP:", guardian_name_position)
        print("postalAddressP:", postal_address_position)

        self.ln(-7)
        line_height = 4  # Control the line height
        gap_height = 1  # Smaller gap between lines
        font_size = 10  # Control the font size

        class_id = getValues("class_id")
        semester_id = getValues("semester_id")
        year = getValues("year")
        student_id = getValues("student_id")

        student_average_mark = get_average_mark(student_id, class_id, semester_id, year)
        teacher_remark = get_remark(student_average_mark)
        headteacher_remark = get_remark(student_average_mark)

        self.set_font('Arial', 'B', font_size)
        self.cell(23, line_height, "Attendance:", 0, 0, 'L')
        self.set_font('Arial', '', font_size)
        attendance = get_attendance(student_id, class_id, semester_id, year)
        self.cell(30, line_height, f"{attendance}", 0, 0, 'L')

        number_on_roll = get_number_on_roll(class_id, semester_id, year)

        self.set_font('Arial', 'B', font_size)
        self.cell(25, line_height, "No. On Roll:", 0, 0, 'L')
        self.set_font('Arial', '', font_size)
        self.cell(10, line_height, f"{number_on_roll}", 0, 1, 'L')

        if student_average_mark is None:
            student_average_mark = 0.00

        self.set_font('Arial', 'B', font_size)
        self.cell(38, line_height, "Student's Avg. Mark:", 0, 0, 'L')
        self.set_font('Arial', '', font_size)
        self.cell(10, line_height, f"{student_average_mark:.2f}", 0, 1, 'L')

        self.ln(gap_height)

        self.set_font('Arial', 'B', font_size)
        self.cell(20, line_height, "Conduct:", 0, 0, 'L')
        self.set_font('Arial', '', font_size)
        self.cell(80, line_height, "Satisfactory", 0, 1, 'L')

        self.ln(gap_height)

        self.set_font('Arial', 'B', font_size)
        self.cell(50, line_height, "Form Teacher's Remarks:", 0, 0, 'L')
        self.set_font('Arial', '', font_size)
        self.cell(80, line_height, teacher_remark, 0, 1, 'L')

        self.ln(gap_height)

        self.set_font('Arial', 'B', font_size)
        self.cell(70, line_height, "House Master's / Mistress' Remarks:", 0, 0, 'L')
        self.set_font('Arial', '', font_size)
        self.cell(30, line_height, headteacher_remark, 0, 1, 'L')

        self.ln(gap_height)

        try:
            headTeacherSignature = getSignature()

            if headTeacherSignature and not os.path.exists(headTeacherSignature):
                headTeacherSignature = get_default_signature_image()

            if headTeacherSignature and os.path.exists(headTeacherSignature):
                self.image(headTeacherSignature, 160, signature_position, 30, 30)
                self.set_font('Arial', 'I', 9)
                self.ln(0)
                self.set_y(text_position)  # Set the y-coordinate for the text
                self.cell(0, 10, "Signature of the Head of School   ", 0, 0, 'R')
            else:
                raise FileNotFoundError("Head teacher signature image not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
            # Handle the error or use a default action

        guardian_name = get_student_guardian(student_id, "guardian_name")
        guardian_title = get_student_guardian(student_id, "guardian_title")
        guardian_postal_address = get_student_guardian(student_id, "postal_address")

        guardian_name = f"{guardian_title} {guardian_name}"
        if len(guardian_name) < 3:
            guardian_name = "    "

        self.set_font('Arial', 'B', 10)
        self.set_y(guardian_name_position)  # Set the y-coordinate for the guardian name
        self.cell(0, 10, f"{guardian_name}", 0, 1, 'C')

        if guardian_postal_address is None:
            guardian_postal_address = "P.O. Box..."
        if len(guardian_postal_address) < 3:
            guardian_postal_address = "P.O. Box..."

        words = guardian_postal_address.split()
        if len(words) > 7:
            lines = ' '.join(words[:7]) + ' ...'
        else:
            lines = ' '.join(words)

        self.set_font('Arial', '', 10)
        self.set_y(postal_address_position)  # Set the y-coordinate for the postal address
        self.cell(0, 10, lines, 0, 1, 'C')


    
    
    
    
        
    def student_details(self, student):
        class_id = getValues("class_id")
        semester_id = getValues("semester_id")
        year = getValues("year")
        student_id = getValues("student_id")
        
        self.set_font('Arial', '', 12)
        student_img = get_student_image(student["student_id"])
        if student_img and os.path.exists(student_img):
            self.image(student_img, 160, 10, 30, 30)
        
        next_term_date = get_next_term(year, semester_id)
        class_name = get_class_name(class_id)

        # Student name at the top
        self.ln(-5)
        self.set_font('Arial', 'B', 9)
        self.cell(0, 10, "STUDENT NAME: " + student['name'], 0, 1, 'L')
        self.ln(-3)
        
        student_position = get_student_position(student["student_id"], class_id, semester_id, year)
        student_aggregate = get_student_aggregate(student["student_id"], class_id, semester_id, year)
    
        programme = student['prog']
        removed = re.sub(r'\d+$', '', programme).strip()
        programme1 = removed

        data = [
            ["Academic Year:", year, "Next semester Begins:", next_term_date],
            ["Student ID:", student['student_id'], "Semester:", semester_id],
            ["Programme:", programme1, "Status:", student['status']],
            ["Class:", class_name, "Aggregate:", student_aggregate],
            ["House:", student['house_name'], "Position in class:", student_position]
        ]

        col_widths = [35, 60, 38, 60]  # Adjust column widths
        # Reduce font size
        for row in data:
            for idx, item in enumerate(row):
                if idx % 2 == 0:
                    self.set_font('Arial', 'B', 10)  # Bold for labels
                else:
                    self.set_font('Arial', '', 10)  # Regular for values
                self.cell(col_widths[idx], 6, str(item), 0)  # Reduce cell height to 6
            self.ln()
        self.ln(10)



        
    def student_assessment(self, student_id):
        self.ln(-9)
        subject_width = 50
        score_width = 21
        remark_width = 30
        grade_width = 15
        rank_width = 20
        initials_width = 15
        cell_height = 6  # Variable to control cell height

        self.set_font('Arial', 'B', 10)
        self.cell(subject_width, cell_height * 2, 'Subject', 1, 0, 'L')
        self.cell(score_width, cell_height * 2, 'Class Score', 1, 0, 'C')
        self.cell(score_width, cell_height * 2, 'Exam Score', 1, 0, 'C')
        self.cell(score_width, cell_height * 2, 'Total', 1, 0, 'C')
        self.cell(grade_width, cell_height * 2, 'Grade', 1, 0, 'C')
        self.cell(rank_width, cell_height * 2, 'Position', 1, 0, 'C')
        self.cell(remark_width, cell_height * 2, 'Remarks', 1, 0, 'C')
        self.cell(initials_width, cell_height * 2, 'Initials', 1, 0, 'C')
        self.ln(cell_height * 2)

        self.set_font('Arial', '', 10)
        records = get_student_assessment(student_id)

        core_subjects = [record for record in records if record["isCore"] == 1]
        elective_subjects = [record for record in records if record["isCore"] == 0]

        # Core Subjects Header
        self.set_fill_color(200, 200, 200)
        total_width = subject_width + 3 * score_width + grade_width + rank_width + remark_width + initials_width
        self.set_font('Arial', 'B', 12)
        self.cell(total_width, cell_height, 'Core Subjects', 1, 1, 'L', True)

        # Core Subjects
        self.set_font('Arial', '', 10)
        for record in core_subjects:
            subject_name = str(record["subject_name"])
            if len(subject_name) > 20:
                subject_name = subject_name[:20] + '...'
            self.cell(subject_width, cell_height, subject_name, 1)
            self.cell(score_width, cell_height, str(record["class_score"]), 1, 0, 'C')
            self.cell(score_width, cell_height, str(record["exam_score"]), 1, 0, 'C')
            self.cell(score_width, cell_height, str(record["total_score"]), 1, 0, 'C')
            self.cell(grade_width, cell_height, record["grade"], 1, 0, 'C')
            self.cell(rank_width, cell_height, str(record["rank"]), 1, 0, 'C')
            self.cell(remark_width, cell_height, record["remarks"], 1, 0, 'C')
            self.cell(initials_width, cell_height, record["teacher_initial_letters"], 1, 0, 'C')
            # print rank
            # print("Rank: ", record["rank"])
            self.ln()
        self.ln(5)

        # Elective Subjects Header
        self.set_fill_color(200, 200, 200)
        self.set_font('Arial', 'B', 12)
        self.cell(total_width, cell_height, 'Elective Subjects', 1, 1, 'L', True)

        # Elective Subjects
        self.set_font('Arial', '', 10)
        for record in elective_subjects:
            subject_name = str(record["subject_name"])
            if len(subject_name) > 20:
                subject_name = subject_name[:20] + '...'
            self.cell(subject_width, cell_height, subject_name, 1)
            self.cell(score_width, cell_height, str(record["class_score"]), 1, 0, 'C')
            self.cell(score_width, cell_height, str(record["exam_score"]), 1, 0, 'C')
            self.cell(score_width, cell_height, str(record["total_score"]), 1, 0, 'C')
            self.cell(grade_width, cell_height, record["grade"], 1, 0, 'C')
            self.cell(rank_width, cell_height, str(record["rank"]), 1, 0, 'C')
            self.cell(remark_width, cell_height, record["remarks"], 1, 0, 'C')
            self.cell(initials_width, cell_height, record["teacher_initial_letters"], 1, 0, 'C')
            self.ln()
        self.ln(10)
        
        
        
def getStudentProgram(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT prog FROM student WHERE student_id = ?", (student_id,))
    record = cursor.fetchone()
    conn.close()
    return record["prog"] if record else None


def generate_student_report(student_id):
    student = get_student_details(student_id)
    student_name = student["name"]

    output_path = os.path.join(REPORT_DIR, f"{student_name.replace(' ', '_')}_report.pdf")
    
    pdf = PDF()
    pdf.student_id = student_id
    pdf.add_page()
    
    pdf.student_details(student)
    pdf.student_assessment(student_id)
    
    pdf.output(output_path)
    # print(f"Report generated successfully: {output_path}")
    #open_student_report_folder()

# Initialize database and create tables if not exist



