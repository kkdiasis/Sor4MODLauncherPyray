import pyray as rl
import subprocess
import json
from pathlib import Path
from src import (
    restauracao_completa,
    listar_mods,
    iniciar_mod,
    bigfile,
    bigfile_bkp,
    bigfile_original,
    mods_path,
    mods_json,
    recarregar_paths,
)

# =============================================================================
# WINDOW SETTINGS
# =============================================================================

WIDTH  = 500
HEIGHT = 650
TITLE  = "Mod Launcher"

STEAM_APP_ID = "985890"

# =============================================================================
# PALETTE — Dark Blue
# =============================================================================

FUNDO         = rl.Color(10,  14,  26,  255)
ITEM_NORMAL   = rl.Color(24,  34,  60,  255)
ITEM_HOVER    = rl.Color(34,  48,  84,  255)
ITEM_ATIVO    = rl.Color(30,  80,  180, 255)
BARRA_ATIVA   = rl.Color(80,  160, 255, 255)
BTN_RESTAURAR = rl.Color(140, 30,  50,  255)
BTN_CONFIG    = rl.Color(28,  42,  80,  255)
BTN_SAIR      = rl.Color(18,  24,  42,  255)
SEPARADOR     = rl.Color(30,  46,  80,  255)
TEXTO         = rl.Color(210, 220, 240, 255)
TEXTO_FRACO   = rl.Color(90,  110, 160, 255)
TITULO_COR    = rl.Color(100, 160, 255, 255)

# =============================================================================
# APP STATE
# =============================================================================

estado = {
    "mods":  [],
    "ativo": None,
}

# =============================================================================
# LABEL MANAGEMENT
# =============================================================================

def carregar_labels(lista_mods: list) -> list:
    """Reads mods.json and returns only active mods with their custom labels."""
    if not mods_json.exists():
        return []

    with open(mods_json, 'r', encoding='utf-8') as f:
        dados = json.load(f)

    cfg = {str(Path(item["caminho"])): item for item in dados}

    resultado = []
    for mod in lista_mods:
        chave = str(Path(mod["caminho"]))
        salvo = cfg.get(chave, {})
        if salvo.get("ativo", False):
            mod["label"] = salvo.get("label") or mod["nome"]
            resultado.append(mod)

    return resultado


# =============================================================================
# ACTIONS
# =============================================================================

def lancar_jogo() -> None:
    """Launches the game via Steam and closes the GUI."""
    subprocess.Popen(["cmd", "/c", "start", f"steam://rungameid/{STEAM_APP_ID}"])
    rl.close_window()
    raise SystemExit


def ativar_e_lancar(caminho: str) -> None:
    """Points the symlink to the chosen mod and launches the game."""
    iniciar_mod(bigfile, caminho)
    estado["ativo"] = caminho
    lancar_jogo()


# =============================================================================
# VISUAL HELPERS
# =============================================================================

def cor_item(caminho: str, hover: bool) -> rl.Color:
    if estado["ativo"] == caminho:
        return ITEM_ATIVO
    return ITEM_HOVER if hover else ITEM_NORMAL


def clarear(cor: rl.Color, quantidade: int = 25) -> rl.Color:
    return rl.Color(
        min(cor.r + quantidade, 255),
        min(cor.g + quantidade, 255),
        min(cor.b + quantidade, 255),
        255,
    )


# =============================================================================
# UI COMPONENTS
# =============================================================================

def desenhar_item(label: str, caminho: str, x: int, y: int, larg: int, alt: int) -> bool:
    """Draws a clickable list item. Returns True if clicked."""
    rect  = rl.Rectangle(x, y, larg, alt)
    mouse = rl.get_mouse_position()
    hover = rl.check_collision_point_rec(mouse, rect)

    rl.draw_rectangle_rec(rect, cor_item(caminho, hover))

    if estado["ativo"] == caminho:
        rl.draw_rectangle(x, y, 4, alt, BARRA_ATIVA)

    rl.draw_text(label, x + 18, y + (alt // 2) - 9, 18, TEXTO)

    return hover and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)


def desenhar_botao(label: str, x: int, y: int, larg: int, alt: int, cor: rl.Color) -> bool:
    """Draws an action button. Returns True if clicked."""
    rect  = rl.Rectangle(x, y, larg, alt)
    mouse = rl.get_mouse_position()
    hover = rl.check_collision_point_rec(mouse, rect)

    rl.draw_rectangle_rec(rect, clarear(cor) if hover else cor)
    rl.draw_text(label, x + 18, y + (alt // 2) - 9, 18, TEXTO)

    return hover and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)


def desenhar_separador(y: int) -> None:
    rl.draw_rectangle(20, y, WIDTH - 40, 1, SEPARADOR)


def desenhar_titulo() -> None:
    rl.draw_text("MOD LAUNCHER", 20, 22, 22, TITULO_COR)
    rl.draw_text("select a mod and play", 22, 50, 14, TEXTO_FRACO)


# =============================================================================
# MAIN LOOP
# =============================================================================

def main() -> None:
    rl.init_window(WIDTH, HEIGHT, TITLE)
    rl.set_target_fps(60)

    mods_brutos    = listar_mods(mods_path)
    estado["mods"] = carregar_labels(mods_brutos)[:5]

    MARGEM    = 20
    ITEM_ALT  = 54
    ITEM_LARG = WIDTH - MARGEM * 2
    BTN_ALT   = 46

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(FUNDO)

        desenhar_titulo()

        y = 80

        # -----------------------------------------------------------------
        # Original option
        # -----------------------------------------------------------------
        caminho_original = str(bigfile_original)

        if desenhar_item("Original", caminho_original, MARGEM, y, ITEM_LARG, ITEM_ALT):
            ativar_e_lancar(caminho_original)

        y += ITEM_ALT + 6

        # -----------------------------------------------------------------
        # Mod list
        # -----------------------------------------------------------------
        if estado["mods"]:
            desenhar_separador(y)
            y += 12

            for mod in estado["mods"]:
                if desenhar_item(mod["label"], mod["caminho"], MARGEM, y, ITEM_LARG, ITEM_ALT):
                    ativar_e_lancar(mod["caminho"])
                y += ITEM_ALT + 6

        # -----------------------------------------------------------------
        # Fixed buttons
        # -----------------------------------------------------------------
        y += 6
        desenhar_separador(y)
        y += 14

        if desenhar_botao("Restore original", MARGEM, y, ITEM_LARG, BTN_ALT, BTN_RESTAURAR):
            restauracao_completa(bigfile, bigfile_bkp)
            if mods_json.exists():
                mods_json.unlink()
            estado["mods"]  = []
            estado["ativo"] = None

        y += BTN_ALT + 8

        if desenhar_botao("Settings", MARGEM, y, ITEM_LARG, BTN_ALT, BTN_CONFIG):
            from gui.config import tela_config
            tela_config()

            paths           = recarregar_paths()
            mods_path_atual = Path(paths["mods"])
            estado["mods"]  = carregar_labels(listar_mods(mods_path_atual))[:5]
            estado["ativo"] = None

        y += BTN_ALT + 8

        if desenhar_botao("Quit", MARGEM, y, ITEM_LARG, BTN_ALT, BTN_SAIR):
            break

        rl.end_drawing()

    rl.close_window()


if __name__ == "__main__":
    main()
