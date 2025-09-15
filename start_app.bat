@echo off
echo Starting CropHealth AI Multi-Spectral Analysis App
echo ================================================

echo.
echo 🚀 Starting Backend Server...
start "Backend Server" cmd /k "cd C:\Users\Lenovo\project\backend && python app.py"

echo.
echo Waiting for backend to initialize...
timeout /t 5 /nobreak > nul

echo.
echo 🌐 Starting Frontend Server...
start "Frontend Server" cmd /k "cd C:\Users\Lenovo\project\frontend && npm start"

echo.
echo ================================================
echo ✅ Both servers are starting up!
echo.
echo Backend:  http://localhost:5000
echo Frontend: http://localhost:3000  
echo.
echo Demo Login Credentials:
echo Email:    demo@crophealth.com
echo Password: demo123
echo.
echo 🛰️ Features Available:
echo - Multi-spectral analysis (NDVI, NDWI, MNDWI, NDSI)
echo - Real satellite data via Google Earth Engine
echo - Weather data integration
echo - AI crop health predictions
echo - Interactive visualizations
echo.
echo Press any key to continue or Ctrl+C to exit...
pause > nul
