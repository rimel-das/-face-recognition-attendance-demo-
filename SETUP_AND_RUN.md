# Setup and Run - Face Recognition Attendance System

This guide will walk you through installing and running the Face Recognition Attendance System on your machine.

---

## Prerequisites

Before starting, ensure you have:

- **Python 3.9 or higher** installed
- Administrator access to install software (for some dependencies)

Check your Python version:

```powershell
python --version
```

---

## Installation

#### Step 1 — Install System Dependencies

1. **CMake**
   - Download from: https://cmake.org/download/
   - Run the installer
   - During installation, check "Add CMake to system PATH"
   - Click "Install"

2. **Visual Studio Build Tools**
   - Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   - Run the installer
   - Select "Desktop development with C++" workload
   - Complete installation

#### Step 2 — Install dlib (Open a NEW terminal after step 1)

```powershell
pip install cmake
pip install dlib
```

**Troubleshooting:** If `pip install dlib` fails, download a pre-built wheel:

- Go to: https://github.com/sachadee/Dlib
- Find the wheel matching your Python version (e.g., `dlib-19.24.1-cp311-cp311-win_amd64.whl`)
- Download it to your project folder, then:

```powershell
pip install dlib-19.24.1-cp311-cp311-win_amd64.whl
```

#### Step 3 — Install Project Dependencies

```powershell
pip install -r requirements.txt
```

---

## How to Run

### 1. Navigate to the Project Folder

```powershell
cd "c:\Users\DELL\OneDrive\Pictures\attendence system demo2"
```

### 2. Start the Application

```powershell
python app.py
```

You should see output like:

```
 * Running on http://127.0.0.1:5000
```

### 3. Open in Your Browser

Go to: **http://localhost:5000**

---

## Using the Application

Once the web interface loads, you can:

### **Dashboard**

- View total number of registered students
- See today's attendance count
- Check recent attendance logs

### **Register**

- Click the camera icon to capture a photo via webcam
- Enter student name and ID
- Save the face encoding (stored in `encodings/` folder)

### **Attendance**

- Click "Scan" to activate the webcam
- The system recognizes faces and marks attendance automatically
- Prevents duplicate attendance marks on the same day

### **Report**

- Filter attendance by date or student name
- View detailed attendance records
- Export to CSV for further analysis

---

## Project Structure

Your project folder should have this structure:

```
attendence system demo2/
├── app.py                    ← Main Flask application
├── database.py               ← Database functions
├── requirements.txt          ← Python dependencies
├── README.md                 ← Project documentation
├── SETUP_AND_RUN.md          ← This setup guide
├── attendance.db             ← Created automatically (SQLite database)
├── encodings/                ← Created automatically (face encoding files)
└── templates/                ← HTML template files
    ├── base.html             ← Base layout
    ├── dashboard.html        ← Dashboard page
    ├── register.html         ← Registration page
    ├── attendance.html       ← Attendance marking page
    └── report.html           ← Report page
```

---

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'face_recognition'"

**Solution:** Ensure all dependencies are installed:

```powershell
pip install -r requirements.txt
```

### Issue: "Could not import dlib"

**Solution:** Try the pre-built wheel method (see Installation troubleshooting above) and ensure you opened a NEW terminal after installing CMake and Visual Studio Build Tools.

### Issue: "Port 5000 already in use"

**Solution:** Stop other Flask applications or use a different port by modifying `app.py`

### Issue: Webcam not working

**Solution:**

- Ensure your browser has camera permissions
- Try a different browser
- Check if another application is using the webcam

---

## Support

For more information, check:

- Original [README.md](README.md)
- Source code in [app.py](app.py)

---

**Happy attendance tracking! 🎓**
