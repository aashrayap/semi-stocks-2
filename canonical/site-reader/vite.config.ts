import { fileURLToPath } from "node:url";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

const readerDir = fileURLToPath(new URL(".", import.meta.url));
const siteDataDir = fileURLToPath(new URL("../site-data", import.meta.url));

export default defineConfig({
  plugins: [react()],
  server: {
    fs: {
      allow: [readerDir, siteDataDir]
    }
  },
  build: {
    outDir: "dist",
    emptyOutDir: true
  }
});
