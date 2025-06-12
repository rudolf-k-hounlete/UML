import sqlite3
import os

def initialize_database():
    """
    Creates an SQLite database file named school.db in the data directory.
    Connects to the database.
    Creates the tables defined in the schema if they don't already exist.
    """
    # Construct path relative to this file (src/database_setup.py)
    # Go up one level to project root, then into 'data' directory
    db_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
    os.makedirs(db_dir, exist_ok=True) # Ensure data directory exists
    db_path = os.path.join(db_dir, 'school.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create departments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS departments (
        department_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL
    )
    ''')

    # Create formations table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS formations (
        formation_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        duration_years INTEGER NOT NULL,
        department_id INTEGER,
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
    )
    ''')

    # Create students table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        student_id TEXT PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
    )
    ''')

    # Create subjects table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        credits INTEGER NOT NULL,
        year INTEGER NOT NULL,
        formation_id INTEGER,
        FOREIGN KEY (formation_id) REFERENCES formations(formation_id)
    )
    ''')

    # Create enrollments table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS enrollments (
        enrollment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        formation_id INTEGER,
        enrollment_year INTEGER NOT NULL,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (formation_id) REFERENCES formations(formation_id),
        UNIQUE(student_id, formation_id)
    )
    ''')

    # Create grades table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS grades (
        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        enrollment_id INTEGER,
        subject_id INTEGER,
        grade REAL,
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(enrollment_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id)
    )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    initialize_database()
