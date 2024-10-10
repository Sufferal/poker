const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');
const timeout = require('connect-timeout');
const axios = require('axios');

const app = express();
const PORT = process.env.PORT || 3333;

// Timeout configuration 
const TIMEOUT_DURATION = '3s';

// Users service rate limiting configuration
const usersLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,                  // Limit each IP to 10 requests every 15 minutes
  message: {                // Message to send when the limit is exceeded
    status: 429,
    message: 'Too many requests to users service. Please try again later.'
  }
});

// Game service rate limiting configuration
const gamesLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5,                  // Limit each IP to 20 requests every 15 minutes
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

// Apply middleware for all routes of the users service
app.use('/users', timeout(TIMEOUT_DURATION), usersLimiter, usersServiceProxy);
app.use('/users/*', timeout(TIMEOUT_DURATION), usersLimiter, usersServiceProxy);

// Apply middleware for all routes of the game service (lobby and games)
app.use('/lobby', timeout(TIMEOUT_DURATION), gamesLimiter, gameServiceProxy);
app.use('/lobby/*', timeout(TIMEOUT_DURATION), gamesLimiter, gameServiceProxy);
app.use('/games', timeout(TIMEOUT_DURATION), gamesLimiter, gameServiceProxy);
app.use('/games/*', timeout(TIMEOUT_DURATION), gamesLimiter, gameServiceProxy);

// Default route
app.get('/', (req, res) => {
  res.send('Hello from Gateway!');
});

// Gateway status route
app.get('/status', (req, res) => {
  const status = {
    status: 'ok',
    uptime: process.uptime(),
    memoryUsage: process.memoryUsage(),
    timestamp: Date.now(),
  };
  res.status(200).json(status);
});

// Service discovery status route
app.get('/sd-status', async (req, res) => {
  try {
    const consulStatus = await axios.get('http://consul:8500/v1/status/leader');
    res.status(200).json({
      status: 'Consul is running',
      leader: consulStatus.data,
    });
  } catch (error) {
    res.status(500).json({
      message: 'Error fetching Consul status',
      error: error.message,
    });
  }
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