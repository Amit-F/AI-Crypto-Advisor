import { Navigate, Outlet } from "react-router-dom";
import { isLoggedIn } from "./auth";

// Simple auth gate for FE: no token -> no protected pages
export default function RequireAuth() {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  return <Outlet />;
}
