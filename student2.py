import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import sqlite3
import GS

from crud import get_db_connection


def get_student_details(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM student WHERE student_id = ?", (student_id,))
    student = cursor.fetchone()
    conn.close()
    return student

def update_student_details(student_id, aggregate, status, denomination, gender, guardian_title, postal_address):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE student
        SET aggregate = ?, status = ?, denomination = ?, gender = ?, guardian_title = ?, postal_address = ?
        WHERE student_id = ?
    ''', (aggregate, status, denomination, gender, guardian_title, postal_address, student_id))
    conn.commit()
    conn.close()

class Student2:
    def __init__(self, root):
        self.root = root
        self.root.title("Update Student Details")
        root.attributes("-topmost", False)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 800
        window_height = 400
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        self.root.resizable(False, False)

        frame_padding = (20, 20)
        label_font = ("Helvetica", 12)
        entry_padding_x = 10
        entry_padding_y = 5
        button_padding_x = 10
        button_padding_y = 5
        button_frame_padding_y = 10

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.place(relx=0.5, rely=0.5, anchor=ttk.CENTER)

        # Create a list of label and entry pairs
        form_fields = [
            ("Student ID", "Aggregate"),
            ("Status", "Denomination"),
            ("Gender", "Guardian Title"),
            ("Postal Address", None)
        ]

        self.entries = {}

        for row_index, (label1, label2) in enumerate(form_fields):
            ttk.Label(self.frame, text=f"{label1}:", font=label_font).grid(
                row=row_index * 2, column=0, padx=2, pady=entry_padding_y, sticky=ttk.W
            )
            var1 = ttk.StringVar()
            entry1 = ttk.Entry(self.frame, textvariable=var1, width=40)
            entry1.grid(row=row_index * 2 + 1, column=0, padx=15, pady=entry_padding_y, sticky=ttk.W)
            self.entries[label1] = var1

            if label1 == "Gender":
                combo1 = ttk.Combobox(self.frame, textvariable=var1, values=["Male", "Female"], state="readonly", width=38)
                combo1.grid(row=row_index * 2 + 1, column=0, padx=15, pady=entry_padding_y, sticky=ttk.W)
                self.entries[label1] = var1

            if label2:
                ttk.Label(self.frame, text=f"{label2}:", font=label_font).grid(
                    row=row_index * 2, column=1, padx=2, pady=entry_padding_y, sticky=ttk.W
                )
                var2 = ttk.StringVar()
                entry2 = ttk.Entry(self.frame, textvariable=var2, width=40)
                entry2.grid(row=row_index * 2 + 1, column=1, padx=15, pady=entry_padding_y, sticky=ttk.W)
                self.entries[label2] = var2

        btn_load = ttk.Button(self.frame, text="Load Details", command=self.load_student_details, bootstyle="primary")
        btn_load.grid(row=10, column=0, pady=button_frame_padding_y, sticky=ttk.W)

        btn_submit = ttk.Button(self.frame, text="Submit", command=self.submit_form, bootstyle="success")
        btn_submit.grid(row=10, column=1, pady=button_frame_padding_y, sticky=ttk.W)

        self.load_student_details()

    def load_student_details(self):
        student_id = self.entries["Student ID"].get() or GS.getValues('student_id')
        self.entries["Student ID"].set(student_id)

        student = get_student_details(student_id)
        if student:
            self.entries["Aggregate"].set(student['aggregate'] if student['aggregate'] else '')
            self.entries["Status"].set(student['status'] if student['status'] else '')
            self.entries["Denomination"].set(student['denomination'] if student['denomination'] else '')
            self.entries["Gender"].set(student['gender'] if student['gender'] else '')
            self.entries["Guardian Title"].set(student['guardian_title'] if student['guardian_title'] else '')
            self.entries["Postal Address"].set(student['postal_address'] if student['postal_address'] else '')
        else:
            messagebox.showerror("Error", "Student not found")

    def submit_form(self):
        student_id = self.entries["Student ID"].get()
        aggregate = self.entries["Aggregate"].get()
        status = self.entries["Status"].get().upper()
        denomination = self.entries["Denomination"].get().upper()
        gender = self.entries["Gender"].get()
        guardian_title = self.entries["Guardian Title"].get().upper()
        postal_address = self.entries["Postal Address"].get()

        # Clear the form
        self.entries["Student ID"].set('')
        self.entries["Aggregate"].set('')
        self.entries["Status"].set('')
        self.entries["Denomination"].set('')
        self.entries["Gender"].set('')
        self.entries["Guardian Title"].set('')
        self.entries["Postal Address"].set('')

        # Save the values
        GS.saveValues(student_id=student_id, aggregate=aggregate, status=status, denomination=denomination, gender=gender, guardian_title=guardian_title, postal_address=postal_address)
        
        update_student_details(student_id, aggregate, status, denomination, gender, guardian_title, postal_address)
        messagebox.showinfo("Success", "Student details updated successfully")


if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = Student2(root)
    root.mainloop()
