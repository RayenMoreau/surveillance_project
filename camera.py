import cv2
import os
import numpy as np
import time
from config import Config

class Camera:
    def __init__(self):
        self.use_webcam = Config.USE_WEBCAM
        self.video_path = Config.VIDEO_PATH
        self.webcam_url = Config.WEBCAM_URL
        self.cap = None
        self.frame_count = 0
        
    def start(self):
        """Initialize camera or video file"""
        if self.use_webcam:
            # For HTTP stream from Windows
            print(f"Connecting to webcam stream at {self.webcam_url}")
            
            # Try different backends
            self.cap = cv2.VideoCapture(self.webcam_url, cv2.CAP_FFMPEG)
            
            if not self.cap.isOpened():
                print("FFMPEG backend failed, trying default...")
                self.cap = cv2.VideoCapture(self.webcam_url)
            
            if not self.cap.isOpened():
                # Try with timeout parameters
                print("Opening with HTTP timeout parameters...")
                os.environ['OPENCV_FFMPEG_CAPTURE_OPTIONS'] = 'timeout;5000'
                self.cap = cv2.VideoCapture(self.webcam_url, cv2.CAP_FFMPEG)
            
            if not self.cap.isOpened():
                raise RuntimeError(f"Failed to open video source: {self.webcam_url}")
            
            # Set buffer size to reduce latency
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
        else:
            # Use video file fallback
            self.cap = cv2.VideoCapture(self.video_path)
            print(f"Using video file: {self.video_path}")
        
        if not self.cap.isOpened():
            raise RuntimeError("Failed to open video source")
        
        return True    
    def read_frame(self):
        """Read a frame from video source"""
        ret, frame = self.cap.read()
        self.frame_count += 1
        if not ret:
            if not self.use_webcam:
                # Loop video file
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                ret, frame = self.cap.read()
        return ret, frame
    
    def release(self):
        """Release camera"""
        if self.cap:
            self.cap.release()
    
    def create_test_video(self):
        """Create a simple test video file"""
        print(f"Creating test video at {self.video_path}...")
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(self.video_path, fourcc, 10.0, (640, 480))
        
        # Write 100 frames
        for i in range(100):
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            cv2.putText(frame, f"Test Frame {i}", (50, 50), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            out.write(frame)
        
        out.release()
        print(f"Test video created: {self.video_path}") 

    def get_fps(self):
        """Get frames per second"""
        return int(self.cap.get(cv2.CAP_PROP_FPS)) if self.cap else 30
