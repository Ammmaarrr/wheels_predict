@echo off
echo === PakWheels ML API MVP - Frontend Launch ===
echo Starting React frontend...

cd frontend\mvp

echo Installing Node.js dependencies...
npm install

echo Starting React development server...
echo Frontend will be available at: http://localhost:3000
echo Make sure the API server is running at: http://localhost:8000

npm start
