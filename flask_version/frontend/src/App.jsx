import { useState, useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppContext } from "./context/AppContext";

import AppShell from "./components/AppShell";
import LoadingScreen from "./components/LoadingScreen";

import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/LoginPage";
import SignupPage from "./pages/SignupPage";
import Tasks from "./pages/Tasks";
import Journal from "./pages/Journal";
import Calendar from "./pages/Calendar";
import Settings from "./pages/Settings";

// Redirects to /login if not authenticated
function ProtectedRoute({ children }) {
  const { user, loading } = useContext(AppContext);
  if (loading) return null; // wait for session check
  return user ? children : <Navigate to="/login" />;
}

function App() {
  const [appLoading, setAppLoading] = useState(true);

  if (appLoading) {
    return <LoadingScreen onFinish={() => setAppLoading(false)} />;
  }

  return (
    <BrowserRouter>
      <Routes>

        {/* Public routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Protected routes — require login */}
        <Route element={
          <ProtectedRoute>
            <AppShell />
          </ProtectedRoute>
        }>
          <Route path="/tasks" element={<Tasks />} />
          <Route path="/journal" element={<Journal />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
