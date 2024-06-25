import ttkbootstrap as ttk

from my_file import get_icon  # Import the get_icon function

def center_window(window, width=800, height=600):
    """Center the window on the screen."""
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    x_coordinate = (screen_width / 2) - (width / 2)
    y_coordinate = (screen_height / 2) - (height / 2)
    
    window.geometry(f"{width}x{height}+{int(x_coordinate)}+{int(y_coordinate)}")

def hide_window(window):
    """Hide the window until it's fully loaded."""
    window.withdraw()

def show_window(window):
    """Show the window once it's fully loaded."""
    window.update_idletasks()
    window.deiconify()

if __name__ == "__main__":
    root = ttk.Window("SDASS STUDENT REPORT SYSTEM V1.0", "darkly", resizable=(False, False))
    
    # Hide the window initially
    hide_window(root)

    # Set the window icon
    icon_path = get_icon('logo.ico')  # Assuming you have a logo.ico in the images folder
    root.wm_iconbitmap(icon_path)
    
    # Center the window
    center_window(root)
    

    
    # Show the window after everything is set up
    show_window(root)
    
    root.mainloop()
