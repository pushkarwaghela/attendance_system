"""
Test recognition with multiple samples
"""

import cv2
import sys
from pathlib import Path
sys.path.append('.')

from face_utils import FaceRecognizer

print("🔍 Testing Face Recognition with Multiple Samples...")

# Initialize recognizer
recognizer = FaceRecognizer()

students = recognizer.get_student_list()
print(f"✅ Found {len(students)} face encodings for: {students}")

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

print("\n📸 Live recognition... Press ESC to exit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Recognize faces
    faces = recognizer.recognize_faces(frame)
    
    # Draw results
    for face in faces:
        x, y, w, h = face['bbox']
        name = face['name']
        confidence = face['confidence']
        
        # Choose color
        if name != "Unknown":
            color = (0, 255, 0)
            # Draw confidence
            cv2.putText(frame, f"{confidence:.1f}%", (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        else:
            color = (0, 0, 255)
        
        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
        
        # Draw name
        cv2.putText(frame, name, (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Show info
    cv2.putText(frame, f"Faces: {len(faces)}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow('Recognition Test', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()