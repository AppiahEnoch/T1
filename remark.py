import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import ttk as tkttk
from tkinter import messagebox
import sqlite3
import os
from db import get_db_connection



class Remark:
    def __init__(self, root):
        self.root = root
        self.root.title("Remarks Entry")

        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = 700
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

        ttk.Label(self.frame, text="Select Marks Range:", font=label_font).grid(row=0, column=0, padx=2, pady=entry_padding_y, sticky=E)
        self.mark_range_var = ttk.StringVar()
        self.mark_range_select = ttk.Combobox(self.frame, textvariable=self.mark_range_var, values=["90-100", "80-89", "70-79", "60-69", "50-59", "40-49", "30-39", "20-29", "10-19", "0-9"])
        self.mark_range_select.grid(row=0, column=1, padx=15, pady=entry_padding_y, sticky=W)
        self.mark_range_select.config(justify="center")

        ttk.Label(self.frame, text="Enter Remark:", font=label_font).grid(row=1, column=0, padx=2, pady=entry_padding_y, sticky=E)
        self.remark_var = ttk.StringVar()
        self.remark_entry = ttk.Entry(self.frame, textvariable=self.remark_var, width=40)
        self.remark_entry.grid(row=1, column=1, padx=15, pady=entry_padding_y, sticky=W)

        button_frame = ttk.Frame(self.frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=button_frame_padding_y)

        self.submit_button = ttk.Button(button_frame, text="Submit", command=self.submit, bootstyle="success")
        self.submit_button.pack(side=LEFT, padx=button_padding_x)

        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset, bootstyle="secondary")
        self.reset_button.pack(side=LEFT, padx=button_padding_x)

        self.remark_list_frame = ttk.Frame(self.frame, padding=(20, 10))
        self.remark_list_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0), sticky=NSEW)

        self.tree = ttk.Treeview(self.remark_list_frame, columns=("id", "mark_range", "remark", "action"), show='headings')
        self.tree.heading("id", text="ID")
        self.tree.heading("mark_range", text="Marks Range")
        self.tree.heading("remark", text="Remark")
        self.tree.heading("action", text="Action")
        self.tree.column("id", anchor=CENTER, width=50)
        self.tree.column("mark_range", anchor=CENTER, width=100)
        self.tree.column("remark", anchor=W, width=400)
        self.tree.column("action", anchor=CENTER, width=100)
        self.tree.grid(row=0, column=0, sticky=NSEW)

        self.tree.column("id", width=0, stretch=False)
        self.tree.column("action", width=75, stretch=False)

        self.populate_remarks()

    def submit(self):
        mark_range = self.mark_range_var.get()
        remark = self.remark_var.get()
        remark = remark.strip().upper()

        if not mark_range or not remark:
            messagebox.showwarning("Input Error", "Please select a marks range and enter a remark.")
            return

        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO remark (mark_range, remark)
                VALUES (?, ?)
            ''', (mark_range, remark))
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Remark added successfully")
            self.populate_remarks()
            self.reset()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add remark: {e}")

    def reset(self):
        self.mark_range_var.set("")
        self.remark_var.set("")

    def delete_remark(self, remark_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this remark?")
        if confirm:
            try:
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute('DELETE FROM remark WHERE id = ?', (remark_id,))
                conn.commit()
                conn.close()
                self.populate_remarks()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete remark: {e}")

    def populate_remarks(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM remark ORDER BY mark_range desc')
        remarks = cursor.fetchall()
        conn.close()

        for row in remarks:
            self.tree.insert("", "end", values=(row["id"], row["mark_range"], row["remark"], "Delete"))

        self.tree.bind("<ButtonRelease-1>", self.on_tree_select)

    def on_tree_select(self, event):
        item = self.tree.identify('item', event.x, event.y)
        column = self.tree.identify_column(event.x)
        if column == '#4':  # Check if the 'Action' column was clicked
            remark_id = self.tree.item(item, 'values')[0]
            self.delete_remark(remark_id)

if __name__ == "__main__":
    root = ttk.Window("Remarks Entry", "darkly")
    app = Remark(root)
    root.mainloop()
