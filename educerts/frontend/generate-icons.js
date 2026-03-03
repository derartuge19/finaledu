// PWA Icon Generator
// Run with: node generate-icons.js

const fs = require('fs');
const path = require('path');
const sharp = require('sharp');

// Create a simple SVG icon
const createSvgIcon = (size) => {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}">
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#4f46e5;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
    </linearGradient>
  </defs>
  <rect width="${size}" height="${size}" rx="${size * 0.22}" fill="url(#grad)"/>
  <g transform="translate(${size * 0.2}, ${size * 0.2})">
    <!-- Wallet icon -->
    <rect x="${size * 0.05}" y="${size * 0.1}" width="${size * 0.5}" height="${size * 0.35}" rx="${size * 0.04}" fill="white" opacity="0.95"/>
    <rect x="${size * 0.35}" y="${size * 0.18}" width="${size * 0.15}" height="${size * 0.1}" rx="${size * 0.02}" fill="#4f46e5"/>
    <circle cx="${size * 0.42}" cy="${size * 0.23}" r="${size * 0.025}" fill="white"/>
    <!-- Checkmark -->
    <circle cx="${size * 0.45}" cy="${size * 0.38}" r="${size * 0.08}" fill="#10b981"/>
    <path d="M${size * 0.4} ${size * 0.38} L${size * 0.44} ${size * 0.42} L${size * 0.52} ${size * 0.34}" stroke="white" stroke-width="${size * 0.02}" fill="none" stroke-linecap="round" stroke-linejoin="round"/>
  </g>
</svg>`;
};

const sizes = [72, 96, 128, 144, 152, 192, 384, 512];
const iconsDir = path.join(__dirname, 'public', 'icons');

// Ensure directory exists
if (!fs.existsSync(iconsDir)) {
  fs.mkdirSync(iconsDir, { recursive: true });
}

async function generateIcons() {
  console.log('Generating PWA icons...');
  
  for (const size of sizes) {
    const svg = createSvgIcon(size);
    const pngPath = path.join(iconsDir, `icon-${size}x${size}.png`);
    
    await sharp(Buffer.from(svg))
      .png()
      .toFile(pngPath);
    
    console.log(`Created: icon-${size}x${size}.png`);
  }
  
  console.log('\nAll icons generated successfully!');
}

generateIcons().catch(console.error);
