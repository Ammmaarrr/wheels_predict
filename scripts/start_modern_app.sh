#!/bin/bash

# Build and run the React + FastAPI application

echo "🚀 Starting PakWheels ML Platform..."

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "❌ Python is not installed. Please install Python first."
    exit 1
fi

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install

# Build the React app
echo "🔨 Building React app..."
npm run build

# Go back to root directory
cd ..

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd api
pip install -r requirements.txt

# Start the FastAPI server
echo "🚀 Starting FastAPI server..."
python dev_server.py
