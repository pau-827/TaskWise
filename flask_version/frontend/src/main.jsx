import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";

import AppThemeProvider from "./context/AppThemeProvider";

ReactDOM.createRoot(document.getElementById("root")).render(
  <AppThemeProvider>
    <App />
  </AppThemeProvider>
);
