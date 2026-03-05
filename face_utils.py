"""
Face recognition utilities - PROFESSIONAL VERSION
"""

import cv2
import numpy as np
import pickle
from pathlib import Path
import time
import os

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.encodings_file = Path("models/face_encodings.pkl")
        self.last_recognition_time = {}
        self.cooldown = 3  # Seconds between recognitions
        self.frame_count = 0
        self.skip_frames = 2  # Process every 2nd frame for speed
        
        # Create models folder
        Path("models").mkdir(exist_ok=True)
        
        # Load face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        # Initialize face recognizer
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        
        # Load existing encodings
        self.load_encodings()
        
        # If no encodings, load from dataset
        if len(self.known_face_encodings) == 0:
            print("📸 Loading from dataset...")
            self.encode_faces()
    
    def load_encodings(self):
        """Load face encodings from file"""
        if self.encodings_file.exists():
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                    
                    if self.known_face_encodings:
                        self.train_recognizer()
                        print(f"✅ Loaded {len(self.known_face_names)} samples for {len(self.get_students())} students")
            except Exception as e:
                print(f"⚠️ Error loading: {e}")
    
    def train_recognizer(self):
        """Train the recognizer"""
        if self.known_face_encodings:
            X = np.array(self.known_face_encodings, dtype=np.uint8)
            unique_names = self.get_students()
            label_map = {name: i for i, name in enumerate(unique_names)}
            y = np.array([label_map[name] for name in self.known_face_names], dtype=np.int32)
            self.face_recognizer.train(X, y)
            print(f"✅ Trained on {len(X)} samples for {len(unique_names)} students")
    
    def save_encodings(self):
        """Save encodings to file"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
            print(f"✅ Saved {len(self.known_face_names)} encodings")
            
            if self.known_face_encodings:
                self.train_recognizer()
        except Exception as e:
            print(f"⚠️ Error saving: {e}")
    
    def detect_faces(self, gray):
        """Detect faces in grayscale image"""
        return self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
    
    def extract_face(self, gray, face):
        """Extract and normalize face"""
        x, y, w, h = face
        face_roi = gray[y:y+h, x:x+w]
        face_roi = cv2.resize(face_roi, (200, 200))
        face_roi = cv2.equalizeHist(face_roi)
        return face_roi
    
    def encode_faces(self):
        """Encode all faces from dataset"""
        dataset_path = Path("dataset")
        if not dataset_path.exists():
            return False
        
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(dataset_path.glob(ext))
        
        if not image_files:
            return False
        
        print(f"📸 Processing {len(image_files)} images...")
        
        self.known_face_encodings = []
        self.known_face_names = []
        
        for img_path in image_files:
            try:
                # Read image
                img = cv2.imread(str(img_path))
                if img is None:
                    continue
                
                # Convert to grayscale
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                
                # Detect faces
                faces = self.detect_faces(gray)
                
                if len(faces) > 0:
                    # Extract face
                    face_roi = self.extract_face(gray, faces[0])
                    
                    # Get student name (remove angle suffix)
                    name = img_path.stem.split('_')[0]
                    
                    self.known_face_encodings.append(face_roi)
                    self.known_face_names.append(name)
                    print(f"  ✅ Encoded: {name}")
                else:
                    print(f"  ❌ No face in: {img_path.name}")
                    
            except Exception as e:
                print(f"  ❌ Error: {img_path.name}")
        
        # Save encodings
        if self.known_face_encodings:
            self.save_encodings()
            print(f"✅ Success! Encoded {len(self.known_face_names)} samples for {len(self.get_students())} students")
            return True
        
        return False
    
    def add_student_angle(self, name, image, angle):
        """Add a new angle for a student"""
        try:
            Path("dataset").mkdir(exist_ok=True)
            
            # Create filename
            filename = f"dataset/{name}_{angle}.jpg"
            
            # Handle different input types
            if hasattr(image, 'getvalue'):
                file_bytes = np.asarray(bytearray(image.getvalue()), dtype=np.uint8)
                img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
            else:
                img = image
            
            # Save image
            cv2.imwrite(filename, img)
            
            # Verify face
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = self.detect_faces(gray)
            
            if len(faces) > 0:
                # Extract and add to encodings
                face_roi = self.extract_face(gray, faces[0])
                self.known_face_encodings.append(face_roi)
                self.known_face_names.append(name)
                self.save_encodings()
                return True, f"✅ {angle} angle captured for {name}!"
            else:
                if Path(filename).exists():
                    Path(filename).unlink()
                return False, "❌ No face detected. Please try again."
        
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def recognize_faces(self, frame):
        """Recognize faces in frame with confidence"""
        self.frame_count += 1
        if self.frame_count % self.skip_frames != 0:
            return []
        
        if frame is None:
            return []
        
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.detect_faces(gray)
            
            results = []
            for face in faces:
                x, y, w, h = face
                face_roi = self.extract_face(gray, face)
                
                name = "Unknown"
                confidence = 0
                can_mark = False
                
                if self.known_face_encodings:
                    try:
                        label, conf = self.face_recognizer.predict(face_roi)
                        
                        # LBPH confidence: lower is better (0 = perfect match)
                        if conf < 60:  # Good match threshold
                            students = self.get_students()
                            if 0 <= label < len(students):
                                name = students[label]
                                confidence = max(0, 100 - conf)
                                
                                # Cooldown check
                                current = time.time()
                                if name in self.last_recognition_time:
                                    if current - self.last_recognition_time[name] > self.cooldown:
                                        can_mark = True
                                        self.last_recognition_time[name] = current
                                else:
                                    can_mark = True
                                    self.last_recognition_time[name] = current
                                
                                print(f"🎯 Recognized: {name} ({confidence:.1f}%)")
                    except:
                        pass
                
                results.append({
                    'name': name,
                    'bbox': (x, y, w, h),
                    'confidence': confidence,
                    'can_mark': can_mark
                })
            
            return results
        
        except Exception as e:
            return []
    
    def get_students(self):
        """Get unique students"""
        return list(set(self.known_face_names))

# Global instance
face_recognizer = FaceRecognizer()