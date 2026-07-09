@echo off
REM Build and run the React + FastAPI application for Windows

echo 🚀 Starting PakWheels ML Platform...

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

REM Build the React app
echo 🔨 Building React app...
call npm run build

REM Go back to root directory
cd ..

REM Install backend dependencies
echo 📦 Installing backend dependencies...
cd api
pip install -r requirements.txt

REM Start the FastAPI server
echo 🚀 Starting FastAPI server...
python dev_server.py
