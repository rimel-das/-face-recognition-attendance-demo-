"""
app.py
------
Main entry point for the Face Recognition Attendance Web App.
Run with:  python app.py

Stack: Flask · OpenCV · face_recognition · SQLite
"""

import os
import base64
import pickle
import io
from datetime import datetime

import cv2
import numpy as np
import face_recognition
from flask import (
    Flask, render_template, request, jsonify,
    Response, send_file
)

from database import (
    init_db, add_student, get_all_students, get_student_count,
    mark_attendance, get_today_attendance_count,
    get_recent_attendance, get_attendance_report
)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__)

# Folder where face encoding .pkl files are stored
ENCODINGS_DIR = "encodings"
os.makedirs(ENCODINGS_DIR, exist_ok=True)

# Tolerance for face comparison (lower = stricter). 0.5 is a good balance.
FACE_MATCH_TOLERANCE = 0.5

# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def load_all_encodings() -> list[dict]:
    """
    Load every student's face encoding from disk.
    Returns a list of {"student_id": str, "name": str, "encoding": np.array}
    """
    students = get_all_students()
    loaded = []
    for student in students:
        path = student.get("encoding_path", "")
        if os.path.exists(path):
            try:
                with open(path, "rb") as f:
                    encoding = pickle.load(f)
                loaded.append({
                    "student_id": student["student_id"],
                    "name": student["name"],
                    "encoding": encoding
                })
            except Exception as e:
                print(f"[WARN] Could not load encoding for {student['name']}: {e}")
    return loaded


def decode_base64_image(b64_string: str) -> np.ndarray | None:
    """
    Convert a base64-encoded image string (from JS canvas) to an OpenCV numpy array.
    Returns None on failure.
    """
    try:
        # Strip the data-URL prefix if present (e.g. "data:image/jpeg;base64,...")
        if "," in b64_string:
            b64_string = b64_string.split(",", 1)[1]
        img_bytes = base64.b64decode(b64_string)
        np_array = np.frombuffer(img_bytes, dtype=np.uint8)
        img = cv2.imdecode(np_array, cv2.IMREAD_COLOR)
        return img
    except Exception as e:
        print(f"[ERROR] base64 decode failed: {e}")
        return None


def get_face_encoding(img_bgr: np.ndarray) -> np.ndarray | None:
    """
    Extract a 128-d face encoding from a BGR OpenCV image.
    Returns None if no face is detected.
    """
    # face_recognition expects RGB
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    face_locations = face_recognition.face_locations(img_rgb)
    if not face_locations:
        return None
    # Use the first detected face
    encodings = face_recognition.face_encodings(img_rgb, face_locations)
    return encodings[0] if encodings else None


def today_str() -> str:
    return datetime.now().strftime("%Y-%m-%d")


def now_time_str() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ---------------------------------------------------------------------------
# Page routes (render HTML templates)
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Dashboard page."""
    today = today_str()
    total_students = get_student_count()
    today_count = get_today_attendance_count(today)
    recent_log = get_recent_attendance(limit=10)
    return render_template(
        "dashboard.html",
        total_students=total_students,
        today_count=today_count,
        recent_log=recent_log,
        today=today
    )


@app.route("/register")
def register_page():
    """Register Student page."""
    return render_template("register.html")


@app.route("/attendance")
def attendance_page():
    """Take Attendance page."""
    return render_template("attendance.html")


@app.route("/report")
def report_page():
    """Report page."""
    date_filter = request.args.get("date", "")
    name_filter = request.args.get("name", "")
    records = get_attendance_report(
        date_filter=date_filter or None,
        name_filter=name_filter or None
    )
    return render_template(
        "report.html",
        records=records,
        date_filter=date_filter,
        name_filter=name_filter
    )


# ---------------------------------------------------------------------------
# API routes — all return JSON  {"success": bool, "message": str, ...}
# ---------------------------------------------------------------------------

@app.route("/api/register", methods=["POST"])
def api_register():
    """
    Register a new student with their face.
    Expects JSON: { "name": str, "student_id": str, "image": base64_str }
    """
    data = request.get_json(force=True)

    name = data.get("name", "").strip()
    student_id = data.get("student_id", "").strip()
    image_b64 = data.get("image", "")

    # --- Input validation ---
    if not name:
        return jsonify({"success": False, "message": "Name is required."})
    if not student_id:
        return jsonify({"success": False, "message": "Student ID is required."})
    if not image_b64:
        return jsonify({"success": False, "message": "No image captured."})

    # --- Decode image ---
    img = decode_base64_image(image_b64)
    if img is None:
        return jsonify({"success": False, "message": "Failed to decode image."})

    # --- Extract face encoding ---
    encoding = get_face_encoding(img)
    if encoding is None:
        return jsonify({"success": False, "message": "No face detected. Please try again with better lighting."})

    # --- Save encoding to disk ---
    pkl_filename = f"{student_id}.pkl"
    pkl_path = os.path.join(ENCODINGS_DIR, pkl_filename)
    try:
        with open(pkl_path, "wb") as f:
            pickle.dump(encoding, f)
    except Exception as e:
        return jsonify({"success": False, "message": f"Could not save encoding: {e}"})

    # --- Save to database ---
    result = add_student(name, student_id, pkl_path)
    if not result["success"]:
        # Clean up the .pkl file if DB insert failed
        os.remove(pkl_path)

    return jsonify(result)


@app.route("/api/recognize", methods=["POST"])
def api_recognize():
    """
    Recognize a face and mark attendance.
    Expects JSON: { "image": base64_str }
    """
    data = request.get_json(force=True)
    image_b64 = data.get("image", "")

    if not image_b64:
        return jsonify({"success": False, "message": "No image provided."})

    # --- Decode image ---
    img = decode_base64_image(image_b64)
    if img is None:
        return jsonify({"success": False, "message": "Failed to decode image."})

    # --- Extract face encoding from captured frame ---
    encoding = get_face_encoding(img)
    if encoding is None:
        return jsonify({"success": False, "message": "No face detected in frame."})

    # --- Load all known encodings ---
    known = load_all_encodings()
    if not known:
        return jsonify({"success": False, "message": "No students registered yet."})

    known_encodings = [k["encoding"] for k in known]

    # --- Compare against all known faces ---
    distances = face_recognition.face_distance(known_encodings, encoding)
    best_idx = int(np.argmin(distances))
    best_distance = distances[best_idx]

    if best_distance > FACE_MATCH_TOLERANCE:
        return jsonify({"success": False, "message": f"Face not recognised (distance: {best_distance:.2f})."})

    # --- Match found — mark attendance ---
    matched = known[best_idx]
    result = mark_attendance(
        student_id=matched["student_id"],
        student_name=matched["name"],
        date=today_str(),
        time=now_time_str()
    )
    # Enrich the response with the student name even on duplicate
    result["student_name"] = matched["name"]
    result["distance"] = round(float(best_distance), 3)
    return jsonify(result)


@app.route("/api/report/export")
def api_export_csv():
    """
    Export the attendance report as a CSV file.
    Accepts optional query params: date, name
    """
    import csv

    date_filter = request.args.get("date") or None
    name_filter = request.args.get("name") or None
    records = get_attendance_report(date_filter=date_filter, name_filter=name_filter)

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=["id", "student_id", "student_name", "date", "time"]
    )
    writer.writeheader()
    writer.writerows(records)
    output.seek(0)

    # Return as downloadable file
    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=attendance_report.csv"}
    )


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 55)
    print("  Face Recognition Attendance App")
    print("  http://127.0.0.1:5000")
    print("=" * 55)
    init_db()
    # debug=True restarts on code changes; set False for production
    app.run(debug=True, port=5000)
