import sqlite3
import os
import pandas as pd
import CPS
import json
from crud import get_db_connection
import difflib



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
    
    
def get_api_key():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT api_key FROM api_key
        ORDER BY recdate DESC
        LIMIT 1
    ''')
    row = cursor.fetchone()
    conn.close()
    if row:
        return row["api_key"]
    return None

    
    

def update_student_house():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all house names and their corresponding IDs from the house table
    cursor.execute("SELECT id, house_name FROM house")
    houses = cursor.fetchall()
    house_dict = {house["house_name"].lower(): house["id"] for house in houses}

    # Fetch all student house values
    cursor.execute("SELECT student_id, house_id FROM student")
    students = cursor.fetchall()

    # Update student house_id with the correct house_id from house table
    for student in students:
        house_name = str(student["house_id"]).lower()  # Convert to string and then to lower case for comparison
        if house_name in house_dict:
            new_house_id = house_dict[house_name]
            cursor.execute("UPDATE student SET house_id = ? WHERE student_id = ?", (new_house_id, student["student_id"]))

    conn.commit()
    conn.close()
    
    
    
def get_preferred_class():
    HOME_DIR = os.path.expanduser('~')
    APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
    filename = os.path.join(APP_DIR, 'selected_class.json')
    
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            number1 = data.get("number1", "")
            programme = data.get("programme", "")
            number2 = data.get("number2", "")
            return f"{number1} {programme} {number2}".strip()
    else:
        return None
    
    
    
    
    
def extract_unique_programme_names(programme_names):
    unique_programmes = set()
    for name in programme_names:
        programme = ' '.join(name.split()[:-1])  # Remove the last word (assumed to be a number)
        unique_programmes.add(programme)
    return list(unique_programmes)

def process_and_insert_unique_programmes():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch existing programme names
    cursor.execute("SELECT programme_name FROM programme")
    existing_programmes = [row['programme_name'] for row in cursor.fetchall()]

    # Process existing programmes to get unique names
    unique_programmes = extract_unique_programme_names(existing_programmes)

    # Insert unique programmes back into the table
    for programme in unique_programmes:
        cursor.execute('INSERT OR IGNORE INTO programme (programme_name) VALUES (?)', (programme,))

    # Commit changes and close connection
    conn.commit()
    conn.close()

    return unique_programmes

# Process and insert unique programmes
unique_programmes = process_and_insert_unique_programmes()







    
    
    
    
