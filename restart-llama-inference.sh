#!/bin/bash
# Restart llama-inference service (requires manual sudo or systemd access)
# Usage: sudo systemctl restart llama-inference

set -e

echo "Starting llama-inference service..."
sudo systemctl start llama-inference

# Wait for service to be ready
sleep 3

# Verify it started
STATUS=$(sudo systemctl is-active llama-inference)
if [ "$STATUS" = "active" ]; then
    echo "✅ llama-inference service started successfully"
    echo ""
    echo "Service status:"
    sudo systemctl status llama-inference --no-pager | head -10
    echo ""
    echo "Port 11435 should be accepting connections in ~5 seconds"
    echo "Test with: curl http://localhost:11435/health"
else
    echo "❌ llama-inference failed to start"
    sudo systemctl status llama-inference --no-pager
    exit 1
fi
