"""
Add multiple samples of the same person for better recognition
"""

import cv2
import sys
from pathlib import Path
sys.path.append('.')

from face_utils import FaceRecognizer

print("📸 ADD MULTIPLE FACE SAMPLES")
print("=============================")

# Initialize recognizer
recognizer = FaceRecognizer()

name = input("\nEnter your name (e.g., Pushkar): ").strip()

if not name:
    print("❌ Name cannot be empty")
    exit()

print(f"\n📸 Taking 10 photos of {name}...")
print("Look at the camera and press SPACE to capture")
print("Press ESC when done\n")

# Open camera
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Cannot open camera")
    exit()

sample_count = 0
max_samples = 10

while sample_count < max_samples:
    ret, frame = cap.read()
    if not ret:
        break
    
    # Show frame with instructions
    cv2.putText(frame, f"Sample {sample_count + 1}/{max_samples}", (10, 30), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.putText(frame, "Press SPACE to capture", (10, 60), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    cv2.imshow('Capture Face Samples', frame)
    
    key = cv2.waitKey(1) & 0xFF
    if key == 32:  # SPACE
        # Save the image
        sample_path = Path(f"dataset/{name}_{sample_count + 1}.jpg")
        cv2.imwrite(str(sample_path), frame)
        print(f"✅ Captured sample {sample_count + 1}")
        sample_count += 1
    elif key == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()

print(f"\n✅ Captured {sample_count} samples")

# Re-encode all faces
print("\n🔄 Re-encoding all faces...")
if recognizer.encode_faces_from_dataset():
    print(f"✅ Success! Now have {len(recognizer.get_student_list())} face encodings")
else:
    print("❌ Failed to encode faces")

print("\n🎯 Now run the main app and try recognition again!")