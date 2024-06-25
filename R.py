import os
import sys


def resource_path(relative_path):
    """Get the absolute path to a resource, works for dev and PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

def get_default_signature_image():
    """Get the absolute path to the default signature image."""
    return resource_path(os.path.join('images', 'default_signature.jpg'))

def get_default_logo_image():
    """Get the absolute path to the default signature image."""
    return resource_path(os.path.join('images', 'logo.jpeg'))

