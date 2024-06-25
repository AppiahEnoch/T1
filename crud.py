import sqlite3
from tkinter import messagebox
from create_table import *
import bcrypt

def create_user(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    if cursor.fetchone():
        messagebox.showerror("Error", "Username already exists")
        conn.close()
        return False
    
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    conn.close()
    return True


def insert_update_table(unique_key_column, table_name, columns, values):
    conn = get_db_connection()
    cursor = conn.cursor()

    placeholders = ', '.join('?' * len(values))
    columns_str = ', '.join(columns)
    update_str = ', '.join(f"{col} = ?" for col in columns)

    query = f"""
        INSERT INTO {table_name} ({unique_key_column}, {columns_str})
        VALUES (?, {placeholders})
        ON CONFLICT({unique_key_column}) 
        DO UPDATE SET {update_str}
    """

    cursor.execute(query, (values[0], *values, *values))
    conn.commit()
    conn.close()

def validate_login(username, password):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row is None:
        #messagebox.showerror("Error", "Username does not exist")
        return False
    
    stored_password = row['password']
    
    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        messagebox.showinfo("Success", "Login successful")
        return True
    else:
        messagebox.showerror("Error", "Incorrect password")
        return False
