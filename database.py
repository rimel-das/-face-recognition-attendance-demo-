"""
database.py
-----------
Handles all SQLite database operations for the Face Attendance App.
Two tables:
  - students   : stores student info and path to face encoding file
  - attendance : stores daily attendance records (UNIQUE per student per day)

Best practices:
  - Always use context managers for connections
  - SQL parameters are used to prevent injection
  - Timestamps are auto-managed by SQLite
"""

import sqlite3
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Path to the SQLite database file
DB_PATH = "attendance.db"


def get_connection():
    """Return a database connection with row_factory for dict-like rows."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    return conn


def init_db():
    """
    Create the database tables if they don't already exist.
    Call this once at app startup.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- Students table ---
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT    NOT NULL,
            student_id  TEXT    NOT NULL UNIQUE,   -- e.g. "STU001"
            encoding_path TEXT  NOT NULL,          -- path to .pkl file on disk
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # --- Attendance table ---
    # UNIQUE(student_id, date) prevents the same student from being marked
    # present more than once on the same day.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  TEXT    NOT NULL,          -- references students.student_id
            student_name TEXT   NOT NULL,
            date        TEXT    NOT NULL,          -- "YYYY-MM-DD"
            time        TEXT    NOT NULL,          -- "HH:MM:SS"
            UNIQUE(student_id, date)               -- duplicate-prevention constraint
        )
    """)

    conn.commit()
    conn.close()
    print("[DB] Database initialised successfully.")


# ---------------------------------------------------------------------------
# Student helpers
# ---------------------------------------------------------------------------

def add_student(name: str, student_id: str, encoding_path: str) -> dict:
    """
    Insert a new student record.
    Returns {"success": True/False, "message": str}
    """
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO students (name, student_id, encoding_path) VALUES (?, ?, ?)",
            (name, student_id, encoding_path)
        )
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Student '{name}' registered successfully."}
    except sqlite3.IntegrityError:
        return {"success": False, "message": f"Student ID '{student_id}' already exists."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_all_students() -> list:
    """Return a list of all students as dicts."""
    conn = get_connection()
    rows = conn.execute("SELECT * FROM students ORDER BY registered_at DESC").fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_student_by_id(student_id: str) -> dict | None:
    """Return a single student dict or None."""
    conn = get_connection()
    row = conn.execute(
        "SELECT * FROM students WHERE student_id = ?", (student_id,)
    ).fetchone()
    conn.close()
    return dict(row) if row else None


def get_student_count() -> int:
    """Return total number of registered students."""
    conn = get_connection()
    count = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    conn.close()
    return count


# ---------------------------------------------------------------------------
# Attendance helpers
# ---------------------------------------------------------------------------

def mark_attendance(student_id: str, student_name: str, date: str, time: str) -> dict:
    """
    Insert an attendance record.
    Silently ignores duplicate (same student, same day) due to UNIQUE constraint.
    Returns {"success": True/False, "message": str}
    """
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO attendance (student_id, student_name, date, time) VALUES (?, ?, ?, ?)",
            (student_id, student_name, date, time)
        )
        conn.commit()
        conn.close()
        return {"success": True, "message": f"Attendance marked for '{student_name}'."}
    except sqlite3.IntegrityError:
        # Already marked today — not an error, just a duplicate
        return {"success": False, "message": f"Attendance already marked for '{student_name}' today."}
    except Exception as e:
        return {"success": False, "message": str(e)}


def get_today_attendance_count(today: str) -> int:
    """Return how many unique students have been marked present today."""
    conn = get_connection()
    count = conn.execute(
        "SELECT COUNT(*) FROM attendance WHERE date = ?", (today,)
    ).fetchone()[0]
    conn.close()
    return count


def get_recent_attendance(limit: int = 10) -> list:
    """Return the most recent attendance records."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM attendance ORDER BY date DESC, time DESC LIMIT ?", (limit,)
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_attendance_report(date_filter: str = None, name_filter: str = None) -> list:
    """
    Return filtered attendance records for the report page.
    Both filters are optional and combinable.
    """
    query = "SELECT * FROM attendance WHERE 1=1"
    params = []

    if date_filter:
        query += " AND date = ?"
        params.append(date_filter)

    if name_filter:
        query += " AND student_name LIKE ?"
        params.append(f"%{name_filter}%")

    query += " ORDER BY date DESC, time DESC"

    conn = get_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in rows]
