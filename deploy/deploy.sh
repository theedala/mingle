#!/bin/bash
# Mingle - Deployment Script
# Run this to deploy updates

set -e

cd /opt/mingle

echo "🔄 Pulling latest changes..."
git pull origin main

echo "🏗️ Building and restarting containers..."
docker compose -f docker-compose.prod.yml build
docker compose -f docker-compose.prod.yml up -d

echo "🧹 Cleaning up old images..."
docker image prune -f

echo "✅ Deployment complete!"
echo "🔍 Check status: docker compose -f docker-compose.prod.yml ps"
