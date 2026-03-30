#!/bin/bash
# Genesis Factory — LaunchAgent Installer
# Installs the plist so the factory auto-starts on login.

set -euo pipefail

FACTORY_DIR="$(cd "$(dirname "$0")/.." && pwd)"
PLIST_SRC="$FACTORY_DIR/scripts/com.genesis.factory.plist"
PLIST_DST="$HOME/Library/LaunchAgents/com.genesis.factory.plist"
LABEL="com.genesis.factory"

# --- Uninstall ---
if [ "${1:-}" = "--uninstall" ]; then
    echo "🗑  Uninstalling Genesis Factory LaunchAgent..."
    if launchctl list | grep -q "$LABEL" 2>/dev/null; then
        launchctl unload "$PLIST_DST" 2>/dev/null || true
        echo "  ✅ Unloaded from launchctl"
    fi
    if [ -f "$PLIST_DST" ]; then
        rm "$PLIST_DST"
        echo "  ✅ Removed $PLIST_DST"
    fi
    echo "Done. Factory will no longer auto-start on login."
    exit 0
fi

# --- Install ---
echo "🏭 Installing Genesis Factory LaunchAgent..."
echo "  Factory directory: $FACTORY_DIR"

# Check source plist exists
if [ ! -f "$PLIST_SRC" ]; then
    echo "❌ Plist template not found: $PLIST_SRC"
    exit 1
fi

# Create LaunchAgents directory if needed
mkdir -p "$HOME/Library/LaunchAgents"

# Unload existing if present
if launchctl list | grep -q "$LABEL" 2>/dev/null; then
    echo "  Unloading existing LaunchAgent..."
    launchctl unload "$PLIST_DST" 2>/dev/null || true
fi

# Generate plist with correct path
sed "s|__FACTORY_DIR__|$FACTORY_DIR|g" "$PLIST_SRC" > "$PLIST_DST"
echo "  ✅ Generated plist with path: $FACTORY_DIR"

# Load
launchctl load "$PLIST_DST"
echo "  ✅ Loaded LaunchAgent"

# Verify
if launchctl list | grep -q "$LABEL"; then
    echo ""
    echo "✅ Genesis Factory will auto-start on login."
    echo "   Plist: $PLIST_DST"
    echo "   Logs:  /tmp/genesis-factory.log"
    echo ""
    echo "   Uninstall: $0 --uninstall"
else
    echo "❌ Verification failed — check: launchctl list | grep genesis"
    exit 1
fi
