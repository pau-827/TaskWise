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
        .from("profiles").select("role").eq("id", userId).maybeSingle();
      const userRole = data?.role ?? "user";
      setRole(userRole);
      return userRole;
    } catch {
      setRole("user");
      return "user";
    }
  };

  useEffect(() => {
    supabase.auth.getSession().then(async ({ data: { session } }) => {
      const u = session?.user ?? null;
      setUser(u);
      if (u) await fetchRole(u.id);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (_event, session) => {
      const u = session?.user ?? null;
      setUser(u);
      if (u) await fetchRole(u.id);
      else { setRole(null); }
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
