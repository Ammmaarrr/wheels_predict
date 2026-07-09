# Wheels Predict ML API - MVP

## 🚗 Overview
A complete Machine Learning API and web application for car price prediction and market analysis, specifically designed for dealers and resellers in the Pakistani automotive market.

## 🎯 MVP Features

### For All Users:
- **User Authentication**: Secure login/registration system
- **Price Prediction**: AI-powered car price estimation
- **Smart Recommendations**: Personalized car suggestions based on budget and preferences
- **Dashboard**: Real-time usage statistics and market overview

### For Dealers (Premium Features):
- **Market Analysis**: Advanced market trends and insights
- **Profit Margins**: Estimated profit margins for inventory planning
- **Inventory Insights**: Turnover rates and demand scoring
- **Strategic Recommendations**: AI-powered business insights

### For Resellers:
- **Basic Analytics**: Essential market data
- **Price Comparisons**: Competitive pricing insights
- **Location-based Search**: Regional market analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup (FastAPI)
```bash
# Install Python dependencies
pip install -r requirements.mvp.txt

# Start the API server
python mvp_fastapi_server.py

# Or use the launch script
./launch_mvp.bat  # Windows
./launch_mvp.sh   # Linux/Mac
```

The API will be available at:
- **API Server**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Demo Credentials**: http://localhost:8000/api/demo-credentials

### Frontend Setup (React)
```bash
# Navigate to frontend directory
cd frontend/mvp

# Install dependencies
npm install

# Start development server
npm start

# Or use the launch script
./launch_frontend.bat  # Windows
```

The frontend will be available at:
- **Web App**: http://localhost:3000

## 👥 Demo Accounts

### Dealer Account
- **Email**: `dealer1@example.com`
- **Password**: `password123`
- **Features**: Full access including market analysis

### Reseller Account
- **Email**: `reseller1@example.com`
- **Password**: `password123`
- **Features**: Price prediction and recommendations

### Admin Account
- **Email**: `admin@pakwheels.com`
- **Password**: `admin123`
- **Features**: All features with elevated limits

## 📊 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - User login
- `GET /auth/profile` - Get user profile

### Core Features
- `POST /api/predict-price` - Car price prediction
- `POST /api/dealer-recommendations` - Smart recommendations
- `POST /api/market-analysis` - Market insights (dealers only)
- `GET /api/dashboard` - Dashboard data

### Public Endpoints
- `GET /` - API information
- `GET /health` - Health check
- `GET /api/demo-credentials` - Demo account details

## 🔧 Configuration

### API Limits
- **Dealers**: 1,000 calls per day
- **Resellers**: 500 calls per day
- **Admins**: 10,000 calls per day

### Security
- JWT token authentication
- bcrypt password hashing
- CORS protection
- Rate limiting

## 📱 User Interface

### Dashboard
- API usage statistics
- Market overview
- Quick actions
- User-specific insights

### Price Predictor
- Car details input form
- Instant price predictions
- Confidence scores
- Market insights (dealers)

### Recommendations
- Budget-based search
- Advanced filtering
- Profit margin analysis (dealers)
- Value scoring

### Market Analysis (Dealers Only)
- Price trend analysis
- Volume insights
- Inventory optimization
- Strategic recommendations

## 🛠️ Technical Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **Pydantic**: Data validation and serialization
- **JWT**: Secure authentication
- **bcrypt**: Password hashing
- **Pandas/NumPy**: Data processing
- **Scikit-learn**: Machine learning models

### Frontend
- **React**: Modern JavaScript library
- **Ant Design**: Professional UI components
- **Axios**: HTTP client
- **React Router**: Navigation
- **Styled Components**: Custom styling

### Data & ML
- **Enhanced Models**: Improved prediction accuracy
- **Feature Engineering**: Advanced car attributes
- **Recommendation Engine**: Collaborative filtering
- **Market Analysis**: Time series analysis

## 🔒 Security Features

### Authentication
- JWT-based token system
- Secure password hashing
- Session management
- Role-based access control

### API Security
- Rate limiting per user type
- Input validation
- CORS configuration
- Error handling

### Data Protection
- User data encryption
- Secure API endpoints
- Privacy-focused design

## 📈 Business Features

### For Dealers
- **Inventory Management**: Optimize stock based on market trends
- **Profit Optimization**: Identify high-margin opportunities
- **Market Timing**: Best times to buy/sell
- **Competitive Analysis**: Market positioning insights

### For Resellers
- **Quick Valuations**: Instant price estimates
- **Market Opportunities**: Undervalued car identification
- **Location Analysis**: Regional price differences
- **Trend Monitoring**: Market movement tracking

## 🚀 Deployment Options

### Local Development
```bash
# Backend
python mvp_fastapi_server.py

# Frontend
cd frontend/mvp && npm start
```

### Production Ready
- Docker support available
- Environment variable configuration
- SSL/HTTPS ready
- Load balancer compatible

## 📊 Monitoring & Analytics

### API Metrics
- Request/response times
- Error rates
- User activity
- Feature usage

### Business Metrics
- User engagement
- Feature adoption
- Revenue tracking
- Market insights

## 🔧 Customization

### Adding New Features
1. Update API endpoints in `mvp_fastapi_server.py`
2. Add new React components in `frontend/mvp/src/components/`
3. Update navigation in `Header.js`
4. Add routes in `App.js`

### Branding
- Update `public/index.html` for title/favicon
- Modify `App.css` for custom styling
- Update API title in FastAPI app configuration

## 📞 Support & Documentation

### API Documentation
- Interactive docs at `/docs`
- OpenAPI specification
- Example requests/responses
- Error code reference

### User Guides
- Getting started tutorial
- Feature walkthroughs
- Best practices
- Troubleshooting

## 🎯 Next Steps

### Phase 1 (Current MVP)
- ✅ User authentication
- ✅ Price prediction
- ✅ Recommendations
- ✅ Market analysis
- ✅ Professional UI

### Phase 2 (Enhanced Features)
- [ ] Real-time data integration
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] API marketplace
- [ ] Multi-language support

### Phase 3 (Scale)
- [ ] Enterprise features
- [ ] White-label solutions
- [ ] API partnerships
- [ ] Advanced ML models

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- PakWheels for market inspiration
- FastAPI community
- React ecosystem
- Open source contributors

---

**Ready to transform the automotive market? Start with our MVP today!** 🚗✨
