import React from 'react';
import { motion } from 'framer-motion';
import { Card, CardContent, Typography, Box } from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledCard = styled(Card)(({ theme }) => ({
  background: `linear-gradient(135deg, ${theme.palette.secondary.main} 0%, ${theme.palette.secondary.dark} 100%)`,
  color: 'white',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    background: 'rgba(255, 255, 255, 0.1)',
    transform: 'translateX(-100%)',
    transition: 'transform 0.6s ease',
  },
  '&:hover::before': {
    transform: 'translateX(100%)',
  },
  '&:hover': {
    transform: 'translateY(-4px)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)',
  },
}));

const MetricValue = styled(Typography)(({ theme }) => ({
  fontSize: '2.5rem',
  fontWeight: 700,
  lineHeight: 1,
  textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
}));

const TrendIndicator = styled(Box)(({ theme, trend }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(0.5),
  fontSize: '0.875rem',
  fontWeight: 500,
  color: trend === 'up' ? theme.palette.success.main : trend === 'down' ? theme.palette.error.main : theme.palette.warning.main,
  backgroundColor: 'rgba(255, 255, 255, 0.1)',
  padding: '4px 8px',
  borderRadius: 12,
  marginTop: theme.spacing(1),
}));

const MetricCard = ({ 
  title, 
  value, 
  subtitle, 
  trend, 
  trendValue, 
  icon, 
  color = 'primary', 
  delay = 0 
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return '↗️';
      case 'down':
        return '↘️';
      default:
        return '→';
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ scale: 1.02 }}
    >
      <StyledCard>
        <CardContent>
          <Box display="flex" justifyContent="space-between" alignItems="flex-start">
            <Box flex={1}>
              <Typography variant="body2" sx={{ opacity: 0.9, mb: 1 }}>
                {title}
              </Typography>
              <MetricValue variant="h2">{value}</MetricValue>
              {subtitle && (
                <Typography variant="body2" sx={{ opacity: 0.8, mt: 0.5 }}>
                  {subtitle}
                </Typography>
              )}
              {trend && trendValue && (
                <TrendIndicator trend={trend}>
                  {getTrendIcon()} {trendValue}
                </TrendIndicator>
              )}
            </Box>
            {icon && (
              <Box sx={{ opacity: 0.7 }}>
                {icon}
              </Box>
            )}
          </Box>
        </CardContent>
      </StyledCard>
    </motion.div>
  );
};

export default MetricCard;
