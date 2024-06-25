import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import *
from tkinter import messagebox
import sqlite3
import os
import re
import json

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    if not os.path.exists(APP_DIR):
        os.makedirs(APP_DIR)
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn



def getValues(key):
    filename = os.path.join(APP_DIR, 'student_data.json')
    
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            data = json.load(json_file)
            return data.get(key, None)
    else:
        return None

class SetClass:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Preferred Class")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 400
        window_height = 250
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        frame_padding = (20, 20)
        entry_padding_x = 10
        entry_padding_y = 5

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)

        # Number 1 Combo Box
        ttk.Label(self.frame, text="Select Number 1:").grid(row=0, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.number1_var = ttk.StringVar()
        self.number1_select = ttk.Combobox(self.frame, textvariable=self.number1_var)
        self.number1_select.grid(row=0, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.number1_select.config(justify="center")
        self.fill_numbers(self.number1_select)

        # Programme Combo Box
        ttk.Label(self.frame, text="Select Programme:").grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.programme_var = ttk.StringVar()
        self.programme_select = ttk.Combobox(self.frame, textvariable=self.programme_var)
        self.programme_select.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.programme_select.config(justify="center")
        self.fill_programmes(self.programme_select)

        # Number 2 Combo Box
        ttk.Label(self.frame, text="Select Number 2:").grid(row=2, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.number2_var = ttk.StringVar()
        self.number2_select = ttk.Combobox(self.frame, textvariable=self.number2_var)
        self.number2_select.grid(row=2, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.number2_select.config(justify="center")
        self.fill_numbers(self.number2_select)

        # Button Frame
        button_frame = ttk.Frame(self.frame, padding=frame_padding)
        button_frame.grid(row=3, column=0, columnspan=2, pady=entry_padding_y)

        # Save Button
        save_button = ttk.Button(button_frame, text="Save", command=self.save_selection, bootstyle="primary",width=10)
        save_button.pack(side=LEFT, padx=entry_padding_x)

        # Reset Button
        reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_selection, bootstyle="success")
        reset_button.pack(side=LEFT, padx=entry_padding_x)

        # Get Values Button
        get_values_button = ttk.Button(button_frame, text="Get Values", command=self.get_all_values, bootstyle="info")
        get_values_button.pack(side=LEFT, padx=entry_padding_x)

        # Load values from JSON file and set the combo boxes
        self.load_values_from_json()

    def fill_numbers(self, combobox):
        numbers = list(range(1, 101))
        combobox['values'] = numbers

    def fill_programmes(self, combobox):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT programme_name FROM programme ORDER BY programme_name ASC')
        programmes = cursor.fetchall()
        conn.close()
        
        programme_names = [programme['programme_name'] for programme in programmes]
        unique_programme_names = set(re.sub(r'\d+', '', name).strip() for name in programme_names)
        combobox['values'] = sorted(unique_programme_names)

    def save_selection(self):
        number1 = self.number1_var.get()
        programme = self.programme_var.get()
        number2 = self.number2_var.get()

        print(f"Selected Number 1: {number1}")
        print(f"Selected Programme: {programme}")
        print(f"Selected Number 2: {number2}")

        self.setPreferredClass(number1, programme, number2)
        
        messagebox.showinfo("Saved", "Selections have been saved.")

    def setPreferredClass(self, number1, programme, number2):
        data = {}
        if number1:
            data["number1"] = number1
        if programme:
            data["programme"] = programme
        if number2:
            data["number2"] = number2
        
        filename = os.path.join(APP_DIR, 'selected_class.json')
        with open(filename, 'w') as json_file:
            json.dump(data, json_file, indent=4)

    def get_all_values(self):
        filename = os.path.join(APP_DIR, 'selected_class.json')
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
                messagebox.showinfo("Stored Values", json.dumps(data, indent=4))
        else:
            messagebox.showinfo("Stored Values", "No data found.")

    def load_values_from_json(self):
        filename = os.path.join(APP_DIR, 'selected_class.json')
        if os.path.exists(filename):
            with open(filename, 'r') as json_file:
                data = json.load(json_file)
                if "number1" in data:
                    self.number1_var.set(data["number1"])
                if "programme" in data:
                    self.programme_var.set(data["programme"])
                if "number2" in data:
                    self.number2_var.set(data["number2"])

    def reset_selection(self):
        # Clear the combo boxes
        self.number1_var.set('')
        self.programme_var.set('')
        self.number2_var.set('')

        # Clear the JSON file content
        filename = os.path.join(APP_DIR, 'selected_class.json')
        with open(filename, 'w') as json_file:
            json.dump({}, json_file, indent=4)
        
        messagebox.showinfo("Reset", "Selections have been reset.")

if __name__ == "__main__":


    root = ttk.Window("SELECT PREFERRED CLASS", "darkly")
    app = SetClass(root)
    root.mainloop()
