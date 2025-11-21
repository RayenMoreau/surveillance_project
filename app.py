from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import cv2
import os
import pickle
from database import AccessDatabase
from face_engine import FaceEngine
from camera import Camera
from telegram_bot import TelegramNotifier
from config import Config
import threading
import time
last_log_time = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY

# Initialize components
db = AccessDatabase(Config.DATABASE_PATH)
face_engine = FaceEngine()
camera = Camera()
notifier = TelegramNotifier()

# Global state
is_streaming = False
stream_lock = threading.Lock()

def generate_frames():
    """Generate video frames for web streaming"""
    frame_counter = 0  # Frame skipping counter
    
    while is_streaming:
        ret, frame = camera.read_frame()
        if not ret:
            time.sleep(0.1)
            continue
        
        frame_counter += 1
        
        # Skip frames based on config (process only every Nth frame)
        if frame_counter % Config.FRAME_SKIP != 0:
            # Still yield frame for video feed, but don't process detection
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            continue
        
        # Process frame with face recognition
        results = face_engine.recognize_face(frame)
        
        # Draw boxes on frame
        frame = face_engine.draw_face_boxes(frame, results)
        
        # Log access and send notifications (with cooldown)
       # Log access and send notifications (with cooldown)
        current_time = time.time()
        for result in results:
            cooldown_key = f"{result['name']}_{result['location']}"  # Unique per face position
    
            if current_time - last_log_time.get(cooldown_key, 0) < Config.LOG_COOLDOWN:
                continue  # Skip if logged recently
    
        last_log_time[cooldown_key] = current_time
    
        if result['name'] != "Unknown":
            person_id = db.register_person(result['name'])
            db.log_access(person_id, True)
            notifier.send_access_granted(result['name'])
        else:
            db.log_access(None, False)
            notifier.send_unknown_person()
        
        # Encode frame for web streaming
        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()
        
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        time.sleep(0.033)  # ~30 FPS max

@app.route('/')
def dashboard():
    """Main dashboard"""
    logs = db.get_all_logs()
    people = db.get_registered_people()
    return render_template('dashboard.html', logs=logs, people=people, 
                         streaming=is_streaming)

@app.route('/video_feed')
def video_feed():
    """Video streaming route"""
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/start_stream')
def start_stream():
    """Start video streaming"""
    global is_streaming
    with stream_lock:
        if not is_streaming:
            camera.start()
            is_streaming = True
    return redirect(url_for('dashboard'))

@app.route('/stop_stream')
def stop_stream():
    """Stop video streaming"""
    global is_streaming
    with stream_lock:
        is_streaming = False
        camera.release()
    return redirect(url_for('dashboard'))

@app.route('/register', methods=['POST'])
def register_face():
    """Register new face"""
    name = request.form.get('name')
    if not name:
        return jsonify({'error': 'Name is required'}), 400
    
    # Save uploaded image
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    # Save temp file
    temp_path = os.path.join('uploads', f"{name}.jpg")
    os.makedirs('uploads', exist_ok=True)
    file.save(temp_path)
    
    try:
        face_engine.register_face(temp_path, name)
        db.register_person(name)
        return jsonify({'success': True, 'message': f'Face registered for {name}'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.route('/get_logs')
def get_logs():
    """Get access logs as JSON"""
    logs = db.get_all_logs()
    return jsonify([{
        'name': log[0] or 'Unknown',
        'timestamp': log[1],
        'access_granted': bool(log[2])
    } for log in logs])

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('faces', exist_ok=True)
    os.makedirs('database', exist_ok=True)
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static/css', exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
