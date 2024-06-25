import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
from datetime import datetime
from dateutil.parser import parse
import sqlite3
import os
from tkcalendar import DateEntry

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def format_date_with_suffix(date):
    day = int(date.strftime("%d"))
    suffix = "th" if 11 <= day <= 13 else {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
    return date.strftime(f"{day}{suffix} %B, %Y")

class NextTerm:
    def __init__(self, root):
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS next_term (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                year TEXT,
                semester TEXT,
                next_term TEXT,
                UNIQUE(year, semester)
            )
        ''')
        conn.commit()
        conn.close()
        
        self.root = root
        self.root.title("Add Next Term")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        window_width = 500
        window_height = 400

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")

        frame_padding = (20, 20)
        label_font = ("Helvetica", 12)
        entry_padding_x = 10
        entry_padding_y = 5
        button_padding_x = 10
        button_padding_y = 5
        button_frame_padding_y = 10

        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)

        ttk.Label(self.frame, text="Select Year:", font=label_font).grid(row=0, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.year_var = ttk.StringVar()
        self.year_select = ttk.Combobox(self.frame, textvariable=self.year_var, values=self.generate_years())
        self.year_select.grid(row=0, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.year_select.config(justify="center")

        ttk.Label(self.frame, text="Select Semester/Term:", font=label_font).grid(row=1, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.semester_var = ttk.StringVar()
        self.semester_select = ttk.Combobox(self.frame, textvariable=self.semester_var, values=["1", "2", "3"])
        self.semester_select.grid(row=1, column=1, padx=entry_padding_x, pady=entry_padding_y, sticky=W)
        self.semester_select.config(justify="center")

        ttk.Label(self.frame, text="Next Term Begin:", font=label_font).grid(row=2, column=0, padx=entry_padding_x, pady=entry_padding_y, sticky=E)
        self.next_term_begin = ttk.DateEntry(self.frame, width=28, bootstyle="info", dateformat='%d/%m/%Y')
        self.next_term_begin.grid(row=2, column=1, padx=15, pady=entry_padding_y, sticky=ttk.W)


        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=button_frame_padding_y)

        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.pack(side=LEFT, padx=button_padding_x)

        # Table style
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25, font=("Helvetica", 10), bordercolor="gray", borderwidth=1)
        style.map('Custom.Treeview', background=[('selected', 'blue')])
        style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 12, "bold"), background="lightgray", foreground="black")

        # Table setup
        columns = ("year", "semester", "next_term", "delete")
        self.table = tkttk.Treeview(self.frame, columns=columns, show="headings", style="Custom.Treeview")
        self.table.heading("year", text="Year")
        self.table.heading("semester", text="Semester")
        self.table.heading("next_term", text="Next Term Begin")
        self.table.heading("delete", text="")

        self.table.column("year", width=100, anchor=CENTER)
        self.table.column("semester", width=100, anchor=CENTER)
        self.table.column("next_term", width=200, anchor=CENTER)
        self.table.column("delete", width=50, anchor=CENTER)

        self.table.grid(row=4, column=0, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        # Scrollbar for the table
        scrollbar = tkttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=4, column=2, sticky='ns')

        # Configure table column weights
        self.frame.grid_rowconfigure(4, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # Initial data
        self.update_table()

    def generate_years(self):
        current_year = datetime.now().year
        start_year = 1991
        end_year = current_year + 1
        return [f"{year}/{year + 1}" for year in range(end_year, start_year - 1, -1)]

    def submit(self):
        year = self.year_var.get()
        semester = self.semester_var.get()
        next_term_date = self.next_term_begin.entry.get()

        if not year or not semester:
            messagebox.showwarning("Input Error", "Please select both year and semester/term.")
            return

        try:
            parsed_date = parse(next_term_date, fuzzy=True)
            formatted_date = format_date_with_suffix(parsed_date)
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS next_term (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    year TEXT,
                    semester TEXT,
                    next_term TEXT,
                    UNIQUE(year, semester)
                )
            ''')
            cursor.execute('''
                INSERT INTO next_term (year, semester, next_term)
                VALUES (?, ?, ?)
                ON CONFLICT(year, semester) DO UPDATE SET next_term=excluded.next_term
            ''', (year, semester, formatted_date))
            conn.commit()
            conn.close()
            self.update_table()
            #messagebox.showinfo("Success", "Next term details added successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add next term details: {e}")

    def update_table(self):
        # Clear the table
        for item in self.table.get_children():
            self.table.delete(item)

        # Insert new data from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT year, semester, next_term FROM next_term ORDER BY year ASC")
        for row in cursor.fetchall():
            self.table.insert("", "end", values=(row["year"], row["semester"], row["next_term"], "Delete"))
        conn.close()

        # Add delete button functionality
        self.table.bind('<ButtonRelease-1>', self.on_delete)

    def on_delete(self, event):
        item = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        if item and column == '#4':  # The 'delete' column is at index 4
            year, semester, next_term = self.table.item(item, "values")[:3]
            if messagebox.askyesno("Delete", f"Are you sure you want to delete the record for year {year}, semester {semester}?"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM next_term WHERE year = ? AND semester = ? AND next_term = ?", (year, semester, next_term))
                conn.commit()
                conn.close()
                self.update_table()

if __name__ == "__main__":
    root = ttk.Window("Add Next Term", "superhero")
    app = NextTerm(root)
    root.mainloop()
