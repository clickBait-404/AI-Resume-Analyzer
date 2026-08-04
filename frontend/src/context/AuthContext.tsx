import { createContext, useContext, useEffect, useRef, useState, type ReactNode } from "react";
import axios from "axios";
import client, { api, clearToken, getToken, setToken } from "../lib/api";
import type { User } from "../lib/types";

interface AuthContextValue {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Auto-logout after this many milliseconds of no user activity.
const INACTIVITY_TIMEOUT_MS = 15 * 60 * 1000; // 15 minutes

// Events that count as "the user is active" — reset the inactivity timer.
const ACTIVITY_EVENTS = ["mousemove", "mousedown", "keydown", "scroll", "touchstart"] as const;

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const inactivityTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // On load, validate any stored token against the real backend via
  // GET /auth/me rather than trusting a cached copy — an expired or
  // tampered token is caught here instead of surfacing as confusing
  // 401s later on a protected page.
  useEffect(() => {
    const token = getToken();
    if (!token) {
      setIsLoading(false);
      return;
    }

    client
      .get<User>("/auth/me")
      .then((res) => setUser(res.data))
      .catch((err) => {
        if (axios.isAxiosError(err) && err.response?.status === 401) {
          clearToken();
        }
        setUser(null);
      })
      .finally(() => setIsLoading(false));
  }, []);

  const persistSession = (token: string, u: User) => {
    setToken(token);
    setUser(u);
  };

  const login = async (email: string, password: string) => {
    const result = await api.auth.login(email, password);
    persistSession(result.access_token, result.user);
  };

  const register = async (email: string, password: string, fullName?: string) => {
    const result = await api.auth.register(email, password, fullName);
    persistSession(result.access_token, result.user);
  };

  const logout = () => {
    clearToken();
    setUser(null);
  };

  // Inactivity auto-logout: only runs while a user is logged in. Any
  // activity event resets the timer; if it ever fires, we log out.
  useEffect(() => {
    if (!user) {
      if (inactivityTimer.current) {
        clearTimeout(inactivityTimer.current);
        inactivityTimer.current = null;
      }
      return;
    }

    const resetTimer = () => {
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      inactivityTimer.current = setTimeout(() => {
        logout();
      }, INACTIVITY_TIMEOUT_MS);
    };

    resetTimer();
    ACTIVITY_EVENTS.forEach((event) => window.addEventListener(event, resetTimer));

    return () => {
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      ACTIVITY_EVENTS.forEach((event) => window.removeEventListener(event, resetTimer));
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user]);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within an AuthProvider");
  return ctx;
}
