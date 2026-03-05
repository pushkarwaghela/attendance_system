"""
Configuration settings - OPTIMIZED for speed and accuracy
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Folders
DATASET_FOLDER = BASE_DIR / "dataset"
MODELS_FOLDER = BASE_DIR / "models"
ATTENDANCE_FOLDER = BASE_DIR / "attendance"

# Files
ENCODINGS_FILE = MODELS_FOLDER / "face_encodings.pkl"
ATTENDANCE_FILE = ATTENDANCE_FOLDER / "attendance.csv"

# Recognition settings - BALANCED for speed/accuracy
RECOGNITION_THRESHOLD = 50  # Balanced threshold
RECOGNITION_COOLDOWN = 3     # Seconds between recognitions
FRAME_SKIP = 2               # Process every 2nd frame for speed

# Camera settings - OPTIMIZED
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Create directories
for folder in [DATASET_FOLDER, MODELS_FOLDER, ATTENDANCE_FOLDER]:
    folder.mkdir(exist_ok=True, parents=True)

print(f"✅ Configuration loaded - OPTIMIZED MODE")
print(f"📁 Dataset: {DATASET_FOLDER}")
print(f"🎯 Threshold: {RECOGNITION_THRESHOLD}")