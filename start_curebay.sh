#!/usr/bin/env bash
# ============================================================
# start_curebay.sh — One-Click CureBay Launcher for Linux/macOS
# ============================================================
# Run: chmod +x start_curebay.sh && ./start_curebay.sh
# ============================================================

set -e

echo ""
echo "  ======================================================="
echo "    CureBay AI Health Assistant — Starting..."
echo "  ======================================================="
echo ""

# Detect script directory
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "  [ERROR] python3 not found."
    echo "  Install Python 3.10+ from https://python.org or your package manager:"
    echo "    Ubuntu/Debian:  sudo apt install python3 python3-pip"
    echo "    macOS:          brew install python3"
    exit 1
fi

PY_VER=$(python3 --version 2>&1)
echo "  Python: $PY_VER"
echo ""

# Run the cross-platform setup script
cd "$DIR"
python3 setup.py "$@"
