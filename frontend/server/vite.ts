import express, { type Express } from "express";
import fs from "fs";
import path from "path";
import { createServer as createViteServer, createLogger } from "vite";
import { type Server } from "http";
import viteConfig from "../vite.config";
import { nanoid } from "nanoid";

const viteLogger = createLogger();

export function log(message: string, source = "express") {
  const formattedTime = new Date().toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
    second: "2-digit",
    hour12: true,
  });

  console.log(`${formattedTime} [${source}] ${message}`);
}

export async function setupVite(app: Express, server: Server) {
  const vite = await createViteServer({
    ...viteConfig,
    configFile: false,
    customLogger: {
      ...viteLogger,
      error: (msg, options) => {
        viteLogger.error(msg, options);
        process.exit(1);
      },
    },
    appType: "custom",
    server: {
      middlewareMode: true,
      hmr: {
        server,
      },
      watch: {
        usePolling: true,
        interval: 100
      },
      strictPort: false,
      host: true,
    }
  });

  app.use(vite.middlewares);
  
  // Add a catch-all route handler without using wildcards
  app.use((req, res, next) => {
    // Skip API routes
    if (req.path.startsWith('/api')) {
      return next();
    }

    const url = req.originalUrl;

    try {
      const clientTemplate = path.resolve(
        import.meta.dirname,
        "..",
        "client",
        "index.html",
      );

      // always reload the index.html file from disk incase it changes
      fs.promises.readFile(clientTemplate, "utf-8")
        .then((template) => {
          template = template.replace(
            `src="/src/main.tsx"`,
            `src="/src/main.tsx?v=${nanoid()}"`,
          );
          return vite.transformIndexHtml(url, template);
        })
        .then((page) => {
          res.status(200).set({ "Content-Type": "text/html" }).end(page);
        })
        .catch((e) => {
          vite.ssrFixStacktrace(e as Error);
          next(e);
        });
    } catch (e) {
      vite.ssrFixStacktrace(e as Error);
      next(e);
    }
  });
}

export function serveStatic(app: Express) {
  const distPath = path.resolve(import.meta.dirname, "public");

  if (!fs.existsSync(distPath)) {
    throw new Error(
      `Could not find the build directory: ${distPath}, make sure to build the client first`,
    );
  }

  app.use(express.static(distPath));

  // Add a catch-all route handler without using wildcards
  app.use((req, res) => {
    // Skip API routes
    if (req.path.startsWith('/api')) {
      return;
    }
    
    res.sendFile(path.resolve(distPath, "index.html"));
  });
}
