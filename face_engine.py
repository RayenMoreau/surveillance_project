import face_recognition
import pickle
import os
import cv2
import numpy as np
from config import Config

class FaceEngine:
    def __init__(self):
        self.encodings_path = Config.FACE_ENCODING_PATH
        self.known_encodings = []
        self.known_names = []
        self.load_encodings()
    
    def load_encodings(self):
        """Load saved face encodings"""
        if os.path.exists(self.encodings_path):
            with open(self.encodings_path, 'rb') as f:
                data = pickle.load(f)
                self.known_encodings = data['encodings']
                self.known_names = data['names']
            print(f"Loaded {len(self.known_names)} known faces")
        else:
            print("No existing face encodings found")
    
    def save_encodings(self):
        """Save face encodings to disk"""
        os.makedirs(os.path.dirname(self.encodings_path), exist_ok=True)
        data = {'encodings': self.known_encodings, 'names': self.known_names}
        with open(self.encodings_path, 'wb') as f:
            pickle.dump(data, f)
        print(f"Saved {len(self.known_names)} face encodings")
    
    def register_face(self, image_path, name):
        """Register a new face from image"""
        image = face_recognition.load_image_file(image_path)
        encodings = face_recognition.face_encodings(image)
        
        if len(encodings) == 0:
            raise ValueError("No face found in image")
        
        # Use the first face found
        encoding = encodings[0]
        
        # Check if person already exists
        if name in self.known_names:
            idx = self.known_names.index(name)
            self.known_encodings[idx] = encoding
            print(f"Updated face encoding for {name}")
        else:
            self.known_names.append(name)
            self.known_encodings.append(encoding)
            print(f"Added new face encoding for {name}")
        
        self.save_encodings()
        return True
    
    def recognize_face(self, frame):
        """Recognize faces in a frame"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)
        
        results = []
        for i, face_encoding in enumerate(face_encodings):
            # Compare with known faces
            matches = face_recognition.compare_faces(
                self.known_encodings, 
                face_encoding, 
                tolerance=Config.FACE_TOLERANCE
            )
            
            name = "Unknown"
            confidence = 0.0
            
            if True in matches:
                matched_idx = matches.index(True)
                name = self.known_names[matched_idx]
                
                # Calculate face distance for confidence
                face_distances = face_recognition.face_distance(
                    self.known_encodings, 
                    face_encoding
                )
                confidence = 1 - face_distances[matched_idx]
            
            results.append({
                'location': face_locations[i],
                'name': name,
                'confidence': confidence
            })
        
        return results
    
    def draw_face_boxes(self, frame, results):
        """Draw boxes and labels on frame"""
        for result in results:
            top, right, bottom, left = result['location']
            name = result['name']
            confidence = result['confidence']
            
            # Color: green for known, red for unknown
            color = (0, 255, 0) if name != "Unknown" else (0, 0, 255)
            
            # Draw box
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            
            # Draw label
            label = f"{name} ({confidence:.2%})"
            cv2.putText(frame, label, (left, top - 10), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return frame
