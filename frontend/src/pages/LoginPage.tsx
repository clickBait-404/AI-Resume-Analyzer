import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Sparkles, ShieldCheck, TrendingUp } from "lucide-react";

import { Navbar } from "../components/Navbar";
import { Button } from "../components/Button";
import { TextField } from "../components/TextField";
import { Card } from "../components/Card";
import { useAuth } from "../context/AuthContext";
import { extractErrorMessage } from "../lib/api";

export function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    setError(null);
    setIsSubmitting(true);

    try {
      await login(email, password);
      navigate("/dashboard");
    } catch (err) {
      setError(extractErrorMessage(err));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />

      <div className="flex-1">
        <div className="grid lg:grid-cols-2 min-h-[calc(100vh-80px)]">
          {/* Left Branding Section */}
          <div
            className="
              hidden
              lg:flex
              flex-col
              justify-center
              px-16
              relative
              overflow-hidden
              bg-gradient-to-br
              from-blue-600
              via-blue-700
              to-violet-700
              text-white
            "
          >
            <div className="relative z-10 max-w-lg">
              <div className="inline-flex items-center gap-2 rounded-full bg-white/10 px-4 py-2 text-sm backdrop-blur">
                <Sparkles size={16} />
                ATS Resume Intelligence
              </div>

              <h1 className="mt-8 text-5xl font-bold leading-tight">
                Land More Interviews With Better Resumes
              </h1>

              <p className="mt-6 text-lg text-blue-100 leading-relaxed">
                Analyze resumes, identify skill gaps,
                improve ATS compatibility and prepare
                for interviews with recruiter-grade insights.
              </p>

              <div className="mt-10 space-y-4">
                <div className="flex items-center gap-3">
                  <ShieldCheck size={20} />
                  <span>ATS Compatibility Analysis</span>
                </div>

                <div className="flex items-center gap-3">
                  <TrendingUp size={20} />
                  <span>Recruiter Feedback & Insights</span>
                </div>

                <div className="flex items-center gap-3">
                  <Sparkles size={20} />
                  <span>Skill Gap Recommendations</span>
                </div>
              </div>
            </div>

            <div
              className="
                absolute
                -bottom-24
                -right-24
                h-72
                w-72
                rounded-full
                bg-white/10
                blur-3xl
              "
            />
          </div>

          {/* Right Form Section */}
          <div className="flex items-center justify-center px-6 py-12">
            <Card className="w-full max-w-md p-10">
              <div className="text-center mb-8">
                <h1 className="text-4xl font-bold tracking-tight text-slate-900">
                  Welcome Back
                </h1>

                <p className="mt-3 text-slate-500">
                  Sign in to continue analyzing resumes.
                </p>
              </div>

              <form
                onSubmit={handleSubmit}
                className="flex flex-col gap-5"
                noValidate
              >
                <TextField
                  label="Email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                />

                <TextField
                  label="Password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                />

                {error && (
                  <div
                    role="alert"
                    className="
                      rounded-2xl
                      border
                      border-red-200
                      bg-red-50
                      text-red-700
                      px-4
                      py-3
                      text-sm
                    "
                  >
                    {error}
                  </div>
                )}

                <Button
                  type="submit"
                  variant="primary"
                  size="lg"
                  disabled={isSubmitting}
                  className="w-full"
                >
                  {isSubmitting
                    ? "Signing In..."
                    : "Sign In"}
                </Button>
              </form>

              <p className="mt-8 text-center text-sm text-slate-500">
                Don't have an account?{" "}
                <Link
                  to="/register"
                  className="
                    font-semibold
                    text-blue-600
                    hover:text-blue-700
                  "
                >
                  Create one
                </Link>
              </p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
