const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');

const app = express();
const PORT = process.env.PORT || 3333;

// Users service rate limiting configuration
const usersLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 10,                  // Limit each IP to 10 requests every 15 minutes
  message: {                // Message to send when the limit is exceeded
    status: 429,
    message: 'Too many requests to users service. Please try again later.'
  }
});

// Game service rate limiting configuration
const gamesLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 20,                  // Limit each IP to 20 requests every 15 minutes
  message: {                // Message to send when the limit is exceeded
    status: 429,
    message: 'Too many requests to games service. Please try again later.'
  }
});

// Proxy configuration
const usersServiceProxy = createProxyMiddleware({
  target: 'http://users:5000',
  changeOrigin: true,
});

const gameServiceProxy = createProxyMiddleware({
  target: 'http://game:5111',
  changeOrigin: true,
});

// Routes for users service with rate limiter
app.use('/users/register', usersLimiter, usersServiceProxy);
app.use('/users/login', usersLimiter, usersServiceProxy);

// Routes for game service with rate limiter
app.use('/lobby', gamesLimiter, gameServiceProxy);
app.use('/lobby/create', gamesLimiter, gameServiceProxy);
app.use('/lobby/:id/join', gamesLimiter, gameServiceProxy);
app.use('/lobby/:id/leave', gamesLimiter, gameServiceProxy);

// Default route
app.get('/', (req, res) => {
  res.send('Hello from Gateway!');
});

// Middleware to handle unauthorized access
app.use((req, res, next) => {
  res.status(401).json({ 
    status: 401,
    message: 'Accessing an unauthorized resource' 
  });
});

// Handle 404 errors
app.use((req, res, next) => {
  res.status(404).json({ 
    status: 404,
    message: 'Resource not found' 
  });
});

app.listen(PORT, () => {
  console.log(`(STATUS): Gateway is running on port ${PORT}`);
});