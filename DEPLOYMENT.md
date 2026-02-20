# Deployment Guide

This guide covers deploying the Face Recognition Attendance System to production.

---

## Production Setup

### 1. Environment Configuration

```powershell
# Copy the example environment file
copy .env.example .env

# Edit .env with production values
# IMPORTANT: Change SECRET_KEY to a random string
# Set FLASK_DEBUG=False
# Update CORS_ORIGINS if needed
```

### 2. Install Production Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Run with Gunicorn (Production Server)

```powershell
# Install gunicorn (already in requirements.txt)
# Run with multiple worker processes
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Windows PowerShell alternative:**

```powershell
python -m gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

---

## Deployment Platforms

### Option 1: Windows Server / IIS

1. Install Python on server
2. Install dependencies: `pip install -r requirements.txt`
3. Use IIS URL Rewrite to forward to Gunicorn
4. Run Gunicorn as a Windows Service (using NSSM or similar)

### Option 2: Linux / Ubuntu (VPS/Cloud)

```bash
# Install Python and dependencies
sudo apt install python3.9 python3-pip
pip install -r requirements.txt

# Create systemd service
sudo nano /etc/systemd/system/face-attendance.service
```

**Service file example:**

```ini
[Unit]
Description=Face Recognition Attendance App
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/home/user/face-recognition-attendance
ExecStart=/usr/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl start face-attendance
sudo systemctl enable face-attendance
```

### Option 3: Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
docker build -t face-attendance .
docker run -p 5000:5000 face-attendance
```

### Option 4: Heroku

1. Create `Procfile`:

```
web: gunicorn app:app
```

2. Deploy:

```bash
heroku login
heroku create your-app-name
git push heroku main
```

---

## Security Best Practices

✓ Always set `FLASK_DEBUG=False` in production  
✓ Use strong `SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)  
✓ Enable HTTPS/SSL (use reverse proxy like Nginx)  
✓ Restrict CORS origins to your domain only  
✓ Use environment variables for sensitive config  
✓ Regularly backup `attendance.db` file  
✓ Keep dependencies updated with `pip install --upgrade`

---

## Performance Tuning

**For high concurrency:**

```powershell
# Use more Gunicorn workers (2-4x CPU cores)
gunicorn -w 8 -b 0.0.0.0:5000 --threads 4 app:app

# Or use eventlet for better concurrency
pip install eventlet
gunicorn -w 1 -k eventlet -b 0.0.0.0:5000 app:app
```

**Database optimization:**

- Regular backup of `attendance.db`
- Consider migration to PostgreSQL for large scale
- Enable WAL (Write-Ahead Logging) in SQLite for concurrent access

---

## Monitoring & Logging

Add logging to production:

```python
import logging
logging.basicConfig(level=logging.INFO, filename='app.log')
```

Monitor with:

- systemd journal: `journalctl -u face-attendance -f`
- Docker logs: `docker logs -f container_name`
- Application logs: Check `app.log` file

---

## Support

For issues, open a GitHub issue or check [documentation](README.md).
