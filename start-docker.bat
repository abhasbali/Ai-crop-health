@echo off
echo ================================================================================
echo 🚀 CropHealth AI Multi-Spectral Analysis Platform - Docker Launch
echo ================================================================================
echo.
echo 🔧 System Overview:
echo    • Backend:  Flask API with Multi-Spectral Analysis Engine
echo    • Frontend: React App with Interactive Visualizations  
echo    • Database: PostgreSQL with Real Agricultural Data
echo    • ML Model: Trained Agricultural Health Prediction Model
echo.
echo 🛰️ Multi-Spectral Features:
echo    • NDVI, NDWI, MNDWI, NDSI calculations
echo    • Google Earth Engine integration
echo    • Real-time weather data (WeatherAPI.com)
echo    • Land cover classification
echo    • Interactive visualizations
echo.

REM Check if Docker is running
echo 📋 Checking Docker status...
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed or not running!
    echo    Please install Docker Desktop and make sure it's running.
    echo    Download from: https://www.docker.com/products/docker-desktop/
    pause
    exit /b 1
)

docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker daemon is not running!
    echo    Please start Docker Desktop and try again.
    pause
    exit /b 1
)

echo ✅ Docker is running

echo.
echo 🧹 Cleaning up previous containers...
docker-compose down --volumes --remove-orphans 2>nul

echo.
echo 📦 Building and starting services...
echo    This may take a few minutes on first run...

REM Build and start all services
docker-compose up --build -d

echo.
echo 🔍 Checking service health...
timeout /t 10 /nobreak >nul

REM Wait for services to be healthy
echo Waiting for database to be ready...
:wait_db
docker-compose exec -T db pg_isready -U cropuser >nul 2>&1
if %errorlevel% neq 0 (
    echo    • Database is starting...
    timeout /t 3 /nobreak >nul
    goto wait_db
)
echo ✅ Database is ready

echo.
echo Waiting for backend to be ready...
:wait_backend
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:5000/api/health' -TimeoutSec 2 -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    echo    • Backend is starting...
    timeout /t 5 /nobreak >nul
    goto wait_backend
)
echo ✅ Backend is ready

echo.
echo Waiting for frontend to be ready...
:wait_frontend
powershell -Command "try { Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 2 -UseBasicParsing | Out-Null; exit 0 } catch { exit 1 }" >nul 2>&1
if %errorlevel% neq 0 (
    echo    • Frontend is starting...
    timeout /t 3 /nobreak >nul
    goto wait_frontend
)
echo ✅ Frontend is ready

echo.
echo ================================================================================
echo 🎉 SUCCESS! All services are running
echo ================================================================================
echo.
echo 🌐 Access Points:
echo    • Application:  http://localhost:3000
echo    • Backend API:  http://localhost:5000
echo    • Database:     localhost:5432
echo.
echo 🔐 Demo Login Credentials:
echo    • Email:     demo@crophealth.com
echo    • Password:  demo123
echo.
echo 🛰️ Multi-Spectral Analysis Features:
echo    1. Navigate to "Spectral Analysis" in the top menu
echo    2. Upload satellite data OR click "Run Analysis" for demo
echo    3. Explore results in Overview/Charts/Technical tabs
echo    4. View field-specific analysis from Dashboard → Field Details
echo.
echo 📊 What You Can Test:
echo    • Multi-spectral indices: NDVI, NDWI, MNDWI, NDSI
echo    • Land cover classification: Water, Vegetation, Soil, etc.
echo    • Interactive charts and visualizations
echo    • Real satellite data integration (if API keys configured)
echo    • AI crop health predictions with 88.7%% accuracy
echo.
echo 💾 Container Management:
echo    • View logs:    docker-compose logs -f
echo    • Stop:         docker-compose down
echo    • Restart:      docker-compose restart
echo    • Status:       docker-compose ps
echo.
echo 🔧 Troubleshooting:
echo    • If services fail to start, check: docker-compose logs
echo    • To reset everything: docker-compose down --volumes
echo    • For fresh rebuild: docker-compose up --build --force-recreate
echo.

REM Check if we should open browser
echo Would you like to open the application in your browser? (Y/N)
set /p choice="Choice: "
if /i "%choice%"=="Y" (
    echo Opening application...
    start http://localhost:3000
)

echo.
echo ================================================================================
echo 🎯 Ready for Multi-Spectral Crop Analysis!
echo.
echo Press any key to view container logs, or Ctrl+C to exit...
pause >nul

echo.
echo 📋 Container Logs (Press Ctrl+C to exit):
docker-compose logs -f
