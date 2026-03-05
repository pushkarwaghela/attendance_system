"""
Test face recognition quality
"""

import cv2
from face_utils import face_recognizer

print("🔍 Testing Face Recognition Quality")
print("=" * 50)

# Load students
students = face_recognizer.get_students()
print(f"📚 Registered students: {students}")

# Open camera
cap = cv2.VideoCapture(0)
print("\n📸 Live recognition - Press ESC to exit")
print("   Green box = recognized, Red box = unknown")
print("   Confidence shown on screen\n")

while True:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Recognize faces
    faces = face_recognizer.recognize_faces(frame)
    
    for face in faces:
        x, y, w, h = face['bbox']
        name = face['name']
        conf = face['confidence']
        
        if name != "Unknown":
            color = (0, 255, 0)
            label = f"{name} ({conf:.1f}%)"
        else:
            color = (0, 0, 255)
            label = "Unknown"
        
        # Draw rectangle
        cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
        
        # Draw label with background
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (x, y-th-10), (x+tw, y), color, -1)
        cv2.putText(frame, label, (x, y-5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    # Show info
    cv2.putText(frame, f"Faces: {len(faces)}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow('Recognition Test', frame)
    
    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()