import React, { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Divider,
  Chip,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  PriceChange as PriceIcon,
  TrendingUp as TrendingUpIcon,
  Speed as SpeedIcon,
} from '@mui/icons-material';
import { apiService } from '../services/api';

const PricePrediction = () => {
  const [formData, setFormData] = useState({
    make: '',
    model: '',
    year: new Date().getFullYear(),
    mileage: '',
    engine_capacity: '',
    transmission: '',
    location: '',
    features: [],
  });
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const makes = ['Toyota', 'Honda', 'Suzuki', 'Hyundai', 'Nissan', 'Mitsubishi', 'Mazda', 'Daihatsu'];
  const engineTypes = ['Petrol', 'Diesel', 'Hybrid', 'Electric', 'CNG'];
  const transmissions = ['Manual', 'Automatic', 'CVT'];
  const locations = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Hyderabad'];
  const availableFeatures = [
    'Air Conditioning',
    'Power Steering',
    'ABS',
    'Airbags',
    'Sunroof',
    'Alloy Wheels',
    'Navigation System',
    'Bluetooth',
    'Backup Camera',
    'Keyless Entry',
  ];

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value,
    }));
    setError(null);
  };

  const handleFeatureToggle = (feature) => {
    setFormData(prev => ({
      ...prev,
      features: prev.features.includes(feature)
        ? prev.features.filter(f => f !== feature)
        : [...prev.features, feature],
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Validate required fields
    if (!formData.make || !formData.model || !formData.year || !formData.mileage || !formData.engine_capacity || !formData.transmission || !formData.location) {
      setError('Please fill in all required fields');
      setLoading(false);
      return;
    }

    try {
      const requestData = {
        ...formData,
        mileage: parseInt(formData.mileage),
        engine_capacity: parseFloat(formData.engine_capacity),
        year: parseInt(formData.year),
      };
      console.log('Sending request data:', requestData);
      
      const result = await apiService.predictPrice(requestData);
      console.log('Received result:', result);
      setPrediction(result);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to predict price. Please try again.';
      setError(errorMessage);
      console.error('Prediction error:', err);
      console.error('Error response:', err.response);
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
          Price Prediction
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary', fontSize: '1.125rem' }}>
          Get accurate price predictions for your car
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <motion.div variants={itemVariants}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Vehicle Details
                </Typography>
                <form onSubmit={handleSubmit}>
                  <Grid container spacing={3}>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Make</InputLabel>
                        <Select
                          value={formData.make}
                          onChange={(e) => handleInputChange('make', e.target.value)}
                          label="Make"
                          required
                        >
                          {makes.map(make => (
                            <MenuItem key={make} value={make}>{make}</MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Model"
                        value={formData.model}
                        onChange={(e) => handleInputChange('model', e.target.value)}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Year"
                        type="number"
                        value={formData.year}
                        onChange={(e) => handleInputChange('year', parseInt(e.target.value))}
                        inputProps={{ min: 1990, max: new Date().getFullYear() }}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Mileage (km)"
                        type="number"
                        value={formData.mileage}
                        onChange={(e) => handleInputChange('mileage', e.target.value)}
                        inputProps={{ min: 0 }}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Engine Capacity (L)"
                        type="number"
                        value={formData.engine_capacity}
                        onChange={(e) => handleInputChange('engine_capacity', e.target.value)}
                        inputProps={{ min: 0.5, max: 5.0, step: 0.1 }}
                        required
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Transmission</InputLabel>
                        <Select
                          value={formData.transmission}
                          onChange={(e) => handleInputChange('transmission', e.target.value)}
                          label="Transmission"
                          required
                        >
                          {transmissions.map(trans => (
                            <MenuItem key={trans} value={trans}>{trans}</MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <FormControl fullWidth>
                        <InputLabel>Location</InputLabel>
                        <Select
                          value={formData.location}
                          onChange={(e) => handleInputChange('location', e.target.value)}
                          label="Location"
                          required
                        >
                          {locations.map(loc => (
                            <MenuItem key={loc} value={loc}>{loc}</MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="subtitle1" sx={{ mb: 2 }}>
                        Features
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {availableFeatures.map(feature => (
                          <Chip
                            key={feature}
                            label={feature}
                            clickable
                            color={formData.features.includes(feature) ? 'primary' : 'default'}
                            onClick={() => handleFeatureToggle(feature)}
                          />
                        ))}
                      </Box>
                    </Grid>
                    <Grid item xs={12}>
                      <Button
                        type="submit"
                        variant="contained"
                        size="large"
                        disabled={loading}
                        sx={{ textTransform: 'none' }}
                      >
                        {loading ? <CircularProgress size={24} /> : 'Predict Price'}
                      </Button>
                    </Grid>
                  </Grid>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={4}>
          <motion.div variants={itemVariants}>
            {error && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
              </Alert>
            )}
            
            {prediction && (
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    Price Prediction
                  </Typography>
                  <Box sx={{ textAlign: 'center', mb: 3 }}>
                    <PriceIcon sx={{ fontSize: 48, color: 'primary.main', mb: 1 }} />
                    <Typography variant="h4" sx={{ fontWeight: 700, color: 'primary.main' }}>
                      PKR {prediction.predicted_price?.toLocaleString()}
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      Predicted Price
                    </Typography>
                  </Box>
                  <Divider sx={{ my: 2 }} />
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Confidence:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {prediction.confidence}
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2">Timestamp:</Typography>
                    <Typography variant="body2" sx={{ fontWeight: 600 }}>
                      {new Date(prediction.timestamp).toLocaleTimeString()}
                    </Typography>
                  </Box>
                </CardContent>
              </Card>
            )}

            <Card sx={{ mt: 3 }}>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Tips for Better Predictions
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <TrendingUpIcon color="primary" />
                    <Typography variant="body2">
                      Accurate mileage improves prediction
                    </Typography>
                  </Box>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SpeedIcon color="primary" />
                    <Typography variant="body2">
                      Select all relevant features
                    </Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>
      </Grid>
    </motion.div>
  );
};

export default PricePrediction;
