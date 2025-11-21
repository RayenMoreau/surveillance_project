# Configuration settings
import os

class Config:
    # Database
    DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database/access_logs.db')
    
    # Telegram Bot (Get from BotFather)
    TELEGRAM_BOT_TOKEN = '8045911193:AAFXu-G5TxWefOnG8uoBI3j8p376iYIc9-Y'
    TELEGRAM_CHAT_ID = '8402390960'  # Use get_chat_id.py to find this
    
    # Camera settings
    USE_WEBCAM = True  # Set True for WSL2 streaming, False for video file
    WEBCAM_URL = 'http://172.27.240.1:8080/video'  # Your Windows IP from above
    VIDEO_PATH = 'test_video.mp4'  # Fallback video for testing
    
    # Face recognition
    FACE_TOLERANCE = 0.6
    FACE_ENCODING_PATH = 'faces/encodings.pkl'
    
    # Flask
    SECRET_KEY = 'your-secret-key-here'

    # Frame
    FRAME_SKIP = 10
    NOTIFICATION_COOLDOWN = 30

    # LOGS
    LOG_COOLDOWN = 30 
