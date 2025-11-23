# IoT Surveillance & Access Control System

Real-time facial recognition system for Raspberry Pi with web dashboard, SQLite logging, and Telegram notifications.

![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)
![OpenCV](https://img.shields.io/badge/opencv-4.8+-green.svg)
![Flask](https://img.shields.io/badge/flask-2.0+-orange.svg)
![Raspberry Pi](https://img.shields.io/badge/platform-Raspberry%20Pi%20OS-red.svg)

## 🎯 Features

- **Live Video Streaming**: MJPEG feed with face bounding boxes and confidence scores
- **Real-Time Face Recognition**: One-shot learning with 128-dim embeddings using dlib
- **SQLite Database**: Persistent storage for access logs and registered faces
- **Telegram Notifications**: Instant alerts for unknown persons and access grants
- **Web Interface**: Responsive dashboard for stream viewing and face registration
- **Cross-Platform**: Runs on WSL2 (development) and Raspberry Pi OS (deployment)
- **Frame Rate Control**: Configurable processing throttling to reduce CPU usage
- **Notification Cooldown**: Prevents spam with intelligent duplicate detection

## 🏗️ Architecture
┌─────────────────────────────────────────────────────────────┐
│                    Video Input (CSI/USB)                    │
└──────────────────────┬──────────────────────────────────────┘
↓
┌─────────────────────────────────────────────────────────────┐
│  Face Engine (face_recognition + dlib CNN)                  │
│  - Detect faces via HOG/SSD                                 │
│  - Generate 128-dim embeddings                              │
│  - Compare with known encodings (Euclidean distance)        │
└──────────────┬────────────────────────┬─────────────────────┘
↓                        ↓
┌──────────────────────┐    ┌────────────────────────────┐
│  SQLite Database     │    │   Telegram Bot (async)     │
│  - people table      │    │   - Send alerts            │
│  - access_logs table │    │   - 30s cooldown           │
└───────┬──────────────┘    └────────────┬───────────────┘
↓                                  ↓
┌──────────────┐                ┌────────────────┐
│  Flask Web   │                │  Mobile Device │
│  Dashboard   │                │  (Your Phone)  │
└──────────────┘                └────────────────┘

## 📂 Project Structure
surveillance_project/
├── app.py                    # Flask web server
├── camera.py                 # Camera abstraction (PiCamera2/OpenCV)
├── config.py                 # Configuration constants
├── database.py               # SQLite CRUD operations
├── face_engine.py            # Face encoding & recognition
├── telegram_bot.py           # Telegram notification handler
├── main.py                   # Standalone CLI mode
├── get_chat_id.py            # Telegram setup utility
├── test_video.mp4            # Fallback video file
├── faces/                    # Face images (temporary)
├── database/                 # SQLite database file
├── templates/
│   └── dashboard.html        # Web UI template
├── uploads/                  # Temporary uploads
└── venv/                     # Python virtual environment

## ⚙️ Configuration

Edit `config.py` before running:

USE_WEBCAM = True          # True for Pi camera, False for video file
WEBCAM_URL = 0             # Camera index (0 for Pi CSI)
VIDEO_PATH = 'test_video.mp4'
TELEGRAM_BOT_TOKEN = 'YOUR_BOT_TOKEN'
TELEGRAM_CHAT_ID = 'YOUR_CHAT_ID'
FRAME_SKIP = 15            # Process every Nth frame (reduce CPU)
NOTIFICATION_COOLDOWN = 30 # Seconds between duplicate alerts
FACE_TOLERANCE = 0.55      # Lower = stricter recognition

🚀 Setup Instructions
Option A: Development on WSL2/PC
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/surveillance-project.git
cd surveillance-project

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install numpy
pip install face_recognition flask python-telegram-bot opencv-python

# 4. Configure Telegram
# - Get token from @BotFather
# - Run: python get_chat_id.py
# - Update config.py

# 5. Run development server
python app.py
# Access: http://localhost:5000

Option B: Deployment on Raspberry Pi
# 1. Enable camera
sudo raspi-config → Interface Options → Camera → Enable

# 2. Install system packages
sudo apt update
sudo apt install -y python3-pip libatlas-base-dev cmake python3-dev

# 3. Clone & setup
git clone https://github.com/YOUR_USERNAME/surveillance-project.git
cd surveillance-project
python3 -m venv venv
source venv/bin/activate

# 4. Install packages (dlib will compile ~20-40 min)
pip install numpy
pip install dlib face_recognition --no-cache-dir
pip install flask python-telegram-bot opencv-python

# 5. Configure & run
nano config.py  # Update WEBCAM_URL=0, TELEGRAM tokens
python app.py &

🔧 Troubleshooting
| Issue                     | Solution                                                               |
| ------------------------- | ---------------------------------------------------------------------- |
| `camera failed`           | Increase GPU memory to 128MB in `/boot/firmware/config.txt`            |
| `supported=0 detected=0`  | Check cable orientation, run `sudo raspi-config`, enable camera        |
| `dlib compilation error`  | Install `libatlas-base-dev`, `cmake`, `python3-dev` before pip install |
| No Telegram notifications | Run `python get_chat_id.py` after messaging the bot                    |
| Black stream in VNC       | Use SSH tunnel: `ssh -L 5000:localhost:5000 pi@<ip>`                   |
| High CPU usage            | Increase `FRAME_SKIP` to 20-30 in `config.py`                          |

📊 Performance Metrics

Raspberry Pi 4: 2-3 FPS processing, 15% CPU usage
Detection Latency: <500ms from capture to notification
Database: 10,000+ logs with sub-second query times
Memory: ~300MB RAM usage on Pi 4

🔄 Future Enhancements

[ ] Multi-camera support: Track across zones
[ ] Face liveness detection: Prevent photo spoofing with eye-blink analysis
[ ] Time-based access: Restrict entry by schedule
[ ] MQTT integration: Connect to Home Assistant
[ ] Cloud backup: Sync logs to AWS S3/Google Drive
[ ] Mobile app: React Native dashboard
[ ] Model fine-tuning: Retrain on custom faces for better accuracy

📄 License

MIT License - Free for personal and academic use.

🤝 Contributing

Pull requests welcome for optimizations and new features!

