#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
VENV_PYTHON="$ROOT/.venv/bin/python"

echo "=== Kouprey-Zip Linux Build Script ==="

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$ROOT/.venv"
    "$VENV_PYTHON" -m pip install --quiet -r "$ROOT/requirements.txt"
fi

if ! "$VENV_PYTHON" -c "import PyInstaller" 2>/dev/null; then
    echo "Installing PyInstaller..."
    "$VENV_PYTHON" -m pip install --quiet pyinstaller
fi

echo "Cleaning old build artifacts..."
rm -rf "$ROOT/build" "$ROOT/dist"

echo "Running PyInstaller..."
"$VENV_PYTHON" -m PyInstaller "$ROOT/Kouprey-Zip.spec" --clean --noconfirm

echo "=== Build complete! ==="
echo "Output: $ROOT/dist/Kouprey-Zip/"
ls -lh "$ROOT/dist/Kouprey-Zip/"
