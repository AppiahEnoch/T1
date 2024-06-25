import sqlite3
import requests
import os
import GS

HOME_DIR = os.path.expanduser('~')
APP_DIR = os.path.join(HOME_DIR, 'SHSStudentReportSystem')
DATABASE_FILENAME = 'shs.db'
DATABASE_FILE = os.path.join(APP_DIR, DATABASE_FILENAME)

def get_db_connection():
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def send_sms(message, mobile):
    apiKey = GS.get_api_key()

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT short_name FROM school_details WHERE id = 1")
    record = cursor.fetchone()
    conn.close()

    if record:
        sender_id = record['short_name']
        if len(sender_id) > 8:
            sender_id = sender_id[:8]
    else:
        sender_id = 'SHS-REP'

    recipient = ""
    if mobile.startswith('0'):
        recipient = '233' + mobile[1:]
    elif not mobile.startswith('+'):
        recipient = '+' + mobile
    else:
        recipient = mobile

    if len(recipient) < 6:
        return False

    url = 'https://sms.arkesel.com/sms/api?action=send-sms'
    encoded_message = requests.utils.quote(message)
    final_url = f"{url}&api_key={apiKey}&to={recipient}&from={sender_id}&sms={encoded_message}"
    response = requests.get(final_url)

    if response.status_code == 200:
        return 1
    else:
        return 0
