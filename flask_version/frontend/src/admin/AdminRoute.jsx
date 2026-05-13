import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AppContext } from "../context/AppContext";

export default function AdminRoute({ children }) {
  const { user, role, loading } = useContext(AppContext);
  if (loading) return null;
  if (!user) return <Navigate to="/" />;
  if (role !== "admin") return <Navigate to="/whoops" />;
  return children;
}
