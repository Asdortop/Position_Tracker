#!/bin/bash

# Position Tracker API Startup Script

echo "🚀 Starting Position Tracker API with Docker..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install docker-compose first."
    exit 1
fi

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Position Tracker Environment Configuration
DATABASE_URL=postgresql+psycopg2://tracker_user:secure_pass_123@postgres:5432/position_tracker
DEBUG=true
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
EOF
    echo "✅ .env file created"
fi

# Start services
echo "🐳 Starting Docker services..."
docker-compose up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 10

# Check if API is responding
echo "🔍 Checking API health..."
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ API is healthy and ready!"
        break
    fi
    echo "⏳ Waiting for API... (attempt $i/30)"
    sleep 2
done

# Show service status
echo "📊 Service Status:"
docker-compose ps

echo ""
echo "🎉 Position Tracker API is ready!"
echo "📍 API URL: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo "🔍 Health Check: http://localhost:8000/health"
echo ""
echo "📋 Useful commands:"
echo "  View logs: docker-compose logs -f"
echo "  Stop services: docker-compose down"
echo "  Restart: docker-compose restart"
echo "  Rebuild: docker-compose up --build -d"
