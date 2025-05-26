import express, { type Request, Response, NextFunction } from "express";
import { registerRoutes } from "./routes";
import { setupVite, serveStatic, log } from "./vite";
import { createProxyMiddleware } from 'http-proxy-middleware';

const app = express();
app.use(express.json());
app.use(express.urlencoded({ extended: false }));

// Add proxy middleware to forward API requests to the FastAPI backend with detailed logging
app.use('/api', createProxyMiddleware({ 
  target: 'http://localhost:8000',
  changeOrigin: true,
  pathRewrite: {
    '^/api': '', // Remove /api prefix when forwarding to FastAPI
  },
  onProxyReq: (proxyReq, req, res) => {
    // Log the request being proxied
    const body = req.body ? JSON.stringify(req.body) : 'no body';
    log(`Proxying ${req.method} request to: ${req.path}`);
    log(`Request headers: ${JSON.stringify(req.headers['content-type'] || 'none')}`);
    
    // For debugging content-type related issues
    if (req.method === 'POST') {
      if (req.headers['content-type']?.includes('application/x-www-form-urlencoded')) {
        log('Processing form-urlencoded data');
      }
    }
  },
  onProxyRes: (proxyRes, req, res) => {
    // Log proxy response
    log(`Received response from backend: ${proxyRes.statusCode} for ${req.method} ${req.path}`);
  },
  onError: (err, req, res) => {
    log(`Proxy error: ${err.message}`);
    res.status(500).json({ error: 'Proxy error', message: err.message });
  }
}));

app.use((req, res, next) => {
  const start = Date.now();
  const path = req.path;
  let capturedJsonResponse: Record<string, any> | undefined = undefined;

  const originalResJson = res.json;
  res.json = function (bodyJson, ...args) {
    capturedJsonResponse = bodyJson;
    return originalResJson.apply(res, [bodyJson, ...args]);
  };

  res.on("finish", () => {
    const duration = Date.now() - start;
    if (path.startsWith("/api")) {
      let logLine = `${req.method} ${path} ${res.statusCode} in ${duration}ms`;
      if (capturedJsonResponse) {
        logLine += ` :: ${JSON.stringify(capturedJsonResponse)}`;
      }

      if (logLine.length > 80) {
        logLine = logLine.slice(0, 79) + "…";
      }

      log(logLine);
    }
  });

  next();
});

(async () => {
  const server = await registerRoutes(app);

  app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
    const status = err.status || err.statusCode || 500;
    const message = err.message || "Internal Server Error";

    res.status(status).json({ message });
    throw err;
  });

  // importantly only setup vite in development and after
  // setting up all the other routes so the catch-all route
  // doesn't interfere with the other routes
  if (app.get("env") === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  // Use environment variable for port, fallback to 3001 if port 3000 is busy
  const port = process.env.FRONTEND_PORT ? parseInt(process.env.FRONTEND_PORT) : 3001;
  server.listen({
    port,
    host: "0.0.0.0",
    reusePort: true,
  }, () => {
    log(`serving on port ${port}`);
  });
})();
