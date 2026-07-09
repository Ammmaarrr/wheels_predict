import React, { useState, useEffect } from 'react';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import { motion } from 'framer-motion';
import {
  Grid,
  Typography,
  Box,
  Card,
  CardContent,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  Chip,
  Alert,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
} from '@mui/material';
import {
  DirectionsCar as CarIcon,
  Star as StarIcon,
  LocationOn as LocationIcon,
} from '@mui/icons-material';
import { apiService } from '../services/api';

const Recommendations = () => {
  const [formData, setFormData] = useState({
    budget: 3500000,
    preferences: {
      make: '',
      fuel_type: '',
      transmission: '',
      body_type: '',
      age_preference: 'any',
    },
    location: '',
    max_results: 10,
  });
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [userInteracted, setUserInteracted] = useState(false);
  const [selectedCar, setSelectedCar] = useState(null);

  // Debug: Log when error state changes
  useEffect(() => {
    console.log('Error state changed:', error);
  }, [error]);

  // Clear any potential errors on component mount
  useEffect(() => {
    console.log('Recommendations component mounted, clearing errors');
    // Clear any cached errors
    sessionStorage.removeItem('recommendations_error');
    localStorage.removeItem('recommendations_error');
    setError(null);
  }, []);

  const makes = ['Toyota', 'Honda', 'Suzuki', 'Hyundai', 'Nissan', 'Mitsubishi', 'Mazda', 'Daihatsu'];
  const fuelTypes = ['Petrol', 'Diesel', 'Hybrid', 'Electric', 'CNG'];
  const transmissions = ['Manual', 'Automatic', 'CVT'];
  const bodyTypes = ['Sedan', 'Hatchback', 'SUV', 'Crossover', 'Coupe', 'Convertible'];
  const locations = ['Karachi', 'Lahore', 'Islamabad', 'Rawalpindi', 'Faisalabad', 'Multan', 'Hyderabad'];

  const handleInputChange = (field, value) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent],
          [child]: value,
        },
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [field]: value,
      }));
    }
    setError(null);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setUserInteracted(true);

    try {
      console.log('Sending recommendations request:', formData);
      const result = await apiService.getRecommendations(formData);
      console.log('Received recommendations result:', result);
      setRecommendations(result.recommendations || []);
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || 'Failed to get recommendations. Please try again.';
      setError(errorMessage);
      console.error('Recommendations error:', err);
      console.error('Error response:', err.response);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return new Intl.NumberFormat('en-PK', {
      style: 'currency',
      currency: 'PKR',
      minimumFractionDigits: 0,
    }).format(price);
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
          Car Recommendations
        </Typography>
        <Typography variant="body1" sx={{ color: 'text.secondary', fontSize: '1.125rem' }}>
          Find the perfect car based on your preferences and budget
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <motion.div variants={itemVariants}>
            <Card>
              <CardContent>
                <Typography variant="h6" sx={{ mb: 3 }}>
                  Your Preferences
                </Typography>
                <form onSubmit={handleSubmit}>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
                    <Box>
                      <Typography variant="subtitle1" sx={{ mb: 1 }}>
                        Budget: {formatPrice(formData.budget)}
                      </Typography>
                      <Slider
                        value={formData.budget}
                        onChange={(e, value) => handleInputChange('budget', value)}
                        min={500000}
                        max={10000000}
                        step={100000}
                        marks={[
                          { value: 500000, label: '5L' },
                          { value: 2500000, label: '25L' },
                          { value: 5000000, label: '50L' },
                          { value: 10000000, label: '1Cr' },
                        ]}
                      />
                    </Box>

                    <FormControl fullWidth>
                      <InputLabel>Preferred Make</InputLabel>
                      <Select
                        value={formData.preferences.make}
                        onChange={(e) => handleInputChange('preferences.make', e.target.value)}
                        label="Preferred Make"
                      >
                        <MenuItem value="">Any</MenuItem>
                        {makes.map(make => (
                          <MenuItem key={make} value={make}>{make}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    <FormControl fullWidth>
                      <InputLabel>Fuel Type</InputLabel>
                      <Select
                        value={formData.preferences.fuel_type}
                        onChange={(e) => handleInputChange('preferences.fuel_type', e.target.value)}
                        label="Fuel Type"
                      >
                        <MenuItem value="">Any</MenuItem>
                        {fuelTypes.map(type => (
                          <MenuItem key={type} value={type}>{type}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    <FormControl fullWidth>
                      <InputLabel>Transmission</InputLabel>
                      <Select
                        value={formData.preferences.transmission}
                        onChange={(e) => handleInputChange('preferences.transmission', e.target.value)}
                        label="Transmission"
                      >
                        <MenuItem value="">Any</MenuItem>
                        {transmissions.map(trans => (
                          <MenuItem key={trans} value={trans}>{trans}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    <FormControl fullWidth>
                      <InputLabel>Body Type</InputLabel>
                      <Select
                        value={formData.preferences.body_type}
                        onChange={(e) => handleInputChange('preferences.body_type', e.target.value)}
                        label="Body Type"
                      >
                        <MenuItem value="">Any</MenuItem>
                        {bodyTypes.map(type => (
                          <MenuItem key={type} value={type}>{type}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    <FormControl fullWidth>
                      <InputLabel>Location</InputLabel>
                      <Select
                        value={formData.location}
                        onChange={(e) => handleInputChange('location', e.target.value)}
                        label="Location"
                      >
                        <MenuItem value="">Any</MenuItem>
                        {locations.map(loc => (
                          <MenuItem key={loc} value={loc}>{loc}</MenuItem>
                        ))}
                      </Select>
                    </FormControl>

                    <Button
                      type="submit"
                      variant="contained"
                      size="large"
                      disabled={loading}
                      sx={{ textTransform: 'none' }}
                    >
                      {loading ? <CircularProgress size={24} /> : 'Get Recommendations'}
                    </Button>
                    
                    <Button
                      variant="outlined"
                      size="large"
                      onClick={async () => {
                        setUserInteracted(true);
                        try {
                          console.log('Testing API connection...');
                          const response = await apiService.healthCheck();
                          console.log('API health response:', response);
                          setError(null);
                          alert('API connection successful!');
                        } catch (error) {
                          console.error('API test failed:', error);
                          setError('API connection failed. Please check if the backend is running.');
                        }
                      }}
                      sx={{ textTransform: 'none' }}
                    >
                      Test Connection
                    </Button>
                  </Box>
                </form>
              </CardContent>
            </Card>
          </motion.div>
        </Grid>

        <Grid item xs={12} md={8}>
          <motion.div variants={itemVariants}>
            {error && userInteracted && (
              <Alert severity="error" sx={{ mb: 3 }}>
                {error}
                <Button 
                  size="small" 
                  onClick={() => setError(null)}
                  sx={{ ml: 2 }}
                >
                  Dismiss
                </Button>
              </Alert>
            )}

            {recommendations.length > 0 ? (
              <Card>
                <CardContent>
                  <Typography variant="h6" sx={{ mb: 3 }}>
                    Recommended Cars ({recommendations.length})
                  </Typography>
                  <List>
                    {recommendations.map((car, index) => (
                      <Box key={index}>
                        <ListItem alignItems="flex-start" button onClick={() => setSelectedCar(car)} sx={{ cursor: 'pointer' }}>
                          <ListItemAvatar>
                            <Avatar sx={{ bgcolor: 'primary.main' }}>
                              <CarIcon />
                            </Avatar>
                          </ListItemAvatar>
                          <ListItemText
                            primary={
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                <Typography variant="h6" component="span">
                                  {car.title || 'No Title'}
                                </Typography>
                                <Chip
                                  label={car.year}
                                  size="small"
                                  color="primary"
                                  variant="outlined"
                                />
                              </Box>
                            }
                            secondary={
                              <Box sx={{ mt: 1 }}>
                                <Typography variant="h6" sx={{ color: 'primary.main', mb: 1 }}>
                                  {formatPrice(car.price)}
                                </Typography>
                                <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                                  <Chip label={car.transmission || 'N/A'} size="small" />
                                  <Chip label={`${car.mileage || 0} km`} size="small" />
                                </Box>
                                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                  <LocationIcon fontSize="small" color="action" />
                                  <Typography variant="body2" color="text.secondary">
                                    {car.location || 'N/A'}
                                  </Typography>
                                  <StarIcon fontSize="small" color="primary" />
                                  <Typography variant="body2" color="text.secondary">
                                    {car.rating || 'N/A'}
                                  </Typography>
                                </Box>
                              </Box>
                            }
                          />
                        </ListItem>
                        {index < recommendations.length - 1 && <Divider />}
                      </Box>
                    ))}
      {/* Car Details Modal */}
      <Dialog open={!!selectedCar} onClose={() => setSelectedCar(null)} maxWidth="sm" fullWidth>
        <DialogTitle>Car Details</DialogTitle>
        <DialogContent>
          {selectedCar && (
            <Box>
              <Typography variant="h5" sx={{ mb: 2 }}>{selectedCar.title || 'No Title'}</Typography>
              <Typography>Year: {selectedCar.year}</Typography>
              <Typography>Price: {formatPrice(selectedCar.price)}</Typography>
              <Typography>Mileage: {selectedCar.mileage} km</Typography>
              <Typography>Location: {selectedCar.location}</Typography>
              <Typography>Transmission: {selectedCar.transmission || 'N/A'}</Typography>
              <Typography sx={{ mt: 2 }}>
                <a href={selectedCar.url} target="_blank" rel="noopener noreferrer">
                  View Original Ad
                </a>
              </Typography>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSelectedCar(null)} color="primary">Close</Button>
        </DialogActions>
      </Dialog>
                  </List>
                </CardContent>
              </Card>
            ) : (
              <Card>
                <CardContent sx={{ textAlign: 'center', py: 8 }}>
                  <CarIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
                  <Typography variant="h6" color="text.secondary">
                    No recommendations yet
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Set your preferences and get personalized car recommendations
                  </Typography>
                </CardContent>
              </Card>
            )}
          </motion.div>
        </Grid>
      </Grid>
    </motion.div>
  );
};

export default Recommendations;
