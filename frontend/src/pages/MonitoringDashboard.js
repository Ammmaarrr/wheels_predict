import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import {
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  Alert,
  LinearProgress,
  Tabs,
  Tab,
  Paper,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
} from '@mui/icons-material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import MetricCard from '../components/MetricCard';
import { apiService } from '../services/api';

const MonitoringDashboard = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [metrics, setMetrics] = useState({
    accuracy: 0,
    precision: 0,
    recall: 0,
    f1_score: 0,
    drift_score: 0,
    prediction_count: 0,
    error_rate: 0,
    response_time: 0,
  });
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [performanceData, setPerformanceData] = useState([]);
  const [driftData, setDriftData] = useState([]);

  useEffect(() => {
    fetchMonitoringData();
    const interval = setInterval(fetchMonitoringData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchMonitoringData = async () => {
    try {
      setLoading(true);
      const [metricsData, alertsData, performanceData] = await Promise.all([
        apiService.getMonitoringMetrics(),
        apiService.getAlerts(),
        apiService.getPerformanceMetrics(),
      ]);

      setMetrics(metricsData);
      setAlerts(alertsData.alerts || []);

      // Generate mock performance data
      const mockPerformanceData = Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}:00`,
        accuracy: 0.85 + Math.random() * 0.1,
        predictions: Math.floor(50 + Math.random() * 100),
        response_time: 100 + Math.random() * 50,
      }));
      setPerformanceData(mockPerformanceData);

      // Generate mock drift data
      const mockDriftData = Array.from({ length: 30 }, (_, i) => ({
        day: `Day ${i + 1}`,
        drift_score: Math.random() * 0.5,
        threshold: 0.3,
      }));
      setDriftData(mockDriftData);
    } catch (error) {
      console.error('Error fetching monitoring data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
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
          Loading monitoring data...
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
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Model Monitoring
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Monitor your ML models' performance and health
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
              title="Model Accuracy"
              value={`${(metrics.accuracy * 100).toFixed(1)}%`}
              trend="up"
              trendValue="+2.1%"
              icon={<CheckCircleIcon />}
              delay={0}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Predictions Today"
              value={metrics.prediction_count.toLocaleString()}
              trend="up"
              trendValue="+15%"
              icon={<TrendingUpIcon />}
              delay={0.1}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Response Time"
              value={`${Math.round(metrics.response_time)}ms`}
              trend="down"
              trendValue="-5ms"
              icon={<SpeedIcon />}
              delay={0.2}
            />
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard
              title="Error Rate"
              value={`${(metrics.error_rate * 100).toFixed(2)}%`}
              trend="down"
              trendValue="-0.1%"
              icon={<WarningIcon />}
              delay={0.3}
            />
          </Grid>
        </Grid>
      </motion.div>

      {/* Tabs */}
      <motion.div variants={itemVariants}>
        <Paper sx={{ mb: 3 }}>
          <Tabs
            value={activeTab}
            onChange={handleTabChange}
            variant="fullWidth"
            sx={{ borderBottom: 1, borderColor: 'divider' }}
          >
            <Tab label="Performance" />
            <Tab label="Model Drift" />
            <Tab label="Detailed Metrics" />
          </Tabs>
        </Paper>
      </motion.div>

      {/* Tab Content */}
      <motion.div variants={itemVariants}>
        {activeTab === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card sx={{ height: 400 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Model Performance (24h)
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={performanceData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="hour" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="accuracy"
                        stroke="#667eea"
                        strokeWidth={3}
                        name="Accuracy"
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
                    Predictions per Hour
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <BarChart data={performanceData.slice(-12)}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="hour" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="predictions" fill="#764ba2" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {activeTab === 1 && (
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card sx={{ height: 400 }}>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Model Drift Detection (30 days)
                  </Typography>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={driftData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="day" />
                      <YAxis />
                      <Tooltip />
                      <Line
                        type="monotone"
                        dataKey="drift_score"
                        stroke="#f44336"
                        strokeWidth={3}
                        name="Drift Score"
                      />
                      <Line
                        type="monotone"
                        dataKey="threshold"
                        stroke="#ff9800"
                        strokeWidth={2}
                        strokeDasharray="5 5"
                        name="Threshold"
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {activeTab === 2 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Model Performance Metrics
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Accuracy:</Typography>
                      <Typography sx={{ fontWeight: 600 }}>
                        {(metrics.accuracy * 100).toFixed(2)}%
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Precision:</Typography>
                      <Typography sx={{ fontWeight: 600 }}>
                        {(metrics.precision * 100).toFixed(2)}%
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Recall:</Typography>
                      <Typography sx={{ fontWeight: 600 }}>
                        {(metrics.recall * 100).toFixed(2)}%
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>F1 Score:</Typography>
                      <Typography sx={{ fontWeight: 600 }}>
                        {(metrics.f1_score * 100).toFixed(2)}%
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    System Metrics
                  </Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Response Time:</Typography>
                      <Typography sx={{ fontWeight: 600 }}>
                        {Math.round(metrics.response_time)}ms
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Error Rate:</Typography>
                      <Typography sx={{ fontWeight: 600 }}>
                        {(metrics.error_rate * 100).toFixed(2)}%
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Drift Score:</Typography>
                      <Typography sx={{ fontWeight: 600 }}>
                        {metrics.drift_score.toFixed(3)}
                      </Typography>
                    </Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography>Total Predictions:</Typography>
                      <Typography sx={{ fontWeight: 600 }}>
                        {metrics.prediction_count.toLocaleString()}
                      </Typography>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}
      </motion.div>
    </motion.div>
  );
};

export default MonitoringDashboard;
