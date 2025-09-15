# AI Crop Health Monitoring Application

A full-stack web application for monitoring crop health using AI/ML models, featuring real-time predictions, NDVI analysis, and alert systems.

## 🌟 Features

### Core Functionality
- **User Authentication**: JWT-based login/signup system
- **Field Management**: Create, read, update, delete crop fields
- **AI Predictions**: Upload sensor data (CSV, NPZ, JSON) and get crop health predictions
- **NDVI Analysis**: Normalized Difference Vegetation Index calculations and visualizations
- **Real-time Alerts**: Automatic notifications for poor crop health conditions
- **Historical Data**: Track crop health trends over time with interactive charts

### Technical Features
- **Responsive Design**: Mobile-first UI with Tailwind CSS
- **Dark Mode**: Toggle between light and dark themes
- **File Upload**: Support for multiple data formats (CSV, NPZ, JSON)
- **Data Visualization**: Interactive charts using Chart.js and Recharts
- **API Integration**: RESTful APIs with comprehensive error handling
- **Containerized Deployment**: Docker and Docker Compose ready

## 🏗️ Architecture

```
project/
├── backend/           # Flask API server
│   ├── app.py         # Main application
│   ├── routes/        # API endpoints
│   ├── models/        # Database models
│   ├── utils/         # Utilities (ML, data processing)
│   └── database/      # Database configuration
├── frontend/          # React application
│   ├── src/
│   │   ├── components/ # Reusable UI components
│   │   ├── pages/     # Route pages
│   │   └── services/  # API and auth services
│   └── public/        # Static assets
└── docker-compose.yml # Multi-service orchestration
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- 4GB+ RAM recommended
- Ports 3000, 5000, and 5432 available

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd project
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configurations
   ```

3. **Start the application**
   ```bash
   docker-compose up --build
   ```

4. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000/api
   - Database: localhost:5432

### Demo Account
- **Email**: demo@crophealth.com
- **Password**: demo123

## 📊 Usage Guide

### 1. Getting Started
1. Create an account or use demo credentials
2. Add your first field with location and crop details
3. Upload sensor data or use manual input
4. Run AI predictions to get health scores

### 2. Data Upload Formats

#### CSV Format
```csv
ndvi,temperature,humidity,soil_moisture,ph
0.75,25.5,65.2,45.8,6.8
0.72,26.1,62.4,48.2,6.9
```

#### JSON Format
```json
{
  "ndvi": [0.75, 0.72, 0.68],
  "temperature": [25.5, 26.1, 27.2],
  "humidity": [65.2, 62.4, 58.9],
  "soil_moisture": [45.8, 48.2, 42.1],
  "ph": [6.8, 6.9, 7.1]
}
```

#### NPZ Format
NumPy arrays with keys: ndvi, temperature, humidity, soil_moisture, ph

### 3. Understanding Results
- **Health Score**: 0-100 scale (Poor: 0-40, Moderate: 40-70, Good: 70-100)
- **NDVI Values**: -1 to 1 scale (higher values indicate healthier vegetation)
- **Confidence**: Model confidence in prediction (0-100%)
- **Status**: Categorical assessment (Poor, Moderate, Good)

## 🛠️ Development

### Local Development Setup

#### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export FLASK_ENV=development
flask run
```

#### Frontend Development
```bash
cd frontend
npm install
npm start
```

#### Database Setup (Local)
```bash
# Install PostgreSQL locally
createdb cropdb
# Update .env with local database URL
```

### API Endpoints

#### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user
- `POST /api/auth/refresh` - Refresh token

#### Fields Management
- `GET /api/fields` - List user fields
- `POST /api/fields` - Create new field
- `GET /api/fields/:id` - Get field details
- `PUT /api/fields/:id` - Update field
- `DELETE /api/fields/:id` - Delete field

#### Predictions
- `POST /api/predictions/upload-data` - Upload sensor data
- `POST /api/predictions/predict` - Run AI prediction
- `GET /api/predictions/alerts` - Get alerts
- `GET /api/predictions/history/:field_id` - Get prediction history
- `GET /api/predictions/model-info` - Get model information

## 🧠 AI/ML Models

### Supported Model Types
- **Scikit-learn**: RandomForest, SVM, etc. (.pkl, .joblib)
- **PyTorch**: Deep learning models (.pt, .pth)
- **TensorFlow/Keras**: Neural networks (.h5)

### Dummy Model
The application includes a pre-trained RandomForest model for demonstration that:
- Uses 5 features: NDVI, temperature, humidity, soil moisture, pH
- Classifies crop health into 3 categories: Poor (0), Moderate (1), Good (2)
- Provides confidence scores and health predictions

### Custom Models
Replace the dummy model by:
1. Training your model with crop health data
2. Saving it in a supported format
3. Mounting it to `/app/model/model.pt` in the container
4. Updating `MODEL_PATH` environment variable

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_USER` | Database username | cropuser |
| `POSTGRES_PASSWORD` | Database password | croppass |
| `POSTGRES_DB` | Database name | cropdb |
| `JWT_SECRET` | JWT signing secret | supersecretjwt |
| `MODEL_PATH` | Path to AI model file | /app/model/model.pt |
| `FLASK_ENV` | Flask environment | production |
| `REACT_APP_API_BASE` | Frontend API base URL | http://localhost:5000/api |

### Customization Options
- **Themes**: Modify Tailwind CSS configuration
- **Models**: Replace AI models with custom trained versions
- **Features**: Extend with additional sensor data types
- **Alerts**: Configure custom alert thresholds
- **Visualizations**: Add new chart types and metrics

## 📈 Monitoring & Health Checks

### Health Endpoints
- Frontend: `http://localhost:3000/health`
- Backend: `http://localhost:5000/api/health`
- Database: Check with `docker-compose ps`

### Logging
- Backend logs: `docker-compose logs backend`
- Frontend logs: `docker-compose logs frontend`
- Database logs: `docker-compose logs db`

## 🚀 Deployment

### Production Deployment

1. **Update environment variables**
   ```bash
   # Use strong passwords and secrets
   JWT_SECRET=your-production-secret
   POSTGRES_PASSWORD=secure-password
   ```

2. **Configure domains**
   ```bash
   # Update API base URL for production domain
   REACT_APP_API_BASE=https://your-api-domain.com/api
   ```

3. **Deploy with SSL**
   ```bash
   # Add reverse proxy (nginx/traefik) for SSL termination
   # Update CORS settings in backend
   ```

### Scaling Options
- **Database**: Use managed PostgreSQL (AWS RDS, Google Cloud SQL)
- **Backend**: Deploy multiple Flask instances behind load balancer
- **Frontend**: Use CDN for static assets
- **Storage**: Use cloud storage for file uploads

## 🛡️ Security

### Current Security Measures
- JWT authentication with expiration
- Password hashing (SHA-256)
- SQL injection protection (parameterized queries)
- CORS configuration
- Input validation and sanitization
- File upload restrictions

### Recommended Enhancements
- Implement rate limiting
- Add input sanitization middleware
- Use HTTPS in production
- Regular security audits
- Database connection pooling
- Implement user roles and permissions

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow existing code style and patterns
- Add tests for new features
- Update documentation
- Ensure Docker build works
- Test on multiple devices/browsers

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Tailwind CSS for the beautiful UI components
- Chart.js for data visualizations
- Flask and React communities
- Scikit-learn for machine learning capabilities
- PostgreSQL for robust data storage

## 📞 Support

For support, email support@crophealth.com or create an issue in the repository.

---

**Made with ❤️ for sustainable agriculture and AI innovation**
