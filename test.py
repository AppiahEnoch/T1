import unittest
from unittest.mock import patch, MagicMock
import pandas as pd

# Import the function to be tested from report module
from report import compute_and_store_assessments, determine_grade, assign_number, determine_remarks, get_ordinal_suffix

class TestComputeAndStoreAssessments(unittest.TestCase):
    
    @patch('report.get_db_connection')
    @patch('report.determine_grade')
    @patch('report.assign_number')
    @patch('report.determine_remarks')
    @patch('report.get_ordinal_suffix')
    def test_compute_and_store_assessments(self, mock_get_ordinal_suffix, mock_determine_remarks, mock_assign_number, mock_determine_grade, mock_get_db_connection):
        # Setup mocks
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_get_db_connection.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor

        # Mock database responses
        mock_cursor.fetchone.return_value = {'class_score': 40, 'exam_score': 60}
        mock_cursor.fetchall.return_value = [
            {'student_id': 1, 'class_id': 1, 'semester_id': 1, 'subject_id': 1, 'year': 2024, 
             'class_score': '30', 'exam_score': '70', 'teacher_initial_letters': 'ABC', 'isCore': 1}
        ]
        
        # Mock other functions
        mock_determine_grade.return_value = 'A1'
        mock_assign_number.return_value = 1
        mock_determine_remarks.return_value = 'Excellent'
        mock_get_ordinal_suffix.side_effect = lambda x: get_ordinal_suffix(x)
        
        # Call the function
        compute_and_store_assessments()

        # Check if DataFrame is populated correctly
        cursor_execute_call_args = mock_cursor.execute.call_args_list
        for call in cursor_execute_call_args:
            print(call)
        
        # Ensure the DataFrame is correctly formed before applying rank
        df_mock = pd.DataFrame([
            {'student_id': 1, 'class_id': 1, 'semester_id': 1, 'subject_id': 1, 'year': 2024, 
             'class_score': 30.0, 'exam_score': 70.0, 'total_score': 54.0, 'grade': 'A1', 
             'number_equivalence': 1, 'remarks': 'Excellent', 'isCore': 1, 'teacher_initial_letters': 'ABC'}
        ])
        print(df_mock)
        
        # Check if the correct SQL queries were executed
        mock_cursor.execute.assert_any_call('SELECT class_score, exam_score FROM score_percentage WHERE id = 1')
        mock_cursor.execute.assert_any_call('''
        SELECT a.student_id, a.class_id, a.semester_id, a.subject_id, a.year, 
               a.class_score, a.exam_score, a.teacher_initial_letters,
               (a.class_score * ? / 100) + (a.exam_score * ? / 100) AS total_score,
               p.is_core AS isCore
        FROM assessment a
        JOIN subject p ON a.subject_id = p.id
    ''', (40.0, 60.0))
        
        # Verify the data inserted into computed_assessment table
        expected_values = [
            (1, 1, 1, 1, 2024, '30', '70', 54.0, 'A1', 1, 'Excellent', 1, 'ABC', '1st')
        ]
        
        mock_cursor.executemany.assert_called_once_with('''
        INSERT INTO computed_assessment (student_id, class_id, semester_id, subject_id, year, class_score, exam_score, total_score, grade, number_equivalence, remarks, isCore, teacher_initial_letters, rank)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', expected_values)
        
        # Check if commit and close were called
        mock_conn.commit.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
