import { createTheme } from '@mui/material/styles';

// Create theme function that takes mode parameter
export const createAppTheme = (mode = 'light') => createTheme({
  palette: {
    mode,
    primary: {
      main: mode === 'light' ? '#0f172a' : '#f8fafc',
      light: mode === 'light' ? '#334155' : '#e2e8f0',
      dark: mode === 'light' ? '#020617' : '#cbd5e1',
      contrastText: mode === 'light' ? '#ffffff' : '#0f172a',
    },
    secondary: {
      main: '#6366f1',
      light: '#818cf8',
      dark: '#4f46e5',
      contrastText: '#ffffff',
    },
    error: {
      main: '#ef4444',
      light: '#f87171',
      dark: '#dc2626',
    },
    warning: {
      main: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
    },
    info: {
      main: '#3b82f6',
      light: '#60a5fa',
      dark: '#2563eb',
    },
    success: {
      main: '#10b981',
      light: '#34d399',
      dark: '#059669',
    },
    background: {
      default: mode === 'light' ? '#ffffff' : '#0f172a',
      paper: mode === 'light' ? '#ffffff' : '#1e293b',
    },
    text: {
      primary: mode === 'light' ? '#0f172a' : '#f8fafc',
      secondary: mode === 'light' ? '#64748b' : '#94a3b8',
    },
    grey: {
      50: mode === 'light' ? '#f8fafc' : '#0f172a',
      100: mode === 'light' ? '#f1f5f9' : '#1e293b',
      200: mode === 'light' ? '#e2e8f0' : '#334155',
      300: mode === 'light' ? '#cbd5e1' : '#475569',
      400: mode === 'light' ? '#94a3b8' : '#64748b',
      500: mode === 'light' ? '#64748b' : '#94a3b8',
      600: mode === 'light' ? '#475569' : '#cbd5e1',
      700: mode === 'light' ? '#334155' : '#e2e8f0',
      800: mode === 'light' ? '#1e293b' : '#f1f5f9',
      900: mode === 'light' ? '#0f172a' : '#f8fafc',
    },
    divider: mode === 'light' ? '#e2e8f0' : '#334155',
    action: {
      hover: mode === 'light' ? '#f8fafc' : '#334155',
      selected: mode === 'light' ? '#f1f5f9' : '#475569',
      disabled: mode === 'light' ? '#cbd5e1' : '#64748b',
    },
  },
  typography: {
    fontFamily: '"Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif',
    h1: {
      fontSize: '3rem',
      fontWeight: 800,
      lineHeight: 1.1,
      letterSpacing: '-0.025em',
      color: mode === 'light' ? '#0f172a' : '#f8fafc',
    },
    h2: {
      fontSize: '2.25rem',
      fontWeight: 700,
      lineHeight: 1.2,
      letterSpacing: '-0.025em',
      color: mode === 'light' ? '#0f172a' : '#f8fafc',
    },
    h3: {
      fontSize: '1.875rem',
      fontWeight: 600,
      lineHeight: 1.3,
      letterSpacing: '-0.025em',
      color: mode === 'light' ? '#0f172a' : '#f8fafc',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.4,
      letterSpacing: '-0.025em',
      color: mode === 'light' ? '#0f172a' : '#f8fafc',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.5,
      color: mode === 'light' ? '#0f172a' : '#f8fafc',
    },
    h6: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.5,
      color: mode === 'light' ? '#0f172a' : '#f8fafc',
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.7,
      color: mode === 'light' ? '#475569' : '#cbd5e1',
    },
    body2: {
      fontSize: '0.875rem',
      lineHeight: 1.6,
      color: mode === 'light' ? '#64748b' : '#94a3b8',
    },
    button: {
      fontWeight: 500,
      letterSpacing: '0.025em',
    },
    caption: {
      fontSize: '0.75rem',
      lineHeight: 1.5,
      color: mode === 'light' ? '#64748b' : '#94a3b8',
    },
  },
  shape: {
    borderRadius: 8,
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          fontWeight: 500,
          padding: '12px 24px',
          fontSize: '0.875rem',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: `0 4px 12px ${mode === 'light' ? 'rgba(0, 0, 0, 0.15)' : 'rgba(0, 0, 0, 0.3)'}`,
            transform: 'translateY(-1px)',
          },
          transition: 'all 0.2s ease-in-out',
        },
        contained: {
          backgroundColor: mode === 'light' ? '#0f172a' : '#f8fafc',
          color: mode === 'light' ? '#ffffff' : '#0f172a',
          '&:hover': {
            backgroundColor: mode === 'light' ? '#1e293b' : '#e2e8f0',
            boxShadow: `0 4px 12px ${mode === 'light' ? 'rgba(15, 23, 42, 0.4)' : 'rgba(248, 250, 252, 0.4)'}`,
          },
        },
        containedSecondary: {
          backgroundColor: '#6366f1',
          color: '#ffffff',
          '&:hover': {
            backgroundColor: '#4f46e5',
            boxShadow: '0 4px 12px rgba(99, 102, 241, 0.4)',
          },
        },
        outlined: {
          borderColor: mode === 'light' ? '#e2e8f0' : '#334155',
          color: mode === 'light' ? '#475569' : '#cbd5e1',
          '&:hover': {
            borderColor: '#6366f1',
            backgroundColor: mode === 'light' ? '#f8fafc' : '#1e293b',
          },
        },
        text: {
          color: mode === 'light' ? '#475569' : '#cbd5e1',
          '&:hover': {
            backgroundColor: mode === 'light' ? '#f8fafc' : '#1e293b',
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: mode === 'light' ? '0 1px 3px rgba(0, 0, 0, 0.1)' : '0 1px 3px rgba(0, 0, 0, 0.3)',
          border: `1px solid ${mode === 'light' ? '#f1f5f9' : '#334155'}`,
          backgroundColor: mode === 'light' ? '#ffffff' : '#1e293b',
          '&:hover': {
            boxShadow: mode === 'light' ? '0 4px 12px rgba(0, 0, 0, 0.15)' : '0 4px 12px rgba(0, 0, 0, 0.4)',
            transform: 'translateY(-2px)',
          },
          transition: 'all 0.3s ease-in-out',
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          boxShadow: mode === 'light' ? '0 1px 3px rgba(0, 0, 0, 0.1)' : '0 1px 3px rgba(0, 0, 0, 0.3)',
          border: `1px solid ${mode === 'light' ? '#f1f5f9' : '#334155'}`,
          backgroundColor: mode === 'light' ? '#ffffff' : '#1e293b',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            backgroundColor: mode === 'light' ? '#ffffff' : '#1e293b',
            '& fieldset': {
              borderColor: mode === 'light' ? '#e2e8f0' : '#334155',
            },
            '&:hover fieldset': {
              borderColor: '#6366f1',
            },
            '&.Mui-focused fieldset': {
              borderColor: '#6366f1',
              borderWidth: '2px',
            },
          },
          '& .MuiInputLabel-root': {
            color: mode === 'light' ? '#64748b' : '#94a3b8',
            '&.Mui-focused': {
              color: '#6366f1',
            },
          },
          '& .MuiOutlinedInput-input': {
            color: mode === 'light' ? '#0f172a' : '#f8fafc',
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 6,
          fontWeight: 500,
          fontSize: '0.75rem',
          backgroundColor: mode === 'light' ? '#f1f5f9' : '#334155',
          color: mode === 'light' ? '#475569' : '#cbd5e1',
          '&:hover': {
            backgroundColor: mode === 'light' ? '#e2e8f0' : '#475569',
          },
        },
        filled: {
          backgroundColor: mode === 'light' ? '#f1f5f9' : '#334155',
          color: mode === 'light' ? '#475569' : '#cbd5e1',
        },
        outlined: {
          borderColor: mode === 'light' ? '#e2e8f0' : '#334155',
          color: mode === 'light' ? '#475569' : '#cbd5e1',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          '& .MuiAlert-message': {
            fontSize: '0.875rem',
          },
        },
      },
    },
    MuiLinearProgress: {
      styleOverrides: {
        root: {
          borderRadius: 4,
          height: 8,
          backgroundColor: mode === 'light' ? '#e2e8f0' : '#334155',
        },
      },
    },
    MuiSlider: {
      styleOverrides: {
        root: {
          color: '#6366f1',
          '& .MuiSlider-thumb': {
            width: 20,
            height: 20,
            backgroundColor: '#6366f1',
            '&:hover': {
              boxShadow: '0 0 0 8px rgba(99, 102, 241, 0.16)',
            },
          },
          '& .MuiSlider-track': {
            backgroundColor: '#6366f1',
          },
          '& .MuiSlider-rail': {
            backgroundColor: mode === 'light' ? '#e2e8f0' : '#334155',
          },
        },
      },
    },
    MuiSelect: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-notchedOutline': {
            borderColor: mode === 'light' ? '#e2e8f0' : '#334155',
          },
          '&:hover .MuiOutlinedInput-notchedOutline': {
            borderColor: '#6366f1',
          },
          '&.Mui-focused .MuiOutlinedInput-notchedOutline': {
            borderColor: '#6366f1',
          },
        },
      },
    },
    MuiMenu: {
      styleOverrides: {
        paper: {
          backgroundColor: mode === 'light' ? '#ffffff' : '#1e293b',
          border: `1px solid ${mode === 'light' ? '#f1f5f9' : '#334155'}`,
        },
      },
    },
    MuiMenuItem: {
      styleOverrides: {
        root: {
          color: mode === 'light' ? '#475569' : '#cbd5e1',
          '&:hover': {
            backgroundColor: mode === 'light' ? '#f8fafc' : '#334155',
          },
        },
      },
    },
  },
});

// Default theme (light mode)
const theme = createAppTheme('light');

export default theme;
