#!/bin/bash

echo "================================================================================"
echo "🚀 CropHealth AI Multi-Spectral Analysis Platform - Docker Launch"
echo "================================================================================"
echo
echo "🔧 System Overview:"
echo "   • Backend:  Flask API with Multi-Spectral Analysis Engine"
echo "   • Frontend: React App with Interactive Visualizations"  
echo "   • Database: PostgreSQL with Real Agricultural Data"
echo "   • ML Model: Trained Agricultural Health Prediction Model"
echo
echo "🛰️ Multi-Spectral Features:"
echo "   • NDVI, NDWI, MNDWI, NDSI calculations"
echo "   • Google Earth Engine integration"
echo "   • Real-time weather data (WeatherAPI.com)"
echo "   • Land cover classification"
echo "   • Interactive visualizations"
echo

# Check if Docker is running
echo "📋 Checking Docker status..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "   Please install Docker and try again."
    echo "   Install from: https://docs.docker.com/get-docker/"
    exit 1
fi

if ! docker ps &> /dev/null; then
    echo "❌ Docker daemon is not running!"
    echo "   Please start Docker daemon and try again."
    exit 1
fi

echo "✅ Docker is running"

echo
echo "🧹 Cleaning up previous containers..."
docker-compose down --volumes --remove-orphans 2>/dev/null || true

echo
echo "📦 Building and starting services..."
echo "   This may take a few minutes on first run..."

# Build and start all services
docker-compose up --build -d

echo
echo "🔍 Checking service health..."
sleep 10

# Wait for database to be ready
echo "Waiting for database to be ready..."
while ! docker-compose exec -T db pg_isready -U cropuser &> /dev/null; do
    echo "   • Database is starting..."
    sleep 3
done
echo "✅ Database is ready"

# Wait for backend to be ready
echo
echo "Waiting for backend to be ready..."
while ! curl -s http://localhost:5000/api/health &> /dev/null; do
    echo "   • Backend is starting..."
    sleep 5
done
echo "✅ Backend is ready"

# Wait for frontend to be ready
echo
echo "Waiting for frontend to be ready..."
while ! curl -s http://localhost:3000 &> /dev/null; do
    echo "   • Frontend is starting..."
    sleep 3
done
echo "✅ Frontend is ready"

echo
echo "================================================================================"
echo "🎉 SUCCESS! All services are running"
echo "================================================================================"
echo
echo "🌐 Access Points:"
echo "   • Application:  http://localhost:3000"
echo "   • Backend API:  http://localhost:5000"
echo "   • Database:     localhost:5432"
echo
echo "🔐 Demo Login Credentials:"
echo "   • Email:     demo@crophealth.com"
echo "   • Password:  demo123"
echo
echo "🛰️ Multi-Spectral Analysis Features:"
echo "   1. Navigate to \"Spectral Analysis\" in the top menu"
echo "   2. Upload satellite data OR click \"Run Analysis\" for demo"
echo "   3. Explore results in Overview/Charts/Technical tabs"
echo "   4. View field-specific analysis from Dashboard → Field Details"
echo
echo "📊 What You Can Test:"
echo "   • Multi-spectral indices: NDVI, NDWI, MNDWI, NDSI"
echo "   • Land cover classification: Water, Vegetation, Soil, etc."
echo "   • Interactive charts and visualizations"
echo "   • Real satellite data integration (if API keys configured)"
echo "   • AI crop health predictions with 88.7% accuracy"
echo
echo "💾 Container Management:"
echo "   • View logs:    docker-compose logs -f"
echo "   • Stop:         docker-compose down"
echo "   • Restart:      docker-compose restart"
echo "   • Status:       docker-compose ps"
echo
echo "🔧 Troubleshooting:"
echo "   • If services fail to start, check: docker-compose logs"
echo "   • To reset everything: docker-compose down --volumes"
echo "   • For fresh rebuild: docker-compose up --build --force-recreate"
echo

# Check if we should open browser
read -p "Would you like to open the application in your browser? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Opening application..."
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    elif command -v open &> /dev/null; then
        open http://localhost:3000
    else
        echo "Please open http://localhost:3000 in your browser"
    fi
fi

echo
echo "================================================================================"
echo "🎯 Ready for Multi-Spectral Crop Analysis!"
echo
echo "Press Enter to view container logs, or Ctrl+C to exit..."
read

echo
echo "📋 Container Logs (Press Ctrl+C to exit):"
docker-compose logs -f
