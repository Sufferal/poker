const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');

const app = express();
const PORT = process.env.PORT || 3333;

// Proxy configuration
const usersServiceProxy = createProxyMiddleware({
  target: 'http://users:5000',
  changeOrigin: true,
});

const gameServiceProxy = createProxyMiddleware({
  target: 'http://game:5111',
  changeOrigin: true,
});

// Routes for users service
app.use('/users/register', usersServiceProxy);
app.use('/users/login', usersServiceProxy);

// Routes for game service
app.use('/lobby', gameServiceProxy);
app.use('/lobby/create', gameServiceProxy);
app.use('/lobby/:id/join', gameServiceProxy);
app.use('/lobby/:id/leave', gameServiceProxy);

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

app.listen(PORT, () => {
  console.log(`(STATUS): Gateway is running on port ${PORT}`);
});