import React, { useState } from "react";
import { AppContext } from "./AppContext";

export const AppProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [notifications, setNotifications] = useState([]);

  const logout = () => {
    setUser(null);
  };

  return (
    <AppContext.Provider value={{ user, notifications, logout, setNotifications }}>
      {children}
    </AppContext.Provider>
  );
};