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
            print(f"Student ID: {student_id}, Programme Name: {programme_name}")
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
    conn.close()


def validate_and_cleanup_assessments():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Query to check and delete invalid assessment records
    cursor.execute('''
        DELETE FROM computed_assessment
        WHERE NOT EXISTS (
            SELECT 1
            FROM class_programme_subject
            WHERE class_programme_subject.class_id = computed_assessment.class_id
            AND class_programme_subject.subject_id = computed_assessment.subject_id
        )
    ''')

    # Commit the changes to the database
    conn.commit()
    conn.close()

    print("Invalid assessment records removed successfully.")
