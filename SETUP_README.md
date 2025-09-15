# 🌾 AI Crop Health Monitoring System - Complete Setup Guide

A comprehensive agricultural monitoring application featuring AI-powered crop health analysis, hyperspectral visualization, multi-spectral indices (NDVI, NDWI, NDSI), real satellite data integration via Google Earth Engine, and advanced pest detection algorithms.

## 🌟 Key Features

- **Multi-Spectral Analysis**: NDVI, NDWI, MNDWI, NDSI calculations with real satellite data
- **Hyperspectral Visualization**: Interactive field maps with health zones and spectral analysis
- **Real Satellite Data**: Integration with Google Earth Engine (Landsat, Sentinel-2, MODIS)
- **AI/ML Predictions**: Crop health assessment and pest risk detection
- **User-Friendly Dashboard**: React-based frontend with interactive charts and maps
- **Authentication & Security**: JWT-based user management
- **Alert System**: Real-time notifications for crop health issues

## 🏗️ System Architecture

```
project/
├── backend/                    # Flask API server (Python)
│   ├── app.py                 # Main Flask application
│   ├── routes/                # API endpoints
│   │   ├── auth.py           # Authentication routes
│   │   ├── fields.py         # Field management
│   │   └── predictions.py    # AI predictions & analysis
│   ├── models/               # Database models
│   ├── utils/                # Core utilities
│   │   ├── ndvi.py          # Multi-spectral indices calculation
│   │   ├── satellite_data.py # Google Earth Engine integration
│   │   ├── hyperspectral_visualization.py # Visualization generation
│   │   ├── model_loader.py   # AI model management
│   │   └── real_model.py     # Agricultural AI model
│   └── requirements.txt      # Python dependencies
├── frontend/                  # React application
│   ├── src/
│   │   ├── components/       # Reusable UI components
│   │   │   ├── SpectralAnalysis.jsx    # Multi-spectral analysis UI
│   │   │   └── HyperspectralVisualization.jsx # Field visualization
│   │   ├── pages/           # Application pages
│   │   └── services/        # API integration services
│   └── package.json         # Node.js dependencies
├── .env                     # Environment variables (create from .env.example)
├── docker-compose.yml       # Docker orchestration
└── README.md               # Original project documentation
```

## 🚀 Prerequisites

### Required Software (Windows)

1. **Python 3.8+**: [Download from python.org](https://www.python.org/downloads/)
   - During installation, check "Add Python to PATH"
   - Verify: `python --version` in PowerShell

2. **Node.js 16+**: [Download from nodejs.org](https://nodejs.org/download/)
   - Includes npm package manager
   - Verify: `node --version` and `npm --version`

3. **Git**: [Download Git for Windows](https://git-scm.com/download/win)
   - Verify: `git --version`

### Optional (Recommended)

4. **Docker Desktop**: [Download for Windows](https://docs.docker.com/desktop/install/windows-install/)
   - For containerized deployment
   - Requires WSL 2 on Windows 10/11

5. **PostgreSQL** (if not using Docker):
   - [Download from postgresql.org](https://www.postgresql.org/download/windows/)

### System Requirements

- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space
- **Ports**: 3000, 5000, 5432 should be available
- **Internet**: Required for satellite data and API access

## 🔧 Installation Guide

### Step 1: Clone and Setup Project

```powershell
# Clone the repository (or download ZIP and extract)
git clone <your-repository-url>
cd project

# Or if you already have the project:
cd C:\Users\Lenovo\project
```

### Step 2: Environment Configuration

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your configurations
notepad .env
```

**Required Environment Variables** (edit `.env` file):

```bash
# Database (can use SQLite for development)
DATABASE_URL=sqlite:///crop_health.db

# JWT Secret (generate a strong secret)
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production

# API Configuration
FLASK_ENV=development
REACT_APP_API_BASE=http://localhost:5000/api

# Google Earth Engine (for real satellite data)
GOOGLE_SERVICE_ACCOUNT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
GOOGLE_SERVICE_ACCOUNT_KEY_FILE=./google-service-account-key.json
GOOGLE_PROJECT_ID=your-google-earth-engine-project

# Weather API (optional - for enhanced predictions)
WEATHER_API_KEY=your-weatherapi-key

# NASA API (optional - for additional satellite data)
NASA_API_KEY=DEMO_KEY
```

### Step 3: Google Earth Engine Setup (For Real Satellite Data)

1. **Create Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Earth Engine API

2. **Create Service Account**:
   - Go to IAM & Admin > Service Accounts
   - Click "Create Service Account"
   - Grant "Earth Engine Resource Admin" role
   - Download JSON key file

3. **Setup Earth Engine**:
   - Place JSON key file as `google-service-account-key.json` in project root
   - Update `.env` with your service account details
   - Register at [Google Earth Engine](https://earthengine.google.com/) and request access

### Step 4: Backend Setup

```powershell
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database (if using SQLite)
python -c "from app import create_app; app = create_app(); app.app_context().push(); from database.database import init_db; init_db()"
```

### Step 5: Frontend Setup

```powershell
# Navigate to frontend directory (open new PowerShell window)
cd frontend

# Install dependencies
npm install

# Install additional required packages (if not already in package.json)
npm install chart.js react-chartjs-2 axios react-router-dom
```

## 🚀 Running the Application

### Option A: Development Mode (Recommended for development)

**Terminal 1 - Backend:**
```powershell
cd backend
venv\Scripts\activate
python app.py
```

**Terminal 2 - Frontend:**
```powershell
cd frontend
npm start
```

**Access Points:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000/api
- Health Check: http://localhost:5000/api/health

### Option B: Docker Deployment

```powershell
# Build and start all services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Option C: Quick Start Scripts

**For Windows (PowerShell):**
```powershell
# Use the provided quick start script
.\quick-start.bat

# Or start individual components
.\start_app.bat
```

## 🔑 Initial Login

**Demo Account:**
- **Email**: demo@crophealth.com
- **Password**: demo123

**Or create new account:**
1. Go to http://localhost:3000
2. Click "Sign Up"
3. Fill in your details
4. Login with your credentials

## 📊 Using the Application

### 1. Basic Workflow

1. **Login**: Use demo credentials or create account
2. **Create Field**: Add a new crop field with location details
3. **Upload Data**: Upload sensor data (CSV, JSON, or NPZ format)
4. **Run Analysis**: Get AI predictions and spectral analysis
5. **View Results**: Interactive charts, maps, and health assessments

### 2. Multi-Spectral Analysis

**Access via:**
- **Field Details**: Click on any field → "Spectral Analysis" tab
- **Direct Page**: Navigate to "Spectral Analysis" in the menu

**Features:**
- NDVI (vegetation health)
- NDWI (water content)
- MNDWI (modified water index)
- NDSI (snow/ice index)
- Land cover classification
- Interactive visualizations

### 3. Hyperspectral Visualization

**Access via:**
- Field Details → "Hyperspectral Visualization" tab
- Features health zones mapping and pest risk assessment

### 4. Data Upload Formats

**CSV Example:**
```csv
ndvi,temperature,humidity,soil_moisture,ph
0.75,25.5,65.2,45.8,6.8
0.72,26.1,62.4,48.2,6.9
```

**JSON Example:**
```json
{
  "ndvi": [0.75, 0.72, 0.68],
  "temperature": [25.5, 26.1, 27.2],
  "humidity": [65.2, 62.4, 58.9],
  "soil_moisture": [45.8, 48.2, 42.1],
  "ph": [6.8, 6.9, 7.1]
}
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**:
   ```powershell
   # Check what's using the port
   netstat -ano | findstr :3000
   netstat -ano | findstr :5000
   
   # Kill process if needed
   taskkill /PID <process-id> /F
   ```

2. **Python Virtual Environment Issues**:
   ```powershell
   # If activation fails, try:
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   
   # Then activate again
   venv\Scripts\activate
   ```

3. **NPM Install Failures**:
   ```powershell
   # Clear npm cache
   npm cache clean --force
   
   # Delete node_modules and reinstall
   rmdir /s node_modules
   del package-lock.json
   npm install
   ```

4. **Database Connection Issues**:
   - For SQLite: Ensure the backend directory is writable
   - For PostgreSQL: Verify connection string in `.env`

5. **Google Earth Engine Authentication**:
   ```powershell
   # Check if service account file exists
   dir google-service-account-key.json
   
   # Verify environment variables
   echo $env:GOOGLE_SERVICE_ACCOUNT_EMAIL
   echo $env:GOOGLE_PROJECT_ID
   ```

### Debug Mode

**Enable verbose logging:**
```powershell
# Backend debug mode
$env:FLASK_ENV="development"
$env:FLASK_DEBUG="1"
python app.py

# Frontend with detailed errors
npm start
```

### Health Checks

**Backend:**
```powershell
curl http://localhost:5000/api/health
```

**Frontend:**
```powershell
curl http://localhost:3000
```

**Test API Integration:**
```powershell
cd backend
python test-api-simple.py
```

## 🧪 Testing

### Run Backend Tests
```powershell
cd backend
python -m pytest -v

# Test Google Earth Engine integration
python test_gee_integration.py
```

### Test API Endpoints
```powershell
# Run comprehensive API tests
python test-api-simple.py
```

### Frontend Testing
```powershell
cd frontend
npm test
```

## 📦 Production Deployment

### Environment Preparation

1. **Update environment variables** for production:
   ```bash
   FLASK_ENV=production
   JWT_SECRET=<strong-production-secret>
   POSTGRES_PASSWORD=<secure-password>
   REACT_APP_API_BASE=https://your-domain.com/api
   ```

2. **Database Setup**:
   - Use managed PostgreSQL (AWS RDS, Azure Database, etc.)
   - Update `DATABASE_URL` accordingly

3. **SSL Configuration**:
   - Add reverse proxy (nginx, Apache)
   - Configure SSL certificates

### Docker Production

```powershell
# Production build
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up --build

# Or with custom environment
docker-compose --env-file .env.production up --build
```

### Performance Optimization

- **Frontend**: Build and serve static files
- **Backend**: Use Gunicorn with multiple workers
- **Database**: Enable connection pooling
- **Caching**: Implement Redis for API caching

## 🔒 Security Considerations

### Development
- Change default JWT secret
- Use environment variables for secrets
- Don't commit `.env` or credential files

### Production
- Enable HTTPS only
- Use strong database passwords
- Implement rate limiting
- Regular security updates
- Backup strategies

## 📚 API Documentation

### Authentication Endpoints
- `POST /api/auth/signup` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user

### Field Management
- `GET /api/fields` - List fields
- `POST /api/fields` - Create field
- `GET /api/fields/:id` - Get field details
- `PUT /api/fields/:id` - Update field
- `DELETE /api/fields/:id` - Delete field

### Analysis Endpoints
- `POST /api/predictions/predict` - Run crop health prediction
- `POST /api/multi-spectral-analysis` - Multi-spectral indices analysis
- `POST /api/hyperspectral-visualization` - Generate field visualizations
- `GET /api/predictions/alerts` - Get health alerts

## 🔄 Updates and Maintenance

### Updating Dependencies

**Backend:**
```powershell
cd backend
pip list --outdated
pip install --upgrade package-name
pip freeze > requirements.txt
```

**Frontend:**
```powershell
cd frontend
npm outdated
npm update package-name
```

### Database Migrations

If you modify database models, create and run migrations:
```powershell
# Flask-Migrate (if implemented)
flask db migrate -m "Description of changes"
flask db upgrade
```

## 🆘 Support and Resources

### Documentation Files
- `README.md` - Original project documentation
- `REAL_DATA_SETUP.md` - Satellite data integration guide
- `DOCKER_SETUP.md` - Docker deployment details
- `MULTISPECTRAL_FEATURES.md` - Multi-spectral analysis features

### Getting Help
1. Check existing documentation files
2. Review error logs in console
3. Test individual components
4. Check network connectivity for API calls

### Useful Links
- [Google Earth Engine Documentation](https://developers.google.com/earth-engine/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [React Documentation](https://reactjs.org/docs/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

---

## 🎉 Quick Start Summary

For the fastest setup on Windows:

```powershell
# 1. Navigate to project
cd C:\Users\Lenovo\project

# 2. Setup environment
copy .env.example .env
# Edit .env with your settings

# 3. Backend setup
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# 4. Frontend setup (new PowerShell window)
cd frontend
npm install

# 5. Run application
# Terminal 1: cd backend && venv\Scripts\activate && python app.py
# Terminal 2: cd frontend && npm start

# 6. Open browser: http://localhost:3000
# Login: demo@crophealth.com / demo123
```

**That's it! Your AI Crop Health Monitoring System with hyperspectral analysis is ready to use! 🚀🌾**
