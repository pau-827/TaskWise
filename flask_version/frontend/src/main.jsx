import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

import AppThemeProvider from "./context/AppThemeProvider";
import { AppProvider } from "./context/AppProvider";

ReactDOM.createRoot(document.getElementById("root")).render(
  <AppThemeProvider>
    <AppProvider>
      <App />
    </AppProvider>
  </AppThemeProvider>
);
