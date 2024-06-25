import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from crud import *
from main_controller import *
import threading
import time

class LoginController:
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

        # Main heading
        main_label = ttk.Label(container, text="SDASS STUDENT REPORT SYSTEM", font=("Helvetica", 18, "bold"))
        main_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Subheading for login
        login_label = ttk.Label(container, text="Login", font=("Helvetica", 18, "bold"))
        login_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Username
        username_label = ttk.Label(container, text="Username")
        username_label.grid(row=2, column=0, padx=5, pady=5, sticky=E)
        self.username_entry = ttk.Entry(container, width=30, font=("Helvetica", 9, "bold"))
        self.username_entry.grid(row=2, column=1, padx=5, pady=5, sticky=W)

        # Password
        password_label = ttk.Label(container, text="Password")
        password_label.grid(row=3, column=0, padx=5, pady=5, sticky=E)
        self.password_entry = ttk.Entry(container, show="*", width=30, font=("Helvetica", 9, "bold"))
        self.password_entry.grid(row=3, column=1, padx=5, pady=5, sticky=W)

        # Buttons
        button_frame = ttk.Frame(container)
        button_frame.grid(row=4, column=0, columnspan=2, pady=10)

        login_button = ttk.Button(button_frame, text="Login", command=self._start_login_thread, bootstyle=SUCCESS)
        login_button.pack(side=LEFT, padx=5)

        register_button = ttk.Button(button_frame, text="Register", command=self.main_controller.show_registration_window, bootstyle=INFO)
        register_button.pack(side=LEFT, padx=5)

    def _start_login_thread(self):
        threading.Thread(target=self._login).start()

    def _login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username:
            self._show_message("Username is required", "Username is required", "error")
        elif not password:
            self._show_message("Password is required", "Password is required", "error")
        elif validate_login(username, password):
            self.root.after(0, self._show_progress_and_navigate)
        else:
            self._show_message("Login failed", "Login failed", "error")

    def _show_progress_and_navigate(self):
        progress = ttk.Progressbar(self.frame, mode='indeterminate', bootstyle=SUCCESS)
        progress.grid(row=5, column=0, columnspan=2, pady=10)
        progress.start()
        self.frame.update_idletasks()

        # Simulate delay for dashboard loading
        self.root.after(2000, lambda: self._navigate_to_dashboard(progress))

    def _navigate_to_dashboard(self, progress):
        progress.stop()
        progress.destroy()
        self.main_controller.show_dashboard()  # Navigate to the dashboard on successful login

    def _show_message(self, title, message, message_type):
        if message_type == "error":
            self.root.after(0, lambda: Messagebox.show_error(message, title))

    def close(self):
        if self.frame:
            self.frame.pack_forget()
            self.frame.destroy()
            self.frame = None

if __name__ == "__main__":
    root = ttk.Window(themename="darkly")
    main_controller = MainController(root)
    login_controller = LoginController(root, main_controller)
    login_controller.show()
    root.mainloop()
