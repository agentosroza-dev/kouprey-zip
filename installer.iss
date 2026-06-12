; InnoSetup script for Kouprey-Zip
; Registers flat individual context menu verbs

#define AppName "Kouprey-Zip"
#define AppVersion "1.2"
#define AppPublisher "Agentos"
#define AppURL "https://github.com/kouprey-zip"
#define AppExeName "Kouprey-Zip.exe"
#define A "{app}\Kouprey-Zip.exe"

[Setup]
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#AppName}
AppVersion={#AppVersion}
AppPublisher={#AppPublisher}
AppPublisherURL={#AppURL}
AppSupportURL={#AppURL}
AppUpdatesURL={#AppURL}
DefaultDirName={autopf}\{#AppName}
DefaultGroupName={#AppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=Kouprey-Zip-Installer-{#AppVersion}
SetupIconFile=assets\icons\Kouprey Logo Variations.ico
UninstallDisplayIcon={app}\{#AppExeName}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=lowest
DisableProgramGroupPage=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "Create a &desktop shortcut"; GroupDescription: "Additional icons:"; Flags: checkedonce

[Files]
Source: "dist\Kouprey-Zip\{#AppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "dist\Kouprey-Zip\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
; ═══════════════════════════════════════════════
; Files (*) – 5 verbs
; ═══════════════════════════════════════════════
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipArchive"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Add Archive with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipArchive\command"; ValueType: string; ValueData: """{#A}"" --compress ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipArchive"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipKPZ"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Create *.kpz"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipKPZ\command"; ValueType: string; ValueData: """{#A}"" --quick-compress ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipKPZ"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\*\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

; ═══════════════════════════════════════════════
; Folders (Directory) – 5 verbs
; ═══════════════════════════════════════════════
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipArchive"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Add Archive with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipArchive\command"; ValueType: string; ValueData: """{#A}"" --compress ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipArchive"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipKPZ"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Create *.kpz"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipKPZ\command"; ValueType: string; ValueData: """{#A}"" --quick-compress ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipKPZ"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

; ═══════════════════════════════════════════════
; Background – 2 verbs
; ═══════════════════════════════════════════════
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\KoupreyZipArchive"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Add Archive with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\KoupreyZipArchive\command"; ValueType: string; ValueData: """{#A}"" --compress ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\KoupreyZipArchive"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\KoupreyZipKPZ"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Create *.kpz"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\KoupreyZipKPZ\command"; ValueType: string; ValueData: """{#A}"" --quick-compress ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Directory\Background\shell\KoupreyZipKPZ"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

; ═══════════════════════════════════════════════
; Drive – 2 verbs
; ═══════════════════════════════════════════════
Root: HKCU; Subkey: "Software\Classes\Drive\shell\KoupreyZipArchive"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Add Archive with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Drive\shell\KoupreyZipArchive\command"; ValueType: string; ValueData: """{#A}"" --compress ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Drive\shell\KoupreyZipArchive"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\Drive\shell\KoupreyZipKPZ"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Create *.kpz"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Drive\shell\KoupreyZipKPZ\command"; ValueType: string; ValueData: """{#A}"" --quick-compress ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\Drive\shell\KoupreyZipKPZ"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

; ═══════════════════════════════════════════════
; SystemFileAssociations archive – 3 verbs
; ═══════════════════════════════════════════════
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\SystemFileAssociations\archive\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

; ═══════════════════════════════════════════════
; Per-extension archive registrations – 3 verbs each
; ═══════════════════════════════════════════════
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.kpz\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.zip\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.7z\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.rar\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.gz\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.bz2\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.xz\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.tar.zst\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtractHere"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract Here"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtractHere\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-here ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtractHere"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtractTo"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract to Folder"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtractTo\command"; ValueType: string; ValueData: """{#A}"" --quick-extract-to ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtractTo"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtract"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Extract with Kouprey"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtract\command"; ValueType: string; ValueData: """{#A}"" --extract ""%1"""; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\.iso\shell\KoupreyZipExtract"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"

; .kpz ProgID + icon
Root: HKCU; Subkey: "Software\Classes\.kpz"; ValueType: string; ValueData: "KoupreyZip.Archive"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\KoupreyZip.Archive\DefaultIcon"; ValueType: string; ValueData: "{#A},0"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\KoupreyZip.Archive\shell\open"; ValueName: "MUIVerb"; ValueType: string; ValueData: "Open with Kouprey-Zip"; Flags: uninsdeletekey
Root: HKCU; Subkey: "Software\Classes\KoupreyZip.Archive\shell\open"; ValueName: "Icon"; ValueType: string; ValueData: "{#A},0"
Root: HKCU; Subkey: "Software\Classes\KoupreyZip.Archive\shell\open\command"; ValueType: string; ValueData: """{#A}"" --open ""%1"""

[Icons]
Name: "{autoprograms}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"
Name: "{autodesktop}\{#AppName}"; Filename: "{app}\{#AppExeName}"; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#AppExeName}"; Description: "Launch {#AppName}"; Flags: nowait postinstall skipifsilent
Filename: "https://www.facebook.com/agentosroza"; Description: "Open Application Website"; Flags: shellexec postinstall

[UninstallRun]
Filename: "https://www.facebook.com/agentosroza"; Flags: shellexec; RunOnceId: "OpenWebsite"

; Registry cleanup is handled by Flags: uninsdeletekey on [Registry] entries above
