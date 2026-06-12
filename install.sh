#!/usr/bin/env bash
set -euo pipefail

REPO="agentosroza-dev/kouprey-zip"
REPO_BRANCH="main-linux"
REPO_URL="https://github.com/$REPO.git"
BRANCH_FLAG="--branch $REPO_BRANCH"
INSTALL_DIR="${HOME}/.local/share/kouprey-zip"
BIN_DIR="${HOME}/.local/bin"
APPLICATIONS_DIR="${HOME}/.local/share/applications"
THUNAR_SENDTO_DIR="${HOME}/.local/share/Thunar/sendto"
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

# ---- Distribution detection ----
detect_pkg_manager() {
    if command -v apt-get >/dev/null 2>&1; then
        echo "apt"
    elif command -v dnf >/dev/null 2>&1; then
        echo "dnf"
    elif command -v yum >/dev/null 2>&1; then
        echo "yum"
    elif command -v zypper >/dev/null 2>&1; then
        echo "zypper"
    elif command -v pacman >/dev/null 2>&1; then
        echo "pacman"
    elif command -v apk >/dev/null 2>&1; then
        echo "apk"
    elif command -v xbps-install >/dev/null 2>&1; then
        echo "xbps"
    elif command -v emerge >/dev/null 2>&1; then
        echo "emerge"
    elif command -v nix-env >/dev/null 2>&1; then
        echo "nix"
    elif command -v pkg >/dev/null 2>&1; then
        echo "pkg"
    else
        echo "unknown"
    fi
}

PKG_MANAGER="$(detect_pkg_manager)"

pkg_install_cmd() {
    case "$PKG_MANAGER" in
        apt)   echo "sudo apt install" ;;
        dnf)   echo "sudo dnf install" ;;
        yum)   echo "sudo yum install" ;;
        zypper) echo "sudo zypper install" ;;
        pacman) echo "sudo pacman -S" ;;
        apk)   echo "sudo apk add" ;;
        xbps)  echo "sudo xbps-install" ;;
        emerge) echo "sudo emerge" ;;
        nix)   echo "nix-env -iA nixpkgs" ;;
        pkg)   echo "sudo pkg install" ;;
        *)     echo "" ;;
    esac
}

pkg_search_cmd() {
    case "$PKG_MANAGER" in
        apt)   echo "dpkg -l" ;;
        dnf|yum) echo "rpm -q" ;;
        zypper) echo "rpm -q" ;;
        pacman) echo "pacman -Qs" ;;
        apk)   echo "apk info -e" ;;
        xbps)  echo "xbps-query" ;;
        emerge) echo "qlist -I" ;;
        nix)   echo "nix-env -q" ;;
        pkg)   echo "pkg info" ;;
        *)     echo "" ;;
    esac
}

pkg_venv_name() {
    local pyver="$1"
    case "$PKG_MANAGER" in
        apt)   echo "python${pyver}-venv" ;;
        dnf|yum) echo "python${pyver}-venv" ;;
        zypper) echo "python${pyver}-venv" ;;
        pacman) echo "python-virtualenv" ;;
        apk)   echo "py3-virtualenv" ;;
        xbps)  echo "python3-venv" ;;
        emerge) echo "dev-python/virtualenv" ;;
        nix)   echo "python3Full" ;;
        pkg)   echo "py${pyver//./}-virtualenv" ;;
        *)     echo "python${pyver}-venv" ;;
    esac
}

pkg_qt_deps() {
    case "$PKG_MANAGER" in
        apt)   echo "libxcb-cursor0 libxcb-xinerama0 libxcb-xkb1 libxkbcommon-x11-0" ;;
        dnf|yum) echo "libxcb-cursor libxcb xcb-util xcb-util-image xcb-util-keysyms xcb-util-wm" ;;
        zypper) echo "libxcb-cursor0 libxcb-xinerama0" ;;
        pacman) echo "libxcb-cursor xcb-util xcb-util-wm" ;;
        apk)   echo "libxcb-dev libxcb-cursor-dev" ;;
        xbps)  echo "libxcb-cursor" ;;
        emerge) echo "x11-libs/libxcb" ;;
        nix)   echo "libxcb" ;;
        pkg)   echo "libxcb" ;;
        *)     echo "libxcb-cursor0" ;;
    esac
}

pkg_check_installed() {
    local pkg="$1"
    local cmd="$(pkg_search_cmd)"
    [ -z "$cmd" ] && return 1
    case "$PKG_MANAGER" in
        apt)   $cmd "$pkg" >/dev/null 2>&1 ;;
        dnf|yum) $cmd "$pkg" >/dev/null 2>&1 ;;
        zypper) $cmd "$pkg" >/dev/null 2>&1 ;;
        pacman) $cmd "$pkg" >/dev/null 2>&1 ;;
        apk)   $cmd "$pkg" >/dev/null 2>&1 ;;
        xbps)  $cmd "$pkg" >/dev/null 2>&1 ;;
        emerge) $cmd "$pkg" >/dev/null 2>&1 ;;
        nix)   $cmd "$pkg" >/dev/null 2>&1 ;;
        pkg)   $cmd "$pkg" >/dev/null 2>&1 ;;
        *)     return 1 ;;
    esac
}

check_qt_deps() {
    local missing=()
    for pkg in $(pkg_qt_deps); do
        if ! pkg_check_installed "$pkg"; then
            missing+=("$pkg")
        fi
    done
    if [ ${#missing[@]} -gt 0 ]; then
        local install_cmd="$(pkg_install_cmd)"
        if [ -n "$install_cmd" ]; then
            warn "Missing Qt system dependencies: ${missing[*]}"
            warn "  Install with: $install_cmd ${missing[*]}"
        else
            warn "Missing Qt system dependencies: ${missing[*]}"
            warn "  Install the packages above using your distribution's package manager."
        fi
    fi
}

cleanup_installation() {
    rm -rf "$INSTALL_DIR"
}

_download() {
    local url="$1" out="$2"
    if command -v curl >/dev/null 2>&1; then
        curl -fsSL "$url" -o "$out"
    elif command -v wget >/dev/null 2>&1; then
        wget -q "$url" -O "$out"
    else
        error "No download tool found (install curl or wget)"
    fi
}

install_from_release() {
    local tmpdir
    tmpdir="$(mktemp -d)"

    info "Downloading pre-built binary for ${ARCH}..."
    if ! _download "$RELEASE_URL" "$tmpdir/release.tar.gz" 2>/dev/null; then
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
    command -v curl >/dev/null 2>&1    || command -v wget >/dev/null 2>&1 || error "curl or wget is required (not found in PATH)"

    local pyver pyvenv_pkg
    pyver="$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "3")"
    pyvenv_pkg="$(pkg_venv_name "$pyver")"

    if ! python3 -c "import venv" 2>/dev/null; then
        local install_cmd="$(pkg_install_cmd)"
        if [ -n "$install_cmd" ]; then
            error "Python venv module is required.\n  Install it with: $install_cmd $pyvenv_pkg"
        else
            error "Python venv module is required.\n  Install the '$pyvenv_pkg' package using your distribution's package manager."
        fi
    fi

    if [ -d "$INSTALL_DIR/.git" ]; then
        info "Updating existing installation at $INSTALL_DIR"
        git -C "$INSTALL_DIR" pull --rebase
    else
        info "Cloning repository to $INSTALL_DIR"
        git clone "$REPO_URL" $BRANCH_FLAG "$INSTALL_DIR"
    fi

    if [ ! -d "$INSTALL_DIR/venv" ]; then
        info "Creating Python virtual environment..."
        if python3 -m venv "$INSTALL_DIR/venv" 2>/dev/null; then
            info "Virtual environment created"
        else
            info "Retrying venv creation without pip..."
            rm -rf "$INSTALL_DIR/venv"
            python3 -m venv --without-pip "$INSTALL_DIR/venv"
            info "Installing pip manually..."
            _download https://bootstrap.pypa.io/get-pip.py /tmp/get-pip.py
            "$INSTALL_DIR/venv/bin/python" /tmp/get-pip.py
        fi
    fi

    if ! "$INSTALL_DIR/venv/bin/python" -m pip --version >/dev/null 2>&1; then
        info "Installing pip in virtual environment..."
        _download https://bootstrap.pypa.io/get-pip.py /tmp/get-pip.py
        "$INSTALL_DIR/venv/bin/python" /tmp/get-pip.py
    fi

    info "Installing Python dependencies..."
    "$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"

    check_qt_deps
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

    for candidate in "$INSTALL_DIR/assets/icons/Kouprey Logo Variations.png" \
                     "$INSTALL_DIR/assets/icons/Kouprey Logo Variations white.png"; do
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

install_thunar_sendto() {
    local src="$INSTALL_DIR/installer/thunar-sendto-kouprey.desktop"
    mkdir -p "$THUNAR_SENDTO_DIR"
    if [ -f "$src" ]; then
        cp "$src" "$THUNAR_SENDTO_DIR/"
        info "Thunar send-to installed: $THUNAR_SENDTO_DIR/thunar-sendto-kouprey.desktop"
    fi
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
    if [ "${AUTO_YES:-0}" != "1" ] && [ -t 0 ]; then
        read -rp "Continue? [y/N] " confirm
        if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
            info "Uninstall cancelled."
            exit 0
        fi
    fi

    rm -f "$BIN_DIR/kouprey-zip"
    info "Removed launcher: $BIN_DIR/kouprey-zip"

    rm -f "$APPLICATIONS_DIR/kouprey-zip.desktop"
    info "Removed desktop entry"

    rm -f "$THUNAR_SENDTO_DIR/thunar-sendto-kouprey.desktop"
    info "Removed Thunar send-to entry"

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
        _update_source() {
            git -C "$INSTALL_DIR" pull --rebase 2>/dev/null || {
                git -C "$INSTALL_DIR" fetch origin "$REPO_BRANCH" 2>/dev/null &&
                git -C "$INSTALL_DIR" reset --hard "origin/$REPO_BRANCH" 2>/dev/null
            } || true
            "$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt" 2>/dev/null || true
        }
        if [ -f "$INSTALL_DIR/Kouprey-Zip" ]; then
            # Previously installed from release; try release update
            local tmpdir
            tmpdir="$(mktemp -d)"
            if _download "$RELEASE_URL" "$tmpdir/release.tar.gz" 2>/dev/null; then
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
                _update_source
            fi
        else
            info "Updating from source..."
            _update_source
        fi
        unset -f _update_source
    else
        info "Installing Kouprey-Zip..."
        if ! install_from_release; then
            install_from_source
        fi
        install_launcher
        install_desktop_file
        install_mime
        install_icons
        install_thunar_sendto
        print_path_message
    fi

    echo ""
    info "Installation complete!"
    info "Run 'kouprey-zip' to start the application."
    echo ""
}

AUTO_YES=0

case "${1:-}" in
    --uninstall|-u)
        shift
        if [ "${1:-}" = "--yes" ] || [ "${1:-}" = "-y" ]; then
            AUTO_YES=1
        fi
        uninstall
        ;;
    *)
        main
        ;;
esac
