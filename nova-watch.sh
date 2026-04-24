#!/bin/bash
# Monitor TO_NOVA.md for Kira's messages
# When Kira writes, this detects it instantly

NOVA_INBOX="/srv/memory-sync/TO_NOVA.md"

echo "✅ Nova message watcher started"
echo "Monitoring: $NOVA_INBOX"
echo ""

while true; do
    inotifywait -e modify "$NOVA_INBOX" 2>/dev/null
    echo ""
    echo "🔔 [$(date '+%Y-%m-%d %H:%M:%S')] NEW MESSAGE FROM KIRA"
    echo "Check: $NOVA_INBOX"
    echo ""
done
