"""
Test script to check if camera and face detection are working
Run this separately: python test_camera.py
"""

import cv2
import time

print("🔍 Testing Camera and Face Detection...")

# Initialize camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ ERROR: Cannot open camera!")
    exit()

# Load face detector
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
if face_cascade.empty():
    print("❌ ERROR: Cannot load face detector!")
    exit()

print("✅ Camera opened successfully")
print("✅ Face detector loaded")
print("\n📸 Press SPACE to detect face, ESC to exit\n")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Cannot read frame")
        break
    
    # Convert to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
    
    # Draw rectangles
    for (x, y, w, h) in faces:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)
        cv2.putText(frame, f"Face Detected ({len(faces)})", (x, y-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Show info
    cv2.putText(frame, f"Faces: {len(faces)}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "Press SPACE to test, ESC to exit", (10, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    
    cv2.imshow('Face Detection Test', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC
        break
    elif key == 32:  # SPACE
        if len(faces) > 0:
            print(f"✅ Face detected! Found {len(faces)} face(s)")
        else:
            print("❌ No face detected. Try adjusting lighting or position")

cap.release()
cv2.destroyAllWindows()