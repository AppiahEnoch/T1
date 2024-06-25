class MainController:
    def __init__(self, root):
        self.root = root
        self.current_window = None

    def show_login_window(self):
        self._switch_window('login', 'LoginController')

    def show_registration_window(self):
        self._switch_window('registration', 'RegistrationController')
        
    def show_dashboard(self):
        self._switch_window('dashboard', 'Dashboard')

    def _switch_window(self, window_module_name, controller_class_name):
        self._close_current_window()
        window_module = __import__(window_module_name)
        controller_class = getattr(window_module, controller_class_name)
        self.current_window = controller_class(self.root, self)
        self.current_window.show()

    def _close_current_window(self):
        if self.current_window:
            self.current_window.close()
        self.current_window = None
