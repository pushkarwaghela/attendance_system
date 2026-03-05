@echo off
title AI ATTENDANCE SYSTEM
color 0A
echo ========================================
echo    AI ATTENDANCE SYSTEM - FINAL FIX
echo ========================================
echo.

:: Activate virtual environment
call venv\Scripts\activate

:: Fix encoding and run
echo 🔄 Loading students from dataset...
python -c "from face_utils import face_recognizer; face_recognizer.encode_faces()"

echo.
echo 🚀 Starting application...
streamlit run app_fixed.py

pause