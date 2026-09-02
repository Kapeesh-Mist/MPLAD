import React, { createContext, useCallback, useEffect, useState } from "react";
import { User } from "../types";
import { fetchCurrentUser, login as loginRequest } from "../services/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

export const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  error: null,
  login: async () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const token = localStorage.getItem("nigraani_token");
    if (!token) {
      setLoading(false);
      return;
    }
    fetchCurrentUser()
      .then(setUser)
      .catch(() => localStorage.removeItem("nigraani_token"))
      .finally(() => setLoading(false));
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    setError(null);
    try {
      const { user: loggedInUser, token } = await loginRequest(email, password);
      localStorage.setItem("nigraani_token", token);
      setUser(loggedInUser);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unable to sign in. Check your credentials.");
      throw err;
    }
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("nigraani_token");
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, error, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}
