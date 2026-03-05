from pathlib import Path
import shutil
import sys
import re
import json

# =============================================================================
# INITIAL CONFIGURATION
# =============================================================================

def _raiz() -> Path:
    """
    Returns the writable root directory:
    - Running as .exe: folder containing the .exe
    - Running as script: project root
    """
    if hasattr(sys, '_MEIPASS'):
        return Path(sys.executable).parent
    return Path(__file__).parent.parent

config_path = _raiz() / "cfg"
paths_json  = config_path / "paths.json"
mods_json   = config_path / "mods.json"

MAX_MOD_SIZE   = 100 * 1024 * 1024  # 100MB
VALID_FILENAME = r'^[a-zA-Z0-9_.-]+$'

# Creates cfg/ folder if it doesn't exist
config_path.mkdir(parents=True, exist_ok=True)

# Creates paths.json with default values if it doesn't exist
if not paths_json.exists():
    default_paths = {
        "game": "C:\\Program Files (x86)\\Steam\\steamapps\\common\\Streets of Rage 4\\data",
        "mods": str(_raiz() / "mods")
    }
    with open(paths_json, 'w', encoding='utf-8') as j:
        json.dump(default_paths, j, indent=4, ensure_ascii=False)

with open(paths_json, 'r', encoding='utf-8') as j:
    cfg_game_paths = json.load(j)

game_path        = Path(cfg_game_paths['game'])
mods_path        = Path(cfg_game_paths['mods'])
bigfile          = game_path / "bigfile"
bigfile_bkp      = game_path / "bigfile_bkp"
bigfile_original = Path(f"{bigfile}_original")


def recarregar_paths() -> dict:
    """Reads paths.json at runtime, bypassing the cached values."""
    with open(paths_json, 'r', encoding='utf-8') as f:
        return json.load(f)


# =============================================================================
# VALIDATION
# =============================================================================

def validar_arquivo(arquivo) -> bool:
    """Checks if the file exists, has a valid name and acceptable size."""
    path = Path(arquivo)

    if not path.exists() or not path.is_file():
        return False

    if not re.match(VALID_FILENAME, path.name):
        return False

    size = path.stat().st_size

    if size == 0:
        return False

    if size > MAX_MOD_SIZE:
        return False

    return True


# =============================================================================
# ENVIRONMENT MANAGEMENT
# =============================================================================

def preparar_ambiente(bigf: Path, bigf_bkp: Path) -> None:
    """
    Prepares the file structure for mod usage.

    - First run: creates a backup and converts bigfile into a symlink.
    - Subsequent runs: verifies the structure is already in place.
    """
    bigf_original = Path(f"{bigf}_original")

    if bigf.exists() and bigf.is_file():
        print("File found. First run — creating backup...")
        try:
            shutil.copy2(bigf, bigf_bkp)
            shutil.move(bigf, bigf_original)
            bigf.symlink_to(bigf_original)
            print("Environment ready.")
        except Exception as e:
            print(f"Error preparing environment: {e}")

    elif bigf.is_symlink() and bigf_bkp.is_file() and bigf_original.is_file():
        print("Environment already configured.")

    else:
        print('Error: "bigfile" not found or corrupted. Check the game path.')


def restauracao_completa(bigf: Path, bigf_bkp: Path) -> None:
    """Removes the symlink and restores the original bigfile from backup."""
    if bigf_bkp.exists() and bigf_bkp.is_file():
        bigf.unlink(missing_ok=True)
        Path(f"{bigf}_original").unlink(missing_ok=True)
        shutil.copy2(bigf_bkp, bigf)
        print("Restore complete.")
    else:
        print("Error: backup file not found.")


# =============================================================================
# MOD MANAGEMENT
# =============================================================================

def listar_mods(path: Path) -> list:
    """Returns a list of dicts with name and path of available mods."""
    if not path.exists() or not path.is_dir():
        return []

    return [
        {
            "nome":    arquivo.name,
            "caminho": str(arquivo),
        }
        for arquivo in path.iterdir()
        if arquivo.is_file()
    ]


def iniciar_mod(bigf: Path, caminho_mod: str) -> None:
    """Points the bigfile symlink to the chosen mod."""
    if not validar_arquivo(caminho_mod):
        print("Error: invalid mod file.")
        return

    if not bigf.is_symlink():
        print("Error: file structure is damaged.")
        return

    bigf.unlink(missing_ok=True)
    bigf.symlink_to(caminho_mod)
    print(f"Mod activated: {caminho_mod}")


# =============================================================================
# UTILITIES
# =============================================================================

def is_symlink(bigf: Path) -> bool:
    """Returns True if bigfile is a symlink."""
    return bigf.is_symlink()
