# 🚀 How to Run Wheels Predict ML API MVP

## ✅ Current Status
**Backend API**: ✅ RUNNING on http://localhost:8000
**Frontend**: Ready to start

## 🔧 Quick Start Guide

### Step 1: Backend API (Already Running!)
The backend API server is already running successfully on port 8000.

**Test it here:**
- **Main API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Demo Credentials**: http://localhost:8000/api/demo-credentials
- **Health Check**: http://localhost:8000/health

### Step 2: Start the Frontend (React App)

Open a **new PowerShell window** and run:

```powershell
# Navigate to the project directory
cd "C:\Users\PC\Desktop\data_scrapping pakwheels"

# Navigate to frontend directory
cd frontend\mvp

# Install dependencies (only needed first time)
npm install

# Start the React development server
npm start
```

The frontend will automatically open in your browser at **http://localhost:3000**

## 🎯 Demo Accounts

### For Dealers (Full Features)
- **Email**: `dealer1@example.com`
- **Password**: `password123`
- **Features**: Price Prediction, Recommendations, Market Analysis

### For Resellers (Standard Features)
- **Email**: `reseller1@example.com`
- **Password**: `password123`
- **Features**: Price Prediction, Recommendations

### For Admins (All Features)
- **Email**: `admin@pakwheels.com`
- **Password**: `admin123`
- **Features**: All features + Admin access

## 📱 How to Use the App

### 1. Backend API (Already Running)
- Visit http://localhost:8000/docs for interactive API documentation
- Use the demo credentials to test authentication
- Try the price prediction and recommendation endpoints

### 2. Frontend Web App (Start with npm start)
1. Open http://localhost:3000 in your browser
2. Click on "Login" tab
3. Use any of the demo credentials above
4. Explore the dashboard, price predictor, and recommendations
5. If you're a dealer, you'll also see "Market Analysis"

## 🛠️ Alternative: Quick Launch Scripts

### Option 1: Use the batch files
Double-click these files in Windows Explorer:
- `launch_mvp.bat` - Starts the backend API
- `launch_frontend.bat` - Starts the React frontend

### Option 2: Manual PowerShell Commands

**For Backend (if it stops):**
```powershell
cd "C:\Users\PC\Desktop\data_scrapping pakwheels"
python simple_mvp_server.py
```

**For Frontend:**
```powershell
cd "C:\Users\PC\Desktop\data_scrapping pakwheels\frontend\mvp"
npm start
```

## 🌐 What You'll See

### Backend API Features
- **Authentication**: JWT-based secure login
- **Price Prediction**: AI-powered car price estimation
- **Recommendations**: Smart car suggestions based on budget
- **Market Analysis**: Advanced insights for dealers
- **Interactive Documentation**: Full API documentation

### Frontend Features
- **Professional UI**: Clean, modern React interface
- **User Dashboard**: Usage statistics and quick actions
- **Price Predictor**: Easy-to-use price estimation tool
- **Recommendations**: Smart car finder with filters
- **Market Analysis**: Advanced analytics (dealers only)

## 🔍 Testing the App

### 1. Test the API Directly
- Go to http://localhost:8000/docs
- Click on "POST /auth/login"
- Use demo credentials to get a token
- Use the token to test other endpoints

### 2. Test the Web Interface
- Go to http://localhost:3000
- Login with demo credentials
- Try predicting car prices
- Get recommendations based on budget
- Check market analysis (dealers only)

## 🚨 Troubleshooting

### If Backend Won't Start
```powershell
# Check if port 8000 is in use
netstat -an | findstr :8000

# If something is using port 8000, kill it or change the port
# in simple_mvp_server.py (line at the bottom: port=8000)
```

### If Frontend Won't Start
```powershell
# Make sure you're in the right directory
cd "C:\Users\PC\Desktop\data_scrapping pakwheels\frontend\mvp"

# Clear npm cache if needed
npm cache clean --force

# Delete node_modules and reinstall
rmdir node_modules /s
npm install
```

### If You See Connection Errors
- Make sure the backend is running on port 8000
- Check that frontend is configured to connect to localhost:8000
- Verify your firewall isn't blocking the connections

## 📊 What Each User Type Can Do

### Dealers (Premium Experience)
- ✅ Get detailed price predictions with market insights
- ✅ Access profit margin calculations
- ✅ View inventory turnover estimates
- ✅ Get comprehensive market analysis
- ✅ See demand scores and regional insights
- ✅ 1,000 API calls per day

### Resellers (Standard Experience)
- ✅ Get accurate price predictions
- ✅ Find cars within budget range
- ✅ See value recommendations
- ✅ Access basic market data
- ✅ 500 API calls per day

### Admins (Full Access)
- ✅ All features available
- ✅ System monitoring capabilities
- ✅ 10,000 API calls per day

## 🎉 You're Ready!

Once both the backend and frontend are running:
1. **Backend**: http://localhost:8000 (API + Documentation)
2. **Frontend**: http://localhost:3000 (Web Application)

**Your PakWheels ML API MVP is now fully operational!** 🚗✨

## 📞 Quick Help

If you need help:
1. Check the server logs in the PowerShell windows
2. Visit the health endpoint: http://localhost:8000/health
3. Use the interactive API docs: http://localhost:8000/docs
4. Try the demo credentials: http://localhost:8000/api/demo-credentials

**Happy testing!** 🎯
