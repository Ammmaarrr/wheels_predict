@echo off
echo === Wheels Predict API MVP Launch ===
echo Installing dependencies and starting services...

echo Installing Python dependencies...
pip install -r requirements.mvp.txt

echo Starting FastAPI server...
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo Demo credentials: http://localhost:8000/api/demo-credentials

python mvp_fastapi_server.py
