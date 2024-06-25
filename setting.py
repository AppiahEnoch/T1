import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
from crud import get_db_connection
import signature
import api
import load_actual_programme

class Setting:
    def __init__(self, root):
        self.root = root
        self.root.title("Setting")
        root.attributes("-topmost", False)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        window_width = 400
        window_height = 300
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

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=ttk.BOTH, expand=ttk.TRUE)

        ttk.Label(self.frame, text="Class Score %:", font=label_font).grid(row=0, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.E)
        self.class_score_var = ttk.StringVar()
        self.class_score_entry = ttk.Entry(self.frame, textvariable=self.class_score_var, width=10)
        self.class_score_entry.grid(row=0, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)

        ttk.Label(self.frame, text="Exam Score %:", font=label_font).grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.E)
        self.exam_score_var = ttk.StringVar()
        self.exam_score_entry = ttk.Entry(self.frame, textvariable=self.exam_score_var, width=10)
        self.exam_score_entry.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=ttk.W)

        self.save_button = ttk.Button(self.frame, text="Save Scores", command=self.save_settings, bootstyle="success")
        self.save_button.grid(row=2, column=0, columnspan=2, padx=button_padding_x, pady=button_padding_y, sticky=ttk.EW)
        
        self.save_button = ttk.Button(self.frame, text="Upload Signature", bootstyle="primary", command=self.open_signature)
        self.save_button.grid(row=3, column=0, columnspan=2, padx=button_padding_x, pady=button_padding_y, sticky=ttk.EW)
        
        #button to open api key window
        self.save_button = ttk.Button(self.frame, text="Add API Key", bootstyle="primary", command=self.open_api_key)
        self.save_button.grid(row=4, column=0, columnspan=2, padx=button_padding_x, pady=button_padding_y, sticky=ttk.EW)
        
        #button to open programme window
        self.save_button = ttk.Button(self.frame, text="Add Programme", bootstyle="primary", command=self.open_programme)
        self.save_button.grid(row=5, column=0, columnspan=2, padx=button_padding_x, pady=button_padding_y, sticky=ttk.EW)
        
        self.load_settings()
        
    def open_signature(self):
        ps_view_window = ttk.Toplevel(self.root)
        ps_view_window.title("UPLOAD HEAD TEACHER'S SIGNATURE")
        ps_view_window.geometry("400x600")
        
        # Center the window on the screen
        screen_width = ps_view_window.winfo_screenwidth()
        screen_height = ps_view_window.winfo_screenheight()
        window_width = 400
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        ps_view_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        signature.LoadSignatureApp(ps_view_window)

    def open_programme(self):
        programme_window = ttk.Toplevel(self.root)
        programme_window.title("Add Programme")
        programme_window.geometry("400x600")
        
        # Center the window on the screen
        screen_width = programme_window.winfo_screenwidth()
        screen_height = programme_window.winfo_screenheight()
        window_width = 400
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        programme_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        load_actual_programme.AddProgramme(programme_window)
        
    def open_api_key(self):
        api_key_window = ttk.Toplevel(self.root)
        api_key_window.title("Add API Key")
        api_key_window.geometry("600x600")
        
        # Center the window on the screen
        screen_width = api_key_window.winfo_screenwidth()
        screen_height = api_key_window.winfo_screenheight()
        window_width = 600
        window_height = 600
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        api_key_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        api.AddApiKey(api_key_window)
            
    def save_settings(self):
        class_score = self.class_score_var.get()
        exam_score = self.exam_score_var.get()

        if not class_score.isdigit() or not exam_score.isdigit():
            messagebox.showerror("Input Error", "Please enter valid percentage values.")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO score_percentage (id, class_score, exam_score)
            VALUES (1, ?, ?)
            ON CONFLICT(id) DO UPDATE SET class_score=excluded.class_score, exam_score=excluded.exam_score
        ''', (class_score, exam_score))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Setting saved successfully.")

    def load_settings(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS score_percentage (
                id INTEGER PRIMARY KEY,
                class_score INTEGER NOT NULL,
                exam_score INTEGER NOT NULL
            )
        ''')
        cursor.execute('SELECT class_score, exam_score FROM score_percentage WHERE id = 1')
        row = cursor.fetchone()
        conn.close()
        if row:
            self.class_score_var.set(row['class_score'])
            self.exam_score_var.set(row['exam_score'])

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    #REMOVE MINIMIZE AND MAXIMIZE BUTTONS
    root.attributes('-toolwindow', True)
    
 
    
    app = Setting(root)
    root.mainloop()
