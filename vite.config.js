import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  // Sub-path the app is served from in production (e.g. /sankalpam/)
  base: process.env.VITE_BASE || "/",
  server: {
    port: 3000,
    // Proxy API calls to backend in development
    proxy: {
      "/generate-sankalpam": "http://localhost:8000",
      "/download-pdf": "http://localhost:8000",
    },
  },
});
