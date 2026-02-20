# FaceAttend — Face Recognition Attendance System

A lightweight, locally-running web app that uses facial recognition to automatically mark student attendance. Built with Python, Flask, OpenCV, and `face_recognition`.

---

## Features

- **Register Students** — Capture a face photo via webcam, assign a name and ID, and save the face encoding.
- **Take Attendance** — Press Scan; the system recognises the face and marks attendance (duplicate prevention built in).
- **Dashboard** — Live stats: total students, today's count, recent log.
- **Report** — Filter by date or name, export to CSV.
- **Dark modern UI** — Bootstrap 5, fully responsive, persistent sidebar.

---

## Project Structure

```
face_attendance_app/
├── app.py              ← Flask routes and recognition logic
├── database.py         ← SQLite helpers (students + attendance tables)
├── requirements.txt
├── README.md
├── attendance.db       ← Created automatically on first run
├── encodings/          ← .pkl face encoding files (auto-created)
└── templates/
    ├── base.html       ← Shared dark layout + sidebar
    ├── dashboard.html
    ├── register.html
    ├── attendance.html
    └── report.html
```

---

## Installation

### 1 — Prerequisites

| Tool | Purpose |
|------|---------|
| Python 3.9+ | Runtime |
| CMake | Required to compile dlib |
| C++ compiler | Required to compile dlib |

---

### Windows Installation

```powershell
# Step 1 — Install CMake
# Download installer from https://cmake.org/download/
# During install, choose "Add CMake to system PATH"

# Step 2 — Install Visual Studio Build Tools
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
# Select "Desktop development with C++" workload

# Step 3 — Install Python packages
# Open a NEW terminal after the above installs
pip install cmake
pip install dlib
pip install -r requirements.txt
```

**Tip for Windows:** If `pip install dlib` fails, use a pre-built wheel:
```powershell
# Find your Python version and download the matching .whl from:
# https://github.com/sachadee/Dlib
# Then install it:
pip install dlib-<version>-cpXX-cpXX-win_amd64.whl
pip install -r requirements.txt
```

---

### Ubuntu / Debian Installation

```bash
# Step 1 — System dependencies
sudo apt update
sudo apt install -y cmake build-essential libboost-all-dev

# Step 2 — (Optional) create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Step 3 — Install Python packages
pip install cmake
pip install dlib
pip install -r requirements.txt
```

---

### macOS Installation

```bash
# Step 1 — Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Step 2 — Install cmake and boost
brew install cmake boost

# Step 3 — Install Python packages
pip install dlib
pip install -r requirements.txt
```

---

## Running the App

```bash
python app.py
```

Then open your browser at: **http://127.0.0.1:5000**

That's it — no build step, no separate server, no deployment setup.

---

## Usage Guide

### Register a Student
1. Go to **Register Student** in the sidebar.
2. Enter the student's **Full Name** and a unique **Student ID** (e.g. `STU001`).
3. Look at the camera and click **Capture Photo**.
4. Click **Register Student**.
5. The face encoding is saved as a `.pkl` file and the student is stored in the database.

### Take Attendance
1. Go to **Take Attendance**.
2. The student faces the camera.
3. Click **Scan Face**.
4. If recognised, attendance is marked and the name is displayed.
5. If already marked today, a friendly duplicate message appears (no double-counting).

### View Reports
1. Go to **Report**.
2. Filter by **date** and/or **name** (optional).
3. Click **Export CSV** to download the filtered records.

---

## Database Schema

```sql
-- Students table
CREATE TABLE students (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT    NOT NULL,
    student_id    TEXT    NOT NULL UNIQUE,
    encoding_path TEXT    NOT NULL,       -- path to .pkl file
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attendance table (one record per student per day)
CREATE TABLE attendance (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   TEXT NOT NULL,
    student_name TEXT NOT NULL,
    date         TEXT NOT NULL,           -- "YYYY-MM-DD"
    time         TEXT NOT NULL,           -- "HH:MM:SS"
    UNIQUE(student_id, date)              -- prevents duplicates
);
```

---

## Configuration

You can tune these settings in `app.py`:

| Variable | Default | Description |
|----------|---------|-------------|
| `FACE_MATCH_TOLERANCE` | `0.5` | Lower = stricter matching. Range: 0.4–0.6 |
| `ENCODINGS_DIR` | `encodings/` | Where `.pkl` files are saved |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `dlib` fails to install | Install CMake + C++ build tools first (see above) |
| "No face detected" during registration | Improve lighting, face the camera directly |
| "Face not recognised" during attendance | Re-register the student in better lighting |
| Camera not starting in browser | Allow camera permissions when the browser prompts |
| Port 5000 already in use | Change `port=5000` in `app.py` to e.g. `5001` |
| `ModuleNotFoundError: face_recognition` | Run `pip install face_recognition` |

---

## System Requirements

- Python 3.9 or later
- 4 GB RAM minimum (8 GB recommended)
- Webcam (built-in or USB)
- Modern browser (Chrome, Firefox, Edge, Safari)

---

## How It Works

1. **Registration**: A JPEG frame is captured from the browser's `getUserMedia` stream, base64-encoded, and POSTed to `/api/register`. The backend decodes the image, runs `face_recognition.face_encodings()` to extract a 128-dimensional face embedding, pickles it to disk, and saves the path in SQLite.

2. **Recognition**: On scan, the same process captures a frame. The backend compares the captured encoding against all stored encodings using Euclidean distance via `face_recognition.face_distance()`. If the best match is within `FACE_MATCH_TOLERANCE`, the student is identified and attendance is inserted (the `UNIQUE` constraint silently rejects duplicates).

---

## License

MIT — free to use, modify, and distribute.
