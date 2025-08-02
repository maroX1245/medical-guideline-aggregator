# Multi-stage build for production deployment
FROM node:18-alpine AS frontend-builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install frontend dependencies
RUN npm ci --only=production

# Copy frontend source
COPY public/ ./public/
COPY src/ ./src/
COPY tailwind.config.js postcss.config.js ./

# Build frontend
RUN npm run build

# Python backend stage
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_DEBUG=False

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        wget \
        gnupg \
        unzip \
        curl \
    && wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - \
    && sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list' \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source
COPY app.py .
COPY scraper.py .
COPY ai_summarizer.py .

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/build ./build

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/health || exit 1

# Run the application
CMD ["python", "app.py"] 