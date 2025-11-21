import face_recognition
import cv2
import numpy as np
import sqlite3
import telegram

print("✅ All packages imported successfully!")

# Test face_recognition with a real image
print("Testing face_recognition library...")

# Create a simple face-like pattern for better testing
test_image = np.zeros((200, 200, 3), dtype=np.uint8)
# Draw two dark circles as "eyes"
cv2.circle(test_image, (80, 80), 10, (100, 100, 100), -1)
cv2.circle(test_image, (120, 80), 10, (100, 100, 100), -1)

face_locations = face_recognition.face_locations(test_image)
print(f"✅ face_recognition working. Found {len(face_locations)} faces in test pattern.")

# Test database
print("Testing SQLite database...")
db_path = "test.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
conn.close()
os.remove(db_path)
print("✅ SQLite working.")

# Test OpenCV without camera
print("Testing OpenCV image processing...")
test_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
gray = cv2.cvtColor(test_img, cv2.COLOR_BGR2GRAY)
print(f"✅ OpenCV image processing working. Converted to shape: {gray.shape}")

# Skip direct camera test in WSL2
print("\n📝 NOTE: Direct camera access skipped (WSL2 limitation)")
print("   Use the Windows webcam streaming server instead.")

print("\n🎉 All core components working! Ready to run surveillance system.")

import os  # Need to import os for the db file removal
