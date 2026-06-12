# Kouprey-Zip  v1.2

A modern file archiver with a WinUI 3-inspired design. Built with Python and PyQt6. Supports **Windows** and **Linux**.

## Features

- **Compress** files/folders into multiple archive formats with optional password encryption
- **Extract** archives with full folder navigation and single-item extraction
- **Encrypt & Decrypt** text and files using AES-256-GCM
- **Archive Viewer** — browse archive contents with folder tree navigation, file type icons, and context menu actions (Open, Copy, Delete, Extract Item)
- **Drag & Drop** support throughout
- **Shell Integration** — right-click context menu on Windows; `.kpz` file association on Linux
- **Dark/Light theme** with WinUI 3 color tokens
- **Khmer & English** language support
- **Single-instance IPC** — multiple file operations merge into one window

## Supported Formats

| Format | Compress | Extract | Encrypted |
|--------|----------|---------|-----------|
| KPZ (native) | ✓ | ✓ | ✓ |
| ZIP | ✓ | ✓ | ✓ |
| 7z | ✓ | ✓ | ✓ |
| RAR | ✓ | ✓ | ✓ |
| TAR | ✓ | ✓ | ✗ |
| TAR.GZ | ✓ | ✓ | ✗ |
| TAR.BZ2 | ✓ | ✓ | ✗ |
| TAR.XZ | ✓ | ✓ | ✗ |
| TAR.ZST | ✓ | ✓ | ✗ |
| ISO | ✗ | ✓ | ✗ |

## Installation

### Linux — one-line installer (no root required)

```bash
curl -fsSL https://raw.githubusercontent.com/agentosroza-dev/kouprey-zip-linux/main/install.sh | bash
```

To uninstall:
```bash
curl -fsSL https://raw.githubusercontent.com/agentosroza-dev/kouprey-zip-linux/main/install.sh | bash -s -- --uninstall
```

> **Status:** `install.sh` is currently non-functional — the release repository
> (`agentosroza-dev/kouprey-zip-linux`) does not exist yet. For now, run from source:
> ```bash
> git clone https://github.com/agentosroza-dev/kouprey-zip.git
> cd kouprey-zip
> python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
> .venv/bin/python main.py
> ```

The installer will download the pre-built binary from the latest GitHub release. If no
release is available for your architecture, it falls back to installation from source.

| Step | Destination |
|------|-------------|
| Download pre-built binary | `~/.local/share/kouprey-zip/` |
| Create CLI launcher | `~/.local/bin/kouprey-zip` |
| Install `.desktop` entry | `~/.local/share/applications/kouprey-zip.desktop` |
| Register `.kpz` MIME type | `~/.local/share/mime/packages/application-x-kouprey-zip.xml` |
| Install app icons | `~/.local/share/icons/hicolor/*/*/` |

#### Requirements

- **curl** — for downloading the pre-built binary
- **`update-mime-database`** (`shared-mime-info` package) — optional, for `.kpz` file association
- *Only for source fallback:* **Python 3.12+**, **git**, **python3-venv**

#### After installation

- Run `kouprey-zip` from the terminal
- Double-click any `.kpz` file to open it in the archive viewer
- If `~/.local/bin` is not in your `PATH`, add this line to your shell rc file:
  ```bash
  export PATH="$PATH:$HOME/.local/bin"
  ```

### Windows — from source

#### Requirements
- Python 3.12+

```powershell
git clone https://github.com/agentosroza-dev/kouprey-zip-linux.git
cd kouprey-zip-linux
pip install -r requirements.txt
python main.py
```

### Windows — build executable

```powershell
.\build.ps1
```

Creates a standalone `.exe` in `dist/Kouprey-Zip/` via PyInstaller. Optionally run with `-Install` to create an InnoSetup installer.

## Usage

### GUI
```bash
kouprey-zip          # Linux (after install)
python main.py       # Windows / from source
```

### CLI commands
| Flag | Description |
|------|-------------|
| `--compress file1 file2 ...` | Pre-load files/folders into the compress page |
| `--open archive.kpz` | Pre-open an archive in the viewer |
| `--extract archive.zip` | Pre-select an archive for extraction |
| `--quick-compress file1 ...` | Compress to `.kpz` in the same directory (no GUI) |
| `--quick-extract-here archive.zip` | Extract to current directory (no GUI) |
| `--quick-extract-to archive.zip` | Extract to a subfolder (no GUI) |

### Shell integration

**Windows:** Register the app in the right-click menu via Settings → Integration → Register.

**Linux:** `.kpz` files are automatically associated after running `install.sh`. Other archive formats (`.zip`, `.7z`, etc.) can be associated manually via the desktop environment's file manager settings.

## Project structure
```
kouprey-zip/
├── main.py                  # Entry point, CLI, IPC
├── app_config.py            # Settings load/save
├── install.sh               # Linux curl installer (no root)
├── installer/
│   └── kouprey-zip.desktop  # Linux desktop entry
├── core/                    # Backend
│   ├── archive.py           # Archive entry listing
│   ├── compressor.py        # Compression engine
│   ├── extractor.py         # Extraction engine
│   ├── encryptor.py         # AES-256-GCM encryption
│   ├── formats.py           # Format definitions
│   ├── icons.py             # Lucide SVG icon rendering
│   ├── theme.py             # WinUI 3 color themes
│   ├── language.py          # i18n / l10n
│   ├── registry.py          # Windows shell context menu
│   └── auth.py              # .env loader
├── ui/                      # PyQt6 pages
│   ├── main_window.py       # Main window, nav panel
│   ├── compress_page.py     # Compress file list
│   ├── archive_page.py      # Archive viewer
│   ├── extract_page.py      # Extraction page
│   ├── encrypt_page.py      # Encrypt/Decrypt
│   ├── settings_page.py     # Settings with sub-pages
│   └── about_dialog.py      # About dialog
├── tools/
│   ├── file_utils.py        # Size formatting
│   └── format_detector.py   # Magic byte detection
├── assets/
│   ├── lang/                # en.json, km.json
│   ├── fonts/               # AgentosUI font family
│   ├── icons/               # PNG icons for Linux desktop integration
│   └── app.ico
├── build.ps1                # Windows PyInstaller build
├── kouprey_context.reg      # Windows context menu registration
```

## Credits

Created by Agentos. Uses [Lucide](https://lucide.dev/) icons and [WinUI 3](https://docs.microsoft.com/en-us/windows/apps/winui/) color system.
