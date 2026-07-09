@echo off
echo ===============================================
echo Wheels Predict ML API - Starting from D: Drive
echo ===============================================

cd /d "D:\data_scrapping_pakwheels"

echo Current directory: %CD%

echo.
echo Starting Backend API Server...
echo API will be available at: http://localhost:8000
echo.

start "Wheels Predict API Server" cmd /k "python simple_mvp_server.py"

echo.
echo Starting Frontend React App...
echo Frontend will be available at: http://localhost:3000
echo.

start "Wheels Predict Frontend" cmd /k "cd frontend\mvp && npm start"

echo.
echo ===============================================
echo Both servers are starting!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo ===============================================
echo.
echo Press any key to open the browser...
pause

start http://localhost:8000/docs
start http://localhost:3000

echo.
echo All services started successfully!
echo.
pause
