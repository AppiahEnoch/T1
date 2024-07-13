# AE.py

from datetime import datetime
import os
import json

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')

def generate_years():
    current_year = datetime.now().year
    start_year = 1991
    return [f"{year-1}/{year}" for year in range(current_year, start_year - 1, -1)]

def set_preferred_year_semester(year, semester):
    data = {}
    if year:
        data["year"] = year
    if semester:
        data["semester"] = semester
    
    filename = os.path.join(APP_DIR, 'selected_year_semester.json')
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def get_preferred_year_semester():
    filename = os.path.join(APP_DIR, 'selected_year_semester.json')
    if os.path.exists(filename):
        with open(filename, 'r') as json_file:
            return json.load(json_file)
    return {}