#!/bin/bash
# LLAMA.CPP MODEL PATH MIGRATION SCRIPT
# NUC: 10.0.0.81 | 2026-05-03
# Migration: /home/leto/.openclaw/models/gguf → /home/leto/models/gguf

set -e

echo "🚀 LLAMA.CPP SERVICE PATH MIGRATION"
echo "===================================="
echo ""
echo "This script will:"
echo "  1. Stop all 9 llama services"
echo "  2. Update all service files with new model path"
echo "  3. Reload systemd"
echo "  4. Restart all services"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 1
fi

echo ""
echo "⏹️  Phase 1: Stopping all llama services..."
sudo systemctl stop llama-cq-gemma4-e2b.service
sudo systemctl stop llama-embedding-q8.service
sudo systemctl stop llama-gemma4-e2b-q5m.service
sudo systemctl stop llama-hermes-2-pro.service
sudo systemctl stop llama-llama3-2-moe.service
sudo systemctl stop llama-mistral-7b.service
sudo systemctl stop llama-nemotron.service
sudo systemctl stop llama-phi.service
sudo systemctl stop llama-qwen2-5-4b.service
sleep 2
echo "✅ All services stopped"

echo ""
echo "✏️  Phase 2: Updating service files..."

# Create backups and update
for svc in llama-cq-gemma4-e2b llama-embedding-q8 llama-gemma4-e2b-q5m \
           llama-hermes-2-pro llama-llama3-2-moe llama-mistral-7b \
           llama-nemotron llama-phi llama-qwen2-5-4b; do
    
    svc_file="/etc/systemd/system/${svc}.service"
    echo "  Updating: $svc"
    
    # Backup
    sudo cp "$svc_file" "${svc_file}.backup"
    
    # Update path
    sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' "$svc_file"
    
    # Verify
    old_count=$(grep -c "\.openclaw/models" "$svc_file" || echo "0")
    new_count=$(grep -c "/home/leto/models/gguf" "$svc_file" || echo "0")
    
    if [ "$old_count" -eq 0 ] && [ "$new_count" -gt 0 ]; then
        echo "    ✅ Updated"
    else
        echo "    ⚠️  Check result (old=$old_count, new=$new_count)"
    fi
done

echo ""
echo "🔄 Phase 3: Reloading systemd..."
sudo systemctl daemon-reload
echo "✅ Daemon reloaded"

echo ""
echo "🚀 Phase 4: Starting PRIMARY llama service only (operational constraint)..."
echo "  Note: Only one server at a time per operational task"
echo "  Starting: llama-hermes-2-pro (PRIMARY, Port 11447)"
sudo systemctl start llama-hermes-2-pro.service
echo "  ✅ Started: llama-hermes-2-pro"
echo ""
echo "⚠️  Other services remain stopped (start individually as needed)"

echo ""
echo "✅ MIGRATION COMPLETE!"
echo ""
echo "📊 Verification:"
echo "  Hermes-2-Pro status:"
systemctl status llama-hermes-2-pro.service --no-pager 2>&1 | head -3
echo ""
echo "  Model path check:"
grep "model" /etc/systemd/system/llama-hermes-2-pro.service | head -2

echo ""
echo "🎯 To start other services individually:"
echo "  sudo systemctl start llama-gemma4-e2b-q5m       (fallback)"
echo "  sudo systemctl start llama-embedding-q8        (embedding)"
echo "  sudo systemctl start llama-qwen2-5-4b          (reasoning)"
echo ""
echo "🎯 Verification:"
echo "  systemctl status llama-hermes-2-pro --no-pager"
echo "  curl http://10.0.0.81:11447/health"
echo "  sudo journalctl -u llama-hermes-2-pro -n 50"
