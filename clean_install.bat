@echo off
title AI Attendance System - Clean Installation
color 0A
echo ====================================================
echo    AI ATTENDANCE SYSTEM - COMPLETE CLEAN INSTALL
echo ====================================================
echo.

echo Step 1: Uninstalling all existing packages...
echo ------------------------------------------------
pip uninstall numpy pandas opencv-python opencv-contrib-python streamlit plotly pillow cmake dlib-bin face-recognition -y

echo.
echo Step 2: Clearing pip cache...
echo ------------------------------------------------
pip cache purge

echo.
echo Step 3: Installing specific compatible versions...
echo ------------------------------------------------
pip install numpy==1.23.5
pip install pandas==1.5.3
pip install opencv-python==4.8.1.78
pip install opencv-contrib-python==4.8.1.78
pip install streamlit==1.28.1
pip install plotly==5.17.0
pip install pillow==10.0.1
pip install cmake==3.27.9
pip install dlib-bin==19.22.0
pip install face-recognition==1.3.0

echo.
echo Step 4: Verifying installation...
echo ------------------------------------------------
python -c "import numpy; import pandas; import cv2; import streamlit; print('✅ All imports successful!')"

echo.
echo ====================================================
echo    INSTALLATION COMPLETE!
echo ====================================================
echo.
echo To run the application:
echo streamlit run app.py
echo.
pause