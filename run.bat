@echo off
title AI Attendance System
color 0A
echo ========================================
echo    AI ATTENDANCE SYSTEM LAUNCHER
echo ========================================
echo.

:: Check if virtual environment exists
if exist venv (
    echo Activating virtual environment...
    call venv\Scripts\activate
) else (
    echo No virtual environment found. Using system Python.
)

echo Starting Streamlit app...
echo.
streamlit run app.py

pause