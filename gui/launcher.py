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

WIDTH  = 900
HEIGHT = 650
TITLE  = "Mod Launcher"

STEAM_APP_ID = "985890"

FAIXA_LARG = 200  # width of the gradient strip behind the menu

# =============================================================================
# PALETTE
# =============================================================================

FUNDO       = rl.Color(10,  14,  26,  255)
ITEM_ATIVO  = rl.Color(30,  80,  180, 255)
BARRA_ATIVA = rl.Color(80,  160, 255, 255)
SEPARADOR   = rl.Color(30,  46,  80,  0)
TEXTO_FRACO = rl.Color(90,  110, 160, 255)
TITULO_COR  = rl.Color(100, 160, 255, 255)

# =============================================================================
# APP STATE
# =============================================================================

estado = {
    "mods":  [],
    "ativo": None,
}

fonte = None

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
# UI COMPONENTS
# =============================================================================

def draw_text_glow(texto: str, x: int, y: int, tamanho: float) -> None:
    """Draws text with a glowing incandescent effect."""
    rl.draw_text_ex(fonte, texto, rl.Vector2(x - 4, y - 4), tamanho + 8, 1, rl.Color(255, 100,  0,  20))
    rl.draw_text_ex(fonte, texto, rl.Vector2(x - 3, y - 3), tamanho + 6, 1, rl.Color(255, 140,  0,  20))
    rl.draw_text_ex(fonte, texto, rl.Vector2(x - 2, y - 2), tamanho + 4, 1, rl.Color(255, 180,  0,  20))
    rl.draw_text_ex(fonte, texto, rl.Vector2(x - 1, y - 1), tamanho + 2, 1, rl.Color(255, 220,  0,  40))
    rl.draw_text_ex(fonte, texto, rl.Vector2(x,     y    ), tamanho,     1, rl.Color(255, 255, 100, 255))


def desenhar_item(label: str, caminho: str, x: int, y: int, larg: int, alt: int) -> bool:
    """Draws a clickable list item — text only, no background."""
    rect  = rl.Rectangle(x, y, larg, alt)
    mouse = rl.get_mouse_position()
    hover = rl.check_collision_point_rec(mouse, rect)
    ativo = estado["ativo"] == caminho

    tamanho  = 70 if hover else 48
    offset_x = 20 if hover else 0

    if ativo:
        rl.draw_circle(x + 6, y + (alt // 2), 4, BARRA_ATIVA)

    if hover:
        draw_text_glow(label, int(x + 18 + offset_x), int(y + (alt // 2) - (tamanho // 2)), tamanho)
    else:
        cor = BARRA_ATIVA if ativo else rl.WHITE
        rl.draw_text_ex(fonte, label, rl.Vector2(x + 18, y + (alt // 2) - (tamanho // 2)), tamanho, 1, cor)

    return hover and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)


def desenhar_botao(label: str, x: int, y: int, larg: int, alt: int, cor: rl.Color) -> bool:
    """Draws a text-only button — grows and glows on hover."""
    rect  = rl.Rectangle(x, y, larg, alt)
    mouse = rl.get_mouse_position()
    hover = rl.check_collision_point_rec(mouse, rect)

    tamanho  = 70 if hover else 48
    offset_x = 20 if hover else 0

    if hover:
        draw_text_glow(label, int(x + 18 + offset_x), int(y + (alt // 2) - (tamanho // 2)), tamanho)
    else:
        rl.draw_text_ex(fonte, label, rl.Vector2(x + 18, y + (alt // 2) - (tamanho // 2)), tamanho, 1, rl.WHITE)

    return hover and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)


def desenhar_separador(y: int) -> None:
    rl.draw_rectangle(20, y, WIDTH - 40, 1, SEPARADOR)


def desenhar_titulo() -> None:
    rl.draw_text_ex(fonte, "SOR4 MOD LAUNCHER", rl.Vector2(20, 22), 36, 1, TITULO_COR)
    rl.draw_text_ex(fonte, "select a mod and play", rl.Vector2(22, 50), 14, 1, TEXTO_FRACO)


# =============================================================================
# MAIN LOOP
# =============================================================================

def main() -> None:
    global fonte

    rl.init_window(WIDTH, HEIGHT, TITLE)
    rl.set_target_fps(60)
    rl.set_window_state(rl.ConfigFlags.FLAG_WINDOW_UNDECORATED)

    assets_path = Path(__file__).parent.parent / "assets"
    bg_texture  = rl.load_texture(str(assets_path / "background.png"))
    fonte       = rl.load_font_ex(str(assets_path / "BebasNeue-Regular.ttf"), 128, None, 0)

    mods_brutos    = listar_mods(mods_path)
    estado["mods"] = carregar_labels(mods_brutos)[:5]

    MARGEM    = 20
    ITEM_ALT  = 54
    ITEM_LARG = WIDTH - MARGEM * 2
    BTN_ALT   = 46

    while not rl.window_should_close():
        rl.begin_drawing()

        # Background
        rl.clear_background(FUNDO)
        rl.draw_texture(bg_texture, 0, 70, rl.WHITE)

        # Dark overlay
        rl.draw_rectangle(0, 0, WIDTH, HEIGHT, rl.Color(0, 0, 0, 100))

        # Gradient strip behind menu — solid black on left, fades to transparent
        rl.draw_rectangle_gradient_h(
            25, 0, FAIXA_LARG, HEIGHT,
            rl.Color(0, 0, 0, 255),  # left — solid
            rl.Color(0, 0, 0, 150)     # right — transparent
        )

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

        if desenhar_botao("Restore original", MARGEM, y, ITEM_LARG, BTN_ALT, rl.WHITE):
            restauracao_completa(bigfile, bigfile_bkp)
            if mods_json.exists():
                mods_json.unlink()
            estado["mods"]  = []
            estado["ativo"] = None

        y += BTN_ALT + 8

        if desenhar_botao("Settings", MARGEM, y, ITEM_LARG, BTN_ALT, rl.WHITE):
            from gui.config import tela_config
            tela_config()

            paths           = recarregar_paths()
            mods_path_atual = Path(paths["mods"])
            estado["mods"]  = carregar_labels(listar_mods(mods_path_atual))[:5]
            estado["ativo"] = None

        y += BTN_ALT + 8

        if desenhar_botao("Quit", MARGEM, y, ITEM_LARG, BTN_ALT, rl.WHITE):
            break

        rl.end_drawing()

    rl.unload_font(fonte)
    rl.unload_texture(bg_texture)
    rl.close_window()


if __name__ == "__main__":
    main()
