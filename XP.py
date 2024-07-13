import os
import datetime
import pandas as pd
from sqlalchemy import create_engine, text
from tkinter import messagebox
import urllib.parse

def export_data_to_csv(batch_size=500, max_rows_per_file=10000):
    params = urllib.parse.quote_plus(
        "DRIVER={ODBC Driver 17 for SQL Server};"
        "SERVER=AECLEANCODES1\\SQLEXPRESS01;"
        "DATABASE=newDB2;"
        "Trusted_Connection=yes;"
    )
    connection_string = f"mssql+pyodbc:///?odbc_connect={params}"
    
    base_query = """
    SELECT TOP (500) [ACADEMIC_YEAR], [STUDENTID], [Name], [StageCode],
           [Stage], [ClassCode], [StudClass], [TERM], 
           [SubjectCode], [Description], [SubjectType], [Shortcode],
           [ProgrammeCode], [PROGRAMME], [CLASSCORE], [EXAM], 
           [OVERALL], [GRADE], [GRD], [REMARKS], [STAFF_ID],
           [HouseCode], [HOUSE], [clspos], [subpos], [GENDER], 
           [ParentName], [ParentAddress], [INITIALS], [DATE_OF_BIRTH],
           [CONV_CS], [CONV_EXAM], [Status], [OutOf], 
           [END_OF_TERM], [nextterm], [ID]
    FROM [newDB2].[dbo].[View_Assessment]
    WHERE [ID] > {last_id}
    ORDER BY [ID]
    """

    folder_path = os.path.join(os.path.expanduser("~"), "Documents", "NEWDATA")
    os.makedirs(folder_path, exist_ok=True)

    engine = create_engine(connection_string, echo=False)

    try:
        with engine.connect() as connection:
            file_counter = 1
            row_counter = 0
            last_id = -1
            current_file = None
            total_rows = 0

            while True:
                query = text(base_query.format(last_id=last_id))
                chunk = pd.read_sql(query, connection)
                
                if chunk.empty:
                    break  # No more records to process

                if row_counter >= max_rows_per_file or current_file is None:
                    if current_file:
                        current_file.close()
                    
                    file_path = os.path.join(folder_path, f"DATA{file_counter}.csv")
                    current_file = open(file_path, 'w', newline='')
                    file_counter += 1
                    row_counter = 0
                    
                    chunk.to_csv(current_file, index=False, header=True)
                else:
                    chunk.to_csv(current_file, index=False, header=False)
                
                row_counter += len(chunk)
                total_rows += len(chunk)
                last_id = chunk['ID'].max()

            if current_file:
                current_file.close()

        messagebox.showinfo("Export Complete", f"Data exported successfully to {file_counter-1} files in {folder_path}\nTotal rows exported: {total_rows}")
    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)  # Print to console for debugging
        messagebox.showerror("Error", error_message)

if __name__ == "__main__":
    export_data_to_csv()