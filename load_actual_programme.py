import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
from crud import *
import os

class AddProgramme:
    def __init__(self, root):
        self.root = root
        self.root.title("Add Programme")
        root.attributes("-topmost", False)

        # Calculate screen width and height
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()

        # Calculate window position to center it on the screen
        window_width = 500
        window_height = 400
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
        self.frame.pack(fill=ttk.BOTH, expand=ttk.TRUE)

        # Programme name entry
        ttk.Label(self.frame, text="Enter Programme Name:", font=label_font).grid(row=0, column=0, padx=2, pady=entry_padding_y)
        
        self.programme_name_var = ttk.StringVar()
        self.programme_name_entry = ttk.Entry(self.frame, textvariable=self.programme_name_var, width=30)
        self.programme_name_entry.grid(row=1, column=0, padx=15, pady=entry_padding_y, sticky=ttk.W)

        # Submit button
        self.submit_button = ttk.Button(self.frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.grid(row=1, column=0, columnspan=3, pady=button_frame_padding_y)

        # Table style
        style = ttk.Style()
        style.configure("Custom.Treeview", rowheight=25, font=("Helvetica", 10), bordercolor="gray", borderwidth=1)
        style.map('Custom.Treeview', background=[('selected', 'blue')])
        style.layout("Custom.Treeview", [('Custom.Treeview.treearea', {'sticky': 'nswe'})])
        style.configure("Custom.Treeview.Heading", font=("Helvetica", 12, "bold"), background="lightgray", foreground="black")

        # Table setup
        columns = ("programme_name", "delete")
        self.table = tkttk.Treeview(self.frame, columns=columns, show="headings", style="Custom.Treeview")
        self.table.heading("programme_name", text="Programme Name")
        self.table.heading("delete", text="")

        self.table.column("programme_name", width=300, anchor=ttk.CENTER)
        self.table.column("delete", width=50, anchor=ttk.CENTER)

        self.table.grid(row=3, column=0, columnspan=2, padx=entry_padding_x, pady=entry_padding_y, sticky="nsew")

        # Scrollbar for the table
        scrollbar = tkttk.Scrollbar(self.frame, orient="vertical", command=self.table.yview)
        self.table.configure(yscroll=scrollbar.set)
        scrollbar.grid(row=3, column=2, sticky='ns')

        # Configure table column weights
        self.frame.grid_rowconfigure(3, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_columnconfigure(1, weight=1)

        # Initial data
        self.update_table()

    def submit(self):
        programme_name = self.programme_name_var.get().strip().lower().title()
        if programme_name:
            insert_update_table('programme_name', 'programme', ['programme_name'], [programme_name])
            self.update_table()
            self.programme_name_var.set("")
            messagebox.showinfo("Success", f"Programme '{programme_name}' added successfully.")

    def update_table(self):
        # Clear the table
        for item in self.table.get_children():
            self.table.delete(item)

        # Insert new data from database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT programme_name FROM programme ORDER BY programme_name ASC")
        for row in cursor.fetchall():
            self.table.insert("", "end", values=(row["programme_name"], "Delete"))
        conn.close()

        # Add delete button functionality
        self.table.bind('<ButtonRelease-1>', self.on_delete)

    def on_delete(self, event):
        item = self.table.identify_row(event.y)
        column = self.table.identify_column(event.x)
        if item and column == '#2':  # The 'delete' column is at index 1 (2nd column)
            programme_name = self.table.item(item, "values")[0]
            if messagebox.askyesno("Delete", f"Are you sure you want to delete '{programme_name}'?"):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM programme WHERE programme_name = ?", (programme_name,))
                conn.commit()
                conn.close()
                self.update_table()

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    app = AddProgramme(root)
    root.mainloop()
