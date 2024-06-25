import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
from crud import *
import os
import CPS

class Addsubject:
    def __init__(self, root):
        self.root = root
        self.root.title("Add subject")
        root.attributes("-topmost", False)

        # Calculate screen width and height
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()

        # Window size
        window_width = 550
        window_height = 450

        # Calculate window position to center it on the screen
        window_x = (screen_width - window_width) // 2
        window_y = (screen_height - window_height) // 2

        # Set window size and position
        self.root.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")
        
        # Resize the window false
        self.root.resizable(False, False)

        # Padding and font size variables
        frame_padding = (20, 20)
        label_font = ("Helvetica", 12)
        entry_padding_x = 10
        entry_padding_y = 5
        button_padding_x = 10
        button_padding_y = 5
        button_frame_padding_y = 10

        # Frame setup
        self.frame = ttk.Frame(self.root, padding=frame_padding)
        self.frame.pack(fill=BOTH, expand=TRUE)

        # subject name entry
        ttk.Label(self.frame, text="Enter Subject Name: eg. ENGLISH LANGUAGE", font=label_font).grid(row=0, column=0, padx=2, pady=entry_padding_y)
        
        self.subject_name_var = ttk.StringVar()
        self.subject_name_entry = ttk.Entry(self.frame, textvariable=self.subject_name_var, width=30)
        self.subject_name_entry.grid(row=1, column=0, padx=1, pady=entry_padding_y)

        # Short name entry
        ttk.Label(self.frame, text="Enter Short Name: eg. ENG,MAT,SOC", font=label_font).grid(row=2, column=0, padx=2, pady=entry_padding_y)
        
        self.short_name_var = ttk.StringVar()
        self.short_name_entry = ttk.Entry(self.frame, textvariable=self.short_name_var, width=30)
        self.short_name_entry.grid(row=3, column=0, padx=1, pady=entry_padding_y)

        # Is Core checkbox
        self.is_core_var = ttk.BooleanVar(value=False)
        self.is_core_check = ttk.Checkbutton(self.frame, text="Is Core", variable=self.is_core_var, bootstyle="round-toggle")
        self.is_core_check.grid(row=4, column=0, padx=15, pady=entry_padding_y, sticky=W)

        # Submit button
        self.submit_button = ttk.Button(self.frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.grid(row=5, column=0, columnspan=3, pady=button_frame_padding_y)

        # Table style
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25, font=("Helvetica", 10), bordercolor="gray", borderwidth=1)
        style.map('Custom.Treeview', background=[('selected', 'blue')])
        style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 12, "bold"), background="lightgray", foreground="black")

        # Table setup
        columns = ("id", "subject_name", "short_name", "is_core", "delete")
        self.table = tkttk.Treeview(self.frame, columns=columns, show="headings", style="Custom.Treeview")
        self.table.heading("id", text="ID")
        self.table.heading("subject_name", text="Subject Name")
        self.table.heading("short_name", text="Short Name")
        self.table.heading("is_core", text="Is Core")
        self.table.heading("delete", text="")

        self.table.column("id", width=50, anchor=CENTER)
        self.table.column("subject_name", width=150, anchor=CENTER)
        self.table.column("short_name", width=100, anchor=CENTER)
        self.table.column("is_core", width=100, anchor=CENTER)
        self.table.column("delete", width=50, anchor=CENTER)

        self.table.grid(row=6, column=0, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        # Scrollbar for the table
        scrollbar = tkttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=6, column=2, sticky='ns')

        # Configure table column weights
        self.frame.grid_rowconfigure(6, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # Initial data
        self.update_table()

        # Bind the table row click event
        self.table.bind('<ButtonRelease-1>', self.on_table_click)

    def submit(self):
        subject_name = self.subject_name_var.get().upper()
        short_name = self.short_name_var.get().upper()
        is_core = 1 if self.is_core_var.get() else 0
        if subject_name and short_name:
            insert_update_table('subject_name', 'subject', ['subject_name', 'short_name', 'is_core'], [subject_name, short_name, is_core])
            self.subject_name_var.set("")
            self.short_name_var.set("")
            self.is_core_var.set(False)
            self.update_table()
            CPS.includeCoreSubjectsIntoProgramme_subject()
            CPS.includeCoreSubjectsIntoClassProgrammeSubject()

    def update_table(self):
        # Clear the table
        for item in self.table.get_children():
            self.table.delete(item)

        # Insert new data from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, subject_name, short_name, is_core FROM subject ORDER BY subject_name ASC")
        for row in cursor.fetchall():
            is_core = "Yes" if row["is_core"] else "No"
            self.table.insert("", "end", values=(row["id"], row["subject_name"], row["short_name"], is_core, "Delete"))
        conn.close()

    def on_table_click(self, event):
        item = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        if item and column == '#5':  # The 'delete' column is at index 4 (5th column)
            record_id = self.table.item(item, "values")[0]
            self.confirm_delete(record_id)
        else:
            self.on_row_click(event)

    def confirm_delete(self, record_id):
        if messagebox.askyesno("Delete", "Are you sure you want to delete this record?"):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM subject WHERE id = ?", (record_id,))
            conn.commit()
            conn.close()
            self.update_table()

    def on_row_click(self, event):
        item = self.table.selection()
        if item:
            item = item[0]
            values = self.table.item(item, "values")
            self.subject_name_var.set(values[1])
            self.short_name_var.set(values[2])
            self.is_core_var.set(values[3] == "Yes")

if __name__ == "__main__":
    root = ttk.Window("Add subject/Subject", "superhero")
    app = Addsubject(root)
    root.mainloop()
