// Test file to validate theme implementation
import React from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { ThemeProvider as MUIThemeProvider } from '@mui/material/styles';
import { CssBaseline, Box, Typography, Button } from '@mui/material';
import { useThemeMode } from './contexts/ThemeContext';

const TestTheme = () => {
  const { mode, theme, toggleMode } = useThemeMode();

  return (
    <MUIThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ p: 4, bgcolor: 'background.default', minHeight: '100vh' }}>
        <Typography variant="h4" color="text.primary" gutterBottom>
          Current Mode: {mode}
        </Typography>
        <Button variant="contained" onClick={toggleMode}>
          Toggle Theme
        </Button>
        <Box sx={{ mt: 2, p: 2, bgcolor: 'background.paper', borderRadius: 1 }}>
          <Typography variant="body1" color="text.secondary">
            This is a test of the theme system
          </Typography>
        </Box>
      </Box>
    </MUIThemeProvider>
  );
};

const App = () => {
  return (
    <ThemeProvider>
      <TestTheme />
    </ThemeProvider>
  );
};

export default App;
