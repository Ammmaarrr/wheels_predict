import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider as MUIThemeProvider } from '@mui/material/styles';
import { CssBaseline } from '@mui/material';
import { ThemeProvider, useThemeMode } from './contexts/ThemeContext';
import Dashboard from './pages/Dashboard';
import PricePrediction from './pages/PricePrediction';
import Recommendations from './pages/Recommendations';
import ChatAssistant from './pages/ChatAssistant';
import MonitoringDashboard from './pages/MonitoringDashboard';
import Layout from './components/Layout';

function AppContent() {
  const { theme } = useThemeMode();
  
  return (
    <MUIThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/predict" element={<PricePrediction />} />
            <Route path="/recommendations" element={<Recommendations />} />
            <Route path="/chat" element={<ChatAssistant />} />
            <Route path="/monitoring" element={<MonitoringDashboard />} />
          </Routes>
        </Layout>
      </Router>
    </MUIThemeProvider>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;
