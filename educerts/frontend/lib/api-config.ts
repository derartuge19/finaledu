// API Configuration
// Automatically detects the correct API URL based on environment

export const getApiBaseUrl = (): string => {
  // If running in browser
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname
    
    // If accessing via localtunnel (for mobile HTTPS)
    if (hostname.includes('loca.lt')) {
      return 'https://educerts-api.loca.lt'
    }
    
    // If accessing via Cloudflare tunnel (for mobile HTTPS)
    if (hostname.includes('trycloudflare.com')) {
      return 'https://fountain-benefit-walking-span.trycloudflare.com'
    }
    
    // If accessing from localhost, use localhost for API
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'http://localhost:8000'
    }
    
    // If accessing from network IP (mobile), use the same IP for API
    return `http://${hostname}:8000`
  }
  
  // Server-side fallback
  return process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
}

export const API_BASE_URL = typeof window !== 'undefined' ? getApiBaseUrl() : 'http://localhost:8000'
