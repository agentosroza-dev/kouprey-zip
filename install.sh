#!/usr/bin/env bash
set -euo pipefail

REPO="agentosroza-dev/kouprey-zip-linux"
REPO_URL="https://github.com/$REPO.git"
INSTALL_DIR="${HOME}/.local/share/kouprey-zip"
BIN_DIR="${HOME}/.local/bin"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
MIME_DIR="${HOME}/.local/share/mime/packages"
ICON_DIR="${HOME}/.local/share/icons/hicolor/128x128"
MIMETYPE_ICON_DIR="${ICON_DIR}/mimetypes"
APP_ICON_DIR="${ICON_DIR}/apps"

# Release asset
ARCH="$(uname -m)"
case "$ARCH" in
    x86_64)  RELEASE_ARCH="x86_64" ;;
    aarch64) RELEASE_ARCH="aarch64" ;;
    *)       RELEASE_ARCH="$ARCH" ;;
esac
RELEASE_FILE="kouprey-zip-linux-${RELEASE_ARCH}.tar.gz"
RELEASE_URL="https://github.com/$REPO/releases/latest/download/$RELEASE_FILE"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

info()  { echo -e "${GREEN}[INFO]${NC}  $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

cleanup_installation() {
    rm -rf "$INSTALL_DIR"
}

install_from_release() {
    local tmpdir
    tmpdir="$(mktemp -d)"

    info "Downloading pre-built binary for ${ARCH}..."
    if ! curl -fsSL "$RELEASE_URL" -o "$tmpdir/release.tar.gz" 2>/dev/null; then
        rm -rf "$tmpdir"
        return 1
    fi

    info "Extracting..."
    tar -xzf "$tmpdir/release.tar.gz" -C "$tmpdir"

    mkdir -p "$INSTALL_DIR"
    cp -r "$tmpdir/Kouprey-Zip/"* "$INSTALL_DIR/"
    chmod +x "$INSTALL_DIR/Kouprey-Zip"
    rm -rf "$tmpdir"
    return 0
}

install_from_source() {
    warn "Pre-built binary not available — installing from source."

    command -v python3 >/dev/null 2>&1 || error "Python 3 is required (not found in PATH)"
    command -v git >/dev/null 2>&1     || error "git is required (not found in PATH)"
    python3 -c "import venv" 2>/dev/null || error "Python venv module is required (install python3-venv)"

    if [ -d "$INSTALL_DIR/.git" ]; then
        info "Updating existing installation at $INSTALL_DIR"
        git -C "$INSTALL_DIR" pull --rebase
    else
        info "Cloning repository to $INSTALL_DIR"
        git clone "$REPO_URL" "$INSTALL_DIR"
    fi

    if [ ! -d "$INSTALL_DIR/venv" ]; then
        info "Creating Python virtual environment..."
        python3 -m venv "$INSTALL_DIR/venv"
    fi
    info "Installing Python dependencies..."
    "$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"

    local launcher="$BIN_DIR/kouprey-zip"
    mkdir -p "$BIN_DIR"
    cat > "$launcher" << 'LAUNCHER'
#!/usr/bin/env bash
DIR="$HOME/.local/share/kouprey-zip"
if [ $# -eq 1 ] && [ "${1#--}" = "$1" ] && [ -e "$1" ]; then
    exec "$DIR/venv/bin/python" "$DIR/main.py" --open "$1"
else
    exec "$DIR/venv/bin/python" "$DIR/main.py" "$@"
fi
LAUNCHER
    chmod +x "$launcher"
    info "Launcher installed: $launcher"
}

install_launcher() {
    mkdir -p "$BIN_DIR"
    local launcher="$BIN_DIR/kouprey-zip"

    if [ -f "$INSTALL_DIR/Kouprey-Zip" ]; then
        cat > "$launcher" << 'LAUNCHER'
#!/usr/bin/env bash
DIR="$HOME/.local/share/kouprey-zip"
exec "$DIR/Kouprey-Zip" "$@"
LAUNCHER
    else
        cat > "$launcher" << 'LAUNCHER'
#!/usr/bin/env bash
DIR="$HOME/.local/share/kouprey-zip"
if [ $# -eq 1 ] && [ "${1#--}" = "$1" ] && [ -e "$1" ]; then
    exec "$DIR/venv/bin/python" "$DIR/main.py" --open "$1"
else
    exec "$DIR/venv/bin/python" "$DIR/main.py" "$@"
fi
LAUNCHER
    fi

    chmod +x "$launcher"
    info "Launcher installed: $launcher"
}

install_desktop_file() {
    mkdir -p "$APPLICATIONS_DIR"
    local src="$INSTALL_DIR/installer/kouprey-zip.desktop"
    local dst="$APPLICATIONS_DIR/kouprey-zip.desktop"

    if [ ! -f "$src" ]; then
        src="$INSTALL_DIR/kouprey-zip.desktop"
    fi

    if [ -f "$src" ]; then
        cp "$src" "$dst"
        sed -i "s|^Exec=kouprey-zip|Exec=$BIN_DIR/kouprey-zip|" "$dst"
        chmod +x "$dst"
        info "Desktop entry installed: $dst"
    else
        warn "Desktop file not found — creating default"
        cat > "$dst" << DESKTOP
[Desktop Entry]
Name=Kouprey-Zip
Comment=Modern file archiver — compress, extract, encrypt
Exec=$BIN_DIR/kouprey-zip %f
Icon=kouprey-zip
Terminal=false
Type=Application
Categories=Utility;Archiving;Compression;
MimeType=application/x-kouprey-zip;
StartupNotify=true
DESKTOP
        chmod +x "$dst"
        info "Desktop entry created: $dst"
    fi
}

install_mime() {
    if ! command -v update-mime-database >/dev/null 2>&1; then
        warn "update-mime-database not found (install shared-mime-info package)"
        warn "MIME type registration for .kpz files will be skipped"
        return
    fi
    mkdir -p "$MIME_DIR"
    cat > "$MIME_DIR/application-x-kouprey-zip.xml" << 'MIME'
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="application/x-kouprey-zip">
    <comment>Kouprey-Zip archive</comment>
    <glob pattern="*.kpz"/>
    <icon name="application-x-kouprey-zip"/>
  </mime-type>
</mime-info>
MIME
    update-mime-database "${HOME}/.local/share/mime/"
    info "MIME type registered: .kpz \u2192 application/x-kouprey-zip"
}

install_icons() {
    local icon_src

    for candidate in "$INSTALL_DIR/assets/icons/output-smallpngtools.png" \
                     "$INSTALL_DIR/output-smallpngtools.png"; do
        if [ -f "$candidate" ]; then
            icon_src="$candidate"
            break
        fi
    done

    if [ -z "${icon_src:-}" ]; then
        warn "App icon not found — skipping icon installation"
        return
    fi

    mkdir -p "$APP_ICON_DIR" "$MIMETYPE_ICON_DIR"
    cp "$icon_src" "$APP_ICON_DIR/kouprey-zip.png"
    cp "$icon_src" "$MIMETYPE_ICON_DIR/application-x-kouprey-zip.png"
    info "Icons installed to $ICON_DIR"

    for size in 64 256; do
        local subdir="${HOME}/.local/share/icons/hicolor/${size}x${size}"
        mkdir -p "$subdir/apps" "$subdir/mimetypes"
        cp "$icon_src" "$subdir/apps/kouprey-zip.png"
        cp "$icon_src" "$subdir/mimetypes/application-x-kouprey-zip.png"
    done
}

print_path_message() {
    if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
        local shell_rc
        case "${SHELL##*/}" in
            zsh) shell_rc="$HOME/.zshrc" ;;
            bash) shell_rc="$HOME/.bashrc" ;;
            *) shell_rc="$HOME/.profile" ;;
        esac
        echo ""
        warn "$BIN_DIR is not in your PATH"
        echo "  Add this line to $shell_rc:"
        echo "    export PATH=\"\$PATH:$BIN_DIR\""
    fi
}

uninstall() {
    echo ""
    echo "  Kouprey-Zip Linux Uninstaller"
    echo "  ============================="
    echo ""
    warn "This will remove Kouprey-Zip and all its files."
    echo "  - $BIN_DIR/kouprey-zip (launcher)"
    echo "  - $APPLICATIONS_DIR/kouprey-zip.desktop"
    echo "  - $INSTALL_DIR (app data)"
    echo "  - MIME registration for .kpz files"
    echo "  - Icons in ~/.local/share/icons/hicolor/"
    echo ""
    read -rp "Continue? [y/N] " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        info "Uninstall cancelled."
        exit 0
    fi

    rm -f "$BIN_DIR/kouprey-zip"
    info "Removed launcher: $BIN_DIR/kouprey-zip"

    rm -f "$APPLICATIONS_DIR/kouprey-zip.desktop"
    info "Removed desktop entry"

    if [ -f "$MIME_DIR/application-x-kouprey-zip.xml" ]; then
        rm -f "$MIME_DIR/application-x-kouprey-zip.xml"
        info "Removed MIME registration"
        if command -v update-mime-database >/dev/null 2>&1; then
            update-mime-database "${HOME}/.local/share/mime/" >/dev/null 2>&1 || true
        fi
    fi

    if [ -d "${HOME}/.local/share/icons/hicolor" ]; then
        find "${HOME}/.local/share/icons/hicolor" -name "kouprey-zip.png" -delete 2>/dev/null || true
        find "${HOME}/.local/share/icons/hicolor" -name "application-x-kouprey-zip.png" -delete 2>/dev/null || true
    fi

    rm -rf "$INSTALL_DIR"
    info "Removed installation directory: $INSTALL_DIR"

    echo ""
    info "Kouprey-Zip has been uninstalled."
    echo ""
}

main() {
    echo ""
    echo "  Kouprey-Zip Linux Installer"
    echo "  ==========================="
    echo ""

    if [ -d "$INSTALL_DIR" ]; then
        info "Existing installation found at $INSTALL_DIR"
        # Try release update first, fall back to source update
        if [ -f "$INSTALL_DIR/Kouprey-Zip" ]; then
            # Previously installed from release; try release update
            local tmpdir
            tmpdir="$(mktemp -d)"
            if curl -fsSL "$RELEASE_URL" -o "$tmpdir/release.tar.gz" 2>/dev/null; then
                info "Updating from pre-built binary..."
                rm -rf "$INSTALL_DIR"
                mkdir -p "$INSTALL_DIR"
                tar -xzf "$tmpdir/release.tar.gz" -C "$tmpdir"
                cp -r "$tmpdir/Kouprey-Zip/"* "$INSTALL_DIR/"
                chmod +x "$INSTALL_DIR/Kouprey-Zip"
                rm -rf "$tmpdir"
            else
                rm -rf "$tmpdir"
                warn "Could not fetch release — updating from source instead."
                git -C "$INSTALL_DIR" pull --rebase 2>/dev/null || true
                "$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || true
            fi
        else
            # Previously installed from source; update from source
            info "Updating from source..."
            git -C "$INSTALL_DIR" pull --rebase 2>/dev/null || true
            "$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || true
        fi
    else
        info "Installing Kouprey-Zip..."
        if ! install_from_release; then
            install_from_source
        fi
        install_launcher
        install_desktop_file
        install_mime
        install_icons
        print_path_message
    fi

    echo ""
    info "Installation complete!"
    info "Run 'kouprey-zip' to start the application."
    echo ""
}

case "${1:-}" in
    --uninstall|-u)
        uninstall
        ;;
    *)
        main
        ;;
esac
