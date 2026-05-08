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
    <Box sx={{ minHeight: "100vh", bgcolor: bgColor, transition: "background 0.4s ease" }}>
      <Header />
      <Box
        sx={{
          width: "100%",
          maxWidth: "100%",

          px: {
            xs: 1.5,
            sm: 2,
            md: 3,
          },

          py: 3,

          flexGrow: 1,

          overflowX: "hidden",
        }}
      >
        <Outlet />
      </Box>
    </Box>
  );
}
