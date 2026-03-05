"""
Capture the perfect face sample for strict matching
"""

import cv2
import sys
from pathlib import Path
sys.path.append('.')

print("📸 CAPTURE PERFECT FACE SAMPLE")
print("===============================")

name = input("\nEnter your name: ").strip()

if not name:
    print("❌ Name cannot be empty")
    exit()

print(f"\n📸 Capturing perfect sample for {name}...")
print("Position your face clearly in the frame")
print("Press SPACE to capture (will take 5 photos from different angles)")
print("Press ESC to cancel\n")

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

samples_taken = 0
max_samples = 5

while samples_taken < max_samples:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Show instructions
    cv2.putText(frame, f"Sample {samples_taken + 1}/{max_samples}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Look straight at camera", (10, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    cv2.putText(frame, "Press SPACE to capture", (10, 90), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    
    cv2.imshow('Capture Perfect Sample', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 32:  # SPACE
        # Save with different angles
        angles = ["front", "slight_left", "slight_right", "up", "down"]
        angle = angles[samples_taken] if samples_taken < len(angles) else f"angle_{samples_taken}"
        
        filename = f"{name}_{angle}.jpg"
        filepath = Path("dataset") / filename
        cv2.imwrite(str(filepath), frame)
        print(f"✅ Captured: {filename}")
        samples_taken += 1
        
        # Give instructions for next shot
        if samples_taken == 1:
            print("   Next: Turn slightly left")
        elif samples_taken == 2:
            print("   Next: Turn slightly right")
        elif samples_taken == 3:
            print("   Next: Tilt head up slightly")
        elif samples_taken == 4:
            print("   Next: Tilt head down slightly")
        
    elif key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()

if samples_taken > 0:
    print(f"\n✅ Captured {samples_taken} perfect samples")
    
    # Re-encode all faces
    print("\n🔄 Re-encoding all faces...")
    from face_utils import FaceRecognizer
    recognizer = FaceRecognizer()
    
    if recognizer.encode_faces_from_dataset():
        print(f"✅ Success! Now have {len(recognizer.get_student_list())} face encodings")
        print("\n🎯 STRICT MODE ACTIVE - Will only match exact person!")
    else:
        print("❌ Failed to encode faces")
else:
    print("\n❌ No samples captured")