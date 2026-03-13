import { Box } from "@mui/material";
import { Outlet } from "react-router-dom";
import Header from "./Header";

export default function AppShell() {
  return (
    <Box sx={{ minHeight: "100vh" }}>

      <Header />

      <Box sx={{ width: "100%", px: 4, py: 3 }}>
        <Outlet />
      </Box>

    </Box>
  );
}
