import { useContext } from "react";
import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";
import Header from "./Header";
import { ThemeContext } from "../context/ThemeContext";
import { THEMES } from "../theme/themes";

export default function AppShell() {
  const { themeName } = useContext(ThemeContext);
  const bgColor = THEMES[themeName]?.palette?.background?.default ?? "#f0f7f5";

  return (
    <Box sx={{
      minHeight: "100vh",
      minWidth: 900,
      bgcolor: bgColor,
      transition: "background 0.4s ease",
      overflowX: "auto",
    }}>
      <Header />
      <Box sx={{
        width: "100%",
        px: 3,
        py: 3,
        flexGrow: 1,
        boxSizing: "border-box",
      }}>
        <Outlet />
      </Box>
    </Box>
  );
}

