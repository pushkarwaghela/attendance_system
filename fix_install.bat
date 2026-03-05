@echo off
echo ========================================
echo AI ATTENDANCE SYSTEM - INSTALLATION FIX
echo ========================================
echo.

echo Step 1: Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Step 2: Installing cmake first...
pip install cmake

echo.
echo Step 3: Installing dlib-bin (Windows compatible)...
pip install dlib-bin

echo.
echo Step 4: Installing face-recognition...
pip install face-recognition

echo.
echo Step 5: Installing other dependencies...
pip install opencv-python opencv-contrib-python numpy pandas==1.5.3 plotly pillow streamlit

echo.
echo ========================================
echo INSTALLATION COMPLETE!
echo ========================================
echo.
echo To run the app:
echo streamlit run app.py
echo.
pause