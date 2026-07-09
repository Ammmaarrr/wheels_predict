# Light/Dark Mode Implementation

## Overview

The PakWheels ML Platform now supports light and dark mode switching with a modern design inspired by reactbits.dev.

## Features Implemented

### 1. Theme Context (`src/contexts/ThemeContext.js`)

- React Context for managing theme state
- Persistent theme preference using localStorage
- Theme factory function that creates light/dark themes
- Custom hook `useThemeMode()` for consuming theme context

### 2. Updated App Structure (`src/App.js`)

- Wrapped application with ThemeProvider
- Separated MUI ThemeProvider from custom ThemeProvider
- Dynamic theme switching support

### 3. Enhanced Layout (`src/components/Layout.js`)

- Added theme toggle button in the AppBar
- Updated styled components to be theme-responsive
- Light/Dark mode icons that switch based on current theme
- Proper color scheme for navigation and UI elements

### 4. Modern Color Palette (`src/theme.js`)

- Slate-based color scheme inspired by reactbits.dev
- Proper contrast ratios for accessibility
- Consistent color tokens for both light and dark modes
- Typography system with Inter font family

## Usage

### For Users

1. Look for the theme toggle button in the top-right corner of the AppBar
2. Click the moon icon to switch to dark mode
3. Click the sun icon to switch to light mode
4. Theme preference is automatically saved and persists across sessions

### For Developers

```javascript
import { useThemeMode } from './contexts/ThemeContext';

function MyComponent() {
  const { mode, theme, toggleMode } = useThemeMode();
  
  return (
    <Box sx={{ bgcolor: 'background.default', color: 'text.primary' }}>
      Current mode: {mode}
      <Button onClick={toggleMode}>Toggle Theme</Button>
    </Box>
  );
}
```

## Theme Colors

### Light Mode

- Background: `#ffffff`
- Paper: `#ffffff`
- Text Primary: `#0f172a`
- Text Secondary: `#64748b`
- Primary: `#0f172a`
- Secondary: `#6366f1`

### Dark Mode

- Background: `#0f172a`
- Paper: `#1e293b`
- Text Primary: `#f8fafc`
- Text Secondary: `#94a3b8`
- Primary: `#f8fafc`
- Secondary: `#6366f1`

## Files Modified

- `src/App.js` - Added ThemeProvider wrapper
- `src/components/Layout.js` - Added toggle button and theme responsiveness
- `src/theme.js` - Enhanced with action colors and theme factory
- `src/contexts/ThemeContext.js` - New theme context implementation

## Next Steps

1. Test the theme toggle functionality
2. Ensure all components are properly themed
3. Add theme-specific animations/transitions
4. Test accessibility in both modes
