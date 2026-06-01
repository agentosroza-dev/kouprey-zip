# Kouprey-Zip

A modern file archiver for Windows with a WinUI 3-inspired design. Built with Python and PyQt6.

## Features

- **Compress** files/folders into multiple archive formats with optional password encryption
- **Extract** archives with full folder navigation and single-item extraction
- **Encrypt & Decrypt** text and files using AES-256-GCM
- **Archive Viewer** — browse archive contents with folder tree navigation, file type icons, and context menu actions (Open, Copy, Delete, Extract Item)
- **Drag & Drop** support throughout
- **Windows Shell Integration** — register/unregister context menu entries for Compress, Extract, Quick KPZ
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

### Requirements
- Python 3.12+
- Windows (primary target)

### From source
```bash
git clone https://github.com/kouprey-zip
cd kouprey-zip
pip install -r requirements.txt
python main.py
```

### Build executable
```powershell
.\build.ps1
```

Creates a standalone `.exe` in `dist/Kouprey-Zip/` via PyInstaller. Optionally run with `-Install` to create an InnoSetup installer.

## Usage

### GUI
```bash
python main.py
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
Register the app in the Windows right-click menu via Settings → Integration → Register.

## Project structure
```
kouprey-zip/
├── main.py                  # Entry point, CLI, IPC
├── app_config.py            # Settings load/save
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
│   └── app.ico
└── build.ps1                # PyInstaller build script
```

## Credits

Created by Agentos. Uses [Lucide](https://lucide.dev/) icons and [WinUI 3](https://docs.microsoft.com/en-us/windows/apps/winui/) color system.
