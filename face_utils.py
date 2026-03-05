"""
Face recognition utilities - ULTIMATE FIX with multiple samples
"""

import cv2
import numpy as np
import pickle
from pathlib import Path
import time
import config
import os

class FaceRecognizer:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.encodings_file = config.ENCODINGS_FILE
        self.last_recognition_time = {}
        self.cooldown = config.RECOGNITION_COOLDOWN
        
        # Load OpenCV's face detector
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        
        if self.face_cascade.empty():
            print("⚠️ Warning: Using alternative cascade path")
            # Try multiple possible paths
            possible_paths = [
                'C:/Users/USER/AppData/Local/Programs/Python/Python311/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml',
                'C:/ProgramData/Anaconda3/Lib/site-packages/cv2/data/haarcascade_frontalface_default.xml',
                cv2.data.haarcascades + 'haarcascade_frontalface_alt2.xml'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    self.face_cascade = cv2.CascadeClassifier(path)
                    if not self.face_cascade.empty():
                        print(f"✅ Loaded cascade from: {path}")
                        break
        
        # Initialize LBPH face recognizer with optimized parameters
        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=2,           # Increased radius for better feature extraction
            neighbors=8,        # Number of neighbors
            grid_x=8,           # Grid cells in X direction
            grid_y=8,           # Grid cells in Y direction
            threshold=100.0     # Default threshold
        )
        
        # Load existing encodings
        self.load_encodings()
        print(f"✅ FaceRecognizer initialized with {len(self.known_face_names)} students")
    
    def load_encodings(self):
        """Load face encodings from file"""
        if self.encodings_file.exists():
            try:
                with open(self.encodings_file, 'rb') as f:
                    data = pickle.load(f)
                    self.known_face_encodings = data['encodings']
                    self.known_face_names = data['names']
                    
                    # Train recognizer if we have data
                    if len(self.known_face_encodings) > 0:
                        # Convert to numpy arrays
                        X = np.array(self.known_face_encodings, dtype=np.uint8)
                        y = np.array(range(len(self.known_face_names)), dtype=np.int32)
                        
                        # Train the recognizer
                        self.face_recognizer.train(X, y)
                        print(f"✅ Trained recognizer with {len(X)} face samples")
                    
                print(f"✅ Loaded {len(self.known_face_names)} face encodings")
            except Exception as e:
                print(f"❌ Error loading encodings: {e}")
                self.known_face_encodings = []
                self.known_face_names = []
    
    def save_encodings(self):
        """Save face encodings to file"""
        try:
            data = {
                'encodings': self.known_face_encodings,
                'names': self.known_face_names
            }
            with open(self.encodings_file, 'wb') as f:
                pickle.dump(data, f)
            print(f"✅ Saved {len(self.known_face_names)} face encodings")
            
            # Retrain recognizer
            if len(self.known_face_encodings) > 0:
                X = np.array(self.known_face_encodings, dtype=np.uint8)
                y = np.array(range(len(self.known_face_names)), dtype=np.int32)
                self.face_recognizer.train(X, y)
                print(f"✅ Retrained recognizer with {len(X)} face samples")
                
        except Exception as e:
            print(f"❌ Error saving encodings: {e}")
    
    def preprocess_face(self, face_roi):
        """Preprocess face for better recognition"""
        # Resize to standard size
        face_roi = cv2.resize(face_roi, (200, 200))
        
        # Apply histogram equalization
        face_roi = cv2.equalizeHist(face_roi)
        
        # Apply Gaussian blur to reduce noise
        face_roi = cv2.GaussianBlur(face_roi, (3, 3), 0)
        
        # Apply adaptive thresholding for better features
        face_roi = cv2.adaptiveThreshold(face_roi, 255, 
                                         cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 11, 2)
        
        return face_roi
    
    def extract_face_features(self, image):
        """Extract face features for recognition"""
        try:
            if image is None:
                return [], []
            
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Detect faces with optimized parameters
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.05,     # Smaller scale factor for better detection
                minNeighbors=3,        # Fewer neighbors to catch more faces
                minSize=(150, 150),    # Minimum face size
                maxSize=(500, 500),    # Maximum face size
                flags=cv2.CASCADE_SCALE_IMAGE
            )
            
            face_features = []
            face_locations = []
            
            for (x, y, w, h) in faces:
                # Extract face ROI
                face_roi = gray[y:y+h, x:x+w]
                
                # Preprocess the face
                face_roi = self.preprocess_face(face_roi)
                
                face_features.append(face_roi)
                face_locations.append((x, y, w, h))
            
            return face_features, face_locations
        
        except Exception as e:
            print(f"Error in extract_face_features: {e}")
            return [], []
    
    def encode_faces_from_dataset(self):
        """Encode all faces from dataset folder"""
        dataset_path = config.DATASET_FOLDER
        
        # Get all image files
        image_files = []
        for ext in ['*.jpg', '*.jpeg', '*.png']:
            image_files.extend(dataset_path.glob(ext))
        
        if len(image_files) == 0:
            print("⚠️ No images found in dataset folder")
            return False
        
        print(f"📸 Processing {len(image_files)} images...")
        
        self.known_face_encodings = []
        self.known_face_names = []
        
        for image_path in image_files:
            try:
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"  ❌ Cannot read: {image_path.name}")
                    continue
                
                # Extract face features
                features, locations = self.extract_face_features(image)
                
                if len(features) > 0:
                    # Take the first face (should be the only one)
                    feature_vector = features[0]
                    student_name = image_path.stem
                    
                    self.known_face_encodings.append(feature_vector)
                    self.known_face_names.append(student_name)
                    print(f"  ✅ Encoded: {student_name}")
                else:
                    print(f"  ❌ No face found in: {image_path.name}")
            
            except Exception as e:
                print(f"  ❌ Error processing {image_path.name}: {e}")
        
        # Save encodings
        if len(self.known_face_encodings) > 0:
            self.save_encodings()
            print(f"✅ Successfully encoded {len(self.known_face_names)} faces")
            return True
        return False
    
    def add_new_student(self, name, image_data):
        """Add a new student to the dataset"""
        try:
            # Create dataset folder
            config.DATASET_FOLDER.mkdir(exist_ok=True)
            
            # Save image
            dest_path = config.DATASET_FOLDER / f"{name}.jpg"
            
            # Read image from upload
            if hasattr(image_data, 'getvalue'):
                file_bytes = np.asarray(bytearray(image_data.getvalue()), dtype=np.uint8)
                image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                
                if image is None:
                    return False, "❌ Invalid image file"
                
                # Save image
                cv2.imwrite(str(dest_path), image)
            else:
                return False, "❌ Invalid image data"
            
            # Extract face features
            features, locations = self.extract_face_features(image)
            
            if len(features) > 0:
                self.known_face_encodings.append(features[0])
                self.known_face_names.append(name)
                self.save_encodings()
                return True, f"✅ Student {name} added successfully!"
            else:
                # Delete image if no face found
                if dest_path.exists():
                    dest_path.unlink()
                return False, "❌ No face detected. Please upload a clear frontal face photo."
        
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def recognize_faces(self, frame):
        """Recognize faces in a frame"""
        try:
            if frame is None:
                return []
            
            # Extract face features
            features, locations = self.extract_face_features(frame)
            
            recognized_faces = []
            
            for feature, (x, y, w, h) in zip(features, locations):
                name = "Unknown"
                confidence = 0
                can_mark = False
                
                # Try to recognize
                if len(self.known_face_encodings) > 0:
                    try:
                        # Predict using LBPH
                        label, confidence_value = self.face_recognizer.predict(feature)
                        
                        # LBPH confidence: lower is better (0 = perfect match)
                        # Adjust threshold based on your results
                        if confidence_value < 90:  # Increased threshold
                            if 0 <= label < len(self.known_face_names):
                                name = self.known_face_names[label]
                                confidence = max(0, 100 - confidence_value)
                                
                                print(f"🎯 Recognized: {name} (confidence: {confidence:.1f}%, value: {confidence_value})")
                                
                                # Check cooldown
                                current_time = time.time()
                                if name in self.last_recognition_time:
                                    if current_time - self.last_recognition_time[name] > self.cooldown:
                                        can_mark = True
                                        self.last_recognition_time[name] = current_time
                                else:
                                    can_mark = True
                                    self.last_recognition_time[name] = current_time
                        else:
                            print(f"❌ Low confidence: {confidence_value}")
                    
                    except Exception as e:
                        print(f"Recognition error: {e}")
                
                recognized_faces.append({
                    'name': name,
                    'bbox': (x, y, w, h),
                    'confidence': confidence,
                    'can_mark': can_mark
                })
            
            return recognized_faces
        
        except Exception as e:
            print(f"Error in recognize_faces: {e}")
            return []
    
    def get_student_list(self):
        """Get list of registered students"""
        return self.known_face_names

# Create global instance
face_recognizer = FaceRecognizer()