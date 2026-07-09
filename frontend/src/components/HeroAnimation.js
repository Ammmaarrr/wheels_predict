import React from 'react';
import { motion } from 'framer-motion';
import { Box, Typography, Button } from '@mui/material';
import { styled } from '@mui/material/styles';

const GlowingButton = styled(Button)(({ theme }) => ({
  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
  color: 'white',
  padding: '12px 32px',
  borderRadius: '25px',
  fontWeight: 600,
  fontSize: '1.1rem',
  textTransform: 'none',
  boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
  position: 'relative',
  overflow: 'hidden',
  '&::before': {
    content: '""',
    position: 'absolute',
    top: 0,
    left: '-100%',
    width: '100%',
    height: '100%',
    background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent)',
    transition: 'left 0.6s ease',
  },
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: '0 6px 20px rgba(102, 126, 234, 0.6)',
    '&::before': {
      left: '100%',
    },
  },
}));

const FloatingCard = styled(motion.div)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.1)',
  backdropFilter: 'blur(10px)',
  border: '1px solid rgba(255, 255, 255, 0.2)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  textAlign: 'center',
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.1)',
}));

const HeroAnimation = ({ title, subtitle, actionText, onAction }) => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.2,
      },
    },
  };

  const itemVariants = {
    hidden: { y: 30, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        duration: 0.6,
        ease: "easeOut",
      },
    },
  };

  const floatingVariants = {
    animate: {
      y: [-10, 10, -10],
      transition: {
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut",
      },
    },
  };

  return (
    <Box
      sx={{
        minHeight: '60vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      {/* Background Animation */}
      <motion.div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)',
        }}
        animate={{
          background: [
            'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)',
            'radial-gradient(circle at 80% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)',
            'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)',
          ],
        }}
        transition={{ duration: 10, repeat: Infinity }}
      />

      <motion.div
        variants={containerVariants}
        initial="hidden"
        animate="visible"
        style={{ zIndex: 1 }}
      >
        <FloatingCard
          variants={floatingVariants}
          animate="animate"
          style={{ maxWidth: '600px', margin: '0 auto' }}
        >
          <motion.div variants={itemVariants}>
            <Typography
              variant="h2"
              sx={{
                color: 'white',
                fontWeight: 700,
                mb: 2,
                textShadow: '0 2px 4px rgba(0,0,0,0.3)',
              }}
            >
              {title}
            </Typography>
          </motion.div>

          <motion.div variants={itemVariants}>
            <Typography
              variant="h6"
              sx={{
                color: 'rgba(255,255,255,0.9)',
                mb: 4,
                fontWeight: 400,
                lineHeight: 1.6,
              }}
            >
              {subtitle}
            </Typography>
          </motion.div>

          <motion.div variants={itemVariants}>
            <GlowingButton
              onClick={onAction}
              size="large"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              component={motion.button}
            >
              {actionText}
            </GlowingButton>
          </motion.div>
        </FloatingCard>
      </motion.div>
    </Box>
  );
};

export default HeroAnimation;
