const https = require('https');
const http = require('http');
const fs = require('fs');
const selfsigned = require('selfsigned');

// Generate self-signed certificate
const attrs = [{ name: 'commonName', value: 'localhost' }];
const pems = selfsigned.generate(attrs, { days: 365 });

console.log('Generated certificate');

// Create HTTPS proxy
const options = {
  key: pems.private,
  cert: pems.cert
};

const server = https.createServer(options, (req, res) => {
  // Forward to localhost:3002
  const proxyReq = http.request({
    hostname: 'localhost',
    port: 3002,
    path: req.url,
    method: req.method,
    headers: req.headers
  }, (proxyRes) => {
    res.writeHead(proxyRes.statusCode, proxyRes.headers);
    proxyRes.pipe(res, { end: true });
  });
  
  req.pipe(proxyReq, { end: true });
});

server.listen(3003, '0.0.0.0', () => {
  console.log('HTTPS Proxy running on https://10.5.87.118:3003');
  console.log('WARNING: Self-signed certificate - accept the security warning in browser');
  console.log('On mobile: Tap "Advanced" → "Proceed to 10.5.87.118 (unsafe)"');
});
