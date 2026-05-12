import { useContext, useState, useEffect } from "react";
import {
  AppBar,
  Toolbar,
  Typography,
  Box,
  IconButton,
  Button,
  Avatar,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogContentText,
  DialogActions,
} from "@mui/material";

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

  const [logoutOpen, setLogoutOpen] = useState(false);
  const [profileImage, setProfileImage] = useState("");

  const headerBg = THEMES[themeName]?.custom?.headerBg ?? "#F8F6F4";
  const headerText = THEMES[themeName]?.custom?.headerText ?? "#1a3a40";

  const displayName =
    user?.user_metadata?.display_name ||
    user?.email?.split("@")[0] ||
    "Guest";

  const initials = displayName.slice(0, 2).toUpperCase();

  useEffect(() => {
    if (!user?.id) return;

    const loadProfileImage = () => {
      const savedImage = localStorage.getItem(`profile_image_${user.id}`);
      setProfileImage(savedImage || "");
    };

    loadProfileImage();

    window.addEventListener("storage", loadProfileImage);

    return () => {
      window.removeEventListener("storage", loadProfileImage);
    };
  }, [user]);

  const navItems = [
    { label: "Tasks", path: "/tasks" },
    { label: "Journal", path: "/journal" },
    { label: "Calendar", path: "/calendar" },
    { label: "Recipes", path: "/recipes" },
    { label: "Settings", path: "/settings" },
  ];

  const handleLogout = async () => {
    setLogoutOpen(false);
    await logout();
    window.location.href = "/";
  };

  return (
    <>
      <AppBar
        position="static"
        elevation={0}
        sx={{
          borderBottom: "1px solid",
          borderColor: "divider",
          bgcolor: headerBg,
          color: headerText,
        }}
      >
        <Toolbar sx={{ display: "flex", justifyContent: "space-between" }}>
          <Typography
            variant="h6"
            sx={{
              fontWeight: 700,
              fontFamily: "'Playfair Display', serif",
              cursor: "pointer",
            }}
            onClick={() => navigate("/")}
          >
            TaskWise
          </Typography>

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
                    px: 2.5,
                    py: 0.6,
                    fontWeight: isActive ? 600 : 400,
                    color: isActive ? "primary.contrastText" : "inherit",
                    bgcolor: isActive ? "primary.main" : "transparent",
                    "&:hover": {
                      bgcolor: isActive
                        ? "primary.dark"
                        : "rgba(0,0,0,0.06)",
                    },
                    transition: "all 0.2s",
                  }}
                >
                  {item.label}
                </Button>
              );
            })}
          </Box>

          <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
            <Typography variant="body2" sx={{ opacity: 0.7 }}>
              {displayName}
            </Typography>

            <Tooltip title="Notifications">
              <IconButton size="small">
                <NotificationsIcon fontSize="small" />
              </IconButton>
            </Tooltip>

            <Tooltip title="Log out">
              <Avatar
                src={profileImage}
                onClick={() => setLogoutOpen(true)}
                sx={{
                  width: 32,
                  height: 32,
                  fontSize: 13,
                  bgcolor: "primary.main",
                  cursor: "pointer",
                  "&:hover": {
                    opacity: 0.85,
                  },
                }}
              >
                {!profileImage && initials}
              </Avatar>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      <Dialog
        open={logoutOpen}
        onClose={() => setLogoutOpen(false)}
        PaperProps={{
          sx: {
            borderRadius: 5,
            px: 2,
            py: 1,
            minWidth: 320,
          },
        }}
      >
        <DialogTitle
          sx={{
            fontWeight: 800,
            textAlign: "center",
            fontSize: 32,
            fontFamily: "'Playfair Display', serif",
          }}
        >
          Confirm Logout
        </DialogTitle>

        <DialogContent>
          <DialogContentText
            sx={{
              textAlign: "center",
              fontSize: 18,
              mt: 1,
            }}
          >
            Are you sure you want to log out?
          </DialogContentText>
        </DialogContent>

        <DialogActions
          sx={{
            pb: 3,
            px: 3,
            display: "flex",
            justifyContent: "center",
            gap: 2,
          }}
        >
          <Button
            variant="outlined"
            onClick={() => setLogoutOpen(false)}
            sx={{
              borderRadius: 50,
              minWidth: 100,
              fontWeight: 700,
              py: 1,
            }}
          >
            NO
          </Button>

          <Button
            color="error"
            variant="contained"
            onClick={handleLogout}
            sx={{
              borderRadius: 50,
              minWidth: 100,
              fontWeight: 700,
              py: 1,
            }}
          >
            YES
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}