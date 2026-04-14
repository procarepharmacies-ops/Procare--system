@echo off
title ProCare Pharmacy Intelligence
echo.
echo  ============================================
echo   ProCare Pharmacy Intelligence System
echo   Starting API Server...
echo  ============================================
echo.

cd /d D:\procare-pharmacy

echo  Installing/checking dependencies...
py -m pip install flask flask-cors pyodbc --quiet

echo.
echo  Starting server on http://localhost:5000
echo  Opening dashboard in browser...
echo.
echo  Press Ctrl+C to stop the server
echo.

start "" "http://localhost:5000"
py app.py

pause
