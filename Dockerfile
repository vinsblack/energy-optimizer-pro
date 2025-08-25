# Frontend Dependencies (Next.js)
FROM node:18-alpine AS frontend-deps
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci --only=production

# Frontend Build
FROM node:18-alpine AS frontend-build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Backend Dependencies (Python)
FROM python:3.11-slim AS backend-deps
WORKDIR /app/backend
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Production Image
FROM python:3.11-slim AS production

# Install Node.js for running Next.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create app user
RUN addgroup --system --gid 1001 appgroup \
    && adduser --system --uid 1001 appuser

# Setup directories
WORKDIR /app
RUN mkdir -p /app/frontend /app/backend /app/logs /app/data \
    && chown -R appuser:appgroup /app

# Copy backend
COPY --from=backend-deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-deps /usr/local/bin /usr/local/bin
COPY backend/ ./backend/

# Copy frontend build
COPY --from=frontend-build /app/frontend/.next ./frontend/.next
COPY --from=frontend-build /app/frontend/public ./frontend/public
COPY --from=frontend-build /app/frontend/package.json ./frontend/package.json
COPY --from=frontend-deps /app/frontend/node_modules ./frontend/node_modules

# Copy startup script
COPY docker/start.sh ./
RUN chmod +x start.sh

# Switch to app user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose ports
EXPOSE 3000 8000

# Environment variables
ENV NODE_ENV=production
ENV PYTHONPATH=/app/backend
ENV PYTHONUNBUFFERED=1

# Start both services
CMD ["./start.sh"]

# Multi-stage build for development
FROM node:18-alpine AS development

# Install Python
RUN apk add --no-cache python3 py3-pip python3-dev build-base

WORKDIR /app

# Copy source code
COPY frontend/ ./frontend/
COPY backend/ ./backend/

# Install dependencies
WORKDIR /app/frontend
RUN npm install

WORKDIR /app/backend  
RUN pip install -r requirements.txt

WORKDIR /app

# Development startup
CMD ["sh", "-c", "cd backend && python main.py & cd frontend && npm run dev"]
