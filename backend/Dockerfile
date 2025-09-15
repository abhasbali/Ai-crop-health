FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies for multi-spectral analysis
RUN apt-get update && apt-get install -y \
    postgresql-client \
    build-essential \
    curl \
    ca-certificates \
    # Dependencies for matplotlib and image processing
    libfreetype6-dev \
    libpng-dev \
    libjpeg62-turbo-dev \
    # Dependencies for scientific computing
    liblapack-dev \
    libblas-dev \
    gfortran \
    # Additional utilities
    git \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/uploads /app/model

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]
