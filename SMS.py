import sqlite3
import os
import json
import datetime


import requests
import os
    # Generate message string
from tabulate import tabulate

from ass import *





# Constants for directory and database
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)


def get_school_details():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS school_details (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            school_name TEXT NOT NULL,
            short_name TEXT NOT NULL,
            tel TEXT,
            email TEXT,
            logo_url TEXT
        )
    ''')

    cursor.execute('SELECT school_name, short_name, tel, email, logo_url FROM school_details WHERE id = 1')
    school_details = cursor.fetchone()
    
    conn.close()

    if school_details:
        return [school_details['school_name'], school_details['short_name'], school_details['tel'], school_details['email'], school_details['logo_url']]
    else:
        return []


    


def saveValues(**kwargs):
    REPORT_DIR = APP_DIR
    
    # Ensure the report directory exists
    os.makedirs(REPORT_DIR, exist_ok=True)
    
    # Save JSON file to the report directory
    filename = os.path.join(REPORT_DIR, 'student_data.json')
    
    with open(filename, 'w') as json_file:
        json.dump(kwargs, json_file)

def getValues(key):
    filename = os.path.join(APP_DIR, 'student_data.json')
    
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            return data.get(key, None)
    else:
        return None

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn





    
    
school_details = get_school_details()
school_name = school_details[0]
short_name = school_details[1]
tel = school_details[2]
email = school_details[3]
logo_url = school_details[4]



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


def get_remark2(average_mark):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT remark
        FROM remark
        WHERE ? BETWEEN 
              CAST(SUBSTR(mark_range, 1, INSTR(mark_range, '-') - 1) AS REAL)
              AND 
              CAST(SUBSTR(mark_range, INSTR(mark_range, '-') + 1) AS REAL)
          AND LENGTH(remark) - LENGTH(REPLACE(remark, ' ', '')) <= 1
        ORDER BY RANDOM()
        LIMIT 1
    ''', (average_mark,))
    record = cursor.fetchone()
    conn.close()
    return record["remark"] if record else "More Room for Improvement"



def get_student_assessment(student_id, class_id, year, semester):
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT ca.subject_id, ca.class_score,ca.short_name, ca.exam_score, ca.total_score, ca.grade, ca.number_equivalence, ca.remarks, ca.isCore, ca.teacher_initial_letters, ca.rank,p.short_name, p.subject_name
        FROM computed_assessment ca
        LEFT JOIN subject p ON ca.subject_id = p.id
        WHERE ca.student_id = ? AND ca.class_id = ? AND ca.year = ? AND ca.semester_id = ?
    ''', (student_id, class_id, year, semester))
    records = cursor.fetchall()
    conn.close()
    return records

def get_student_details(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.student_id, s.name, s.prog, h.house_name, 
               s.guardian_name, s.guardian_title, s.mobile, s.email, s.dateofbirth
        FROM student s
        LEFT JOIN house h ON s.house_id = h.id
        WHERE s.student_id = ?
    ''', (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

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




def get_total_students_in_class(class_id, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT COUNT(DISTINCT student_id) as total_students
        FROM assessment
        WHERE class_id = ? AND year = ?
    ''', (class_id, year))
    record = cursor.fetchone()
    conn.close()
    return record["total_students"] if record else 0


def generate_tabular_string(data):
    # Determine maximum width for each column
    max_subject_len = max(len(subject) for subject, _, _ in data)
    max_score_len = max(len(str(score)) for _, score, _ in data)
    max_grade_len = max(len(grade) for _, _, grade in data)
    
    # Create format string
    row_format = "{:<" + str(max_subject_len) + "} {:>" + str(max_score_len) + "} {:>" + str(max_grade_len) + "}"
    
    # Generate the tabular string
    tabular_string = ""
    for subject, score, grade in data:
        tabular_string += row_format.format(subject, score, grade) + "\n"
    
    return tabular_string

def generate_student_message(student_id, class_id, year, semester):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch student details
    student = get_student_details(student_id)
    if not student:
        return "Student not found"

    student_name = student['name']
    student_id = student['student_id']

    # Fetch class name
    class_name = get_class_name(class_id) or 'N/A'

    # Fetch total number of students in the class
    total_students = get_total_students_in_class(class_id, year) or 0

    # Fetch assessment records
    assessments = get_student_assessment(student_id, class_id, year, semester) or []

    # Fetch overall student position
    overall_position = get_student_position(student_id, class_id, semester, year) or 'N/A'

    # Fetch class teacher's remark
    average_mark = get_average_mark(student_id, class_id, semester, year) or 0
    class_teacher_remark = get_remark2(average_mark) or 'N/A'

    # Fetch headteacher's remark
    headteacher_remark = get_remark2(average_mark) or 'N/A'

    # Fetch student aggregate
    student_aggregate = get_student_aggregate(student_id, class_id, semester, year)

    # Generate message string
    message = f"Student: {student_name}\n"
    message += f"ID: {student_id}\n"
    message += f"Class: {class_name}\n"
    message += f"Semester: {semester}\n"
    message += f"Year: {year}\n"
    message += f"Total Students in Class: {total_students}\n"
    message += "--------------------\n"

    # Prepare assessment details
    assessment_data = [(assessment['short_name'] or assessment['subject_name'], assessment['total_score'], assessment['grade']) for assessment in assessments]
    assessments_details = generate_tabular_string(assessment_data)
    message += assessments_details
    message += "--------------------\n"
    message += f"Aggregate: {student_aggregate}\n"
    message += f"Position: {overall_position}\n"
    message += f"Teacher's Remark: {class_teacher_remark}\n"
    message += f"Headteacher's Remark: {headteacher_remark}\n"
    message += f"Support line: {tel}\n"  # Added this line for the support line with the school's telephone number

    conn.close()
    return message
