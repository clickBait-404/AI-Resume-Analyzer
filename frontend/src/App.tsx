import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "framer-motion";

import { AuthProvider } from "./context/AuthContext";
import { ProtectedRoute } from "./components/ProtectedRoute";

import { LandingPage } from "./pages/LandingPage";
import { LoginPage } from "./pages/LoginPage";
import { RegisterPage } from "./pages/RegisterPage";
import { DashboardPage } from "./pages/DashboardPage";
import { AnalyzePage } from "./pages/AnalyzePage";
import { AnalysisResultPage } from "./pages/AnalysisResultPage";

function AnimatedRoutes() {
  const location = useLocation();

  return (
    <AnimatePresence mode="wait">
      <motion.div
  key={location.pathname}
  initial={{ opacity: 0.98 }}
  animate={{ opacity: 1 }}
  exit={{ opacity: 0.98 }}
  transition={{ duration: 0.15 }}
>
        <Routes location={location}>
          <Route path="/" element={<LandingPage />} />

          <Route path="/login" element={<LoginPage />} />

          <Route path="/register" element={<RegisterPage />} />

          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <DashboardPage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/analyze"
            element={
              <ProtectedRoute>
                <AnalyzePage />
              </ProtectedRoute>
            }
          />

          <Route
            path="/analysis/:id"
            element={
              <ProtectedRoute>
                <AnalysisResultPage />
              </ProtectedRoute>
            }
          />
        </Routes>
      </motion.div>
    </AnimatePresence>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AnimatedRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
