#!/usr/bin/env bash
# Paytm ResolveAI Public Tunnel Launcher
# Generates a live public HTTPS URL with QR code for hackathon judges

echo "========================================================"
echo "Starting Public HTTPS Tunnel for Paytm ResolveAI..."
echo "Backend Target: http://localhost:8000"
echo "========================================================"

if command -v cloudflared &> /dev/null; then
    echo "Using Cloudflare Tunnel (Zero login, instant SSL)..."
    cloudflared tunnel --url http://localhost:8000
elif [ -f "/opt/homebrew/bin/cloudflared" ]; then
    /opt/homebrew/bin/cloudflared tunnel --url http://localhost:8000
elif command -v npx &> /dev/null; then
    echo "cloudflared not found, falling back to localtunnel..."
    npx localtunnel --port 8000
else
    echo "Please install cloudflared or node to generate public URL."
    exit 1
fi
