import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import filedialog
from tkinter import ttk as tkttk
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import shutil
import re

# Constants for directory and database
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)
LOGO_DIR = os.path.join(APP_DIR, 'school_logo')

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn


    
#droptable()


# Create directories if they do not exist
os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(LOGO_DIR, exist_ok=True)

# Initialize the database


class SchoolDetails:
    def __init__(self, root):
        self.root = root
        self.root.title("School Details")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 600
        window_height = 400
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        frame_padding = (20, 20)
        label_font = ("Helvetica", 12)
        entry_padding_x = 10
        entry_padding_y = 5
        button_padding_x = 10
        button_padding_y = 5
        button_frame_padding_y = 10

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)

        ttk.Label(self.frame, text="Enter School Name:", font=label_font).grid(row=0, column=0, padx=2, pady=entry_padding_y, sticky=E)
        self.school_name_var = ttk.StringVar()
        self.school_name_entry = ttk.Entry(self.frame, textvariable=self.school_name_var, width=40)
        self.school_name_entry.grid(row=0, column=1, padx=15, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="Enter Short Name:", font=label_font).grid(row=1, column=0, padx=2, pady=entry_padding_y, sticky=E)
        self.short_name_var = ttk.StringVar()
        self.short_name_entry = ttk.Entry(self.frame, textvariable=self.short_name_var, width=40)
        self.short_name_entry.grid(row=1, column=1, padx=15, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="Enter Tel:", font=label_font).grid(row=2, column=0, padx=2, pady=entry_padding_y, sticky=E)
        self.tel_var = ttk.StringVar()
        self.tel_entry = ttk.Entry(self.frame, textvariable=self.tel_var, width=40)
        self.tel_entry.grid(row=2, column=1, padx=15, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="Enter Email:", font=label_font).grid(row=3, column=0, padx=2, pady=entry_padding_y, sticky=E)
        self.email_var = ttk.StringVar()
        self.email_entry = ttk.Entry(self.frame, textvariable=self.email_var, width=40)
        self.email_entry.grid(row=3, column=1, padx=15, pady=entry_padding_y, sticky=W)

        ttk.Label(self.frame, text="Upload Logo (PNG/JPG):", font=label_font).grid(row=4, column=0, padx=2, pady=entry_padding_y, sticky=E)
        self.upload_button = ttk.Button(self.frame, text="Browse", command=self.upload_logo, bootstyle="info")
        self.upload_button.grid(row=4, column=1, padx=15, pady=entry_padding_y, sticky=W)
        self.logo_path = None

        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=5, column=0, columnspan=2, pady=button_frame_padding_y)

        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.pack(side=LEFT, padx=button_padding_x)

        self.load_logo_preview()
        self.load_existing_details()

    def load_existing_details(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM school_details WHERE id = 1")
            record = cursor.fetchone()
            conn.close()

            if record:
                self.school_name_var.set(record["school_name"])
                self.short_name_var.set(record["short_name"])
                self.tel_var.set(record["tel"])
                self.email_var.set(record["email"])
                self.logo_path = record["logo_url"]
                self.load_logo_preview()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load existing school details: {e}")

    def upload_logo(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png;*.jpg")])
        if file_path:
            self.logo_path = file_path
            self.load_logo_preview()

    def load_logo_preview(self):
        if self.logo_path:
            img = Image.open(self.logo_path)
            img = img.resize((100, 100), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            if hasattr(self, 'logo_label'):
                self.logo_label.config(image=self.logo_img)
                self.logo_text_label.config(text=os.path.basename(self.logo_path))
            else:
                self.logo_label = ttk.Label(self.frame, image=self.logo_img)
                self.logo_label.grid(row=6, column=0, pady=10, padx=10, sticky=W)
                self.logo_text_label = ttk.Label(self.frame, text=os.path.basename(self.logo_path), font=("Helvetica", 10))
                self.logo_text_label.grid(row=6, column=1, pady=10, padx=10, sticky=W)
        else:
            if hasattr(self, 'logo_label'):
                self.logo_label.config(image='')
                self.logo_text_label.config(text='')

    def validate_email(self, email):
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        return re.match(pattern, email)

    
    def submit(self):
        school_name = self.school_name_var.get()
        short_name = self.short_name_var.get()
        tel = self.tel_var.get()
        email = self.email_var.get()

        if not school_name or not short_name or not tel or not email:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        if not self.validate_email(email):
            messagebox.showwarning("Input Error", "Please enter a valid email address.")
            return

        logo_dest_path = None
        if self.logo_path:
            logo_filename = os.path.basename(self.logo_path)
            logo_dest_path = os.path.join(LOGO_DIR, logo_filename)

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT logo_url FROM school_details WHERE id = 1")
            old_logo = cursor.fetchone()

            if self.logo_path:
                if old_logo and old_logo["logo_url"] and old_logo["logo_url"] != logo_dest_path:
                    if os.path.exists(old_logo["logo_url"]):
                        os.remove(old_logo["logo_url"])

                shutil.copy(self.logo_path, logo_dest_path)

            cursor.execute('''
                INSERT INTO school_details (id, school_name, short_name, tel, email, logo_url)
                VALUES (1, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    school_name = excluded.school_name,
                    short_name = excluded.short_name,
                    tel = excluded.tel,
                    email = excluded.email,
                    logo_url = CASE WHEN excluded.logo_url IS NOT NULL THEN excluded.logo_url ELSE school_details.logo_url END
            ''', (school_name, short_name, tel, email, logo_dest_path))

            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "School details added successfully")
            self.clear_fields()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add school details: {e}")

    
    def clear_fields(self):
        self.school_name_var.set("")
        self.short_name_var.set("")
        self.tel_var.set("")
        self.email_var.set("")
        self.logo_path = None
        self.load_logo_preview()

if __name__ == "__main__":
    root = ttk.Window("School Details", "superhero")
    app = SchoolDetails(root)
    root.mainloop()
