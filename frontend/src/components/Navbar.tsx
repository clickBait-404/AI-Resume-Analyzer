
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
    <header
      className="
      sticky top-0 z-50
      border-b border-white/20
      bg-white/70
      backdrop-blur-xl
      shadow-[0_8px_32px_rgba(15,23,42,.04)]
    "
    >
      <div className="container-page flex h-20 items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-3">
          <div
            className="
            flex h-10 w-10 items-center justify-center
            rounded-2xl
            bg-gradient-to-br
            from-blue-600
            to-violet-600
            text-white
            font-bold
            shadow-lg
          "
          >
            R
          </div>

          <div>
            <h1 className="font-display text-xl font-bold tracking-tight text-slate-900">
              AI-Resume-Analyzer
            </h1>

            <p className="text-xs text-slate-500">
              ATS Resume Intelligence
            </p>
          </div>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-8">
          <Link
            to="/"
            className="text-sm font-medium text-slate-600 hover:text-slate-900 transition"
          >
            Home
          </Link>

          {user && (
            <>
              <Link
                to="/dashboard"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition"
              >
                Dashboard
              </Link>

              <Link
                to="/analyze"
                className="text-sm font-medium text-slate-600 hover:text-slate-900 transition"
              >
                Analyze Resume
              </Link>
            </>
          )}
        </nav>

        {/* Right Side */}
        <div className="flex items-center gap-3">
          {user ? (
            <>
              <div
                className="
                hidden sm:flex
                items-center
                rounded-full
                bg-slate-100
                px-4 py-2
                text-sm
                text-slate-600
              "
              >
                {user.email}
              </div>

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
                <button
                  className="
                  rounded-xl
                  bg-gradient-to-r
                  from-blue-600
                  to-violet-600
                  px-5
                  py-2.5
                  text-sm
                  font-semibold
                  text-white
                  shadow-lg
                  transition-all
                  duration-300
                  hover:scale-105
                  hover:shadow-xl
                "
                >
                  Get Started
                </button>
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
