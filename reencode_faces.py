"""
Force re-encode all faces with proper training
"""

import sys
from pathlib import Path
sys.path.append('.')

from face_utils import FaceRecognizer

print("🔄 Force re-encoding all faces...")

# Create new recognizer
recognizer = FaceRecognizer()

# Clear old encodings file
encodings_file = Path("models/face_encodings.pkl")
if encodings_file.exists():
    encodings_file.unlink()
    print("✅ Cleared old encodings")

# Re-encode all faces
if recognizer.encode_faces_from_dataset():
    print(f"\n✅ Success! Encoded {len(recognizer.get_student_list())} faces:")
    for name in recognizer.get_student_list():
        print(f"  - {name}")
else:
    print("❌ Failed to encode faces")

print("\n🎯 Now run the main app and try recognition again!")