import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { Button } from "./Button";

export function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/");
  };

  return (
    <header className="border-b border-line bg-paper/90 backdrop-blur-sm sticky top-0 z-50">
      <div className="container-page flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="font-display text-xl font-semibold tracking-tight">Resumeter</span>
        </Link>

        <nav className="hidden md:flex items-center gap-8 text-sm text-slate">
          {user && (
            <>
              <Link to="/dashboard" className="hover:text-ink transition-colors">
                Dashboard
              </Link>
              <Link to="/analyze" className="hover:text-ink transition-colors">
                New analysis
              </Link>
            </>
          )}
        </nav>

        <div className="flex items-center gap-3">
          {user ? (
            <>
              <span className="hidden sm:inline text-sm text-slate">{user.email}</span>
              <Button variant="ghost" size="md" onClick={handleLogout}>
                Sign out
              </Button>
            </>
          ) : (
            <>
              <Link to="/login">
                <Button variant="ghost" size="md">
                  Sign in
                </Button>
              </Link>
              <Link to="/register">
                <Button variant="primary" size="md">
                  Get started
                </Button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
