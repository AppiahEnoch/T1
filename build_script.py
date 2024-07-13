import os
import shutil
import subprocess
import logging
from pathlib import Path

HOME_DIR = Path.home()
APP_DIR = HOME_DIR / 'SHSStudentReportSystem'
DATABASE_FILE = APP_DIR / 'shs.db'
LOG_FILE = APP_DIR / 'shs.log'

# Set up logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_print(message):
    print(message)
    logging.info(message)

def clean_and_build():
    # Directories to be removed and recreated
    directories = ['build', 'dist']

    try:
        # Remove old directories
        for dir in directories:
            if os.path.exists(dir):
                log_print(f"Removing old {dir} directory...")
                shutil.rmtree(dir)

        # Create new directories
        for dir in directories:
            log_print(f"Creating new {dir} directory...")
            os.makedirs(dir)

        # Run PyInstaller
        log_print("Running PyInstaller...")
        result = subprocess.run(['pyinstaller', 'main.spec'], capture_output=True, text=True)

        # Log PyInstaller output
        logging.info(result.stdout)
        
        if result.returncode != 0:
            log_print("Error occurred during build:")
            logging.error(result.stderr)
        else:
            log_print("Build completed successfully.")

    except Exception as e:
        logging.exception("An error occurred during the clean and build process:")
        log_print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    clean_and_build()