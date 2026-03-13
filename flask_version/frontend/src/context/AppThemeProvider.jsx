import { useState } from "react";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import { ThemeContext } from "./ThemeContext";
import { THEMES } from "../theme/themes";

export default function AppThemeProvider({ children }) {

  const [themeName, setThemeName] = useState("dark");

  const muiTheme = createTheme(THEMES[themeName]);

  return (
    <ThemeContext.Provider value={{ themeName, setThemeName }}>
      <ThemeProvider theme={muiTheme}>
        {children}
      </ThemeProvider>
    </ThemeContext.Provider>
  );
}
