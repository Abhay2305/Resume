import { useState, useEffect, useCallback } from "react";
import { api } from "../services/api";
import { AuthContext } from "./AuthContext.context";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authToken, setAuthToken] = useState(() => localStorage.getItem("token"));
  const [sessionExpired, setSessionExpired] = useState(false);

  const isAuthenticated = !!authToken;

  const refreshUser = useCallback(async () => {
    if (!api.auth.isAuthenticated()) {
      setUser(null);
      setAuthToken(null);
      return;
    }
    try {
      const me = await api.auth.getMe();
      setUser(me);
      setSessionExpired(false);
    } catch {
      setUser(null);
      setAuthToken(null);
      setSessionExpired(true);
      api.auth.logout();
    }
  }, []);

  useEffect(() => {
    (async () => {
      await refreshUser();
      setLoading(false);
    })();
  }, [refreshUser]);

  // Check for token expiration on storage events (multi-tab support)
  useEffect(() => {
    const handleStorageChange = (e) => {
      if (e.key === "token" && !e.newValue) {
        setUser(null);
        setAuthToken(null);
        setSessionExpired(true);
      }
    };
    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  const login = useCallback(async (email, password, rememberMe = false) => {
    await api.auth.login(email, password, rememberMe);
    setAuthToken(localStorage.getItem("token"));
    await refreshUser();
  }, [refreshUser]);

  const register = useCallback(async (email, password, fullName) => {
    await api.auth.register(email, password, fullName);
    await api.auth.login(email, password);
    setAuthToken(localStorage.getItem("token"));
    await refreshUser();
  }, [refreshUser]);

  const loginWithGoogle = useCallback(async (credential) => {
    await api.auth.loginWithGoogle(credential);
    setAuthToken(localStorage.getItem("token"));
    await refreshUser();
  }, [refreshUser]);

  const logout = useCallback(() => {
    api.auth.logout();
    setUser(null);
    setAuthToken(null);
    setSessionExpired(false);
  }, []);

  const clearSessionExpired = useCallback(() => {
    setSessionExpired(false);
  }, []);

  const isAdmin = !!(user?.roles?.some((r) => r.name === "admin") || user?.is_superuser);

  const value = {
    user,
    loading,
    isAuthenticated,
    isAdmin,
    sessionExpired,
    login,
    register,
    loginWithGoogle,
    logout,
    refreshUser,
    clearSessionExpired,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
