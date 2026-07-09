import React from 'react';
import { motion } from 'framer-motion';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Box, 
  Button, 
  Container,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { 
  Dashboard as DashboardIcon,
  PriceChange as PriceIcon,
  Recommend as RecommendIcon,
  Chat as ChatIcon,
  Monitor as MonitoringIcon,
  Menu as MenuIcon,
  LightMode as LightModeIcon,
  DarkMode as DarkModeIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { Link, useLocation } from 'react-router-dom';
import { useThemeMode } from '../contexts/ThemeContext';

const drawerWidth = 240;

const StyledAppBar = styled(AppBar)(({ theme }) => ({
  background: theme.palette.background.paper,
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
  backdropFilter: 'blur(10px)',
  borderBottom: `1px solid ${theme.palette.divider}`,
  color: theme.palette.text.primary,
}));

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: drawerWidth,
    boxSizing: 'border-box',
    background: theme.palette.background.paper,
    border: 'none',
    borderRight: `1px solid ${theme.palette.divider}`,
    boxShadow: 'none',
  },
}));

const StyledListItem = styled(ListItem)(({ theme, active }) => ({
  borderRadius: '8px',
  margin: '2px 12px',
  padding: '12px 16px',
  cursor: 'pointer',
  transition: 'all 0.2s ease',
  background: active ? theme.palette.secondary.main : 'transparent',
  color: active ? theme.palette.secondary.contrastText : theme.palette.text.secondary,
  '&:hover': {
    background: active ? theme.palette.secondary.dark : theme.palette.action.hover,
    color: active ? theme.palette.secondary.contrastText : theme.palette.text.primary,
    transform: 'translateX(2px)',
  },
}));

const MainContent = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  marginLeft: drawerWidth,
  background: theme.palette.background.default,
  minHeight: '100vh',
  [theme.breakpoints.down('md')]: {
    marginLeft: 0,
  },
}));

const menuItems = [
  { text: 'Dashboard', icon: <DashboardIcon />, path: '/' },
  { text: 'Price Prediction', icon: <PriceIcon />, path: '/predict' },
  { text: 'Recommendations', icon: <RecommendIcon />, path: '/recommendations' },
  { text: 'Chat Assistant', icon: <ChatIcon />, path: '/chat' },
  { text: 'Monitoring', icon: <MonitoringIcon />, path: '/monitoring' },
];

const Layout = ({ children }) => {
  const theme = useTheme();
  const { mode, toggleMode } = useThemeMode();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const location = useLocation();
  const [mobileOpen, setMobileOpen] = React.useState(false);

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const drawer = (
    <Box sx={{ mt: 2 }}>
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="h6" sx={{ fontWeight: 800, color: theme.palette.text.primary, fontSize: '1.125rem' }}>
          Wheels Predict
        </Typography>
        <Typography variant="body2" sx={{ color: theme.palette.text.secondary, mt: 0.5, fontSize: '0.75rem' }}>
          Platform
        </Typography>
      </Box>
      <List>
        {menuItems.map((item, index) => (
          <motion.div
            key={item.text}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <StyledListItem
              component={Link}
              to={item.path}
              active={location.pathname === item.path}
              onClick={() => isMobile && setMobileOpen(false)}
            >
              <ListItemIcon sx={{ 
                color: location.pathname === item.path ? theme.palette.secondary.contrastText : theme.palette.text.secondary,
                minWidth: 40 
              }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text}
                primaryTypographyProps={{ fontWeight: 500 }}
              />
            </StyledListItem>
          </motion.div>
        ))}
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <StyledAppBar position="fixed" sx={{ zIndex: theme.zIndex.drawer + 1 }}>
        <Toolbar>
          {isMobile && (
            <IconButton
              color="inherit"
              aria-label="open drawer"
              edge="start"
              onClick={handleDrawerToggle}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
          )}
          <Typography variant="h6" sx={{ flexGrow: 1, fontWeight: 700, color: theme.palette.text.primary }}>
            Wheels Predict Platform
          </Typography>
          
          <IconButton
            color="inherit"
            onClick={toggleMode}
            sx={{ 
              mr: 2,
              color: theme.palette.text.secondary,
              '&:hover': {
                backgroundColor: theme.palette.action.hover,
              }
            }}
            title={`Switch to ${mode === 'light' ? 'dark' : 'light'} mode`}
          >
            {mode === 'light' ? <DarkModeIcon /> : <LightModeIcon />}
          </IconButton>
          
          <Button 
            color="inherit" 
            sx={{ 
              textTransform: 'none', 
              color: theme.palette.text.secondary,
              '&:hover': {
                backgroundColor: theme.palette.action.hover,
              }
            }}
          >
            Profile
          </Button>
        </Toolbar>
      </StyledAppBar>

      <Box
        component="nav"
        sx={{ width: { md: drawerWidth }, flexShrink: { md: 0 } }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{ keepMounted: true }}
            sx={{
              display: { xs: 'block', md: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
        ) : (
          <StyledDrawer variant="permanent" open>
            <Toolbar />
            {drawer}
          </StyledDrawer>
        )}
      </Box>

      <MainContent component="main">
        <Toolbar />
        <Container maxWidth="xl" sx={{ mt: 2 }}>
          {children}
        </Container>
      </MainContent>
    </Box>
  );
};

export default Layout;
