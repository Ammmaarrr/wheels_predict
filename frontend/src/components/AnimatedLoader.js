import React from 'react';
import { motion } from 'framer-motion';
import { Box, Typography, CircularProgress } from '@mui/material';

const AnimatedLoader = ({ message = "Loading...", size = 40 }) => {
  const pulseVariants = {
    initial: { scale: 1, opacity: 0.7 },
    animate: {
      scale: [1, 1.2, 1],
      opacity: [0.7, 1, 0.7],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: "easeInOut"
      }
    }
  };

  const textVariants = {
    initial: { opacity: 0 },
    animate: {
      opacity: 1,
      transition: {
        delay: 0.3,
        duration: 0.5
      }
    }
  };

  return (
    <Box
      sx={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '200px',
        gap: 2
      }}
    >
      <motion.div
        variants={pulseVariants}
        initial="initial"
        animate="animate"
      >
        <CircularProgress 
          size={size} 
          sx={{ 
            color: 'primary.main',
            filter: 'drop-shadow(0 0 8px rgba(102, 126, 234, 0.3))'
          }} 
        />
      </motion.div>
      
      <motion.div
        variants={textVariants}
        initial="initial"
        animate="animate"
      >
        <Typography 
          variant="body1" 
          sx={{ 
            color: 'text.secondary',
            fontWeight: 500,
            textAlign: 'center'
          }}
        >
          {message}
        </Typography>
      </motion.div>
    </Box>
  );
};

export default AnimatedLoader;
