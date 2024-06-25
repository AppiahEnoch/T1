import re
import sqlite3
import os

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

def extract_programme_from_class(class_name):
    """Extract the programme name from the class name using regex."""
    pattern = r"\d\s(.+)"
    match = re.search(pattern, class_name)
    if match:
        return match.group(1)
    return None

def get_class_and_programme_ids():
    """Fetch and return all class names and their corresponding programme names, along with their IDs."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, class_name FROM class_name')
    class_rows = cursor.fetchall()
    
    cursor.execute('SELECT id, programme_name FROM programme')
    programme_rows = cursor.fetchall()
    
    programme_dict = {programme['programme_name']: programme['id'] for programme in programme_rows}
    
    class_programme_ids = []
    
    for class_row in class_rows:
        class_id = class_row['id']
        class_name = class_row['class_name']
        programme_name = extract_programme_from_class(class_name)
        if programme_name in programme_dict:
            programme_id = programme_dict[programme_name]
            class_programme_ids.append((class_id, programme_id))
            #print(f"Class ID: {class_id}, Class Name: {class_name}, Programme Name: {programme_name}, Programme ID: {programme_id}")
    
    conn.close()
    return class_programme_ids

def insert_class_programme_subject():
    """Insert the class, programme, and subject IDs into the class_programme_subject table."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        class_programme_ids = get_class_and_programme_ids()
        
        for class_id, programme_id in class_programme_ids:
            cursor.execute('''
                SELECT subject_id FROM programme_subject
                WHERE programme_id = ?
            ''', (programme_id,))
            subject_rows = cursor.fetchall()
            
            for subject_row in subject_rows:
                subject_id = subject_row['subject_id']
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO class_programme_subject (class_id, programme_id, subject_id)
                        VALUES (?, ?, ?)
                    ''', (class_id, programme_id, subject_id))
                except Exception as e:
                    print(f"Error inserting subject {subject_id} into class {class_id} and programme {programme_id}: {e}")
        
        conn.commit()
    except Exception as e:
        print(f"Error inserting class, programme, and subject IDs: {e}")
    finally:
        if conn:
            conn.close()

    
    
def get_subjects_by_class_id(class_id):
    """Fetch and return all subject names done by a given class, including core subjects listed last."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get subjects associated with the class
        cursor.execute('''
            SELECT subject.subject_name 
            FROM class_programme_subject
            JOIN subject ON class_programme_subject.subject_id = subject.id
            WHERE class_programme_subject.class_id = ?
        ''', (class_id,))
        subject_rows = cursor.fetchall()
        subject_names = [row['subject_name'] for row in subject_rows]
        
        # Get core subjects
        cursor.execute('''
            SELECT subject_name 
            FROM subject
            WHERE is_core = 1
        ''')
        core_subject_rows = cursor.fetchall()
        core_subject_names = [row['subject_name'] for row in core_subject_rows]
        
        # Remove core subjects from subject_names if they exist
        subject_names = [name for name in subject_names if name not in core_subject_names]
        
        # Combine the lists, appending core subjects last
        all_subject_names = subject_names + core_subject_names
    except Exception as e:
        print(f"Error fetching subjects by class id {class_id}: {e}")
        all_subject_names = []
    finally:
        if conn:
            conn.close()
    
    return all_subject_names



def get_programme_by_class_id(class_id):
    """Fetch and return the programme name associated with a given class."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT programme_id 
            FROM class_programme_subject
            WHERE class_id = ?
            LIMIT 1
        ''', (class_id,))
        
        row = cursor.fetchone()
        programme_id = row['programme_id'] if row else None
        
        if programme_id:
            cursor.execute('''
                SELECT programme_name 
                FROM programme
                WHERE id = ?
            ''', (programme_id,))
            
            row = cursor.fetchone()
            programme_name = row['programme_name'] if row else None
        else:
            programme_name = None
    except Exception as e:
        print(f"Error fetching programme by class id {class_id}: {e}")
        programme_name = None
    finally:
        if conn:
            conn.close()
    
    return programme_name



    
def includeCoreSubjectsIntoProgramme_subject():
    """Include all core subjects into the programme_subject table for each programme."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve all core subjects
        cursor.execute('SELECT id FROM subject WHERE is_core = 1')
        core_subjects = cursor.fetchall()

        # Retrieve all programmes
        cursor.execute('SELECT id FROM programme')
        programmes = cursor.fetchall()

        # Insert core subjects into the programme_subject table for each programme
        for programme in programmes:
            for subject in core_subjects:
                try:
                    cursor.execute('''
                        INSERT OR IGNORE INTO programme_subject (subject_id, programme_id)
                        VALUES (?, ?)
                    ''', (subject['id'], programme['id']))
                except Exception as e:
                    print(f"Error inserting subject {subject['id']} into programme {programme['id']}: {e}")

        conn.commit()
    except Exception as e:
        print(f"Error including core subjects into programme_subject: {e}")
    finally:
        if conn:
            conn.close()

    
def includeCoreSubjectsIntoClassProgrammeSubject():
    """Include all core subjects into the class_programme_subject table for each class and programme."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Retrieve all classes
        cursor.execute('SELECT id, programme FROM class_name')
        classes = cursor.fetchall()

        # Retrieve all core subjects
        cursor.execute('SELECT id FROM subject WHERE is_core = 1')
        core_subjects = cursor.fetchall()

        # Insert core subjects into the class_programme_subject table for each class and programme
        for class_row in classes:
            class_id = class_row['id']
            programme_name = class_row['programme']

            # Get programme id from programme name
            cursor.execute('SELECT id FROM programme WHERE programme_name = ?', (programme_name,))
            programme = cursor.fetchone()
            if programme:
                programme_id = programme['id']
                for subject in core_subjects:
                    try:
                        cursor.execute('''
                            INSERT OR IGNORE INTO class_programme_subject (class_id, programme_id, subject_id)
                            VALUES (?, ?, ?)
                        ''', (class_id, programme_id, subject['id']))
                    except Exception as e:
                        print(f"Error inserting subject {subject['id']} into class {class_id} and programme {programme_id}: {e}")

        conn.commit()
    except Exception as e:
        print(f"Error including core subjects into class_programme_subject: {e}")
    finally:
        if conn:
            conn.close()



    
