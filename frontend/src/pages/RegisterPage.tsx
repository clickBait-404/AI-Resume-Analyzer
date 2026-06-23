import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import {
  Sparkles,
  CheckCircle,
  ShieldCheck,
  Rocket,
} from "lucide-react";

import { Navbar } from "../components/Navbar";
import { Button } from "../components/Button";
import { TextField } from "../components/TextField";
import { Card } from "../components/Card";
import { useAuth } from "../context/AuthContext";
import { extractErrorMessage } from "../lib/api";

const MIN_PASSWORD_LENGTH = 8;

export function RegisterPage() {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const [fieldError, setFieldError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    setError(null);
    setFieldError(null);

    if (password.length < MIN_PASSWORD_LENGTH) {
      setFieldError(
        `Password must be at least ${MIN_PASSWORD_LENGTH} characters.`
      );
      return;
    }

    setIsSubmitting(true);

    try {
      await register(
        email,
        password,
        fullName || undefined
      );

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
          {/* Left Branding Panel */}
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
                Start Optimizing Your Resume Today
              </h1>

              <p className="mt-6 text-lg text-blue-100 leading-relaxed">
                Create your account and unlock ATS analysis,
                recruiter insights, interview preparation,
                and personalized career recommendations.
              </p>

              <div className="mt-10 space-y-4">
                <div className="flex items-center gap-3">
                  <CheckCircle size={20} />
                  <span>ATS Score Breakdown</span>
                </div>

                <div className="flex items-center gap-3">
                  <ShieldCheck size={20} />
                  <span>Recruiter Simulation</span>
                </div>

                <div className="flex items-center gap-3">
                  <Rocket size={20} />
                  <span>Career Growth Roadmaps</span>
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
                  Create Account
                </h1>

                <p className="mt-3 text-slate-500">
                  Start improving your ATS score today.
                </p>
              </div>

              <form
                onSubmit={handleSubmit}
                className="flex flex-col gap-5"
                noValidate
              >
                <TextField
                  label="Full Name"
                  type="text"
                  autoComplete="name"
                  value={fullName}
                  onChange={(e) =>
                    setFullName(e.target.value)
                  }
                />

                <TextField
                  label="Email"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) =>
                    setEmail(e.target.value)
                  }
                />

                <TextField
                  label="Password"
                  type="password"
                  autoComplete="new-password"
                  required
                  minLength={MIN_PASSWORD_LENGTH}
                  value={password}
                  onChange={(e) =>
                    setPassword(e.target.value)
                  }
                  error={fieldError || undefined}
                  helperText={
                    !fieldError
                      ? `Minimum ${MIN_PASSWORD_LENGTH} characters`
                      : undefined
                  }
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
                    ? "Creating Account..."
                    : "Create Account"}
                </Button>
              </form>

              <p className="mt-8 text-center text-sm text-slate-500">
                Already have an account?{" "}
                <Link
                  to="/login"
                  className="
                    font-semibold
                    text-blue-600
                    hover:text-blue-700
                  "
                >
                  Sign In
                </Link>
              </p>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}