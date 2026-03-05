"""
Test strict face recognition
Shows confidence values so you can tune the threshold
"""

import cv2
import sys
from pathlib import Path
sys.path.append('.')

from face_utils import FaceRecognizer

print("🔍 Testing STRICT Face Recognition...")
print("This will show confidence values for tuning\n")

# Initialize recognizer
recognizer = FaceRecognizer()

students = recognizer.get_student_list()
print(f"✅ Registered students: {students}")
print(f"🎯 Current strict threshold: 45 (lower = stricter)\n")

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

print("📸 Live recognition with confidence display...")
print("   - Green box = STRICT match (confidence < 45)")
print("   - Red box = rejected (confidence >= 45)")
print("   Press ESC to exit\n")

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
        
        if name != "Unknown":
            # STRICT match
            color = (0, 255, 0)
            # Show confidence
            cv2.putText(frame, f"{name} ({confidence:.1f}%)", (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        else:
            # Not a match
            color = (0, 0, 255)
            # Show that it was rejected
            cv2.putText(frame, "REJECTED", (x, y-30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 3)
        
        # Draw name
        cv2.putText(frame, name, (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
    
    # Show instructions
    cv2.putText(frame, "STRICT MODE - Threshold: 45", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "Green = Match | Red = Rejected", (10, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.imshow('STRICT Face Recognition Test', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()