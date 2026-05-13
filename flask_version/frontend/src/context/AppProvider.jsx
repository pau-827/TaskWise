import { useState, useEffect } from "react";
import { AppContext } from "./AppContext";
import { supabase } from "../services/supabase";

const ADMIN_EMAIL = "dueitsquad.taskwise@gmail.com";

export const AppProvider = ({ children }) => {
  const [user,          setUser]          = useState(null);
  const [role,          setRole]          = useState(null);
  const [loading,       setLoading]       = useState(true);
  const [notifications, setNotifications] = useState([]);

  const resolveRole = (u) => {
    const r = u?.email === ADMIN_EMAIL ? "admin" : "user";
    setRole(r);
    return r;
  };

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      const u = session?.user ?? null;
      setUser(u);
      resolveRole(u);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      const u = session?.user ?? null;
      setUser(u);
      if (u) resolveRole(u);
      else setRole(null);
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