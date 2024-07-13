
import sys
import traceback

def log_uncaught_exceptions(ex_cls, ex, tb):
    print(''.join(traceback.format_tb(tb)))
    print('{0}: {1}'.format(ex_cls.__name__, ex))

sys.excepthook = log_uncaught_exceptions


import sys
import traceback

def log_uncaught_exceptions(ex_cls, ex, tb):
    print(''.join(traceback.format_tb(tb)))
    print('{0}: {1}'.format(ex_cls.__name__, ex))

sys.excepthook = log_uncaught_exceptions

import os
import sys
import ttkbootstrap as ttk
from main_controller import MainController
from my_file import get_icon
import LCS
from ass import compute_and_store_assessments
import threading
import multiprocessing

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def center_window(window, width=800, height=650):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_coordinate = (screen_width / 2) - (width / 2)
    y_coordinate = (screen_height / 2) - (height / 2)
    window.geometry(f"{width}x{height}+{int(x_coordinate)}+{int(y_coordinate)}")

def create_splash_screen():
    splash = ttk.Toplevel()
    splash.overrideredirect(True)
    splash.title("Loading...")
    
    center_window(splash, 500, 200)
    
    label = ttk.Label(splash, text="SDASS student Report system V1.8\nBy the IT Department-2024 \nLoading...\nPlease wait", font=("Helvetica", 16))
    label.pack(expand=True)
    
    return splash

def run_parallel_tasks():
    # REMOVE THIS IN NEW UPDATES
    LCS.update__year_24()
    compute_and_store_assessments()
    LCS.delete_invalid_assessment_records()
    
    # LCS.update_student_programme()
    # LCS.reset_guardian_title()

    with multiprocessing.Pool(processes=3) as pool:
        pool.apply_async(LCS.update_student_programme())
        pool.apply_async(LCS.reset_guardian_title())
        pool.apply_async(LCS.update_student_boarding_and_house())

        pool.close()
        pool.join()

def load_main_application(root, splash):
    # Run loading tasks in parallel
    run_parallel_tasks()

    # Set the window icon
    try:
        icon_path = get_icon('logo.ico')
        root.wm_iconbitmap(resource_path(icon_path))
    except Exception as e:
        print(f"Failed to set window icon: {e}")

    # Center the main window
    center_window(root)
    
    main_controller = MainController(root)
    main_controller.show_login_window()

    # Destroy splash screen and show main window
    splash.destroy()
    root.deiconify()

if __name__ == "__main__":
    multiprocessing.freeze_support()  # Necessary for multiprocessing to work with PyInstaller
    
    root = ttk.Window("SDASS STUDENT REPORT SYSTEM V1.8   --By  SDASS IT Department-2024", "darkly", resizable=(False, False))
    
    # Hide the main window initially
    root.withdraw()

    # Create and show splash screen
    splash = create_splash_screen()

    # Start loading the main application in a separate thread
    threading.Thread(target=load_main_application, args=(root, splash)).start()

    root.mainloop()