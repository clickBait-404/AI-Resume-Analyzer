import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// When running inside Docker Compose, the backend is reachable at the
// service name "backend", not "localhost". When running the frontend
// directly on the host (npm run dev, no Docker), it's localhost.
// VITE_API_PROXY_TARGET lets either setup work without editing this file.
const proxyTarget = process.env.VITE_API_PROXY_TARGET || "http://localhost:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: proxyTarget,
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
    },
  },
});
