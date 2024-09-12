import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
from crud import get_db_connection
import datetime
from GS import *

class BestStudent:
    def __init__(self, root):
        self.root = root
        self.root.title("Best Student Selector")
        root.attributes("-topmost", False)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 800
        window_height = 600
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        self.root.resizable(True, True)

        style = ttk.Style()
        style.configure("TCheckbutton", font=("Helvetica", 10))
        style.configure("TLabel", font=("Helvetica", 12, "bold"))
        style.configure("Custom.TLabelframe", borderwidth=2, relief="solid")
        style.configure("Custom.TLabelframe.Label", font=("Helvetica", 12, "bold"))

        main_frame = ttk.Frame(self.root, padding=(20, 20, 20, 10))
        main_frame.pack(fill=BOTH, expand=YES)

        # Create frames for each section
        year_frame = self.create_section(main_frame, "Select Year(s)", 0)
        programme_frame = self.create_section(main_frame, "Select Programme(s)", 1)
        semester_frame = self.create_section(main_frame, "Select Semester(s)", 2)
        subject_frame = self.create_section(main_frame, "Select Subject(s)", 3)
        class_frame = self.create_section(main_frame, "Select Class(es)", 4)

        # Populate sections
        self.populate_section(year_frame, self.generate_years())
        self.populate_section(programme_frame, self.get_programmes())
        self.populate_section(semester_frame, ["1", "2", "3"])
        self.populate_section(subject_frame, self.get_subjects())
        self.populate_section(class_frame, self.get_classes())
        
        process_and_insert_unique_programmes()

        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=(20, 0), sticky=EW)

        self.find_button = ttk.Button(button_frame, text="Find Best Student", command=self.find_best_student, bootstyle="success-outline", width=20)
        self.find_button.pack(side=LEFT, padx=(0, 10))

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_fields, bootstyle="danger-outline", width=20)
        self.reset_button.pack(side=LEFT)

    def create_section(self, parent, title, row):
        frame = ttk.LabelFrame(parent, text=title, padding=(10, 5), style="Custom.TLabelframe")
        frame.grid(row=row, column=0, padx=10, pady=5, sticky=NSEW)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_rowconfigure(row, weight=1)

        # Create a canvas and scrollbar
        canvas = ttk.Canvas(frame, width=700, height=100)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return scrollable_frame

    def populate_section(self, frame, items):
        for i, item in enumerate(items):
            var = ttk.BooleanVar()
            cb = ttk.Checkbutton(frame, text=item, variable=var, bootstyle="round-toggle")
            cb.grid(row=i // 3, column=i % 3, sticky=W, padx=5, pady=2)
            setattr(self, f"{frame.master.master.cget('text').lower().replace(' ', '_')}_{i}", var)

    def generate_years(self):
        current_year = datetime.datetime.now().year
        return [f"{year}/{year + 1}" for year in range(current_year, current_year - 10, -1)]

    def get_programmes(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT programme_name FROM programme")
        programmes = [row['programme_name'] for row in cursor.fetchall()]
        conn.close()
        return programmes

    def get_subjects(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT subject_name FROM subject")
        subjects = [row['subject_name'] for row in cursor.fetchall()]
        conn.close()
        return subjects

    def get_classes(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT class_name FROM class_name")
        classes = [row['class_name'] for row in cursor.fetchall()]
        conn.close()
        preferred_class = get_preferred_class()
        if preferred_class:
            return [c for c in classes if preferred_class.lower() in c.lower()]
        return classes

    def get_selected_items(self, section_name):
        items = getattr(self, f"get_{section_name}s")()
        return [item for i, item in enumerate(items) 
                if getattr(self, f"{section_name}s_{i}").get()]

    def find_best_student(self):
        selected_years = self.get_selected_items('year')
        selected_programmes = self.get_selected_items('programme')
        selected_semesters = [sem for i, sem in enumerate(["1", "2", "3"]) if getattr(self, f"select_semesters_{i}").get()]
        selected_subjects = self.get_selected_items('subject')
        selected_classes = self.get_selected_items('class')

        if not all([selected_years, selected_programmes, selected_semesters, selected_subjects, selected_classes]):
            messagebox.showwarning("Warning", "Please select at least one item from each category.")
            return

        # Here you would implement the logic to find the best student based on the selected criteria
        print(f"Selected Years: {selected_years}")
        print(f"Selected Programmes: {selected_programmes}")
        print(f"Selected Semesters: {selected_semesters}")
        print(f"Selected Subjects: {selected_subjects}")
        print(f"Selected Classes: {selected_classes}")

        messagebox.showinfo("Info", "Best student search functionality not yet implemented.")

    def reset_fields(self):
        for attr in dir(self):
            if attr.startswith(("years_", "programmes_", "select_semesters_", "subjects_", "classes_")):
                getattr(self, attr).set(False)

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = BestStudent(root)
    root.mainloop()