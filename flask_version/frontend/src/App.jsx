import { useState, useContext, useEffect } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Box, CircularProgress } from "@mui/material";
import { AppContext } from "./context/AppContext";
import { supabase } from "./services/supabase";

import AppShell      from "./components/AppShell";
import LoadingScreen from "./components/LoadingScreen";

import LandingPage   from "./pages/LandingPage";
import LoginPage     from "./pages/LoginPage";
import SignupPage    from "./pages/SignupPage";
import Tasks         from "./pages/Tasks";
import Journal       from "./pages/Journal";
import Calendar      from "./pages/Calendar";
import Settings      from "./pages/Settings";
import Recipes       from "./pages/Recipes";

import AdminLogin    from "./admin/AdminLogin";
import AdminPanel    from "./admin/AdminPanel";
import AdminRoute    from "./admin/AdminRoute";

// Handles admin Google OAuth redirect
function AdminCallback() {
  useEffect(() => {
    const check = async () => {
      await new Promise(r => setTimeout(r, 1500));
      const { data: { session } } = await supabase.auth.getSession();
      if (!session?.user) { window.location.replace("/whoops"); return; }
      const { data: profile } = await supabase
        .from("profiles").select("role").eq("id", session.user.id).maybeSingle();
      if (profile?.role === "admin") {
        window.location.replace("/admin/panel");
      } else {
        // Not admin — sign them out and redirect to the quirky page
        await supabase.auth.signOut();
        window.location.replace("/whoops");
      }
    };
    check();
  }, []);

  return (
    <Box sx={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", minHeight: "100vh", gap: 2 }}>
      <CircularProgress />
      <Box sx={{ fontSize: 14, color: "#7aaa97" }}>Verifying credentials...</Box>
    </Box>
  );
}

// Funny "not supposed to be here" page for non-admins who try the admin login
function Whoops() {
  return (
    <Box sx={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 2, bgcolor: "#f0f7f5", fontFamily: "'DM Sans', sans-serif" }}>
      <Box sx={{ fontSize: 64 }}>🚨</Box>
      <Box sx={{ fontSize: 22, fontWeight: 700, color: "#1a4a3a", fontFamily: "'Playfair Display', serif" }}>
        That's a no.
      </Box>
      <Box sx={{ fontSize: 14, color: "#7aaa97", textAlign: "center", maxWidth: 320 }}>
        You are not authorized to access this area. This incident may be logged.
      </Box>
      <button
        onClick={() => window.location.replace("/")}
        style={{ marginTop: 8, padding: "10px 28px", borderRadius: 50, border: "none", background: "#4a9b82", color: "#fff", cursor: "pointer", fontSize: 14, fontFamily: "inherit", fontWeight: 500 }}>
        Take me home
      </button>
    </Box>
  );
}

function ProtectedRoute({ children }) {
  const { user, loading } = useContext(AppContext);
  if (loading) return null;
  return user ? children : <Navigate to="/login" />;
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
        <Route path="/whoops"              element={<Whoops />} />
        <Route path="/admin"               element={<AdminLogin />} />
        <Route path="/auth/admin-callback" element={<AdminCallback />} />
        <Route path="/admin/panel"         element={<AdminRoute><AdminPanel /></AdminRoute>} />

        {/* Protected user routes */}
        <Route element={<ProtectedRoute><AppShell /></ProtectedRoute>}>
          <Route path="/tasks"    element={<Tasks />} />
          <Route path="/journal"  element={<Journal />} />
          <Route path="/calendar" element={<Calendar />} />
          <Route path="/recipes"  element={<Recipes />} />
          <Route path="/settings" element={<Settings />} />
        </Route>

        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
