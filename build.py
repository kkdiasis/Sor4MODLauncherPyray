"""
build.py — SOR4 Mod Launcher build script
Run with: python build.py
"""

import subprocess
import shutil
from pathlib import Path

# =============================================================================
# SETTINGS
# =============================================================================

APP_NAME = "SOR4ModLauncher"
OUTPUT   = Path("dist") / APP_NAME

# =============================================================================
# STEP 1 — Clean previous build
# =============================================================================

print("[ 1/4 ] Cleaning previous build...")
for folder in ["build", "dist"]:
    if Path(folder).exists():
        shutil.rmtree(folder)

# =============================================================================
# STEP 2 — Run PyInstaller (onefile)
# =============================================================================

print("[ 2/4 ] Building executable...")
subprocess.run([
    "pyinstaller",
    "--onefile",
    "--noconsole",
    "--uac-admin",
    f"--name={APP_NAME}",
    "--icon=assets/icon.ico",
    "--hidden-import=pyray",
    "--hidden-import=tkinter",
    "--hidden-import=tkinter.filedialog",
    "--add-data=assets;assets",
    "main.py"
], check=True)

# =============================================================================
# STEP 3 — Assemble distribution folder
# =============================================================================

print("[ 3/4 ] Assembling distribution folder...")








OUTPUT.mkdir(parents=True, exist_ok=True)

# Move compiled .exe to output folder
shutil.move(f"dist/{APP_NAME}.exe", OUTPUT / f"{APP_NAME}.exe")

# Copiar apenas cfg e mods — assets agora estão dentro do .exe
for folder in ["cfg", "mods"]:
    src = Path(folder)
    if src.exists():
        shutil.copytree(src, OUTPUT / folder)

# Copy docs






for doc in ["README.md", "LICENSE"]:
    if Path(doc).exists():
        shutil.copy2(doc, OUTPUT / doc)

# =============================================================================
# STEP 4 — Create distributable .zip
# =============================================================================

print("[ 4/4 ] Creating zip archive...")
shutil.make_archive(str(OUTPUT), "zip", "dist", APP_NAME)

print(f"\nDone!")
print(f"  Folder : dist/{APP_NAME}/")
print(f"  Archive: dist/{APP_NAME}.zip")
