const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');
const timeout = require('connect-timeout');

const app = express();
const PORT = process.env.PORT || 3333;

// Timeout configuration 
const TIMEOUT_DURATION = '3s';

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

// Routes for users service with rate limiter and timeout
app.use('/users/register', timeout(TIMEOUT_DURATION), usersLimiter, usersServiceProxy);
app.use('/users/login', timeout(TIMEOUT_DURATION), usersLimiter, usersServiceProxy);

// Routes for game service with rate limiter and timeout
app.use('/lobby', timeout(TIMEOUT_DURATION), gamesLimiter, gameServiceProxy);
app.use('/lobby/create', timeout(TIMEOUT_DURATION), gamesLimiter, gameServiceProxy);
app.use('/lobby/:id/join', timeout(TIMEOUT_DURATION), gamesLimiter, gameServiceProxy);
app.use('/lobby/:id/leave', timeout(TIMEOUT_DURATION), gamesLimiter, gameServiceProxy);

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

// Middleware to handle timeouts
app.use((err, req, res, next) => {
  if (err.code === 'ETIMEDOUT') {
    res.status(408).json({
      status: 408,
      message: 'Request Timeout: Failed to process request in time. Please try again.'
    });
  } else {
    next(err);
  }
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