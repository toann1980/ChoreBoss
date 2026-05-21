# QUICK MIGRATION COMMANDS (Copy-Paste Ready)

**Execute in order. Each command group is independent.**

---

## STOP ALL SERVICES (9 commands)

```bash
sudo systemctl stop llama-cq-gemma4-e2b.service && \
sudo systemctl stop llama-embedding-q8.service && \
sudo systemctl stop llama-gemma4-e2b-q5m.service && \
sudo systemctl stop llama-hermes-2-pro.service && \
sudo systemctl stop llama-llama3-2-moe.service && \
sudo systemctl stop llama-mistral-7b.service && \
sudo systemctl stop llama-nemotron.service && \
sudo systemctl stop llama-phi.service && \
sudo systemctl stop llama-qwen2-5-4b.service
```

---

## UPDATE SERVICE FILES (9 sed commands)

```bash
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-cq-gemma4-e2b.service && \
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-embedding-q8.service && \
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-gemma4-e2b-q5m.service && \
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-hermes-2-pro.service && \
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-llama3-2-moe.service && \
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-mistral-7b.service && \
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-nemotron.service && \
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-phi.service && \
sudo sed -i 's|/home/leto/\.openclaw/models/gguf|/home/leto/models/gguf|g' /etc/systemd/system/llama-qwen2-5-4b.service
```

---

## RELOAD & START (Primary Only)

**Operational constraint:** Only one server at a time.

```bash
# Reload systemd
sudo systemctl daemon-reload

# Start PRIMARY inference server only
sudo systemctl start llama-hermes-2-pro.service
```

**To start other servers individually:**
```bash
# Fallback inference
sudo systemctl start llama-gemma4-e2b-q5m.service

# Embedding service
sudo systemctl start llama-embedding-q8.service

# Reasoning queries
sudo systemctl start llama-qwen2-5-4b.service

# Others (as needed)
sudo systemctl start llama-mistral-7b.service
sudo systemctl start llama-nemotron.service
sudo systemctl start llama-phi.service
sudo systemctl start llama-llama3-2-moe.service
sudo systemctl start llama-cq-gemma4-e2b.service
```

---

## VERIFY (Run after services restart)

```bash
# Check Hermes (PRIMARY)
systemctl status llama-hermes-2-pro.service --no-pager | head -10

# Check Gemma (FALLBACK)
systemctl status llama-gemma4-e2b-q5m.service --no-pager | head -10

# Show updated model path
grep "\-\-model" /etc/systemd/system/llama-hermes-2-pro.service

# Test API
curl http://10.0.0.81:11447/health
```

---

## ROLLBACK (if needed)

```bash
# Stop services
sudo systemctl stop llama-*.service

# Restore from backup
for f in /etc/systemd/system/llama-*.service.backup; do
  sudo cp "$f" "${f%.backup}"
done

# Reload & restart
sudo systemctl daemon-reload
sudo systemctl start llama-*.service
```

---

**Time estimate:** ~3 minutes total (stop + update + start + verify)  
**Risk level:** LOW (graceful shutdown, reversible changes, backups created)
