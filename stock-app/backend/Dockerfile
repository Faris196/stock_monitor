# Use Python 3.10 slim image
FROM python:3.10.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (required for pandas, matplotlib, and other packages)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first (for better caching)
COPY app_requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r app_requirements.txt

# Copy the rest of your application code
COPY . .

# Expose the port your app runs on (changed to 5000)
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=backend.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1
ENV MPLBACKEND=Agg  # Important for matplotlib in Docker

# Run the application with Gunicorn
CMD ["gunicorn", "backend:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120"]
