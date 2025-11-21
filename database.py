import sqlite3
import os
from datetime import datetime

class AccessDatabase:
    def __init__(self, db_path):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create tables if they don't exist"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS people (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS access_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                person_id INTEGER,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                access_granted BOOLEAN,
                FOREIGN KEY (person_id) REFERENCES people(id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def register_person(self, name):
        """Register a new person"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO people (name) VALUES (?)', (name,))
            conn.commit()
            person_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            cursor.execute('SELECT id FROM people WHERE name = ?', (name,))
            person_id = cursor.fetchone()[0]
        finally:
            conn.close()
        return person_id
    
    def log_access(self, person_id, access_granted):
        """Log access attempt"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO access_logs (person_id, access_granted)
            VALUES (?, ?)
        ''', (person_id, access_granted))
        conn.commit()
        conn.close()
    
    def get_all_logs(self):
        """Get all access logs with person names"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.name, l.timestamp, l.access_granted
            FROM access_logs l
            LEFT JOIN people p ON l.person_id = p.id
            ORDER BY l.timestamp DESC
        ''')
        logs = cursor.fetchall()
        conn.close()
        return logs
    
    def get_registered_people(self):
        """Get list of registered people"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name FROM people ORDER BY name')
        people = cursor.fetchall()
        conn.close()
        return people
