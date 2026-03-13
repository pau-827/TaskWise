import { AppBar, Toolbar, Typography, Box, IconButton, Button } from "@mui/material";
import AccountCircleIcon from "@mui/icons-material/AccountCircle";
import NotificationsIcon from "@mui/icons-material/Notifications";
import { Link, useLocation } from "react-router-dom";

export default function Header() {
  const location = useLocation();

  const navItems = [
    { label: "Tasks", path: "/tasks" },
    { label: "Journal", path: "/journal" },
    { label: "Calendar", path: "/calendar" },
    { label: "Settings", path: "/settings" }
  ];

  return (
    <AppBar position="static" color="transparent" elevation={0} sx={{ borderBottom: "1px solid #ddd" }}>
      <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
        
        {/* Left Logo */}
        <Typography variant="h6" sx={{ fontWeight: 600 }}>
          TaskWise
        </Typography>

        {/* Center Navigation */}
        <Box sx={{ display: "flex", gap: 2 }}>
          {navItems.map((item) => (
            <Button
              key={item.label}
              component={Link}
              to={item.path}
              color={location.pathname === item.path ? "primary" : "inherit"}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        {/* Right Profile */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Typography variant="body2">Guest</Typography>
          <IconButton>
            <AccountCircleIcon />
          </IconButton>
          <IconButton>
            <NotificationsIcon />
          </IconButton>
        </Box>

      </Toolbar>
    </AppBar>
  );
}
