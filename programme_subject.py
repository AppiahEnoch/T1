import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import sqlite3
import os
import ps_view
import CPS
import threading

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
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executescript('''
    CREATE TABLE IF NOT EXISTS subject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS programme (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        programme_name TEXT NOT NULL UNIQUE
    );
    CREATE TABLE IF NOT EXISTS programme_subject (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_id INTEGER NOT NULL,
        programme_id INTEGER NOT NULL,
        FOREIGN KEY (subject_id) REFERENCES subject(id) ON UPDATE CASCADE ON DELETE CASCADE,
        FOREIGN KEY (programme_id) REFERENCES programme(id) ON UPDATE CASCADE ON DELETE CASCADE,
        UNIQUE (subject_id, programme_id)
    );
    ''')
    conn.commit()
    conn.close()

class PairSubjectAndProgramme:
    def __init__(self, root):
        self.root = root
        self.root.title("Pair Subject and Programme")
        self.setup_ui()
        self.populate_subject_names()
        self.populate_programme_names()

    def setup_ui(self):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width, window_height = 400, 250
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        self.frame = ttk.Frame(self.root, padding=(20, 20))
        self.frame.pack(fill=BOTH, expand=TRUE)

        ttk.Label(self.frame, text="Select Programme:", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5, sticky=W)
        self.programme_var = ttk.StringVar()
        self.programme_select = ttk.Combobox(self.frame, textvariable=self.programme_var)
        self.programme_select.grid(row=0, column=1, padx=10, pady=5, sticky=W)
        self.programme_select.config(justify="center")

        ttk.Label(self.frame, text="Select Subject:", font=("Helvetica", 12)).grid(row=1, column=0, padx=10, pady=5, sticky=W)
        self.subject_var = ttk.StringVar()
        self.subject_select = ttk.Combobox(self.frame, textvariable=self.subject_var)
        self.subject_select.grid(row=1, column=1, padx=10, pady=5, sticky=W)
        self.subject_select.config(justify="center")

        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.pack(side=LEFT, padx=10)

        self.view_button = ttk.Button(button_frame, text="View", command=self.view_pairs, bootstyle="primary")
        self.view_button.pack(side=LEFT, padx=10)

        self.progress_var = ttk.IntVar()
        self.progress_bar = ttk.Progressbar(self.frame, variable=self.progress_var, maximum=100, bootstyle="success-striped")
        self.progress_bar.grid(row=3, column=0, columnspan=2, pady=10, sticky=(W, E))

        self.status_var = ttk.StringVar(value="Ready")
        self.status_label = ttk.Label(self.frame, textvariable=self.status_var, font=("Helvetica", 10))
        self.status_label.grid(row=4, column=0, columnspan=2, pady=5)

    def populate_subject_names(self):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, subject_name FROM subject")
            self.subject_names = {row["subject_name"]: row["id"] for row in cursor.fetchall()}
        self.subject_select["values"] = list(self.subject_names.keys())

    def populate_programme_names(self):
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, programme_name FROM programme")
            self.programme_names = {row["programme_name"]: row["id"] for row in cursor.fetchall()}
        self.programme_select["values"] = list(self.programme_names.keys())

    def submit(self):
        subject_id = self.subject_names.get(self.subject_var.get())
        programme_id = self.programme_names.get(self.programme_var.get())

        if subject_id is None or programme_id is None:
            messagebox.showerror("Error", "Please select both a subject and a programme.")
            return

        self.status_var.set("Processing...")
        self.progress_var.set(0)
        self.submit_button.config(state="disabled")
        self.view_button.config(state="disabled")

        threading.Thread(target=self.process_submission, args=(subject_id, programme_id)).start()

    def process_submission(self, subject_id, programme_id):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                SELECT 1 FROM programme_subject
                WHERE programme_id = ? AND subject_id = ?
            ''', (programme_id, subject_id))
            exists = cursor.fetchone()

            if exists:
                self.root.after(0, lambda: messagebox.showinfo("Info", f"Subject and Programme already paired\nSubject ID: {subject_id}, Programme ID: {programme_id}"))
            else:
                cursor.execute('''
                    INSERT INTO programme_subject (programme_id, subject_id)
                    VALUES (?, ?)
                ''', (programme_id, subject_id))
                conn.commit()
                self.root.after(0, lambda: messagebox.showinfo("Success", f"Subject and Programme paired successfully\nSubject ID: {subject_id}, Programme ID: {programme_id}"))

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to pair Subject and Programme:\n{e}\nSubject ID: {subject_id}, Programme ID: {programme_id}"))
        finally:
            if conn:
                conn.close()

        self.progress_var.set(33)
        self.status_var.set("Running CPS functions...")

        def run_cps_functions():
            try:
                CPS.insert_class_programme_subject()
                self.progress_var.set(55)
                CPS.includeCoreSubjectsIntoProgramme_subject()
                self.progress_var.set(77)
                CPS.includeCoreSubjectsIntoClassProgrammeSubject()
                self.progress_var.set(100)
                self.status_var.set("Processing complete")
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Error", f"An error occurred during processing: {e}"))
            finally:
                self.root.after(0, self.reset_ui)

        run_cps_functions()
        


    def reset_ui(self):
        self.submit_button.config(state="normal")
        self.view_button.config(state="normal")
        self.status_var.set("Ready")
        self.progress_var.set(0)

    def view_pairs(self):
        ps_view_window = ttk.Toplevel(self.root)
        ps_view_window.title("Programme-Subject View")
        window_width, window_height = 400, 600
        screen_width = ps_view_window.winfo_screenwidth()
        screen_height = ps_view_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        ps_view_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        ps_view.ProgrammeSubjectApp(ps_view_window)

if __name__ == "__main__":
    initialize_database()
    root = ttk.Window("Pair Subject and Programme", "superhero")
    app = PairSubjectAndProgramme(root)
    root.mainloop()
