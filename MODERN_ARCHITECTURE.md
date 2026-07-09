# 🚀 PakWheels ML Platform - Modern Architecture

A high-fidelity, modern web application for car price prediction and recommendations with beautiful animations and professional UI/UX.

## ✨ New Features

### 🎨 Modern UI/UX
- **Beautiful animations** using Framer Motion
- **High-fidelity design** with Material-UI
- **Responsive layout** that works on all devices
- **Professional color scheme** with gradients and shadows
- **Interactive components** with hover effects and transitions

### 🔧 Modern Architecture
- **React 18** with TypeScript support
- **FastAPI** backend with async/await
- **Material-UI** components with custom theming
- **Framer Motion** for smooth animations
- **Recharts** for beautiful data visualizations
- **Axios** for API communication

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React App     │    │   FastAPI       │    │   ML Models     │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Processing)  │
│   Port: 3000    │    │   Port: 8000    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Development Mode (Recommended)
```bash
# Windows
scripts\start_dev_servers.bat

# Linux/Mac
chmod +x scripts/start_dev_servers.sh
./scripts/start_dev_servers.sh
```

This will start:
- React development server at http://localhost:3000
- FastAPI server at http://localhost:8000
- API documentation at http://localhost:8000/docs

### Production Build
```bash
# Windows
scripts\start_modern_app.bat

# Linux/Mac
chmod +x scripts/start_modern_app.sh
./scripts/start_modern_app.sh
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose -f docker-compose.modern.yml up --build

# Access the application
# Frontend + Backend: http://localhost:8000
# API docs: http://localhost:8000/docs
```

## 📱 Features

### 🎯 Dashboard
- Real-time metrics with animated cards
- Beautiful charts and visualizations
- System health monitoring
- Quick action buttons

### 💰 Price Prediction
- Interactive form with modern inputs
- Real-time price prediction
- Feature selection with chips
- Animated results display

### 🎯 Recommendations
- Intelligent car recommendations
- Budget slider with instant feedback
- Preference-based filtering
- Beautiful car listings

### 🤖 AI Chat Assistant
- Real-time chat interface
- Context-aware responses
- Quick action buttons
- Typing indicators

### 📊 Monitoring Dashboard
- Model performance tracking
- Real-time alerts
- Drift detection
- Interactive charts

## 🎨 Design System

### Colors
- **Primary**: #667eea (Modern Blue)
- **Secondary**: #764ba2 (Purple)
- **Success**: #4caf50 (Green)
- **Warning**: #ff9800 (Orange)
- **Error**: #f44336 (Red)

### Typography
- **Font**: Inter (Modern, clean)
- **Weights**: 300, 400, 500, 600, 700
- **Sizes**: Responsive scale

### Animations
- **Fade in**: Smooth opacity transitions
- **Slide in**: Horizontal movement
- **Scale**: Hover effects
- **Stagger**: Sequential animations

## 🔧 Development

### Frontend Structure
```
frontend/
├── src/
│   ├── components/          # Reusable components
│   │   ├── Layout.js       # Main layout with navigation
│   │   └── MetricCard.js   # Animated metric cards
│   ├── pages/              # Main pages
│   │   ├── Dashboard.js    # Main dashboard
│   │   ├── PricePrediction.js
│   │   ├── Recommendations.js
│   │   ├── ChatAssistant.js
│   │   └── MonitoringDashboard.js
│   ├── services/           # API services
│   │   └── api.js         # API client
│   ├── theme.js           # Material-UI theme
│   ├── App.js             # Main app component
│   └── index.js           # Entry point
└── public/                 # Static assets
```

### Backend Structure
```
api/
├── main.py                 # FastAPI application
├── dev_server.py          # Development server
└── requirements.txt       # Python dependencies
```

## 🔌 API Endpoints

### System
- `GET /health` - Health check
- `GET /api/v1/status` - System status

### Predictions
- `POST /api/v1/predict` - Price prediction
- `POST /api/v1/recommend` - Car recommendations

### Chat
- `POST /api/v1/chat` - Chat with AI assistant

### Monitoring
- `GET /api/v1/monitoring/metrics` - Current metrics
- `GET /api/v1/monitoring/alerts` - Active alerts
- `POST /api/v1/monitoring/retrain` - Trigger retraining

## 🎭 Animations & Effects

### Card Animations
- **Hover lift**: Cards lift on hover
- **Shimmer effect**: Loading shimmer
- **Fade in**: Smooth entrance
- **Stagger**: Sequential loading

### Form Interactions
- **Input focus**: Smooth border transitions
- **Button hover**: Lift and shadow
- **Loading states**: Spinner animations
- **Success feedback**: Checkmark animation

### Data Visualization
- **Chart animations**: Smooth data transitions
- **Progress bars**: Animated progress
- **Metric counters**: Number counting up
- **Status indicators**: Color transitions

## 🚀 Performance Optimizations

### Frontend
- **Code splitting**: Lazy loading pages
- **Memoization**: React.memo for components
- **Debounced inputs**: Search optimization
- **Image optimization**: WebP format

### Backend
- **Async/await**: Non-blocking operations
- **Background tasks**: Long-running processes
- **Response caching**: Redis integration
- **Connection pooling**: Database optimization

## 📦 Dependencies

### Frontend
- React 18.2.0
- Material-UI 5.14.19
- Framer Motion 10.16.16
- Recharts 2.8.0
- Axios 1.6.2

### Backend
- FastAPI 0.104.1
- Uvicorn 0.24.0
- Pydantic 2.5.0
- Aiofiles 23.2.1

## 🔧 Environment Variables

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_NAME=PakWheels ML Platform
REACT_APP_VERSION=2.0.0
```

### Backend
```
ENVIRONMENT=development
DATABASE_URL=postgresql://user:pass@localhost/pakwheels
REDIS_URL=redis://localhost:6379
```

## 🎨 Customization

### Theme Customization
Edit `frontend/src/theme.js` to customize:
- Colors
- Typography
- Component styles
- Animation settings

### Adding New Components
1. Create component in `frontend/src/components/`
2. Add animations with Framer Motion
3. Style with Material-UI
4. Export and use in pages

## 🚀 Deployment

### Production Build
```bash
# Build React app
cd frontend
npm run build

# The built files will be served by FastAPI
cd ../api
python main.py
```

### Docker Production
```bash
docker-compose -f docker-compose.modern.yml up -d
```

## 🎯 Future Enhancements

- [ ] Dark mode support
- [ ] PWA capabilities
- [ ] Real-time notifications
- [ ] Advanced filtering
- [ ] Export functionality
- [ ] Mobile app version

## 🐛 Troubleshooting

### Common Issues
1. **Port conflicts**: Change ports in scripts
2. **Dependencies**: Run `npm install` and `pip install -r requirements.txt`
3. **API connection**: Check backend is running on port 8000

### Development Tips
- Use browser dev tools for debugging
- Check FastAPI docs at `/docs`
- Monitor console for errors
- Use React DevTools extension

---

🎉 **Welcome to the future of car price prediction!** 🚗💨
