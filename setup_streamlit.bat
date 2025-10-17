@echo off
echo ======================================================================
echo Cholera Prediction System - Streamlit Setup
echo ======================================================================
echo.
echo This script will set up the Streamlit web application
echo.

echo Step 1: Installing Streamlit dependencies...
cd streamlit_app
pip install -r requirements.txt

echo.
echo Step 2: Testing installation...
streamlit --version

echo.
echo ======================================================================
echo Setup Complete!
echo ======================================================================
echo.
echo To run the application:
echo   1. cd streamlit_app
echo   2. streamlit run app.py
echo.
echo Or simply run: streamlit_app\run_app.bat
echo.
echo The app will open at: http://localhost:8501
echo ======================================================================
pause
