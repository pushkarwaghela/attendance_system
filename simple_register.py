"""
Simple standalone registration test
"""

import cv2
import time
from pathlib import Path

def test_camera():
    print("📸 Testing Camera...")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Cannot open camera")
        return
    
    print("✅ Camera opened")
    print("Press SPACE to capture, ESC to exit")
    
    Path("dataset").mkdir(exist_ok=True)
    
    angles = ["FRONT", "LEFT", "RIGHT", "UP", "DOWN"]
    angle_count = 0
    
    while angle_count < 5:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Show instructions
        cv2.putText(frame, f"Angle: {angles[angle_count]}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Press SPACE to capture", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
        
        cv2.imshow('Registration Test', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == 32:  # SPACE
            # 3 second countdown
            for i in range(3, 0, -1):
                ret, frame = cap.read()
                cv2.putText(frame, f"Capturing in: {i}", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Registration Test', frame)
                cv2.waitKey(1000)
            
            # Capture
            ret, frame = cap.read()
            filename = f"dataset/test_{angles[angle_count].lower()}.jpg"
            cv2.imwrite(filename, frame)
            print(f"✅ Captured: {filename}")
            angle_count += 1
        
        elif key == 27:  # ESC
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Registration complete!")

if __name__ == "__main__":
    test_camera()