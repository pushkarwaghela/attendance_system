"""
Test face recognition with a single image
"""

import cv2
import sys
from pathlib import Path
sys.path.append('.')

from face_utils import FaceRecognizer

print("🔍 Testing Face Recognition...")

# Initialize recognizer
recognizer = FaceRecognizer()

if len(recognizer.get_student_list()) == 0:
    print("❌ No students registered. Please add students first.")
    exit()

print(f"✅ Found {len(recognizer.get_student_list())} students: {recognizer.get_student_list()}")

# Try to open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

print("\n📸 Press SPACE to capture and recognize, ESC to exit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Show frame
    cv2.imshow('Test Recognition - Press SPACE', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == 32:  # SPACE
        print("\n🔄 Analyzing frame...")
        
        # Recognize
        faces = recognizer.recognize_faces(frame)
        
        if faces:
            for face in faces:
                print(f"  → Name: {face['name']}")
                print(f"    Confidence: {face['confidence']:.1f}%")
                print(f"    Can mark: {face['can_mark']}")
        else:
            print("❌ No faces detected or recognized")

cap.release()
cv2.destroyAllWindows()