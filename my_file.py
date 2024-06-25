import os
import ttkbootstrap as ttk
import sys

def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller"""
    try:
        # PyInstaller creates a temporary folder and stores the path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_image(image_filename):
    """Retrieve the image file path."""
    # Determine the path to the image
    image_path = resource_path(os.path.join('images', image_filename))
    
    # Load the image using ttk.PhotoImage
    return ttk.PhotoImage(file=image_path)

def get_icon(icon_filename):
    """Retrieve the icon file path."""
    icon_path = resource_path(os.path.join('images', icon_filename))
    return icon_path
