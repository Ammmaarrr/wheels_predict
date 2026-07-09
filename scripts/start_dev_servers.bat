@echo off
REM Development script to run both React and FastAPI servers simultaneously

echo 🚀 Starting PakWheels ML Platform in Development Mode...

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Node.js is not installed. Please install Node.js first.
    exit /b 1
)

REM Check if Python is installed
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python first.
    exit /b 1
)

REM Install frontend dependencies
echo 📦 Installing frontend dependencies...
cd frontend
call npm install
if %errorlevel% neq 0 (
    echo ❌ Failed to install frontend dependencies
    exit /b 1
)

REM Go back to root directory
cd ..

REM Install backend dependencies
echo 📦 Installing backend dependencies...
cd api
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install backend dependencies
    exit /b 1
)

REM Start both servers
echo 🚀 Starting development servers...
echo 🔵 FastAPI will be available at http://localhost:8000
echo 🔴 React app will be available at http://localhost:3000

REM Start FastAPI server in background
start /b cmd /c "python dev_server.py"

REM Wait a moment for FastAPI to start
timeout /t 3 /nobreak > nul

REM Go to frontend directory and start React dev server
cd ..\frontend
call npm start

echo 🎉 Development servers started successfully!
echo 🔵 FastAPI: http://localhost:8000
echo 🔴 React: http://localhost:3000
echo 📊 API Documentation: http://localhost:8000/docs

pause
