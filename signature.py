import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import filedialog
from PIL import Image, ImageTk
import sqlite3
import os
import shutil
from ttkbootstrap.dialogs import Messagebox
import logging

#message box
from tkinter import messagebox

# Set up logging
logging.basicConfig(filename='app.log', level=logging.ERROR, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Constants for directory and database
HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)
SIGNATURE_DIR = os.path.join(APP_DIR, 'signature')
REQUIRED_WIDTH = 306
REQUIRED_HEIGHT = 216

def safe_makedirs(directory):
    try:
        os.makedirs(directory, exist_ok=True)
    except Exception as e:
        logging.error(f"Error creating directory {directory}: {str(e)}")
        raise

try:
    safe_makedirs(APP_DIR)
    safe_makedirs(SIGNATURE_DIR)
except Exception as e:
    Messagebox.show_error("Directory Creation Error", 
                          f"Failed to create necessary directories: {str(e)}")
    exit(1)

def get_db_connection():
    try:
        conn = sqlite3.connect(DATABASE_FILE)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logging.error(f"Database connection error: {str(e)}")
        raise

def initialize_database():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS signature (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                img_url TEXT
            )
        ''')

        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Database initialization error: {str(e)}")
        raise
    finally:
        if conn:
            conn.close()

# Initialize the database
try:
    initialize_database()
except Exception as e:
    Messagebox.show_error("Database Initialization Error", 
                          f"Failed to initialize database: {str(e)}")
    exit(1)

class LoadSignatureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Load Signature")
        
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 600
        window_height = 500
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.resizable(False, False)
        
        self.setup_ui()
        self.image_path = None
     
    def setup_ui(self):
        self.label = ttk.Label(self.root, text="Signature of head of school", font=("Arial", 20, "bold"))
        self.label.pack(pady=10)

        frame_padding = (10, 10)
        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)
        
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

        self.load_signature_image()

        self.upload_button = ttk.Button(self.frame, text="Upload Signature", command=self.upload_signature, bootstyle="info")
        self.upload_button.grid(row=2, column=0, padx=10, pady=10, sticky=W)

        self.submit_button = ttk.Button(self.frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.grid(row=2, column=0, padx=10, pady=10, sticky=E)

        self.delete_button = ttk.Button(self.frame, text="Delete", command=self.delete_signature, bootstyle="danger")
        self.delete_button.grid(row=2, column=1, padx=10, pady=10, sticky=W)

        card_frame = ttk.Frame(self.frame, bootstyle="primary")
        card_frame.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky=NSEW)
        card_frame.grid_rowconfigure(0, weight=1)
        card_frame.grid_columnconfigure(0, weight=1)

        card_title = ttk.Label(card_frame, text="Image Information", font=("Arial", 16, "bold"))
        card_title.grid(row=0, column=0, pady=10, padx=10, sticky=N)

        self.image_info_label = ttk.Label(card_frame, text=self.get_image_info_text(), font=("Arial", 10), justify=LEFT)
        self.image_info_label.grid(row=1, column=0, pady=10, padx=10, sticky=W)
        
    def clear_image_label(self):
        if hasattr(self, 'img_label'):
            self.img_label.grid_forget()
            del self.img_label
        self.img_preview = None
        
    def load_signature_image(self):
        self.img_preview = None
        
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT img_url FROM signature WHERE id = 1")
                record = cursor.fetchone()
            
            if not record:
                self.clear_image_label()
                return

            img_path = record["img_url"]
            if not os.path.exists(img_path):
                self.clear_image_label()
                logging.warning(f"Image file not found: {img_path}")
                return

            img = Image.open(img_path)
            img = img.resize((200, 100), Image.LANCZOS)
            self.img_preview = ImageTk.PhotoImage(img)

            if hasattr(self, 'img_label'):
                self.img_label.config(image=self.img_preview)
            else:
                self.img_label = ttk.Label(self.frame, image=self.img_preview)
                self.img_label.grid(row=1, column=0, pady=10, padx=10, columnspan=2, sticky='n')

        except sqlite3.Error as e:
            logging.error(f"Database query error: {str(e)}")
            messagebox.showerror("Database Error", "Failed to load signature image from database.")
        except IOError as e:
            logging.error(f"Error opening image file: {str(e)}")
            messagebox.showerror("Image Load Error", f"Failed to open image file: {str(e)}")
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"An unexpected error occurred: {str(e)}")

    def upload_signature(self):
        file_path = filedialog.askopenfilename(filetypes=[("JPEG files", "*.JPG")])
        if file_path:
            try:
                img = Image.open(file_path)
                if img.size != (REQUIRED_WIDTH, REQUIRED_HEIGHT):
                    full_message = (f"Invalid Image DIMENSION\n\n"
                                    f"The image must be exactly {REQUIRED_WIDTH}x{REQUIRED_HEIGHT} pixels. "
                                    f"Current dimensions are {img.size[0]}x{img.size[1]} pixels.\n\n"
                                    "Please resize your image to the correct dimensions and try again.")
                    Messagebox.show_warning("Invalid Image Size", full_message)
                self.image_path = file_path
                img = img.resize((200, 100), Image.LANCZOS)
                self.img_preview = ImageTk.PhotoImage(img)
                if hasattr(self, 'img_label'):
                    self.img_label.config(image=self.img_preview)
                else:
                    self.img_label = ttk.Label(self.frame, image=self.img_preview)
                    self.img_label.grid(row=1, column=0, pady=10, padx=10, columnspan=2, sticky='n')
                self.display_image_info()
            except Exception as e:
                logging.error(f"Error uploading image: {str(e)}")
                full_message = (f"Error: {str(e)}\n\n"
                                "There was an error loading the image. Please ensure the file is a valid JPEG image and try again.")
                Messagebox.show_error("Image Load Error", full_message)
                self.image_path = None

    def submit(self):
        if not self.image_path:
            full_message = ("Input Error\n\n"
                            "No signature image uploaded. You must upload a signature image before submitting.")
            Messagebox.show_warning("Missing Signature Image", full_message)
            return

        img_dest_path = os.path.join(SIGNATURE_DIR, "headteacher_signature.jpg")
        self.root.after(0, self._submit, img_dest_path)

    def _submit(self, img_dest_path):
        try:
            shutil.copy(self.image_path, img_dest_path)
            conn = get_db_connection()
            cursor = conn.cursor()

            # Delete all existing entries
            cursor.execute('DELETE FROM signature')

            # Insert the new entry
            cursor.execute('INSERT INTO signature (id, img_url) VALUES (1, ?)', (img_dest_path,))

            conn.commit()
            self._show_success_message()
        except Exception as e:
            logging.error(f"Error submitting signature: {str(e)}")
            self._show_error_message(f"Error: {str(e)}\n\nThere was an error uploading the signature. Please try again.")
        finally:
            if conn:
                conn.close()
            self.image_path = None

    def _show_success_message(self):
        full_message = ("Success\n\n"
                        "Signature upload was successful. The headteacher's signature image has been uploaded successfully.")
        Messagebox.show_info("Upload Successful", full_message)
        self.load_signature_image()

    def _show_error_message(self, message):
        Messagebox.show_error("Signature Upload Error", message)

    def delete_signature(self):
        self.root.after(0, self._delete)

    def _delete(self):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT img_url FROM signature WHERE id = 1")
            record = cursor.fetchone()

            if record:
                img_path = record["img_url"]
                if os.path.exists(img_path):
                    os.remove(img_path)

                cursor.execute("DELETE FROM signature WHERE id = 1")
                conn.commit()
                self._show_delete_success_message()
            else:
                self._show_no_signature_message()
        except Exception as e:
            logging.error(f"Error deleting signature: {str(e)}")
            self._show_delete_error_message(f"Error: {str(e)}\n\nThere was an error deleting the signature. Please try again.")
        finally:
            if conn:
                conn.close()

    def _show_delete_success_message(self):
        full_message = ("Success\n\n"
                        "Signature deletion was successful. The headteacher's signature image has been deleted.")
        Messagebox.show_info("Deletion Successful", full_message)
        self.load_signature_image()

    def _show_no_signature_message(self):
        full_message = ("Deletion Error\n\n"
                        "No signature image found to delete.")
        Messagebox.show_warning("No Signature Image", full_message)

    def _show_delete_error_message(self, message):
        Messagebox.show_error("Signature Deletion Error", message)

    def display_image_info(self):
        image_info = self.get_image_info_text()
        self.image_info_label.config(text=image_info)

    def get_image_info_text(self):
        return (
            "Dimensions:\n"
            "Width: 306 pixels\n"
            "Height: 216 pixels\n"
            "Aspect Ratio: 1.417 (width to height ratio)\n"
            "Metadata:\n"
            "File Type: JPEG\n"
            "File Size: Approximately 3.44 KB\n"
            "Color Profile: RGB\n"
            "Date Created: Not specified (Check properties if available)\n"
            "Resolution: Standard web resolution (72 DPI)\n"
            "\n"
            "Description for User:\n"
            "\"The image you uploaded is a JPEG file with dimensions of 306 pixels in width and 216 pixels in height. "
            "The aspect ratio of the image is approximately 1.417. It has a file size of around 3.44 KB and uses the RGB "
            "color profile, which is standard for web images.\""
        )

if __name__ == "__main__":
    try:
        root = ttk.Window("Load Signature", "superhero")
        app = LoadSignatureApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Unhandled exception in main: {str(e)}")
        Messagebox.show_error("Critical Error", f"An unexpected error occurred: {str(e)}\nPlease check the log file for more details.")
