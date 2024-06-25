import os
import shutil
import subprocess

def clean_and_build():
    # Directories to be removed and recreated
    directories = ['build', 'dist']

    # Remove old directories
    for dir in directories:
        if os.path.exists(dir):
            print(f"Removing old {dir} directory...")
            shutil.rmtree(dir)

    # Create new directories
    for dir in directories:
        print(f"Creating new {dir} directory...")
        os.makedirs(dir)

    # Run PyInstaller
    print("Running PyInstaller...")
    result = subprocess.run(['pyinstaller', '--clean', 'main.spec'], capture_output=True, text=True)

    # Print PyInstaller output
    print(result.stdout)
    
    if result.returncode != 0:
        print("Error occurred during build:")
        print(result.stderr)
    else:
        print("Build completed successfully.")

if __name__ == "__main__":
    clean_and_build()