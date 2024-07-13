import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from load_assessment import LoadAssessment
from add_class import AddClass
from add_subject import Addsubject # Import the AddProgramme class
from add_house import *  # Import the AddProgramme class
from student import *  # Import the AddProgramme class
from next_term import *  # Import the AddProgramme class
from setting import *  # Import the AddProgramme class
from remark import *  # Import the AddProgramme class
from school_details import *  # Import the AddProgramme class
from attendance import *  # Import the AddProgramme class
from report import *  # Import the AddProgramme class
from my_file import get_icon 
from not_submitted import NotSubmitted
from load_image import LoadImage

from sms_window import SMS
from programme_subject import PairSubjectAndProgramme
from ranking import Ranking
from change_class import ChangeStudentClass

import LCS
from THREAD import *
from set_class import SetClass
import signature
from set_year import SetYearSemester


class Dashboard:
    def __init__(self, root, main_controller):                                                                                                                                                                       
        self.root = root
        self.main_controller = main_controller
        self.frame = None

    def show(self):
        padx_value = 5  # Change this value to adjust all padx values simultaneously
        pady_value = 10  # Assuming you might also want to adjust pady similarly
        self.frame = ttk.Frame(self.root, padding=(50, 10))
        self.frame.grid(row=0, column=0, padx=padx_value, pady=pady_value, sticky="nsew")

        container = ttk.Frame(self.frame)
        container.grid(row=0, column=0, padx=padx_value, pady=pady_value, sticky="nsew")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=1)
        container.grid_rowconfigure(0, weight=1)
        container.grid_rowconfigure(1, weight=1)
        container.grid_rowconfigure(2, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(3, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(4, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(5, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(6, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(7, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(8, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(9, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(10, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(11, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(12, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(13, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(14, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(15, weight=1)  # Added another row for the new button
        container.grid_rowconfigure(16, weight=1)  # Added another row for the new button
 
        

        # Define a style for the buttons
        style = ttk.Style()
        style.configure("Dashboard.TButton", font=("Helvetica", 14, "bold"), padding=(pady_value, pady_value))

        # Create and place buttons in the grid
        button1 = ttk.Button(container, text="Upload Assessment", style="Dashboard.TButton", command=self.open_load_assessment)
        button1.grid(row=0, column=0, padx=padx_value, pady=pady_value, sticky="nsew")

        button2 = ttk.Button(container, text="Report/Transcript", style="Dashboard.TButton", command=self.open_report)
        button2.grid(row=0, column=1, padx=padx_value, pady=pady_value, sticky="nsew")

        button3 = ttk.Button(container, text="Add Class", style="Dashboard.TButton", command=self.open_add_class)
        button3.grid(row=1, column=0, padx=padx_value, pady=pady_value, sticky="nsew")

        button4 = ttk.Button(container, text="SMS", style="Dashboard.TButton", command=self.open_sms)
        button4.grid(row=1, column=1, padx=padx_value, pady=pady_value, sticky="nsew")

        button5 = ttk.Button(container, text="Student Details", style="Dashboard.TButton", command=self.open_student)
        button5.grid(row=2, column=0, padx=padx_value, pady=pady_value, sticky="nsew")

        button6 = ttk.Button(container, text="Subject", style="Dashboard.TButton", command=self.open_add_program)
        button6.grid(row=2, column=1, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button7 = ttk.Button(container, text="House", style="Dashboard.TButton", command=self.open_add_house)
        button7.grid(row=3, column=0, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button8 = ttk.Button(container, text="Next Semester Begins", style="Dashboard.TButton", command=self.open_next_term)
        button8.grid(row=3, column=1, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button9 = ttk.Button(container, text="Settings", style="Dashboard.TButton", command=self.open_setting)
        button9.grid(row=4, column=0, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button10 = ttk.Button(container, text="Remarks", style="Dashboard.TButton", command=self.open_remark)
        button10.grid(row=4, column=1, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button11 = ttk.Button(container, text="School Details", style="Dashboard.TButton", command=self.open_school_details)
        button11.grid(row=5, column=0, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button12 = ttk.Button(container, text="Attendance", style="Dashboard.TButton", command=self.open_attendance)
        button12.grid(row=5, column=1, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button13 = ttk.Button(container, text="Not Submitted", style="Dashboard.TButton", command=self.open_not_submitted)
        button13.grid(row=6, column=0, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button13 = ttk.Button(container, text="Student Image", style="Dashboard.TButton", command=self.open_load_image)
        button13.grid(row=6, column=1, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button13 = ttk.Button(container, text="Programme/Subject", style="Dashboard.TButton", command=self.open_programe_subject)
        button13.grid(row=7, column=0, padx=padx_value, pady=pady_value, sticky="nsew")
        
        button13 = ttk.Button(container, text="Ranking", style="Dashboard.TButton", command=self.open_ranking)
        button13.grid(row=7, column=1, padx=padx_value, pady=pady_value, sticky="nsew")
       
        button14 = ttk.Button(container, text="Change Student Class", style="Dashboard.TButton", command=self.open_change_class)
        button14.grid(row=8, column=0, padx=padx_value, pady=pady_value, sticky="nsew")
        
    
        button15 = ttk.Button(container, text="Pref Class", style="Dashboard.TButton", command=self.open_set_class)
        button15.grid(row=8, column=1, padx=padx_value, pady=pady_value, sticky="nsew")
        # set my default  year and semester button
        button16 = ttk.Button(container, text="Pref. year and semester", style="Dashboard.TButton", command=self.open_set_year)
        button16.grid(row=9, column=0, padx=padx_value, pady=pady_value, sticky="nsew")
        
 
        
        
  
        
        


    def open_load_assessment(self):
        new_window = ttk.Toplevel(self.root)
        LoadAssessment(new_window)
    def open_set_year(self):
        new_window = ttk.Toplevel(self.root)
        SetYearSemester(new_window)
        
    def open_change_class(self):
        new_window = ttk.Toplevel(self.root)
        ChangeStudentClass(new_window)
        
    def open_set_class(self):
        new_window = ttk.Toplevel(self.root)
        SetClass(new_window)
        
        
        
    def open_ranking(self):
        new_window = ttk.Toplevel(self.root)
        Ranking(new_window)
        
    def open_programe_subject(self):
        new_window = ttk.Toplevel(self.root)
        PairSubjectAndProgramme(new_window)
        
    def open_load_image(self):
        new_window = ttk.Toplevel(self.root)
        LoadImage(new_window)
        
    def open_sms(self):
        new_window = ttk.Toplevel(self.root)
        SMS(new_window)
        
    def open_not_submitted(self):
        new_window = ttk.Toplevel(self.root)
        NotSubmitted(new_window)
        
    def open_report(self):
        new_window = ttk.Toplevel(self.root)
        Report(new_window)
        
    def open_add_class(self):
        new_window = ttk.Toplevel(self.root)
        AddClass(new_window)

    def open_add_program(self):
        new_window = ttk.Toplevel(self.root)
        Addsubject(new_window)
        
    def open_add_house(self):
        new_window = ttk.Toplevel(self.root)
        AddHouse(new_window)
        
    def open_student(self):
        new_window = ttk.Toplevel(self.root)
        Student(new_window)
        
    def open_next_term(self):
        new_window = ttk.Toplevel(self.root)
        NextTerm(new_window)
        
    def open_setting(self):
        new_window = ttk.Toplevel(self.root)
        Setting(new_window)
        
    def open_remark(self):
        new_window = ttk.Toplevel(self.root)
        Remark(new_window)
        
    def open_school_details(self):
        new_window = ttk.Toplevel(self.root)
        SchoolDetails(new_window)
        
    def open_attendance(self):
        new_window = ttk.Toplevel(self.root)
        Attendance(new_window)
        
    def close(self):
        if self.frame:
            self.frame.pack_forget()
            self.frame.destroy()
            self.frame = None

# Example of how to use this Dashboard class
if __name__ == "__main__":
    root = ttk.Window("SDASS STUDENT REPORT SYSTEM (BY THE IT DEPARTMENT)", "darkly", resizable=(False, False))
    
    # Set the window icon
    icon_path = get_icon('logo.ico')  # Assuming you have a logo.ico in the images folder
    root.wm_iconbitmap(icon_path)
    #set theme darkly
  
   
    
    root.geometry("800x650")
    dashboard = Dashboard(root, None)
    dashboard.show()
    root.mainloop()
