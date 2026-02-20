# Quick Troubleshooting Guide

Common issues and solutions for the Face Recognition Attendance System.

---

## Installation Issues

### ❌ `ModuleNotFoundError: No module named 'face_recognition'`

**Solution:**

```powershell
# Ensure pip is up to date
python -m pip install --upgrade pip

# Install all requirements
pip install -r requirements.txt

# If still failing, try installing dlib separately
pip install cmake
pip install dlib
```

### ❌ CMake not found during dlib installation

**Solution:**

1. Download CMake from https://cmake.org/download/
2. Run the installer
3. **Important:** Select "Add CMake to system PATH"
4. Close and reopen PowerShell/Terminal
5. Verify: `cmake --version`
6. Try installing again

### ❌ `error: Microsoft Visual C++ 14.0 or greater is required`

**Solution:**

1. Download Visual Studio Build Tools: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run installer, select "Desktop development with C++"
3. Complete installation
4. Open **new** PowerShell window
5. Try `pip install dlib` again

---

## Runtime Issues

### ❌ Address already in use (Port 5000)

**Solution:**

```powershell
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID {PID} /F

# Or use a different port:
# Edit app.py line: app.run(debug=True, port=8080)
```

### ❌ Webcam not working

**Solution:**

- Give browser camera permissions
  - Chrome: Settings → Privacy → Camera
  - Firefox: about:preferences → Permissions → Camera
- Try a different browser
- Restart the app
- Check if another application is using the camera

### ❌ Database file is locked

**Solution:**

```powershell
# Restart Flask app
python app.py

# Or delete the database to start fresh (lose all data):
Remove-Item attendance.db
python app.py
```

### ❌ Face not recognized even for registered students

**Solution:**

- **Lighting:** Ensure good lighting conditions
- **Distance:** Position face 30-60cm from camera
- **Angle:** Look directly at camera (not sideways)
- **Tolerance:** Increase `FACE_MATCH_TOLERANCE` in app.py:
  ```python
  FACE_MATCH_TOLERANCE = 0.6  # default is 0.5
  ```
- **Re-register:** Ask student to re-register with better photo

---

## Performance Issues

### ❌ App running slow / Face detection lagging

**Solution:**

```python
# In app.py, change face detection model from HOG to CNN:
# (CNN is more accurate but slower on CPU)

# Or reduce face detection frequency
# Implement frame skipping in JavaScript
```

### ❌ Large attendance database is slow

**Solution:**

```powershell
# Create a backup
copy attendance.db attendance.db.backup

# Or migrate to PostgreSQL for better performance
# (see DEPLOYMENT.md)
```

---

## Development Issues

### ❌ Changes not reflecting in browser

**Solution:**

```powershell
# Restart Flask app
# Hard refresh browser: Ctrl+Shift+R (Chrome/Firefox)
# Clear browser cache

# Or disable browser cache in DevTools
```

### ❌ CSS/JavaScript not loading

**Solution:**

- Check browser console for errors (F12)
- Verify static files path if you moved files
- Check CDN links are accessible:
  - Bootstrap: https://cdn.jsdelivr.net/
  - Bootstrap Icons: https://cdn.maxcdn.com/
- Try browser incognito mode

---

## Security Issues

### ❌ Should I change FACE_MATCH_TOLERANCE?

**Recommendation:**

- **0.4-0.5** = Strict (fewer false positives)
- **0.5-0.6** = Balanced (default)
- **0.6+** = Loose (more false positives)

Start with 0.5 and adjust if needed.

---

## Getting Help

1. Check this guide first
2. Review [README.md](README.md) for full documentation
3. Check app logs for error messages
4. Open an issue: https://github.com/rimel-das/-face-recognition-attendance-demo-/issues
5. Provide:
   - Error message
   - Steps to reproduce
   - Operating system & Python version
   - Screenshots if applicable

---

## Emergency Commands

```powershell
# Restart everything
Remove-Item attendance.db
python app.py

# Reset encodings
Remove-Item encodings -Recurse
python app.py

# Check Python version
python --version

# Verify key packages
pip show flask opencv-python face_recognition numpy

# Create fresh virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

---

**Last Updated:** February 2026  
**For more help:** Visit [CONTRIBUTING.md](CONTRIBUTING.md) or open an issue
