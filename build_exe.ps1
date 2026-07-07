$ErrorActionPreference = "Stop"

$AppName = "SteganographyToolkit"
$EntryFile = "app.py"
$IconFile = "assets\st.ico"

if (-not (Test-Path $EntryFile)) {
    throw "Could not find $EntryFile. Run this script from the project folder."
}

if (-not (Test-Path $IconFile)) {
    throw "Icon file not found: $IconFile. Put your icon there and name it st.ico."
}

if (-not (Test-Path ".venv\Scripts\python.exe")) {
    python -m venv .venv
}

.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pip install pyinstaller

.\.venv\Scripts\python.exe -m PyInstaller `
    --onefile `
    --windowed `
    --name $AppName `
    --icon $IconFile `
    --add-data "assets;assets" `
    $EntryFile

Write-Host ""
Write-Host "Done. Your EXE is here: dist\$AppName.exe"
