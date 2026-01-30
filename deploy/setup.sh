#!/bin/bash
# Mingle - Initial Droplet Setup Script
# Run this on a fresh Ubuntu 24.04 Droplet

set -e

echo "🚀 Setting up Mingle on DigitalOcean..."

# Update system
echo "📦 Updating system packages..."
apt-get update && apt-get upgrade -y

# Install Docker
echo "🐳 Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
rm get-docker.sh

# Install Docker Compose
echo "🔧 Installing Docker Compose..."
apt-get install -y docker-compose-plugin

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw --force enable

# Create app directory
echo "📁 Creating app directory..."
mkdir -p /opt/mingle
cd /opt/mingle

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Clone your repo: git clone <your-repo-url> ."
echo "2. Copy .env.production.example to .env"
echo "3. Edit .env with your production secrets"
echo "4. Run: docker compose -f docker-compose.prod.yml up -d"
echo ""
echo "🎉 Done! Your server is ready for deployment."
