#!/bin/bash

# Docker Compose Validation Script
# This script validates the Docker Compose setup

set -e

echo "🔍 Validating Docker Compose setup..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi
echo "✅ Docker is installed"

# Check if Docker Compose is available
if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not available. Please install Docker Compose."
    exit 1
fi
echo "✅ Docker Compose is available"

# Check if required files exist
echo ""
echo "📁 Checking required files..."

required_files=(
    "docker-compose.yaml"
    "backend/Dockerfile"
    "backend/requirements.txt"
    "frontend/Dockerfile"
    "frontend/nginx.conf"
)

for file in "${required_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file exists"
    else
        echo "❌ $file is missing"
        exit 1
    fi
done

# Validate docker-compose.yaml syntax
echo ""
echo "🔧 Validating docker-compose.yaml syntax..."
if docker compose config > /dev/null 2>&1; then
    echo "✅ docker-compose.yaml syntax is valid"
else
    echo "❌ docker-compose.yaml has syntax errors"
    docker compose config
    exit 1
fi

# Check for port conflicts
echo ""
echo "🔌 Checking for port conflicts..."

check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "⚠️  Port $port is already in use"
        echo "   You may need to stop the service using this port or change the port in docker-compose.yaml"
        return 1
    else
        echo "✅ Port $port is available"
        return 0
    fi
}

port_conflicts=0
check_port 3000 || port_conflicts=1
check_port 8000 || port_conflicts=1

if [ $port_conflicts -eq 1 ]; then
    echo ""
    echo "⚠️  Warning: Some ports are already in use. You may want to:"
    echo "   1. Stop the services using these ports"
    echo "   2. Change the ports in docker-compose.yaml"
fi

echo ""
echo "✅ Docker Compose setup validation complete!"
echo ""
echo "To start the application, run:"
echo "  docker-compose up --build"
echo ""
echo "Or use the Makefile:"
echo "  make build && make up"
