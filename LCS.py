from crud import get_db_connection
import re


def get_subjects_by_class_id(class_id):
    """Fetch and return all subject names and ids done by a given class, including core subjects listed last."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get subjects associated with the class
    cursor.execute('''
        SELECT DISTINCT subject.subject_name, subject.id
        FROM class_programme_subject
        JOIN subject ON class_programme_subject.subject_id = subject.id
        WHERE class_programme_subject.class_id = ?
    ''', (class_id,))
    subject_rows = cursor.fetchall()
    subject_names = [(row['subject_name'], row['id']) for row in subject_rows]
    
    # Get core subjects
    cursor.execute('''
        SELECT subject_name, id
        FROM subject
        WHERE is_core = 1
    ''')
    core_subject_rows = cursor.fetchall()
    core_subject_names = [(row['subject_name'], row['id']) for row in core_subject_rows]
    
    # Remove core subjects from subject_names if they exist
    subject_names = [(name, subject_id) for name, subject_id in subject_names if (name, subject_id) not in core_subject_names]
    
    # Combine the lists, appending core subjects last
    all_subject_names = subject_names + core_subject_names
    
    conn.close()
    return all_subject_names




def get_programme_by_class_id(class_id):
    """Fetch and return the programme name and id associated with a given class."""
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
            SELECT id, programme_name 
            FROM programme
            WHERE id = ?
        ''', (programme_id,))
        
        row = cursor.fetchone()
        programme_name = row['programme_name'] if row else None
        programme = (programme_id, programme_name)
    else:
        programme = None
    
    conn.close()
    return programme




def extract_sort_keys(class_name):
    """Extract the numeric and middle word(s) for sorting."""
    match = re.match(r'(\d+)\s+(.*?)\s+(\d+)', class_name)
    if match:
        return match.group(2), int(match.group(1)), int(match.group(3))
    return class_name, float('inf'), float('inf')

def get_classes_by_subject_id(subject_id):
    """Fetch and return all class names and ids associated with a given subject. 
    If the subject is a core subject, return all class names."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if the subject is a core subject
    cursor.execute('''
        SELECT is_core
        FROM subject
        WHERE id = ?
    ''', (subject_id,))
    
    row = cursor.fetchone()
    is_core = row['is_core'] if row else 0
    
    if is_core:
        # Fetch all class names if the subject is a core subject
        cursor.execute('''
            SELECT id, class_name
            FROM class_name
        ''')
    else:
        # Fetch class names associated with the subject
        cursor.execute('''
            SELECT DISTINCT class_name.id, class_name.class_name
            FROM class_programme_subject
            JOIN class_name ON class_programme_subject.class_id = class_name.id
            WHERE class_programme_subject.subject_id = ?
        ''', (subject_id,))
    
    class_rows = cursor.fetchall()
    classes = [(row['class_name'], row['id']) for row in class_rows]

    # Sort classes by the extracted keys
    sorted_classes = sorted(classes, key=lambda x: extract_sort_keys(x[0]))
    
    conn.close()
    #print(sorted_classes)
    return sorted_classes

def update_student_programme():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Fetch all assessments and count programme occurrences for each student
    cursor.execute('''
        SELECT student_id, programme_id 
        FROM assessment
    ''')
    assessments = cursor.fetchall()

    student_programmes = {}
    for student_id, programme_id in assessments:
        if student_id not in student_programmes:
            student_programmes[student_id] = {}
        if programme_id not in student_programmes[student_id]:
            student_programmes[student_id][programme_id] = 0
        student_programmes[student_id][programme_id] += 1

    for student_id, programmes in student_programmes.items():
        # Determine the programme ID with the max number of appearances
        true_programme_id = max(programmes, key=programmes.get)

        # Fetch the programme name from the programme table
        cursor.execute('''
            SELECT programme_name 
            FROM programme 
            WHERE id = ?
        ''', (true_programme_id,))
        programme_name = cursor.fetchone()

        if programme_name:
            programme_name = programme_name[0]
            # print(f"Student ID: {student_id}, Programme Name: {programme_name}")
            # Update the prog column of the student table with the programme name if it is NULL or empty
            cursor.execute('''
                UPDATE student 
                SET prog = ? 
                WHERE student_id = ?
            ''', (programme_name, student_id))

    # Commit the changes
    conn.commit()
    conn.close()


def reset_guardian_title():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update the guardian_title to NULL where it is 'BOARDING' or 'DAY' (case insensitive)
    cursor.execute('''
        UPDATE student
        SET guardian_title = NULL
        WHERE UPPER(guardian_title) IN ('BOARDING', 'DAY')
    ''')

    # Commit the changes
    conn.commit()
    print("Guardian titles reset successfully.")
    conn.close()

def delete_invalid_assessment_records():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Delete assessment records where the combination of class_id, subject_id, and programme_id does not exist in the class_programme_subject table
    cursor.execute('''
        DELETE FROM assessment
        WHERE NOT EXISTS (
            SELECT 1
            FROM class_programme_subject
            WHERE class_programme_subject.class_id = assessment.class_id
            AND class_programme_subject.subject_id = assessment.subject_id
            AND class_programme_subject.programme_id = assessment.programme_id
        )
    ''')

    # Commit the changes
    conn.commit()
    print("Deleted assessment records removed successfully.")
    conn.close()



import sqlite3

def delete_invalid_assessment_records():
    conn = get_db_connection()
    cursor = conn.cursor()

    batch_size = 10000  # Adjust based on your system's capabilities
    total_deleted = 0

    try:
        # SQLite automatically starts a transaction when needed
        while True:
            # Find all subject_id and class_id combinations in computed_assessment
            # that don't exist in assessment
            cursor.execute('''
                SELECT DISTINCT ca.subject_id, ca.class_id
                FROM computed_assessment ca
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM assessment a
                    WHERE a.subject_id = ca.subject_id
                    AND a.class_id = ca.class_id
                )
                LIMIT ?
            ''', (batch_size,))

            invalid_combinations = cursor.fetchall()

            if not invalid_combinations:
                break  # No more invalid combinations

            # Delete the invalid records
            placeholders = ','.join(['(?,?)'] * len(invalid_combinations))
            flat_list = [item for sublist in invalid_combinations for item in sublist]
            
            cursor.execute(f'''
                DELETE FROM computed_assessment
                WHERE (subject_id, class_id) IN ({placeholders})
            ''', flat_list)

            deleted_count = cursor.rowcount
            total_deleted += deleted_count

            # Commit the batch
            conn.commit()

            print(f"Deleted {deleted_count} records with invalid subject_id and class_id combinations in this batch.")

            if len(invalid_combinations) < batch_size:
                break  # Last batch processed

        print(f"Total deleted records: {total_deleted}")

    except sqlite3.Error as e:
        print(f"An SQLite error occurred: {e}")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        conn.close()


def update_student_boarding_and_house():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Update status to 'BOARDING' where it's NULL
    cursor.execute('''
        UPDATE student
        SET status = 'BOARDING'
        WHERE status IS NULL
    ''')

    # Get the least house_id
    cursor.execute('SELECT MIN(id) FROM house')
    least_house_id = cursor.fetchone()[0]

    if least_house_id is not None:
        # Update house_id to the least id where it's NULL
        cursor.execute('''
            UPDATE student
            SET house_id = ?
            WHERE house_id IS NULL
        ''', (least_house_id,))

    # Commit the changes
    conn.commit()
    print("Student boarding status and house_id updated successfully.")
    conn.close()
    
    
    
def update__year_24():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Update year to '2023/2024' for all rows
    cursor.execute('''
        UPDATE assessment
        SET year = '2023/2024'
    ''')
    
    # Commit the changes
    conn.commit()
    
    # Get the number of rows updated
    rows_affected = cursor.rowcount
    
    print(f"Assessment year updated successfully. {rows_affected} rows affected.")
    
    conn.close()
    
    
    
