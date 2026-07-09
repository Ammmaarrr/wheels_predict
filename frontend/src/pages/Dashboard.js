import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  Alert,
  LinearProgress,
  useTheme,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import MetricCard from '../components/MetricCard';
import { apiService } from '../services/api';

const Dashboard = () => {
  const theme = useTheme();
  const [metrics, setMetrics] = useState({
    totalPredictions: 0,
    accuracy: 0,
    systemHealth: 'healthy',
    activeModels: 0,
  });
  const [loading, setLoading] = useState(true);
  const [alerts, setAlerts] = useState([]);
  const [performanceData, setPerformanceData] = useState([]);

  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [status, monitoringMetrics, alertsData] = await Promise.all([
        apiService.getSystemStatus(),
        apiService.getMonitoringMetrics(),
        apiService.getAlerts(),
      ]);

      setMetrics({
        totalPredictions: monitoringMetrics.prediction_count || 0,
        accuracy: (monitoringMetrics.accuracy * 100).toFixed(1),
        systemHealth: status.system,
        activeModels: 3, // Assuming 3 models
      });

      setAlerts(alertsData.alerts || []);

      // Generate mock performance data
      const mockData = Array.from({ length: 12 }, (_, i) => ({
        month: `${i + 1}`,
        accuracy: 85 + Math.random() * 10,
        predictions: 1000 + Math.random() * 500,
      }));
      setPerformanceData(mockData);
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.5,
      },
    },
  };

  if (loading) {
    return (
      <Box sx={{ width: '100%', mt: 4 }}>
        <LinearProgress />
        <Typography variant="h6" sx={{ mt: 2, textAlign: 'center' }}>
          Loading dashboard...
        </Typography>
      </Box>
    );
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
    >
      <Box sx={{ mb: 4 }}>
        <Typography 
          variant="h3" 
          sx={{ 
            fontWeight: 800, 
            color: 'text.primary', 
            mb: 1,
            fontSize: { xs: '1.875rem', md: '2.25rem' }
          }}
        >
          Dashboard
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary', fontSize: '1.125rem' }}>
          Welcome to your Wheels Predict Platform
        </Typography>
      </Box>

      {/* Alerts */}
      {alerts.length > 0 && (
        <motion.div variants={itemVariants}>
          <Box sx={{ mb: 3 }}>
            {alerts.slice(0, 3).map((alert, index) => (
              <Alert
                key={index}
                severity={alert.type}
                sx={{ mb: 1 }}
                action={
                  <Button color="inherit" size="small">
                    View
                  </Button>
                }
              >
                {alert.message}
              </Alert>
            ))}
          </Box>
        </motion.div>
      )}

      {/* Metrics Cards */}
      <motion.div variants={itemVariants}>
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Total Predictions"
              value={metrics.totalPredictions.toLocaleString()}
              trend="up"
              trendValue="+12%"
              icon={<TrendingUpIcon />}
              delay={0}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Model Accuracy"
              value={`${metrics.accuracy}%`}
              trend="up"
              trendValue="+2.1%"
              icon={<SpeedIcon />}
              delay={0.1}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="System Health"
              value={metrics.systemHealth === 'healthy' ? 'Healthy' : 'Issues'}
              trend="neutral"
              icon={<CheckCircleIcon />}
              delay={0.2}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Active Models"
              value={metrics.activeModels}
              trend="neutral"
              icon={<WarningIcon />}
              delay={0.3}
            />
          </Grid>
        </Grid>
      </motion.div>

      {/* Performance Chart */}
      <motion.div variants={itemVariants}>
        <Grid container spacing={3}>
          <Grid item xs={12} md={8}>
            <Card sx={{ height: 400 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Model Performance Over Time
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={performanceData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line
                      type="monotone"
                      dataKey="accuracy"
                      stroke={theme.palette.secondary.main}
                      strokeWidth={3}
                      dot={{ fill: theme.palette.secondary.main, strokeWidth: 2, r: 4 }}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={4}>
            <Card sx={{ height: 400 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Quick Actions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    size="large"
                    sx={{ textTransform: 'none' }}
                    href="/predict"
                  >
                    Price Prediction
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    sx={{ textTransform: 'none' }}
                    href="/recommendations"
                  >
                    Get Recommendations
                  </Button>
                  <Button
                    variant="outlined"
                    size="large"
                    sx={{ textTransform: 'none' }}
                    href="/monitoring"
                  >
                    View Monitoring
                  </Button>
                  <Button
                    variant="text"
                    size="large"
                    sx={{ textTransform: 'none' }}
                    href="/chat"
                  >
                    Chat Assistant
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </motion.div>
    </motion.div>
  );
};

export default Dashboard;
