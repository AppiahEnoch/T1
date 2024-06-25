import sqlite3
import os
import pandas as pd
import CPS
import json



# Use os.path.expanduser to get the path to the user's home directory
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    """Establish and return a connection to the SQLite database."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row  # Enable access by column name
    return conn

def initialize_database():
 
    """Initialize the database with the required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    
    
    
    
    
    

    

    

    
    # Users table creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    ''')
    
    # Class name table creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS class_name (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT NOT NULL UNIQUE,
            programme TEXT 
        )
    ''')

    # Programme table creation with is_core column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subject (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject_name TEXT NOT NULL UNIQUE,
            short_name TEXT,
            is_core INTEGER NOT NULL DEFAULT 0
        )
    ''')

    # Assessment table creation with unique constraint and teacher_initial_letters column
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS assessment (
                student_id INTEGER NOT NULL,
                semester_id INTEGER NOT NULL,
                programme_id INTEGER NOT NULL,
                subject_id INTEGER NOT NULL,
                class_id INTEGER NOT NULL,
                year VARCHAR(9) NOT NULL,
                class_score DECIMAL(5,2) NOT NULL,
                exam_score DECIMAL(5,2) NOT NULL,
                teacher_initial_letters TEXT DEFAULT NULL,
                PRIMARY KEY (student_id, semester_id, subject_id, class_id),
                FOREIGN KEY (class_id) REFERENCES class_name(id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (subject_id) REFERENCES subject(id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (programme_id) REFERENCES programme(id) ON DELETE CASCADE ON UPDATE CASCADE
              
            )
        ''')

    # Student table creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student (
            student_id TEXT PRIMARY KEY,
            name TEXT,
            mobile TEXT,
            email TEXT,
            dateofbirth TEXT DEFAULT CURRENT_DATE,
            house_id INTEGER,
            guardian_title TEXT,
            guardian_name TEXT,
            prog TEXT,
            gender TEXT,
            postal_address TEXT,
            aggregate INTEGER,
            denomination TEXT,
            status TEXT,
            year TEXT,
            class_id INTEGER
        )
    ''')




    # House table creation
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS house (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            house_name TEXT NOT NULL UNIQUE
        )
    ''')
    
    # Insert default houses
    cursor.execute('''
        INSERT OR IGNORE INTO house (house_name) VALUES ('PAULSEN')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO house (house_name) VALUES ('CLIFFORD')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO house (house_name) VALUES ('AMEYAW')
    ''')
    cursor.execute('''
        INSERT OR IGNORE INTO house (house_name) VALUES ('AMOAH')
    ''')
    

 
    
    # Create the school_details table if it doesn't exist
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
    
    # Insert the default values if they do not already exist
    cursor.execute('''
        INSERT OR IGNORE INTO school_details (id, school_name, short_name, tel, email, logo_url)
        VALUES (1, 'SEVENTH-DAY ADVENTIST SENIOR HIGH SCHOOL', 'SDASS', '+233240715501', 'report@sdass.edu.gh', NULL)
    ''')
    


    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS computed_assessment (
            student_id INTEGER NOT NULL,
            class_id INTEGER NOT NULL,
            semester_id INTEGER NOT NULL,
            subject_id INTEGER NOT NULL,
            year VARCHAR(9) NOT NULL,
            class_score DECIMAL(5,2) NOT NULL,
            exam_score DECIMAL(5,2) NOT NULL,
            total_score DECIMAL(5,2) NOT NULL,
            grade TEXT,
            number_equivalence INTEGER,
            remarks TEXT,
            isCore INTEGER NOT NULL,
            teacher_initial_letters TEXT,
            rank TEXT,
            short_name TEXT,
            PRIMARY KEY (student_id, semester_id, subject_id, class_id, year)
        )
    ''')
    
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_img (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            img_url TEXT,
            FOREIGN KEY (student_id) REFERENCES student (student_id)
        )
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS programme (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programme_name VARCHAR(255) UNIQUE
    )
''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS class_programme_subject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER NOT NULL,
        programme_id INTEGER NOT NULL,
        subject_id INTEGER NOT NULL,
        FOREIGN KEY (class_id) REFERENCES class_name(id),
        FOREIGN KEY (programme_id) REFERENCES programme(id),
        FOREIGN KEY (subject_id) REFERENCES subject(id)
    )
    ''')

    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS score_percentage (
        id INTEGER PRIMARY KEY,
        class_score INTEGER NOT NULL,
        exam_score INTEGER NOT NULL
        )
    ''')
    
    #insert 30, 70 as default values for class_score and exam_score
    cursor.execute('''
        INSERT OR IGNORE INTO score_percentage (id, class_score, exam_score)
        VALUES (1, 30, 70)
    ''')
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS programme_subject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        programme_id INTEGER NOT NULL,
        FOREIGN KEY (subject_id) REFERENCES subject(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (programme_id) REFERENCES programme(id) ON UPDATE CASCADE ON DELETE CASCADE
    )
''')
    
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
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS signature (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        img_url TEXT
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
    CREATE TABLE IF NOT EXISTS api_key (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        key_name VARCHAR(255) UNIQUE,
        api_key TEXT,
        recdate TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

    conn.commit()
    conn.close()
    

    

# Create the application-specific directory if it does not exist
os.makedirs(APP_DIR, exist_ok=True)

# Initialize the database if it does not exist





def insert_class_names(class_names):
    conn = get_db_connection()
    cursor = conn.cursor()
    for name in class_names:
        cursor.execute('INSERT OR IGNORE INTO class_name (class_name) VALUES (?)', (name,))
    conn.commit()
    conn.close()

def update_programme():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, class_name FROM class_name')
    rows = cursor.fetchall()
    for row in rows:
        class_name = row[1]
        parts = class_name.split(' ')
        if len(parts) > 2:
            programme = ' '.join(parts[1:-1])
            cursor.execute('UPDATE class_name SET programme = ? WHERE id = ?', (programme, row[0]))
        elif len(parts) == 2:
            programme = parts[1]
            cursor.execute('UPDATE class_name SET programme = ? WHERE id = ?', (programme, row[0]))
    conn.commit()
    conn.close()


class_names = [
"1 General Science 1",
"1 General Science 2",
"1 General Science 3",
"1 General Science 4",
"1 General Science 5",
"2 General Science 1",
"2 General Science 2",
"2 General Science 3",
"2 General Science 4",
"2 General Science 5",
"3 General Science 1",
"3 General Science 2",
"3 General Science 3",
"3 General Science 4",
"3 General Science 5",
"1 Business 1",
"1 Business 2",
"1 Business 3",
"1 Business 4",
"1 Business 5",
"2 Business 1",
"2 Business 2",
"2 Business 3",
"2 Business 4",
"2 Business 5",
"3 Business 1",
"3 Business 2",
"3 Business 3",
"3 Business 4",
"3 Business 5",


"1 General Arts 1",
"1 General Arts 2",
"1 General Arts 3",
"1 General Arts 4",
"1 General Arts 5",
"1 General Arts 6",
"1 General Arts 7",
"1 General Arts 8",
"1 General Arts 9",
"1 General Arts 10",
"1 General Arts 11",
"1 General Arts 12",
"1 General Arts 13",
"1 General Arts 14",
"1 General Arts 15",
"1 General Arts 16",
"2 General Arts 1",
"2 General Arts 2",
"2 General Arts 3",
"2 General Arts 4",
"2 General Arts 5",
"2 General Arts 6",
"2 General Arts 7",
"2 General Arts 8",
"2 General Arts 9",
"2 General Arts 10",
"2 General Arts 11",
"2 General Arts 12",
"2 General Arts 13",
"2 General Arts 14",
"2 General Arts 15",
"2 General Arts 16",
"3 General Arts 1",
"3 General Arts 2",
"3 General Arts 3",
"3 General Arts 4",
"3 General Arts 5",
"3 General Arts 6",
"3 General Arts 7",
"3 General Arts 8",
"3 General Arts 9",
"3 General Arts 10",
"3 General Arts 11",
"3 General Arts 12",
"3 General Arts 13",
"3 General Arts 14",
"3 General Arts 15",
"3 General Arts 16",





  
"1 Visual Arts 1",
"1 Visual Arts 2",
"1 Visual Arts 3",
"1 Visual Arts 4",
"1 Visual Arts 5",
"2 Visual Arts 1",
"2 Visual Arts 2",
"2 Visual Arts 3",
"2 Visual Arts 4",
"2 Visual Arts 5",
"3 Visual Arts 1",
"3 Visual Arts 2",
"3 Visual Arts 3",
"3 Visual Arts 4",
"3 Visual Arts 5",
"1 Home Economics 1",
"1 Home Economics 2",
"1 Home Economics 3",
"1 Home Economics 4",
"1 Home Economics 5",
"2 Home Economics 1",
"2 Home Economics 2",
"2 Home Economics 3",
"2 Home Economics 4",
"2 Home Economics 5",
"3 Home Economics 1",
"3 Home Economics 2",
"3 Home Economics 3",
"3 Home Economics 4",
"3 Home Economics 5",
"1 Agricultural Science 1",
"2 Agricultural Science 1",
"3 Agricultural Science 1",
]


def insert_programme_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    programme_names = [
    "General Science 1",
    "General Science 2",
    "General Science 3",
    "General Science 4",
    "General Science 5",
    "General Science 6",
    "General Science 7",
    "General Science 8",
    "General Science 9",
    "General Science 10",
    "General Science 11",
    "General Science 12",
    "General Science 13",
    "General Science 14",
    "General Science 15",
    "General Science 16",
    "General Science 17",
    "General Science 18",
    "General Science 19",
    "General Science 20",
    "Business 1",
    "Business 2",
    "Business 3",
    "Business 4",
    "Business 5",
    "Business 6",
    "Business 7",
    "Business 8",
    "Business 9",
    "Business 10",
    "Business 11",
    "Business 12",
    "Business 13",
    "Business 14",
    "Business 15",
    "Business 16",
    "Business 17",
    "Business 18",
    "Business 19",
    "Business 20",
    "General Arts 1",
    "General Arts 2",
    "General Arts 3",
    "General Arts 4",
    "General Arts 5",
    "General Arts 6",
    "General Arts 7",
    "General Arts 8",
    "General Arts 9",
    "General Arts 10",
    "General Arts 11",
    "General Arts 12",
    "General Arts 13",
    "General Arts 14",
    "General Arts 15",
    "General Arts 16",
    "General Arts 17",
    "General Arts 18",
    "General Arts 19",
    "General Arts 20",
    "Visual Arts 1",
    "Visual Arts 2",
    "Visual Arts 3",
    "Visual Arts 4",
    "Visual Arts 5",
    "Visual Arts 6",
    "Visual Arts 7",
    "Visual Arts 8",
    "Visual Arts 9",
    "Visual Arts 10",
    "Visual Arts 11",
    "Visual Arts 12",
    "Visual Arts 13",
    "Visual Arts 14",
    "Visual Arts 15",
    "Visual Arts 16",
    "Visual Arts 17",
    "Visual Arts 18",
    "Visual Arts 19",
    "Visual Arts 20",
    "Home Economics 1",
    "Home Economics 2",
    "Home Economics 3",
    "Home Economics 4",
    "Home Economics 5",
    "Home Economics 6",
    "Home Economics 7",
    "Home Economics 8",
    "Home Economics 9",
    "Home Economics 10",
    "Home Economics 11",
    "Home Economics 12",
    "Home Economics 13",
    "Home Economics 14",
    "Home Economics 15",
    "Home Economics 16",
    "Home Economics 17",
    "Home Economics 18",
    "Home Economics 19",
    "Home Economics 20",
    "Agricultural Science 1",
    "Agricultural Science 2",
    "Agricultural Science 3",
    "Agricultural Science 4",
    "Agricultural Science 5",
    "Agricultural Science 6",
    "Agricultural Science 7",
    "Agricultural Science 8",
    "Agricultural Science 9",
    "Agricultural Science 10",
    "Agricultural Science 11",
    "Agricultural Science 12",
    "Agricultural Science 13",
    "Agricultural Science 14",
    "Agricultural Science 15",
    "Agricultural Science 16",
    "Agricultural Science 17",
    "Agricultural Science 18",
    "Agricultural Science 19",
    "Agricultural Science 20",
    "Technical 1",
    "Technical 2",
    "Technical 3",
    "Technical 4",
    "Technical 5",
    "Technical 6",
    "Technical 7",
    "Technical 8",
    "Technical 9",
    "Technical 10",
    "Technical 11",
    "Technical 12",
    "Technical 13",
    "Technical 14",
    "Technical 15",
    "Technical 16",
    "Technical 17",
    "Technical 18",
    "Technical 19",
    "Technical 20"
    ]
    
    







        
    for name in programme_names:
        cursor.execute('''
            INSERT OR IGNORE INTO programme (programme_name)
            VALUES (?)
        ''', (name,))
    
    conn.commit()
    conn.close()
    
    
    
    
    




def insert_subjects():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    subjects = [
    "ELECTIVE MATHEMATICS",
    "PHYSICS",
    "CHEMISTRY",
    "BIOLOGY",
    "ELECTIVE ICT",
    "ECONOMICS",
    "ACCOUNTING",
    "PRINCIPLES OF COST ACCOUNTING",
    "BUSINESS MANAGEMENT",
    "GENERAL AGRICULTURE",
    "ANIMAL HUSBANDRY",
    "FOOD AND NUTRITION",
    "MANAGEMENT IN LIVING",
    "GENERAL KNOWLEDGE IN ART",
    "CLOTHING AND TEXTILES",
    "GRAPHIC DESIGN",
    "TEXTILES",
    "SCULPTURE",
    "LEATHER WORKS",
    "PICTURE MAKING",
    "GEOGRAPHY",
    "GOVERNMENT",
    "CHRISTIAN RELIGIOUS STUDIES",
    "HISTORY",
    "LITERATURE",
    "TWI",
    "FRENCH",
    "MUSIC"
]
    for subject in subjects:
        cursor.execute('INSERT OR IGNORE INTO subject (subject_name) VALUES (?)', (subject,))
    conn.commit()
    conn.close()
    
def generate_short_name(subject):
    words = subject.split()
    short_name = ""
    
    # Loop through each word and accumulate characters until short_name is 5 characters long
    for word in words:
        needed_length = 5 - len(short_name)
        short_name += word[:needed_length].upper()
        if len(short_name) >= 5:
            break
    
    # Ensure the short name is exactly 5 characters
    return short_name[:5]
def update_short_names():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, subject_name FROM subject WHERE short_name IS NULL')
    rows = cursor.fetchall()
    for row in rows:
        subject_id, subject_name = row
        short_name = generate_short_name(subject_name)
        cursor.execute('UPDATE subject SET short_name = ? WHERE id = ?', (short_name, subject_id))
    conn.commit()
    conn.close()
    
    

def match_programmes_subjects():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Define the relationships
    programme_subject_pairs = {
        "General Science 1": ["ELECTIVE MATHEMATICS", "PHYSICS", "CHEMISTRY", "BIOLOGY"],
        "General Science 2": ["ELECTIVE MATHEMATICS", "PHYSICS", "CHEMISTRY", "BIOLOGY"],
        "General Science 3": ["ELECTIVE MATHEMATICS", "PHYSICS", "CHEMISTRY", "BIOLOGY"],
        "General Science 4": ["ELECTIVE MATHEMATICS", "PHYSICS", "CHEMISTRY", "ELECTIVE ICT"],
        "Business 1": ["ECONOMICS", "ACCOUNTING", "PRINCIPLES OF COST ACCOUNTING", "ELECTIVE MATHEMATICS", "BUSINESS MANAGEMENT"],
        "Business 2": ["ECONOMICS", "ACCOUNTING", "PRINCIPLES OF COST ACCOUNTING", "ELECTIVE MATHEMATICS", "BUSINESS MANAGEMENT"],
        "Business 3": ["ECONOMICS", "ACCOUNTING", "PRINCIPLES OF COST ACCOUNTING", "ELECTIVE MATHEMATICS", "BUSINESS MANAGEMENT"],
        "General Arts 1": ["ECONOMICS", "GEOGRAPHY", "GOVERNMENT", "ELECTIVE MATHEMATICS"],
        "General Arts 2": ["ECONOMICS", "GEOGRAPHY", "GOVERNMENT", "ELECTIVE MATHEMATICS"],
        "General Arts 3": ["ECONOMICS", "GEOGRAPHY", "GOVERNMENT", "ELECTIVE MATHEMATICS"],
        "General Arts 4": ["CHRISTIAN RELIGIOUS STUDIES", "HISTORY", "LITERATURE", "TWI", "FRENCH"],
        "General Arts 5": ["MUSIC", "GEOGRAPHY", "GOVERNMENT", "TWI", "FRENCH"],
        "General Arts 6": ["MUSIC", "GEOGRAPHY", "GOVERNMENT", "TWI", "FRENCH"],
        "General Arts 7": ["CHRISTIAN RELIGIOUS STUDIES", "ECONOMICS", "GOVERNMENT", "GEOGRAPHY"],
        "General Arts 8": ["CHRISTIAN RELIGIOUS STUDIES", "ECONOMICS", "GOVERNMENT", "GEOGRAPHY"],
        "General Arts 9": ["CHRISTIAN RELIGIOUS STUDIES", "ECONOMICS", "GOVERNMENT", "GEOGRAPHY"],
        "General Arts 10": ["CHRISTIAN RELIGIOUS STUDIES", "ECONOMICS", "GOVERNMENT", "GEOGRAPHY"],
        "General Arts 11": ["CHRISTIAN RELIGIOUS STUDIES", "ECONOMICS", "GOVERNMENT", "GEOGRAPHY"],
        "General Arts 12": ["HISTORY", "CHRISTIAN RELIGIOUS STUDIES", "GOVERNMENT", "TWI", "FRENCH"],
        "General Arts 13": ["HISTORY", "CHRISTIAN RELIGIOUS STUDIES", "GOVERNMENT", "TWI", "FRENCH"],
        "General Arts 14": ["ECONOMICS", "GEOGRAPHY", "ELECTIVE MATHEMATICS", "ELECTIVE ICT"],
        "General Arts 15": ["CHRISTIAN RELIGIOUS STUDIES", "ECONOMICS", "GOVERNMENT", "GEOGRAPHY"],
        "Visual Arts 1": ["GENERAL KNOWLEDGE IN ART", "GRAPHIC DESIGN", "TEXTILES", "SCULPTURE", "LEATHER WORKS", "PICTURE MAKING"],
        "Visual Arts 2": ["GENERAL KNOWLEDGE IN ART", "GRAPHIC DESIGN", "TEXTILES", "SCULPTURE", "LEATHER WORKS", "PICTURE MAKING"],
        "Visual Arts 3": ["GENERAL KNOWLEDGE IN ART", "GRAPHIC DESIGN", "TEXTILES", "SCULPTURE", "LEATHER WORKS", "PICTURE MAKING"],
        "Home Economics 1": ["FOOD AND NUTRITION", "MANAGEMENT IN LIVING", "GENERAL KNOWLEDGE IN ART", "BIOLOGY", "CHEMISTRY"],
        "Home Economics 2": ["FOOD AND NUTRITION", "MANAGEMENT IN LIVING", "GENERAL KNOWLEDGE IN ART", "BIOLOGY", "CHEMISTRY"],
        "Home Economics 3": ["FOOD AND NUTRITION", "MANAGEMENT IN LIVING", "GENERAL KNOWLEDGE IN ART", "BIOLOGY", "CHEMISTRY"],
        "Home Economics 4": ["CLOTHING AND TEXTILES", "MANAGEMENT IN LIVING", "GENERAL KNOWLEDGE IN ART", "BIOLOGY", "CHEMISTRY"],
        "Home Economics 5": ["CLOTHING AND TEXTILES", "MANAGEMENT IN LIVING", "GENERAL KNOWLEDGE IN ART", "BIOLOGY", "CHEMISTRY"],
        "Agricultural Science 1": ["GENERAL AGRICULTURE", "PHYSICS", "ANIMAL HUSBANDRY", "CHEMISTRY"],
        "Agricultural Science 2": ["GENERAL AGRICULTURE", "PHYSICS", "ANIMAL HUSBANDRY", "CHEMISTRY"],
        "Agricultural Science 3": ["GENERAL AGRICULTURE", "PHYSICS", "ANIMAL HUSBANDRY", "CHEMISTRY"],
        "Technical 1": ["ELECTIVE MATHEMATICS", "PHYSICS", "CHEMISTRY", "GRAPHIC DESIGN"],
        "Technical 2": ["ELECTIVE MATHEMATICS", "PHYSICS", "CHEMISTRY", "GRAPHIC DESIGN"],
        "Technical 3": ["ELECTIVE MATHEMATICS", "PHYSICS", "CHEMISTRY", "GRAPHIC DESIGN", "MUSIC"]
    }

    # Insert the pairs into the programme_subject table
    for programme, subjects in programme_subject_pairs.items():
        cursor.execute('SELECT id FROM programme WHERE programme_name = ?', (programme,))
        programme_row = cursor.fetchone()
        if programme_row is None:
            #print(f"Programme not found: {programme}")
            continue
        programme_id = programme_row['id']
        
        for subject in subjects:
            cursor.execute('SELECT id FROM subject WHERE subject_name = ?', (subject,))
            subject_row = cursor.fetchone()
            if subject_row is None:
                #print(f"Subject not found: {subject}")
                continue
            subject_id = subject_row['id']
            
            cursor.execute('INSERT INTO programme_subject (programme_id, subject_id) VALUES (?, ?)', (programme_id, subject_id))

    conn.commit()
    conn.close()

# Match and insert data

def insert_core_subjects():
    conn = get_db_connection()
    cursor = conn.cursor()

    # List of subjects to insert
    subjects = [
        "MATHEMATICS(CORE)",
        "ENGLISH LANGUAGE",
        "SCIENCE(CORE)",
        "SOCIAL STUDIES"
        "PYSICAL EDUCATION",
        "RELIGIOUS AND MORAL EDUCATION",
        "ICT(CORE)"
        
    ]

    # Insert subjects and set is_core to 1
    for subject in subjects:
        cursor.execute('INSERT OR IGNORE INTO subject (subject_name, is_core) VALUES (?, 1)', (subject,))

    # Commit the changes
    conn.commit()
    conn.close()
    
 

def update_student_table():
    # Connect to the SQLite database
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # List of new columns to add with their types
    new_columns = {
        'poatal_address': 'TEXT',
        'aggregate': 'INTEGER',
        'denomination': 'TEXT',
        'status': 'TEXT',
        'year':'TEXT',
        'class_id':'INTEGER'
    }
    
    # Fetch existing columns from the table
    cursor.execute("PRAGMA table_info(student)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    
    # Iterate over new columns and add them if they don't exist
    for column, col_type in new_columns.items():
        if column not in existing_columns:
            cursor.execute(f"ALTER TABLE student ADD COLUMN {column} {col_type}")
            print(f"Column {column} added to student table.")
        else:
            print(f"Column {column} already exists in student table.")
    
    # Commit changes and close connection
    conn.commit()
    conn.close()

# Example usage: update_student_table('path_to_your_database.db')






def setVersion(new_version):
    # Define paths within the function
    HOME_DIR = os.path.expanduser('~')
    APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
    VERSION_FILE = os.path.join(APP_DIR, 'version.json')

    # Ensure the directory exists
    os.makedirs(APP_DIR, exist_ok=True)
    
    # Initialize version_info
    version_info = {'old_version': None, 'new_version': new_version}

    # Check if the version file exists and read the existing version
    if os.path.exists(VERSION_FILE):
        with open(VERSION_FILE, 'r') as file:
            existing_info = json.load(file)
            version_info['old_version'] = existing_info.get('new_version')
    else:
        # If the file does not exist, initialize both versions to "1.0"
        version_info = {'old_version': '1.0', 'new_version': '1.0'}
    
    # Write the version to the version.json file
    with open(VERSION_FILE, 'w') as file:
        json.dump(version_info, file)
    print(f"Version updated to {new_version}")

def getVersion():
    # Define paths within the function
    HOME_DIR = os.path.expanduser('~')
    APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
    VERSION_FILE = os.path.join(APP_DIR, 'version.json')

    # Check if the version file exists
    if os.path.exists(VERSION_FILE):
        # Read the version from the version.json file
        with open(VERSION_FILE, 'r') as file:
            version_info = json.load(file)
            old_version = version_info.get('old_version')
            new_version = version_info.get('new_version')

            # Compare old and new versions
            if old_version == new_version:
                return 0  # Versions are the same
            else:
                # Update the file with new version set as both old and new
                version_info['old_version'] = new_version
                with open(VERSION_FILE, 'w') as file:
                    json.dump(version_info, file)
                return 1  # Versions were different and have been updated
    else:
        # If the file does not exist, create it and initialize version to "1.0"
        setVersion('1.0')
        return 1  # File created for the first time


def drop_subject():
    conn=get_db_connection()
    cursor=conn.cursor()
    #drop table if exists
    cursor.execute('DROP TABLE IF EXISTS subject')
    conn.commit()
    conn.close()
    

def initialize_remark():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS remark (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mark_range TEXT NOT NULL,
        remark TEXT NOT NULL
    )
''')
    
    # delete all records in the remark table
    cursor.execute('DELETE FROM remark')

    def shorten_remark(remark):
        return remark.split(',')[0]

    def insert_remarks(remarks, mark_range):
        for remark in remarks:
            cursor.execute('''
                INSERT INTO remark (mark_range, remark)
                VALUES (?, ?)
            ''', (mark_range, shorten_remark(remark)))

    remarks_90_100 = [
        "Remarkable achievement!",
        "Outstanding! Maintain this level.",
        "Excellent work!",
        "Superb performance!",
        "Great job! Keep it up!",
        "Impressive effort!",
        "Fantastic result!",
        "Exceptional work!",
        "Brilliant! Well done!",
        "Keep up the great work!",
        "Outstanding performance!",
        "Superb effort!",
        "Keep shining!",
        "Top-notch work!",
        "You're doing amazing!",
        "Excellent dedication!",
        "High quality work!",
        "Fantastic achievement!",
        "Wonderful effort!",
        "You're a star!",
        "Well done!",
        "Great!",
        "Awesome!",
        "Amazing!",
        "Excellent!",
        "Outstanding!",
        "Remarkable!",
        "Incredible!",
        "Wonderful!",
        "Superb!",
        "Really great job!",
        "Absolutely fantastic!",
        "Marvelous effort!",
        "Exceptional result!",
        "Incredible achievement!",
        "Amazing dedication!",
        "Brilliant performance!",
        "Wonderful job!",
        "Excellent effort!",
        "Great work!",
        "Superb result!",
        "Consistently great work!",
        "Impressive and remarkable!",
        "Outstanding continuous effort!",
        "Brilliant and inspiring!",
        "Fantastic ongoing performance!",
        "Excellent and admirable!",
        "Superb dedication and effort!",
        "Wonderful and consistent!",
        "Outstanding and superb!",
        "Remarkable and top-notch!",
        "You're a shining star!",
        "Keep up the excellent work!",
        "Your dedication is inspiring!",
        "You're setting a high standard!",
        "Your hard work is evident!",
        "You're an exemplary student!",
        "Your effort is paying off!",
        "Your performance is stellar!",
        "Your achievements are admirable!",
        "Your progress is remarkable!",
        "Your commitment is commendable!",
        "Your excellence is inspiring!"
        ]


    remarks_80_89 = [
        "Good performance, keep it up!",
        "Amazing! Keep performing.",
        "Well done!",
        "Great effort!",
        "Nice work!",
        "You're doing great!",
        "Keep up the good work!",
        "Very good!",
        "Impressive performance!",
        "Keep pushing!",
        "Nice job!",
        "Great work!",
        "Keep going!",
        "Well done!",
        "Good job!",
        "Impressive!",
        "Fantastic!",
        "Excellent!",
        "Amazing!",
        "Well done!",
        "Solid effort! Keep striving!",
        "Very impressive work!",
        "You are on the right track!",
        "Great consistency! Keep it up!",
        "Your hard work is showing!",
        "Keep up the solid performance!",
        "You're making great progress!",
        "Your effort is commendable!",
        "You're doing very well!",
        "Fantastic job! Keep pushing!",
        "Excellent progress! Keep it up!",
        "Your performance is improving!",
        "You're achieving great results!",
        "Keep up the dedication!",
        "Your work is very good!",
        "Stay focused and keep going!",
        "Your effort is paying off!",
        "Keep up the good performance!",
        "Your progress is impressive!",
        "Keep striving for excellence!",
        "You're doing a fantastic job!"
    ]


    remarks_70_79 = [
        "Good job, strive for more!",
        "Keep it up, you can do even better!",
        "Well done, aim higher!",
        "Good effort, keep going!",
        "Nice work, push for more!",
        "Solid performance, reach higher!",
        "Keep improving, great job!",
        "Doing well, keep it up!",
        "Good work, continue to excel!",
        "Great start, keep pushing!",
        "Good effort!",
        "Well done!",
        "Keep trying!",
        "Nice job!",
        "Great start!",
        "Well done!",
        "Keep going!",
        "Nice effort!",
        "Keep pushing!",
        "Great effort!",
        "You're on the right track, keep it up!",
        "Good job, aim for higher goals!",
        "Solid start, continue improving!",
        "You're doing well, strive for more!",
        "Nice effort, keep progressing!",
        "Good work, reach for higher levels!",
        "Keep pushing, you're doing well!",
        "Great start, aim higher!",
        "Good effort, continue to excel!",
        "Solid performance, keep improving!",
        "Well done, push for more!",
        "Nice job, keep striving!",
        "Great effort, aim for excellence!",
        "Keep trying, you're doing great!",
        "Good work, stay focused!",
        "Nice effort, keep advancing!",
        "Well done, keep aiming higher!",
        "Keep improving, you're on the right path!",
        "Good job, keep up the progress!",
        "Solid work, continue striving for more!"
    ]


    remarks_60_69 = [
        "Room for improvement, keep trying!",
        "Keep pushing, you can do it!",
        "Decent effort, aim higher!",
        "Good start, strive for more!",
        "Keep working hard, you'll get there!",
        "Not bad, but you can do better!",
        "Keep at it, you have potential!",
        "You're improving, keep going!",
        "Continue to work hard, you can succeed!",
        "Keep trying, you're getting there!",
        "Keep pushing!",
        "Try harder!",
        "Keep going!",
        "Not bad!",
        "You can!",
        "Push more!",
        "Keep striving!",
        "Try more!",
        "Good effort!",
        "Well done!",
        "You're on the right path, keep pushing!",
        "Decent start, aim for higher!",
        "Keep up the effort, you can improve!",
        "You're getting better, keep at it!",
        "Good job, strive for more!",
        "Keep working, you'll reach your goals!",
        "Not bad, keep aiming higher!",
        "You have potential, keep going!",
        "Keep improving, you're on the way!",
        "Continue to push yourself, you can do it!",
        "Keep trying, progress is happening!",
        "Keep at it, you'll get there!",
        "You're making progress, keep it up!",
        "Good start, keep pushing forward!",
        "Keep striving, you have what it takes!",
        "Push harder, you can achieve more!",
        "Keep going, you're doing fine!",
        "Keep working, success is within reach!",
        "Keep improving, you're getting better!",
        "Keep trying, you're making headway!"
    ]


    remarks_50_59 = [
        "Needs more effort, keep pushing!",
        "Keep working, you can improve!",
        "Not bad, but aim higher!",
        "Keep trying, you can do better!",
        "You're making progress, keep at it!",
        "Needs improvement, keep working!",
        "Keep striving, you have potential!",
        "Don't give up, keep trying!",
        "Work harder, you can succeed!",
        "Keep pushing, you're getting there!",
        "Try more!",
        "Work hard!",
        "Push on!",
        "Keep at it!",
        "Keep striving!",
        "Don't stop!",
        "Push harder!",
        "Improve more!",
        "Keep working!",
        "Keep going!",
        "You have potential, keep trying!",
        "Needs more dedication, keep working!",
        "You're improving, aim higher!",
        "Keep pushing, you can do it!",
        "Work harder, you're getting better!",
        "Keep at it, progress is showing!",
        "Don't give up, you can succeed!",
        "Keep striving, you'll improve!",
        "Push harder, you can reach higher!",
        "Keep working, you're on the way!",
        "You're capable, keep trying!",
        "Needs more effort, don't stop!",
        "Keep improving, you can do it!",
        "Work harder, potential is there!",
        "Keep trying, you'll get better!",
        "Push more, you can succeed!",
        "Keep going, progress is happening!",
        "Strive for more, you can do it!",
        "Work harder, you're making progress!",
        "Keep at it, you can improve!",
        "Keep striving, don't give up!"
    ]


    remarks_40_49 = [
        "Needs more effort, keep pushing!",
        "Keep working, you can improve!",
        "Not bad, but aim higher!",
        "Keep trying, you can do better!",
        "You're making progress, keep at it!",
        "Needs improvement, keep working!",
        "Keep striving, you have potential!",
        "Don't give up, keep trying!",
        "Work harder, you can succeed!",
        "Keep pushing, you're getting there!",
        "Keep going!",
        "Try harder!",
        "Don't stop!",
        "Aim higher!",
        "Push more!",
        "Work harder!",
        "Try more!",
        "Keep improving!",
        "Keep striving!",
        "Push harder!",
        "You can do better, keep trying!",
        "Needs more dedication, keep at it!",
        "Aim higher, you have potential!",
        "Keep working, improvement is possible!",
        "Keep pushing, you can get there!",
        "You have potential, strive for more!",
        "Work harder, progress will come!",
        "Don't stop, you can improve!",
        "Push more, you can succeed!",
        "Keep at it, you can do it!",
        "Needs more effort, keep going!",
        "You're improving, aim for more!",
        "Keep striving, you can get better!",
        "Work harder, you're making progress!",
        "Try more, you can reach higher!",
        "Don't stop, keep pushing forward!",
        "Keep working, you can get better!",
        "Push harder, you have the potential!",
        "Keep improving, don't give up!",
        "Aim higher, you can succeed!",
        "Keep trying, you can achieve more!"
    ]

    remarks_30_39 = [
        "Struggling, keep trying!",
        "Needs significant improvement!",
        "Work harder, you can do better!",
        "Needs more effort, keep pushing!",
        "Keep working, you can improve!",
        "Not bad, but aim higher!",
        "Keep trying, you can do better!",
        "You're making progress, keep at it!",
        "Needs improvement, keep working!",
        "Keep striving, you have potential!",
        "Try more!",
        "Work hard!",
        "Push on!",
        "Don't stop!",
        "Keep going!",
        "Aim higher!",
        "Work harder!",
        "Push more!",
        "Try harder!",
        "Improve more!",
        "You can do it, keep pushing!",
        "Needs more focus, keep trying!",
        "Work harder, aim for higher!",
        "Don't stop, keep improving!",
        "Keep trying, progress is possible!",
        "You're capable, push harder!",
        "Needs more dedication, keep at it!",
        "Keep pushing, you can get better!",
        "Work harder, you have potential!",
        "Don't give up, keep striving!",
        "Aim higher, keep working!",
        "Keep improving, you can do it!",
        "Push more, success is possible!",
        "Keep going, you can get better!",
        "Try more, you're making progress!",
        "Keep striving, aim higher!",
        "Work harder, don't give up!",
        "You can improve, keep pushing!",
        "Don't stop, you can succeed!",
        "Keep at it, progress will come!",
        "Strive for more, you can do it!"
    ]


    remarks_20_29 = [
        "Struggling, keep trying!",
        "Needs significant improvement!",
        "Work harder, you can do better!",
        "Needs more effort, keep pushing!",
        "Keep working, you can improve!",
        "Not bad, but aim higher!",
        "Keep trying, you can do better!",
        "You're making progress, keep at it!",
        "Needs improvement, keep working!",
        "Keep striving, you have potential!",
        "Try more!",
        "Work hard!",
        "Push on!",
        "Don't stop!",
        "Keep going!",
        "Aim higher!",
        "Work harder!",
        "Push more!",
        "Try harder!",
        "Improve more!",
        "Needs more focus, keep trying!",
        "Struggling, aim for improvement!",
        "Keep working, aim higher!",
        "More effort needed, keep pushing!",
        "Work harder, progress will come!",
        "Keep striving, you can improve!",
        "Push more, you have potential!",
        "Don't give up, keep trying!",
        "Needs dedication, keep working!",
        "You're capable, aim higher!",
        "Keep going, improvement is possible!",
        "Push harder, you can succeed!",
        "Keep trying, progress will come!",
        "Don't stop, keep striving!",
        "Work harder, aim for higher!",
        "Needs more effort, keep at it!",
        "You can do better, keep pushing!",
        "Keep working, don't give up!",
        "Aim higher, you can improve!",
        "Push more, progress is possible!",
        "Try harder, you have potential!"
    ]


    remarks_10_19 = [
        "Struggling, keep trying!",
        "Needs significant improvement!",
        "Work harder, you can do better!",
        "Needs more effort, keep pushing!",
        "Keep working, you can improve!",
        "Not bad, but aim higher!",
        "Keep trying, you can do better!",
        "You're making progress, keep at it!",
        "Needs improvement, keep working!",
        "Keep striving, you have potential!",
        "Try more!",
        "Work hard!",
        "Push on!",
        "Don't stop!",
        "Keep going!",
        "Aim higher!",
        "Work harder!",
        "Push more!",
        "Try harder!",
        "Improve more!"
    ]

    remarks_0_9 = [
        "Struggling, keep trying!",
        "Needs significant improvement!",
        "Work harder, you can do better!",
        "Needs more effort, keep pushing!",
        "Keep working, you can improve!",
        "Not bad, but aim higher!",
        "Keep trying, you can do better!",
        "You're making progress, keep at it!",
        "Needs improvement, keep working!",
        "Keep striving, you have potential!",
        "Try more!",
        "Work hard!",
        "Push on!",
        "Don't stop!",
        "Keep going!",
        "Aim higher!",
        "Work harder!",
        "Push more!",
        "Try harder!",
        "Improve more!"
    ]

    insert_remarks(remarks_90_100, "90-100")
    insert_remarks(remarks_80_89, "80-89.999")
    insert_remarks(remarks_70_79, "70-79.999")
    insert_remarks(remarks_60_69, "60-69.999")
    insert_remarks(remarks_50_59, "50-59.999")
    insert_remarks(remarks_40_49, "40-49.999")
    insert_remarks(remarks_30_39, "30-39.999")
    insert_remarks(remarks_20_29, "20-29.999")
    insert_remarks(remarks_10_19, "10-19.999")
    insert_remarks(remarks_0_9, "0-9.999")

    conn.commit()
    conn.close()
    
def create_indexes():
    index_queries = [
        "CREATE INDEX IF NOT EXISTS idx_year ON assessment (year);",
        "CREATE INDEX IF NOT EXISTS idx_class_id ON assessment (class_id);",
        "CREATE INDEX IF NOT EXISTS idx_subject_id ON assessment (subject_id);",
        "CREATE INDEX IF NOT EXISTS idx_semester_id ON assessment (semester_id);"
    ]

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        for query in index_queries:
            cursor.execute(query)
        conn.commit()
        conn.close()
        print("Indexes created successfully.")
    except Exception as e:
        print(f"Failed to create indexes: {e}")

# Call this function to create the indexes



if getVersion() == 1:
    initialize_database()
    initialize_remark()
    update_student_table()
    insert_subjects()
    insert_core_subjects()
    update_short_names()
    insert_class_names(class_names)
    update_programme()
    insert_programme_names()
    match_programmes_subjects()
    create_indexes()
    CPS.insert_class_programme_subject()
    CPS.includeCoreSubjectsIntoProgramme_subject()
    CPS.includeCoreSubjectsIntoClassProgrammeSubject()




