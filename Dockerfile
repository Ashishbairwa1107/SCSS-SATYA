# Multi-stage Dockerfile for SCSS SATYA

# Stage 1: Build Frontend
FROM node:22-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: Backend & Unified Application
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies for OpenCV and Pillow
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./backend/
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend code, scripts, and built frontend
COPY backend/ ./backend/
COPY scripts/ ./scripts/
COPY docs/ ./docs/
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Initialize directories
RUN mkdir -p storage/vault storage/artifacts storage/reports storage/database storage/specimens

ENV PYTHONPATH=/app/backend
EXPOSE 8000

CMD ["python", "scripts/run_backend.py"]
