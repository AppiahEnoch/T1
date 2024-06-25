import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import filedialog
from tkinter import messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import shutil
from ttkbootstrap.dialogs import Messagebox
from crud import *

# Constants for directory and database
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)
LOGO_DIR = os.path.join(APP_DIR, 'school_logo')
STUDENT_IMG_DIR = os.path.join(APP_DIR, 'student_image')

os.makedirs(APP_DIR, exist_ok=True)
os.makedirs(LOGO_DIR, exist_ok=True)
os.makedirs(STUDENT_IMG_DIR, exist_ok=True)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_database():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS student_img (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT,
            img_url TEXT,
            FOREIGN KEY (student_id) REFERENCES student (student_id)
        )
    ''')

    conn.commit()
    conn.close()

# Initialize the database
initialize_database()

class LoadImage:
    def __init__(self, root):
        self.root = root
        self.root.title("Load Image")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 800
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)

        frame_padding = (20, 20)
        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)
        
        self.search_var = ttk.StringVar()
        self.search_entry = ttk.Entry(self.frame, textvariable=self.search_var, width=100)
        self.search_entry.grid(row=0, column=0, padx=10, pady=10, sticky=E)
        self.search_entry.bind("<KeyRelease>", self.on_key_release)
        
        self.label = ttk.Label(self.frame, text="Search:")
        self.label.grid(row=0, column=0, padx=10, pady=10, sticky=W)
        
        self.tree = tkttk.Treeview(self.frame, columns=('ID', 'Name'), show='headings')
        self.tree.heading('ID', text='ID')
        self.tree.heading('Name', text='Name')
        self.tree.grid(row=2, column=0, padx=10, pady=10, sticky='nsew')
        self.tree.bind("<ButtonRelease-1>", self.on_row_select)
        
        self.details_label = ttk.Label(self.frame, text="", font=("Helvetica", 10))
        self.details_label.grid(row=1, column=0, padx=10, pady=10, sticky=W)

        self.upload_button = ttk.Button(self.frame, text="Upload Image", command=self.upload_image, bootstyle="info")
        self.upload_button.grid(row=3, column=0, padx=10, pady=10, sticky=W)
        self.submit_button = ttk.Button(self.frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.grid(row=3, column=0, padx=10, pady=10, sticky=E)

        self.image_path = None
        self.student_id = None

        self.frame.grid_rowconfigure(2, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def on_key_release(self, event):
        query = self.search_var.get()
        self.search_students(query)

    def search_students(self, query):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, name FROM student WHERE name LIKE ? OR student_id LIKE ?", (f"%{query}%", f"%{query}%"))
        rows = cursor.fetchall()
        conn.close()

        self.tree.delete(*self.tree.get_children())
        for row in rows:
            self.tree.insert('', 'end', values=(row["student_id"], row["name"]))

    def on_row_select(self, event):
        selected_item = self.tree.selection()[0]
        self.student_id, self.student_name = self.tree.item(selected_item, 'values')
        self.details_label.config(text=f"Selected Student ID: {self.student_id}, Name: {self.student_name}")
        self.load_student_image(self.student_id)

    def load_student_image(self, student_id):
        self.img_preview = None
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT img_url FROM student_img WHERE student_id = ?", (student_id,))
        record = cursor.fetchone()
        conn.close()

        if record:
            img_path = record["img_url"]
            if os.path.exists(img_path):
                img = Image.open(img_path)
                img = img.resize((100, 100), Image.LANCZOS)
                self.img_preview = ImageTk.PhotoImage(img)
                if hasattr(self, 'img_label'):
                    self.img_label.config(image=self.img_preview)
                else:
                    self.img_label = ttk.Label(self.frame, image=self.img_preview)
                    self.img_label.grid(row=4, column=0, pady=10, padx=10, sticky=W)
            else:
                if hasattr(self, 'img_label'):
                    self.img_label.config(image='')

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.JPG")])
        if file_path:
            self.image_path = file_path
            try:
                img = Image.open(self.image_path)
                img = img.resize((100, 100), Image.LANCZOS)
                self.img_preview = ImageTk.PhotoImage(img)
                if hasattr(self, 'img_label'):
                    self.img_label.config(image=self.img_preview)
                else:
                    self.img_label = ttk.Label(self.frame, image=self.img_preview)
                    self.img_label.grid(row=4, column=0, pady=10, padx=10, sticky=W)
            except Exception as e:
                Messagebox.show_error("Error", f"Failed to load image: {e}")

    def submit(self):
        print(self.student_id, self.image_path)
        if not self.image_path or not self.student_id:
            Messagebox.show_warning("Input Error", "Please select a student and upload an image.")
            return

        img_dest_path = os.path.join(STUDENT_IMG_DIR, f"{self.student_id}.jpg")

        try:
            shutil.copy(self.image_path, img_dest_path)

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COUNT(1) FROM student_img WHERE student_id = ?
            ''', (self.student_id,))
            exists = cursor.fetchone()[0]

            if exists:
                cursor.execute('''
                    UPDATE student_img SET img_url = ? WHERE student_id = ?
                ''', (img_dest_path, self.student_id))
            else:
                cursor.execute('''
                    INSERT INTO student_img (student_id, img_url)
                    VALUES (?, ?)
                ''', (self.student_id, img_dest_path))

            conn.commit()
            conn.close()

            Messagebox.show_info("Success", "Image uploaded and student details updated successfully")
        except Exception as e:
            Messagebox.show_error("Error", f"Failed to upload image: {e}")


if __name__ == "__main__":
    root = ttk.Window("Load Image", "superhero")
    app = LoadImage(root)
    root.mainloop()
