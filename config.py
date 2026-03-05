"""
Configuration settings for the attendance system
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent

# Folders
DATASET_FOLDER = BASE_DIR / "dataset"
MODELS_FOLDER = BASE_DIR / "models"
ATTENDANCE_FOLDER = BASE_DIR / "attendance"
TEMP_FOLDER = BASE_DIR / "temp"

# Files
ENCODINGS_FILE = MODELS_FOLDER / "face_encodings.pkl"
ATTENDANCE_FILE = ATTENDANCE_FOLDER / "attendance.csv"

# Recognition settings - STRICT MODE
RECOGNITION_THRESHOLD = 45  # VERY STRICT - only match if confidence is very low
RECOGNITION_COOLDOWN = 10    # Seconds between recognitions

# Camera settings
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Create directories if they don't exist
for folder in [DATASET_FOLDER, MODELS_FOLDER, ATTENDANCE_FOLDER, TEMP_FOLDER]:
    folder.mkdir(exist_ok=True, parents=True)

print(f"✅ Configuration loaded - STRICT MODE ENABLED")
print(f"📁 Dataset folder: {DATASET_FOLDER}")
print(f"📁 Models folder: {MODELS_FOLDER}")
print(f"📁 Attendance folder: {ATTENDANCE_FOLDER}")
print(f"🎯 Recognition threshold: {RECOGNITION_THRESHOLD} (very strict)")