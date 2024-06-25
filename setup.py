from cx_Freeze import setup, Executable

build_exe_options = {
    "packages": ["os", "tkinter", "typeguard", "inflect", "ttkbootstrap"],
    "excludes": [],
    "include_files": [
        'images/logo.ico', 'images/logo.jpeg', 
        'add_class.py', 'add_house.py', 'add_subject.py', 
        'ADDC.py', 'ass.py', 'attendance.py', 'create_table.py', 
        'crud.py', 'dashboard.py', 'load_actual_programme.py', 
        'load_assessment copy.py', 'load_assessment.py', 'load_image.py', 
        'load_subject.py', 'login.py', 'main_controller.py', 'my_file.py', 
        'next_term.py', 'not_submitted.py', 'programme_subject.py', 
        'ps_view.py', 'ranking.py', 'registration.py', 'report.py', 
        'school_details.py', 'SendSMSToParents.py', 'setting.py', 
        'signature.py', 'sms_report.py', 'sms_util.py', 'sms_window.py', 
        'SMS.py', 'student_rankings.xlsx', 'student.py', 'styles.py', 
        'terminal_report.py', 'getters.txt'
    ]
}

setup(
    name="MyApp",
    version="0.1",
    description="My App Description",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=None, icon="images/logo.ico")]
)
