import pyray as rl
import json
import tkinter as tk
from tkinter import filedialog
from pathlib import Path
from src import (
    mods_json,
    paths_json,
    listar_mods,
)

# =============================================================================
# PALETTE — Dark Blue
# =============================================================================

FUNDO         = rl.Color(10,  14,  26,  255)
ITEM_NORMAL   = rl.Color(24,  34,  60,  255)
ITEM_HOVER    = rl.Color(34,  48,  84,  255)
SEPARADOR     = rl.Color(30,  46,  80,  255)
BTN_SALVAR    = rl.Color(30,  100, 60,  255)
BTN_VOLTAR    = rl.Color(18,  24,  42,  255)
BTN_PASTA     = rl.Color(28,  42,  80,  255)
CHECK_ATIVO   = rl.Color(30,  80,  180, 255)
CHECK_BORDA   = rl.Color(80,  110, 180, 255)
TEXTO         = rl.Color(210, 220, 240, 255)
TEXTO_FRACO   = rl.Color(90,  110, 160, 255)
TITULO_COR    = rl.Color(100, 160, 255, 255)
INPUT_FUNDO   = rl.Color(20,  30,  55,  255)
INPUT_ATIVO   = rl.Color(25,  40,  75,  255)
INPUT_BORDA   = rl.Color(50,  80,  160, 255)

MARGEM        = 20
LARGURA       = 500
ITEM_ALT      = 54
BTN_ALT       = 44
INPUT_ALT     = 32
CHECK_TAMANHO = 20

MODS_VISIVEIS = 4
MODS_AREA_ALT = MODS_VISIVEIS * (ITEM_ALT + 6)


# =============================================================================
# STATE
# =============================================================================

def estado_inicial() -> dict:
    """Loads current configuration into an editable state dict."""

    with open(paths_json, 'r', encoding='utf-8') as f:
        paths = json.load(f)

    mods_salvos = {}
    if mods_json.exists():
        with open(mods_json, 'r', encoding='utf-8') as f:
            dados = json.load(f)
            mods_salvos = {str(Path(item["caminho"])): item for item in dados}

    mods_na_pasta = listar_mods(Path(paths.get("mods", "")))
    mods = []
    for mod in mods_na_pasta:
        salvo = mods_salvos.get(str(Path(mod["caminho"])), {})
        mods.append({
            "nome":    mod["nome"],
            "caminho": mod["caminho"],
            "label":   salvo.get("label", mod["nome"]),
            "ativo":   salvo.get("ativo", False),
        })

    return {
        "game_path":     paths.get("game", ""),
        "mods_path":     paths.get("mods", ""),
        "mods":          mods,
        "editando_idx":  -1,
        "input_buffer":  "",
        "mensagem":      "",
        "scroll_offset": 0,
    }


# =============================================================================
# NATIVE WINDOWS DIALOG
# =============================================================================

def selecionar_pasta() -> str | None:
    """Opens the native Windows folder picker and returns the chosen path."""
    root = tk.Tk()
    root.withdraw()
    root.wm_attributes("-topmost", True)
    pasta = filedialog.askdirectory()
    root.destroy()
    return pasta if pasta else None


# =============================================================================
# SAVE SETTINGS
# =============================================================================

def salvar_configuracoes(estado: dict) -> None:
    """Persists paths.json and mods.json with the edited values."""
    with open(paths_json, 'w', encoding='utf-8') as f:
        json.dump({
            "game": estado["game_path"],
            "mods": estado["mods_path"],
        }, f, indent=4, ensure_ascii=False)

    with open(mods_json, 'w', encoding='utf-8') as f:
        json.dump(estado["mods"], f, indent=4, ensure_ascii=False)

    estado["mensagem"] = "Settings saved!"


# =============================================================================
# VISUAL HELPERS
# =============================================================================

def clarear(cor: rl.Color, v: int = 25) -> rl.Color:
    return rl.Color(min(cor.r+v,255), min(cor.g+v,255), min(cor.b+v,255), 255)


def desenhar_separador(y: int) -> None:
    rl.draw_rectangle(MARGEM, y, LARGURA - MARGEM * 2, 1, SEPARADOR)


def desenhar_secao(titulo: str, y: int) -> None:
    rl.draw_text(titulo, MARGEM, y, 14, TEXTO_FRACO)


def truncar_path(caminho: str, largura_px: int, tamanho_fonte: int = 13) -> str:
    """Truncates a path preserving start and end for readability."""
    chars_max = largura_px // (tamanho_fonte // 2 + 3)

    if len(caminho) <= chars_max:
        return caminho

    partes    = Path(caminho).parts
    inicio    = partes[0] if partes else ""
    fim       = str(Path(*partes[-2:])) if len(partes) >= 2 else caminho
    resultado = f"{inicio}\\...\\{fim}"

    if len(resultado) > chars_max:
        resultado = f"...\\{fim}"

    return resultado


# =============================================================================
# COMPONENTS
# =============================================================================

def desenhar_botao(label: str, x: int, y: int, larg: int, alt: int, cor: rl.Color) -> bool:
    rect  = rl.Rectangle(x, y, larg, alt)
    hover = rl.check_collision_point_rec(rl.get_mouse_position(), rect)
    rl.draw_rectangle_rec(rect, clarear(cor) if hover else cor)
    rl.draw_text(label, x + 14, y + (alt // 2) - 9, 16, TEXTO)
    return hover and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)


def desenhar_campo_path(valor: str, x: int, y: int, larg: int) -> None:
    """Draws a read-only field showing the truncated path."""
    rect = rl.Rectangle(x, y, larg, INPUT_ALT)
    rl.draw_rectangle_rec(rect, INPUT_FUNDO)
    rl.draw_rectangle_lines_ex(rect, 1, INPUT_BORDA)
    texto = truncar_path(valor, larg - 16)
    rl.draw_text(texto, int(rect.x) + 8, int(rect.y) + 8, 13, TEXTO)


def desenhar_checkbox(marcado: bool, x: int, y: int) -> bool:
    """Draws a checkbox. Returns True if clicked."""
    rect  = rl.Rectangle(x, y, CHECK_TAMANHO, CHECK_TAMANHO)
    hover = rl.check_collision_point_rec(rl.get_mouse_position(), rect)

    cor_fundo = CHECK_ATIVO if marcado else (clarear(ITEM_NORMAL) if hover else ITEM_NORMAL)
    rl.draw_rectangle_rec(rect, cor_fundo)
    rl.draw_rectangle_lines_ex(rect, 1, CHECK_BORDA)

    if marcado:
        rl.draw_line(x + 3,  y + 10, x + 8,  y + 15, rl.WHITE)
        rl.draw_line(x + 8,  y + 15, x + 17, y + 5,  rl.WHITE)

    return hover and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT)


def desenhar_label_editavel(estado: dict, idx: int, x: int, y: int, larg: int, alt: int) -> None:
    """
    Draws the mod label. If being edited, shows an inline text input.
    Click on the label activates edit mode.
    """
    mod      = estado["mods"][idx]
    rect     = rl.Rectangle(x, y, larg, alt)
    editando = estado["editando_idx"] == idx
    hover    = rl.check_collision_point_rec(rl.get_mouse_position(), rect)

    cor_fundo = INPUT_ATIVO if editando else (ITEM_HOVER if hover else ITEM_NORMAL)
    rl.draw_rectangle_rec(rect, cor_fundo)

    if editando:
        rl.draw_rectangle_lines_ex(rect, 1, INPUT_BORDA)

        while True:
            key = rl.get_char_pressed()
            if key == 0:
                break
            if 32 <= key <= 125:
                estado["input_buffer"] += chr(key)

        if rl.is_key_pressed(rl.KeyboardKey.KEY_BACKSPACE) and estado["input_buffer"]:
            estado["input_buffer"] = estado["input_buffer"][:-1]

        if rl.is_key_pressed(rl.KeyboardKey.KEY_ENTER):
            mod["label"]           = estado["input_buffer"] or mod["nome"]
            estado["editando_idx"] = -1
            estado["input_buffer"] = ""

        if rl.is_key_pressed(rl.KeyboardKey.KEY_ESCAPE):
            estado["editando_idx"] = -1
            estado["input_buffer"] = ""

        cursor = "|" if (rl.get_time() % 1.0) < 0.5 else ""
        rl.draw_text(
            estado["input_buffer"] + cursor,
            int(rect.x) + 10, int(rect.y) + (alt // 2) - 9, 16, TEXTO
        )
    else:
        rl.draw_text(mod["label"], int(rect.x) + 10, int(rect.y) + (alt // 2) - 9, 16, TEXTO)
        rl.draw_text("click to rename", int(rect.x) + 10, int(rect.y) + alt - 14, 11, TEXTO_FRACO)

        if hover and rl.is_mouse_button_pressed(rl.MouseButton.MOUSE_BUTTON_LEFT):
            estado["editando_idx"] = idx
            estado["input_buffer"] = mod["label"]


# =============================================================================
# SETTINGS SCREEN
# =============================================================================

def tela_config() -> bool:
    """
    Renders the settings screen.
    Returns True when the user clicks Back.
    """
    estado = estado_inicial()

    ativos_count = lambda: sum(1 for m in estado["mods"] if m["ativo"])

    while not rl.window_should_close():
        rl.begin_drawing()
        rl.clear_background(FUNDO)

        y = 20

        # -----------------------------------------------------------------
        # Title
        # -----------------------------------------------------------------
        rl.draw_text("SETTINGS", MARGEM, y, 22, TITULO_COR)
        y += 40

        desenhar_separador(y)
        y += 16

        # -----------------------------------------------------------------
        # Game installation path
        # -----------------------------------------------------------------
        desenhar_secao("GAME INSTALLATION", y)
        y += 18

        larg_campo = LARGURA - MARGEM * 2 - 110
        desenhar_campo_path(estado["game_path"], MARGEM, y, larg_campo)

        if desenhar_botao("Browse", MARGEM + larg_campo + 10, y, 100, INPUT_ALT, BTN_PASTA):
            pasta = selecionar_pasta()
            if pasta:
                estado["game_path"] = pasta

        y += INPUT_ALT + 16
        desenhar_separador(y)
        y += 16

        # -----------------------------------------------------------------
        # Mods folder path
        # -----------------------------------------------------------------
        desenhar_secao("MODS FOLDER", y)
        y += 18

        desenhar_campo_path(estado["mods_path"], MARGEM, y, larg_campo)

        if desenhar_botao("Browse", MARGEM + larg_campo + 10, y, 100, INPUT_ALT, BTN_PASTA):
            pasta = selecionar_pasta()
            if pasta:
                estado["mods_path"]     = pasta
                estado["scroll_offset"] = 0
                novos = listar_mods(Path(pasta))
                estado["mods"] = [
                    {"nome": m["nome"], "caminho": m["caminho"],
                     "label": m["nome"], "ativo": False}
                    for m in novos
                ]

        y += INPUT_ALT + 16
        desenhar_separador(y)
        y += 16

        # -----------------------------------------------------------------
        # Mod list with scroll
        # -----------------------------------------------------------------
        desenhar_secao(f"MODS  ({ativos_count()}/5 enabled)", y)
        y += 20

        if not estado["mods"]:
            rl.draw_text("No mods found in folder.", MARGEM, y, 15, TEXTO_FRACO)
            y += 30
        else:
            total      = len(estado["mods"])
            max_scroll = max(0, total - MODS_VISIVEIS)

            delta = rl.get_mouse_wheel_move()
            if delta != 0:
                estado["scroll_offset"] = max(0, min(
                    estado["scroll_offset"] - int(delta),
                    max_scroll
                ))

            area_scroll   = rl.Rectangle(MARGEM, y, LARGURA - MARGEM * 2, MODS_AREA_ALT)
            mouse_na_area = rl.check_collision_point_rec(rl.get_mouse_position(), area_scroll)

            rl.begin_scissor_mode(MARGEM, y, LARGURA - MARGEM * 2, MODS_AREA_ALT)

            for i, mod in enumerate(estado["mods"]):
                item_y = y + i * (ITEM_ALT + 6) - estado["scroll_offset"] * (ITEM_ALT + 6)

                if item_y + ITEM_ALT < y or item_y > y + MODS_AREA_ALT:
                    continue

                clicou_check = desenhar_checkbox(
                    mod["ativo"],
                    MARGEM,
                    item_y + (ITEM_ALT // 2) - CHECK_TAMANHO // 2
                ) if mouse_na_area else False

                if clicou_check:
                    if mod["ativo"]:
                        mod["ativo"] = False
                    elif ativos_count() < 5:
                        mod["ativo"] = True
                    else:
                        estado["mensagem"] = "Maximum of 5 mods reached."

                desenhar_label_editavel(
                    estado, i,
                    x    = MARGEM + CHECK_TAMANHO + 10,
                    y    = item_y,
                    larg = LARGURA - MARGEM * 2 - CHECK_TAMANHO - 10,
                    alt  = ITEM_ALT,
                )

            rl.end_scissor_mode()

            if total > MODS_VISIVEIS:
                sb_x       = LARGURA - MARGEM - 6
                sb_h_total = MODS_AREA_ALT
                sb_h_thumb = max(30, sb_h_total // total)
                sb_y       = y + int(
                    (estado["scroll_offset"] / max_scroll) * (sb_h_total - sb_h_thumb)
                ) if max_scroll > 0 else y

                rl.draw_rectangle(sb_x, y,    4, sb_h_total, ITEM_NORMAL)
                rl.draw_rectangle(sb_x, sb_y, 4, sb_h_thumb, CHECK_BORDA)

            y += MODS_AREA_ALT + 10

        desenhar_separador(y)
        y += 14

        # -----------------------------------------------------------------
        # Feedback message
        # -----------------------------------------------------------------
        if estado["mensagem"]:
            rl.draw_text(estado["mensagem"], MARGEM, y, 14, TITULO_COR)

        y += 24

        # -----------------------------------------------------------------
        # Buttons
        # -----------------------------------------------------------------
        metade = (LARGURA - MARGEM * 2 - 10) // 2

        if desenhar_botao("Save", MARGEM, y, metade, BTN_ALT, BTN_SALVAR):
            salvar_configuracoes(estado)

        if desenhar_botao("Back", MARGEM + metade + 10, y, metade, BTN_ALT, BTN_VOLTAR):
            rl.end_drawing()
            return True

        rl.end_drawing()

    return False
