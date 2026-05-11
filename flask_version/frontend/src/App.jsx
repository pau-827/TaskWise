import { useState, useContext } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AppContext } from "./context/AppContext";

import AppShell from "./components/AppShell";
import LoadingScreen from "./components/LoadingScreen";

import LandingPage  from "./pages/LandingPage";
import LoginPage    from "./pages/LoginPage";
import SignupPage   from "./pages/SignupPage";
import Tasks        from "./pages/Tasks";
import Journal      from "./pages/Journal";
import Calendar     from "./pages/Calendar";
import Settings     from "./pages/Settings";
import Recipes      from "./pages/Recipes";

import AdminPanel   from "./admin/AdminPanel";

// Redirects to /login if not authenticated
function ProtectedRoute({ children }) {
  const { user, loading } = useContext(AppContext);
  if (loading) return null;
  return user ? children : <Navigate to="/login" />;
}

// Redirects to /tasks if not admin
function AdminRoute({ children }) {
  const { user, role, loading } = useContext(AppContext);
  if (loading) return null;
  if (!user)              return <Navigate to="/login" />;
  if (role !== "admin")   return <Navigate to="/tasks" />;
  return children;
}

function App() {
  const [appLoading, setAppLoading] = useState(true);
  if (appLoading) return <LoadingScreen onFinish={() => setAppLoading(false)} />;

  return (
    <BrowserRouter>
      <Routes>

        {/* Public routes */}
        <Route path="/"       element={<LandingPage />} />
        <Route path="/login"  element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />

        {/* Admin routes */}
        <Route path="/admin/panel" element={
          <AdminRoute><AdminPanel /></AdminRoute>
        } />

        {/* Protected user routes */}
        <Route element={
          <ProtectedRoute><AppShell /></ProtectedRoute>
        }>
          <Route path="/tasks"    element={<Tasks />} />
          <Route path="/journal"  element={<Journal />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/recipes"  element={<Recipes />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        {/* Fallback */}
        <Route path="*" element={<Navigate to="/" />} />

      </Routes>
    </BrowserRouter>
  );
}

export default App;
