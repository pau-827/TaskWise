import { useContext } from "react";
import { AppBar, Toolbar, Typography, Box, IconButton, Button, Avatar, Tooltip } from "@mui/material";
import NotificationsIcon from "@mui/icons-material/Notifications";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { AppContext } from "../context/AppContext";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

export default function Header() {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useContext(AppContext);
  const { themeName } = useContext(ThemeContext);
  const headerBg = THEMES[themeName]?.custom?.headerBg ?? "#F8F6F4";
  const headerText = THEMES[themeName]?.custom?.headerText ?? "#1a3a40";

  const displayName = user?.user_metadata?.display_name || user?.email?.split("@")[0] || "Guest";
  const initials = displayName.slice(0, 2).toUpperCase();

  const navItems = [
    { label: "Tasks",    path: "/tasks" },
    { label: "Journal",  path: "/journal" },
    { label: "Calendar", path: "/calendar" },
    { label: "Recipes",  path: "/recipes" },
    { label: "Settings", path: "/settings" },
  ];

  const handleLogout = async () => {
    await logout();
    navigate("/");
  };

  return (
    <AppBar position="static" elevation={0}
      sx={{ borderBottom: "1px solid", borderColor: "divider", bgcolor: headerBg, color: headerText }}>
      <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>

        {/* Logo */}
        <Typography
          variant="h6"
          sx={{ fontWeight: 700, fontFamily: "'Playfair Display', serif", cursor: "pointer" }}
          onClick={() => navigate("/")}
        >
          TaskWise
        </Typography>

        {/* Nav */}
        <Box sx={{ display: "flex", gap: 1 }}>
          {navItems.map((item) => {
            const isActive = location.pathname === item.path;
            return (
              <Button
                key={item.label}
                component={Link}
                to={item.path}
                sx={{
                  borderRadius: 50,
                  px: 2,
                  fontWeight: isActive ? 600 : 400,
                  position: "relative",
                  "&::after": isActive ? {
                    content: '"✦"',
                    position: "absolute",
                    top: 2, left: "50%",
                    transform: "translateX(-50%)",
                    fontSize: 8,
                    color: "primary.main",
                  } : {},
                }}
                color={isActive ? "primary" : "inherit"}
              >
                {item.label}
              </Button>
            );
          })}
        </Box>

        {/* Right — user */}
        <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
          <Typography variant="body2" sx={{ opacity: 0.7 }}>{displayName}</Typography>

          <Tooltip title="Notifications">
            <IconButton size="small">
              <NotificationsIcon fontSize="small" />
            </IconButton>
          </Tooltip>

          <Tooltip title="Log out">
            <Avatar
              onClick={handleLogout}
              sx={{
                width: 32, height: 32, fontSize: 13,
                bgcolor: "primary.main", cursor: "pointer",
                "&:hover": { opacity: 0.85 },
              }}
            >
              {initials}
            </Avatar>
          </Tooltip>
        </Box>

      </Toolbar>
    </AppBar>
  );
}
