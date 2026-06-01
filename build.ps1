param(
    [switch]$Install,
    [switch]$SkipPyInstaller
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $MyInvocation.MyCommand.Path

Write-Host "=== Kouprey-Zip Build Script ===" -ForegroundColor Cyan

# Step 1: Ensure config directory
if (-not (Test-Path "$ROOT\config")) {
    New-Item -ItemType Directory -Path "$ROOT\config" -Force | Out-Null
    Write-Host "Created config directory" -ForegroundColor Green
}

# Step 1.5: Create default settings if not exists
if (-not (Test-Path "$ROOT\config\settings.json")) {
    @{ theme = "light"; language = "km"; recent_files = @() } | ConvertTo-Json | Set-Content "$ROOT\config\settings.json" -Encoding UTF8
    Write-Host "Created default config/settings.json" -ForegroundColor Green
}

if (-not $SkipPyInstaller) {
    # Step 2: Clean old build/dist
    Write-Host "Cleaning old build artifacts..." -ForegroundColor Yellow
    if (Test-Path "$ROOT\build") { Remove-Item -Recurse -Force "$ROOT\build" }
    if (Test-Path "$ROOT\dist\Kouprey-Zip") { Remove-Item -Recurse -Force "$ROOT\dist\Kouprey-Zip" }

    # Step 3: Run PyInstaller
    Write-Host "Running PyInstaller..." -ForegroundColor Cyan
    pyinstaller "$ROOT\Kouprey-Zip.spec" --clean --noconfirm

    if ($LASTEXITCODE -ne 0) {
        Write-Host "PyInstaller failed!" -ForegroundColor Red
        exit 1
    }

    Write-Host "PyInstaller build complete!" -ForegroundColor Green
}

if ($Install) {
    # Step 4: Build installer with InnoSetup if available
    $iscc = Get-Command "iscc" -ErrorAction SilentlyContinue
    if ($iscc) {
        Write-Host "Building InnoSetup installer..." -ForegroundColor Cyan
        & iscc "$ROOT\installer.iss"
        Write-Host "Installer built!" -ForegroundColor Green
    } else {
        Write-Host "InnoSetup (iscc) not found. Skipping installer step." -ForegroundColor Yellow
    }
}

Write-Host "=== Build complete! ===" -ForegroundColor Cyan
