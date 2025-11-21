import cv2
import time
from database import AccessDatabase
from face_engine import FaceEngine
from camera import Camera
from telegram_bot import TelegramNotifier
from config import Config

def main():
    print("Starting IoT Surveillance System")
    print("Press 'q' to quit, 'r' to register from current frame")
    
    # Initialize components
    db = AccessDatabase(Config.DATABASE_PATH)
    face_engine = FaceEngine()
    camera = Camera()
    notifier = TelegramNotifier()
    
    # Start camera
    camera.start()
    
    # Main loop
    try:
        while True:
            ret, frame = camera.read_frame()
            if not ret:
                print("Failed to read frame")
                break
            
            # Recognize faces
            results = face_engine.recognize_face(frame)
            
            # Draw boxes
            frame = face_engine.draw_face_boxes(frame, results)
            
            # Log and notify
            for result in results:
                if result['name'] != "Unknown":
                    person_id = db.register_person(result['name'])
                    db.log_access(person_id, True)
                    notifier.send_access_granted(result['name'])
                else:
                    db.log_access(None, False)
                    notifier.send_unknown_person()
            
            # Display
            cv2.imshow('IoT Surveillance', frame)
            
            # Controls
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                # Save current frame for registration
                cv2.imwrite('temp_registration.jpg', frame)
                name = input("Enter name for this person: ")
                try:
                    face_engine.register_face('temp_registration.jpg', name)
                    db.register_person(name)
                    print(f"Registered {name}")
                except Exception as e:
                    print(f"Registration failed: {e}")
                finally:
                    if os.path.exists('temp_registration.jpg'):
                        os.remove('temp_registration.jpg')
            
            time.sleep(0.033)  # ~30 FPS
    
    except KeyboardInterrupt:
        print("Shutting down...")
    
    finally:
        camera.release()
        cv2.destroyAllWindows()
        print("System stopped")

if __name__ == '__main__':
    main()
