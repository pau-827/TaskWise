import { useState, useEffect } from "react";
import { AppContext } from "./AppContext";
import { supabase } from "../services/supabase";

export const AppProvider = ({ children }) => {
  const [user,          setUser]          = useState(null);
  const [role,          setRole]          = useState(null);
  const [loading,       setLoading]       = useState(true);
  const [notifications, setNotifications] = useState([]);

  const fetchRole = async (userId) => {
    try {
      const { data } = await supabase
        .from("profiles")
        .select("role")
        .eq("id", userId)
        .maybeSingle();
      const userRole = data?.role ?? "user";
      setRole(userRole);
      return userRole;
    } catch (err) {
      console.error("fetchRole error:", err);
      setRole("user");
      return "user";
    }
  };

  const redirectByRole = (userRole) => {
    const path = window.location.pathname;
    if (userRole === "admin" && path !== "/admin/panel") {
      window.location.replace("/admin/panel");
    } else if (userRole !== "admin" && path === "/auth/callback") {
      window.location.replace("/tasks");
    }
  };

  useEffect(() => {
    // Listen for auth state changes first
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      const u = session?.user ?? null;
      setUser(u);
      if (u) {
        const userRole = await fetchRole(u.id);
        // On any sign in event, redirect based on role
        if (event === "SIGNED_IN" || event === "TOKEN_REFRESHED" || event === "INITIAL_SESSION") {
          redirectByRole(userRole);
        }
      } else {
        setRole(null);
      }
      setLoading(false);
    });

    // Also check session on mount (catches hash-based OAuth tokens)
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      const u = session?.user ?? null;
      setUser(u);
      if (u) {
        const userRole = await fetchRole(u.id);
        // If we're stuck on auth/callback, redirect now
        if (window.location.pathname === "/auth/callback") {
          redirectByRole(userRole);
        }
      }
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const logout = async () => {
    await supabase.auth.signOut();
    setUser(null);
    setRole(null);
  };

  return (
    <AppContext.Provider value={{ user, setUser, role, loading, notifications, setNotifications, logout }}>
      {children}
    </AppContext.Provider>
  );
};
