import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from crud import *

class RegistrationController:
    def __init__(self, root, main_controller):
        self.root = root
        self.main_controller = main_controller
        self.frame = None

    def show(self):
        self.frame = ttk.Frame(self.root, padding=(150, 50))
        self.frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        container = ttk.Frame(self.frame)
        container.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)
        self.frame.grid_rowconfigure(0, weight=1)

        row = 0

        # Main heading
        main_label = ttk.Label(container, text="SDASS STUDENT REPORT SYSTEM", font=("Helvetica", 18, "bold"))
        main_label.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        # Subheading for registration
        register_label = ttk.Label(container, text="Register", font=("Helvetica", 18, "bold"))
        register_label.grid(row=row, column=0, columnspan=2, pady=10)
        row += 1

        # Username
        username_label = ttk.Label(container, text="Username")
        username_label.grid(row=row, column=0, padx=5, pady=5, sticky=E)
        self.username_entry = ttk.Entry(container, width=30)
        self.username_entry.grid(row=row, column=1, padx=5, pady=5, sticky=W)
        row += 1

        # Password
        password_label = ttk.Label(container, text="Password")
        password_label.grid(row=row, column=0, padx=5, pady=5, sticky=E)
        self.password_entry = ttk.Entry(container, show="*", width=30)
        self.password_entry.grid(row=row, column=1, padx=5, pady=5, sticky=W)
        row += 1

        # Confirm Password
        confirm_password_label = ttk.Label(container, text="ConfirmPassword")
        confirm_password_label.grid(row=row, column=0, padx=5, pady=5, sticky=E)
        self.confirm_password_entry = ttk.Entry(container, show="*", width=30)
        self.confirm_password_entry.grid(row=row, column=1, padx=5, pady=5, sticky=W)
        row += 1

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.grid(row=row, column=1, columnspan=4, pady=10, sticky=W)
        
        register_button = ttk.Button(button_frame, text="Register", command=self._register, bootstyle=SUCCESS)
        register_button.pack(side=LEFT, padx=5)

        back_button = ttk.Button(button_frame, text="Back to Login", command=self.main_controller.show_login_window, bootstyle=INFO)
        back_button.pack(side=LEFT, padx=5)

    def _register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        if not username:
            Messagebox.show_error("Username is required", "Username is required")
        elif not password:
            Messagebox.show_error("Password is required", "Password is required")
        elif not confirm_password:
            Messagebox.show_error("Confirm password is required", "Confirm password is required")
        elif password != confirm_password:
            Messagebox.show_error("Passwords do not match", "Passwords do not match")
        else:
            if create_user(username, password):
                Messagebox.show_info("Success", "Registration successful!")
            else:
                Messagebox.show_error("Error", "User creation failed")


    def close(self):
        if self.frame:
            self.frame.pack_forget()
            self.frame.destroy()
            self.frame = None
