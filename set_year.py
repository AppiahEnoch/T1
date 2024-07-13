import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import *
from tkinter import messagebox
import os
import json
import AE

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')

class SetYearSemester:
    def __init__(self, root):
        self.root = root
        self.root.title("Set Preferred Year and Semester")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 200
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        frame_padding = (20, 20)
        entry_padding_x = 10
        entry_padding_y = 5

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)

        # Year Combo Box
        ttk.Label(self.frame, text="Select Year:").grid(row=0, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.frame, textvariable=self.year_var)
        self.year_select.grid(row=0, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.year_select.config(justify="center")
        self.year_select['values'] = AE.generate_years()

        # Semester Combo Box
        ttk.Label(self.frame, text="Select Semester:").grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.semester_var = ttk.StringVar()
        self.semester_select = ttk.Combobox(self.frame, textvariable=self.semester_var)
        self.semester_select.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.semester_select.config(justify="center")
        self.fill_semesters(self.semester_select)

        # Button Frame
        button_frame = ttk.Frame(self.frame, padding=frame_padding)
        button_frame.grid(row=2, column=0, columnspan=2, pady=entry_padding_y)

        # Save Button
        save_button = ttk.Button(button_frame, text="Save", command=self.save_selection, bootstyle="primary", width=10)
        save_button.pack(side=LEFT, padx=entry_padding_x)

        # Reset Button
        reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_selection, bootstyle="success")
        reset_button.pack(side=LEFT, padx=entry_padding_x)

        # Get Values Button
        get_values_button = ttk.Button(button_frame, text="Get Values", command=self.get_all_values, bootstyle="info")
        get_values_button.pack(side=LEFT, padx=entry_padding_x)

        # Load values from JSON file and set the combo boxes
        self.load_values_from_json()



    def fill_semesters(self, combobox):
        semesters = ["1", "2"]
        combobox['values'] = semesters

    def save_selection(self):
        year = self.year_var.get()
        semester = self.semester_var.get()

        print(f"Selected Year: {year}")
        print(f"Selected Semester: {semester}")

        AE.set_preferred_year_semester(year, semester)
        
        messagebox.showinfo("Saved", "Selections have been saved.")

    def get_all_values(self):
        data = AE.get_preferred_year_semester()
        if data:
            messagebox.showinfo("Stored Values", json.dumps(data, indent=4))
        else:
            messagebox.showinfo("Stored Values", "No data found.")

    def load_values_from_json(self):
        data = AE.get_preferred_year_semester()
        if "year" in data:
            self.year_var.set(data["year"])
        if "semester" in data:
            self.semester_var.set(data["semester"])

    def reset_selection(self):
        # Clear the combo boxes
        self.year_var.set('')
        self.semester_var.set('')

        # Clear the JSON file content
        AE.set_preferred_year_semester("", "")
        
        messagebox.showinfo("Reset", "Selections have been reset.")

if __name__ == "__main__":
    root = ttk.Window("SET PREFERRED YEAR AND SEMESTER", "darkly")
    app = SetYearSemester(root)
    root.mainloop()