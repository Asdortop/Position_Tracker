@echo off
REM Position Tracker API Startup Script for Windows

echo 🚀 Starting Position Tracker API with Docker...

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if docker-compose is available
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ docker-compose is not installed. Please install docker-compose first.
    pause
    exit /b 1
)

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file...
    (
        echo # Position Tracker Environment Configuration
        echo DATABASE_URL=postgresql+psycopg2://tracker_user:secure_pass_123@postgres:5432/position_tracker
        echo DEBUG=true
        echo LOG_LEVEL=INFO
        echo HOST=0.0.0.0
        echo PORT=8000
    ) > .env
    echo ✅ .env file created
)

REM Start services
echo 🐳 Starting Docker services...
docker-compose up -d

REM Wait for services to be ready
echo ⏳ Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check if API is responding
echo 🔍 Checking API health...
for /l %%i in (1,1,30) do (
    curl -s http://localhost:8000/health >nul 2>&1
    if !errorlevel! equ 0 (
        echo ✅ API is healthy and ready!
        goto :ready
    )
    echo ⏳ Waiting for API... (attempt %%i/30)
    timeout /t 2 /nobreak >nul
)

:ready
REM Show service status
echo 📊 Service Status:
docker-compose ps

echo.
echo 🎉 Position Tracker API is ready!
echo 📍 API URL: http://localhost:8000
echo 📚 API Docs: http://localhost:8000/docs
echo 🔍 Health Check: http://localhost:8000/health
echo.
echo 📋 Useful commands:
echo   View logs: docker-compose logs -f
echo   Stop services: docker-compose down
echo   Restart: docker-compose restart
echo   Rebuild: docker-compose up --build -d
echo.
pause
