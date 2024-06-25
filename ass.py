import sqlite3
import pandas as pd
from crud import get_db_connection


    


def create_temp_table():
    conn = get_db_connection()
    cursor = conn.cursor()
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
    cursor.execute('DELETE FROM computed_assessment')  # Truncate the table
    conn.commit()
    conn.close()



def get_ordinal_suffix(number):
    if number is None or number == "":
        return "N/A"
    if not isinstance(number, int):
        return str(number)
    if number % 100 in {11, 12, 13}:
        return f"{number}th"
    return f"{number}{['th', 'st', 'nd', 'rd', 'th'][min(number % 10, 4)]}"


def determine_grade(score):
    #print(f"Determining grade for score: {score}")
    if 80 <= score <= 100: return 'A1'
    if 75 <= score < 80: return 'B2'
    if 70 <= score < 75: return 'B3'
    if 65 <= score < 70: return 'C4'
    if 60 <= score < 65: return 'C5'
    if 55 <= score < 60: return 'C6'
    if 50 <= score < 55: return 'D7'
    if 45 <= score < 50: return 'E8'
    if 0 <= score < 45: return 'F9'
    return 'N/A'



def determine_remarks(score):
    if 80 <= score <= 100: return 'Excellent'
    if 75 <= score < 80: return 'Very Good'
    if 70 <= score < 75: return 'Good'
    if 65 <= score < 70: return 'Credit'
    if 60 <= score < 65: return 'Credit'
    if 55 <= score < 60: return 'Credit'
    if 50 <= score < 55: return 'Pass'
    if 45 <= score < 50: return 'Pass'
    if 0 <= score < 45: return 'Fail'
    return 'N/A'


def assign_number(grade):
    grades = {
        'A1': 1, 
        'B2': 2, 
        'B3': 3, 
        'C4': 4, 
        'C5': 5, 
        'C6': 6, 
        'D7': 7, 
        'E8': 8, 
        'F9': 9
    }
    #print(f"Assigning number for grade: {grade}")
    return grades.get(grade, 'N/A')


def delete_all_from_computed_assessment():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM computed_assessment')
    conn.commit()
    conn.close()
    

def compute_and_store_assessments():
    create_temp_table()
    delete_all_from_computed_assessment()
    conn = get_db_connection()
    cursor = conn.cursor()

    # Retrieve the percentage values
    cursor.execute('SELECT class_score, exam_score FROM score_percentage WHERE id = 1')
    percentage_values = cursor.fetchone()
    if not percentage_values:
        raise ValueError("Score percentages not set in the score_percentage table.")
    
    class_score_percentage = float(percentage_values['class_score'])
    exam_score_percentage = float(percentage_values['exam_score'])

    cursor.execute('''
        SELECT a.student_id, a.class_id, a.semester_id, a.subject_id, a.year, 
               a.class_score, a.exam_score, a.teacher_initial_letters,
               s.is_core AS isCore, s.short_name
        FROM assessment a
        JOIN subject s ON a.subject_id = s.id
    ''')

    rows = cursor.fetchall()
    student_scores = {}
    for row in rows:
        student_id = row['student_id']
        if student_id not in student_scores:
            student_scores[student_id] = {
                'class_id': row['class_id'],
                'semester_id': row['semester_id'],
                'year': row['year'],
                'subjects': [],
                'total_score': 0,
                'subject_count': 0
            }

        try:
            class_score = str(row['class_score']).strip()
            exam_score = str(row['exam_score']).strip()

            if class_score == 'N/A' or exam_score == 'N/A':
                # Handle N/A scores
                weighted_class_score = weighted_exam_score = subject_total_score = 'N/A'
            else:
                class_score = float(class_score or 0)
                exam_score = float(exam_score or 0)

                # Ensure scores are within valid range (0-100)
                class_score = max(0, min(100, class_score))
                exam_score = max(0, min(100, exam_score))

                weighted_class_score = round(class_score * class_score_percentage / 100.0, 1)
                weighted_exam_score = round(exam_score * exam_score_percentage / 100.0, 1)
                subject_total_score = round(weighted_class_score + weighted_exam_score, 1)
                
                

                # Ensure subject total score doesn't exceed 100
                subject_total_score = min(100, subject_total_score)

                student_scores[student_id]['total_score'] += subject_total_score
                student_scores[student_id]['subject_count'] += 1

            student_scores[student_id]['subjects'].append({
                'subject_id': row['subject_id'],
                'class_score': weighted_class_score,
                'exam_score': weighted_exam_score,
                'subject_total_score': subject_total_score,
                'isCore': row['isCore'],
                'teacher_initial_letters': row['teacher_initial_letters'],
                'short_name': row['short_name']
            })
        except ValueError as e:
            print(f"Error processing scores for student {student_id}, subject {row['subject_id']}: {e}")

    assessments = []
    for student_id, data in student_scores.items():
        for subject in data['subjects']:
            subject_total_score = subject['subject_total_score']
            
            grade = determine_grade(subject_total_score)
            number_equivalence = assign_number(grade)
            remarks = determine_remarks(subject_total_score)
            if student_id == "BB1460":
                print(f"Student ID: {student_id}, Subject ID: {subject['subject_id']}, Total Score: {subject_total_score}, Grade: {grade}, Number Equivalence: {number_equivalence}, Remarks: {remarks}")
            assessments.append((
                student_id, data['class_id'], data['semester_id'], subject['subject_id'], data['year'],
                subject['class_score'], subject['exam_score'], subject['subject_total_score'],
                grade, number_equivalence, remarks, subject['isCore'],
                subject['teacher_initial_letters'], subject['short_name'], 0  # Initial rank placeholder
            ))

    # Compute ranks for each subject within the same class, semester, and year
    df = pd.DataFrame(assessments, columns=[
        'student_id', 'class_id', 'semester_id', 'subject_id', 'year',
        'class_score', 'exam_score', 'total_score', 'grade', 'number_equivalence',
        'remarks', 'isCore', 'teacher_initial_letters', 'short_name', 'rank'
    ])
    df['rank'] = df.groupby(['class_id', 'semester_id', 'subject_id', 'year'])['total_score'].rank(ascending=False, method='min').astype(int)

    for assessment in df.itertuples(index=False):
        student_id = assessment.student_id
        cursor.execute('''
            SELECT COUNT(*) FROM computed_assessment 
            WHERE student_id = ? AND class_id = ? AND semester_id = ? AND subject_id = ? AND year = ?
        ''', (assessment.student_id, assessment.class_id, assessment.semester_id, assessment.subject_id, assessment.year))
        exists = cursor.fetchone()[0]

        if exists:
            cursor.execute('''
                UPDATE computed_assessment
                SET class_score = ?, exam_score = ?, total_score = ?, grade = ?, number_equivalence = ?, remarks = ?, isCore = ?, teacher_initial_letters = ?, short_name = ?, rank = ?
                WHERE student_id = ? AND class_id = ? AND semester_id = ? AND subject_id = ? AND year = ?
            ''', (assessment.class_score, assessment.exam_score, assessment.total_score, assessment.grade, assessment.number_equivalence, assessment.remarks, assessment.isCore, assessment.teacher_initial_letters, assessment.short_name, assessment.rank, assessment.student_id, assessment.class_id, assessment.semester_id, assessment.subject_id, assessment.year))
        else:
            cursor.execute('''
                INSERT INTO computed_assessment (student_id, class_id, semester_id, subject_id, year, class_score, exam_score, total_score, grade, number_equivalence, remarks, isCore, teacher_initial_letters, short_name, rank)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (assessment.student_id, assessment.class_id, assessment.semester_id, assessment.subject_id, assessment.year, assessment.class_score, assessment.exam_score, assessment.total_score, assessment.grade, assessment.number_equivalence, assessment.remarks, assessment.isCore, assessment.teacher_initial_letters, assessment.short_name,get_ordinal_suffix(assessment.rank)))

    conn.commit()
    conn.close()

    print("Assessment computation and update completed.")


def get_student_aggregate(student_id, class_id, semester_id, year):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT number_equivalence, 
               (SELECT subject_name FROM subject WHERE subject.id = computed_assessment.subject_id) as subject_name,
               (SELECT is_core FROM subject WHERE subject.id = computed_assessment.subject_id) as is_core
        FROM computed_assessment
        WHERE student_id = ? AND class_id = ? AND semester_id = ? AND year = ?
    ''', (student_id, class_id, semester_id, year))
    records = cursor.fetchall()
    abbreMath = "MATHEMATICS(CORE)"
    abbreSci = "SCIENCE(CORE)"
    abbreEng = "ENGLISH LANGUAGE"
    core_subject_names = {abbreMath: 9, abbreSci: 9, abbreEng: 9}
    core_subjects = {}
    elective_subjects = []
    for record in records:
        subject_name = record["subject_name"]
        number_equivalence = record["number_equivalence"]
        is_core = record["is_core"]
        if is_core == 1:
            if abbreMath in subject_name:
                core_subjects[abbreMath] = number_equivalence
            elif abbreSci in subject_name:
                core_subjects[abbreSci] = number_equivalence
            elif abbreEng in subject_name:
                core_subjects[abbreEng] = number_equivalence
            else:
                core_subjects[subject_name] = number_equivalence
        else:
            elective_subjects.append(number_equivalence)
    # Ensure core subjects contain MATH, SCI, ENG with default score of 9 if not found
    for subject, default_score in core_subject_names.items():
        if subject not in core_subjects:
            core_subjects[subject] = default_score
    # Convert elective_subjects to integers for sorting
    try:
        elective_subjects = [int(subject) for subject in elective_subjects]
    except ValueError as e:
        print(f"Error converting elective subjects to integers: {e}")
        # Filter out non-integer elements
        elective_subjects = [subject for subject in elective_subjects if isinstance(subject, int)]
    elective_subjects = sorted(elective_subjects)
    # Select the scores for MATH, SCI, ENG
    best_3_core = [core_subjects[subject] for subject in [abbreMath, abbreSci, abbreEng]]
    # Sort and select the top 3 elective subjects
    best_3_elective = elective_subjects[:3]
            
    # if student_id == "BB1460":
    #     print("Core Subjectsxxxxx:", core_subjects)
    #     print("Elective Subjectsxx:", elective_subjects)
    #     # show the best 3 core subjects
    #     print("Best 3 Core Subjects:", best_3_core)
    #     # show the best 3 elective subjects
    #     print("Best 3 Elective Subjects:", best_3_elective)
    
    aggregate = sum(best_3_core) + sum(best_3_elective)
    aggregate = round(aggregate, 1)
    if student_id == "BB1460":
        print("Aggregate:", aggregate)
    
    cursor.execute('SELECT name FROM student WHERE student_id = ?', (student_id,))
    student_name = cursor.fetchone()['name']
    #print(f"Aggregate for student id and name {student_id} - {student_name} is {aggregate}")
    
    # Print all grades for the core subjects
    for subject, grade in core_subjects.items():
        if student_id == "BB1460":
            if grade == 1:
                grade_letter = "A1"
            elif grade == 2:
                grade_letter = "B2"
            elif grade == 3:
                grade_letter = "B3"
            elif grade == 4:
                grade_letter = "C4"
            elif grade == 5:
                grade_letter = "C5"
            elif grade == 6:
                grade_letter = "C6"
            elif grade == 7:
                grade_letter = "D7"
            elif grade == 8:
                grade_letter = "E8"
            else:
                grade_letter = "F9"
            #print(f"{subject}: [{grade_letter}, {grade}]")
    
    conn.close()
    return aggregate