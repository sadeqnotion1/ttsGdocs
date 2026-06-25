"""
ui_theme.py - portable cyberpunk terminal styling (truecolor gradients + Nerd Font icons).

Drop this single file into ANY project (no required dependencies) and call:

    import ui_theme
    ui_theme.print_banner("MyProject", "A generic description of my project features")
    ui_theme.print_check("pass", "Python version", "3.12")
    ui_theme.print_check("warn", "Backend port 8080", "already in use")
    ui_theme.print_check("fail", "Package: PySide6", "pip install PySide6")
    ui_theme.print_server_online("http://127.0.0.1:8080", "E:/Projects/MyProject/data")

Design goals
------------
* ZERO required dependencies. Pure ANSI escape codes -> works in any repo.
* NEVER fatal. If the terminal can't do color, it degrades to clean plain text.
* Icons, NOT emojis. Uses Nerd Font glyphs with an automatic ASCII fallback.
* Big rainbow title via pyfiglet IF it's installed; otherwise a boxed fallback.

Environment toggles
-------------------
    NO_COLOR=1            disable all color (honoured industry-wide)
    FORCE_COLOR=1         force color even when stdout is not a TTY
    UITHEME_ICONS=ascii   force ASCII status markers instead of Nerd Font glyphs
    UITHEME_THEME=name    palette: cyber (default), matrix, sunset, ice, mono

Requirements for the FULL look (the screenshot):
    * Windows Terminal (NOT legacy cmd.exe) for truecolor + glyph rendering.
    * A Nerd Font installed and selected (e.g. CaskaydiaCove / FiraCode Nerd Font).
    * Optional: `pip install pyfiglet` for the large ASCII-art title.
"""
from __future__ import annotations

import os
import re
import sys

__all__ = [
    "print_banner",
    "print_check",
    "print_rule",
    "print_server_online",
    "panel",
    "gradient",
    "icon",
    "colorize",
    "set_theme",
]

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
_RESET = "\x1b[0m"


# --------------------------------------------------------------------------- #
#  Terminal capability detection / Windows VT enabling
# --------------------------------------------------------------------------- #
def _enable_windows_vt() -> bool:
    """Turn on ANSI escape processing on modern Windows consoles."""
    if os.name != "nt":
        return True
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if not kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            return False
        ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
        kernel32.SetConsoleMode(handle, mode.value | ENABLE_VIRTUAL_TERMINAL_PROCESSING)
        return True
    except Exception:
        return False


_VT_OK = _enable_windows_vt()


def _color_on() -> bool:
    if os.environ.get("NO_COLOR") is not None:
        return False
    if os.environ.get("FORCE_COLOR"):
        return True
    if not _VT_OK:
        return False
    try:
        return bool(sys.stdout.isatty())
    except Exception:
        return False


def _icons_nerd() -> bool:
    return os.environ.get("UITHEME_ICONS", "nerd").lower() != "ascii"


# --------------------------------------------------------------------------- #
#  Themes (gradient color stops)
# --------------------------------------------------------------------------- #
_THEMES = {
    "cyber":  ["#ff2e97", "#ff6ec7", "#b14aff", "#6a5cff", "#00e5ff", "#00ffa3"],
    "matrix": ["#003b00", "#00ff41", "#9bff9b", "#00ff41", "#008f11"],
    "sunset": ["#ff0080", "#ff8c00", "#ffd500", "#ff8c00", "#ff0080"],
    "ice":    ["#00d4ff", "#7af5ff", "#a0c4ff", "#5e8bff", "#9d4edd"],
    "mono":   ["#9a9a9a", "#ffffff", "#9a9a9a"],
}

_STATE = {"stops": _THEMES[os.environ.get("UITHEME_THEME", "cyber").lower()
                            if os.environ.get("UITHEME_THEME", "cyber").lower() in _THEMES
                            else "cyber"]}


def set_theme(name_or_stops) -> None:
    """Set the active palette by name or by a list of hex color stops."""
    if isinstance(name_or_stops, str):
        _STATE["stops"] = _THEMES.get(name_or_stops.lower(), _THEMES["cyber"])
    else:
        _STATE["stops"] = list(name_or_stops)


# --------------------------------------------------------------------------- #
#  Low-level color helpers
# --------------------------------------------------------------------------- #
def _hex_to_rgb(h: str):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _fg(r: int, g: int, b: int) -> str:
    return f"\x1b[38;2;{r};{g};{b}m"


def _visible_len(s: str) -> int:
    return len(_ANSI_RE.sub("", s))


def colorize(text: str, hex_color: str, *, bold: bool = False,
             dim: bool = False, italic: bool = False, underline: bool = False) -> str:
    """Wrap text in a single truecolor + style sequence (or return plain)."""
    if not _color_on():
        return text
    codes = []
    if bold:
        codes.append("1")
    if dim:
        codes.append("2")
    if italic:
        codes.append("3")
    if underline:
        codes.append("4")
    r, g, b = _hex_to_rgb(hex_color)
    codes.append(f"38;2;{r};{g};{b}")
    return f"\x1b[{';'.join(codes)}m{text}{_RESET}"


def gradient(text: str, stops=None) -> str:
    """Apply a horizontal multi-stop color gradient across each line of text."""
    if not _color_on():
        return text
    stops = stops or _STATE["stops"]
    rgb_stops = [_hex_to_rgb(s) for s in stops]
    if len(rgb_stops) == 1:
        rgb_stops = rgb_stops * 2
    out_lines = []
    for line in text.split("\n"):
        width = max(len(line), 1)
        buf = []
        for x, ch in enumerate(line):
            seg = (x / max(width - 1, 1)) * (len(rgb_stops) - 1)
            i = int(seg)
            frac = seg - i
            c1 = rgb_stops[i]
            c2 = rgb_stops[min(i + 1, len(rgb_stops) - 1)]
            r, g, b = (round(a + (b - a) * frac) for a, b in zip(c1, c2))
            buf.append(_fg(r, g, b) + ch)
        out_lines.append("".join(buf) + _RESET)
    return "\n".join(out_lines)


# --------------------------------------------------------------------------- #
#  Icons (Nerd Font glyph, ASCII fallback, color)
# --------------------------------------------------------------------------- #
_ICONS = {
    "pass":   ("\uf00c", "OK ", "#00ffa3"),   # nf-fa-check
    "ok":     ("\uf00c", "OK ", "#00ffa3"),
    "fail":   ("\uf00d", "X  ", "#ff2e97"),   # nf-fa-times
    "error":  ("\uf00d", "X  ", "#ff2e97"),
    "warn":   ("\uf071", "!  ", "#ffcc00"),   # nf-fa-warning
    "info":   ("\uf05a", "i  ", "#00e5ff"),   # nf-fa-info_circle
    "net":    ("\uf0ac", "@  ", "#6a5cff"),   # nf-fa-globe
    "rocket": ("\uf135", ">> ", "#ff6ec7"),   # nf-fa-rocket
    "gear":   ("\uf013", "*  ", "#9a9a9a"),   # nf-fa-cog
    "bolt":   ("\uf0e7", "~  ", "#ffd500"),   # nf-fa-bolt
    "folder": ("\uf07b", "D  ", "#6a5cff"),   # nf-fa-folder
    "link":   ("\uf0c1", "-> ", "#00e5ff"),   # nf-fa-link
}


def icon(name: str, *, colored: bool = True) -> str:
    glyph, ascii_, color = _ICONS.get(name, ("\uf059", "?  ", "#9a9a9a"))
    text = glyph if _icons_nerd() else ascii_
    return colorize(text, color, bold=True) if colored else text


# --------------------------------------------------------------------------- #
#  High-level rendering
# --------------------------------------------------------------------------- #
def print_banner(app_name: str | None = None, subtitle: str | None = None, *,
                 font: str = "ansi_shadow", stops=None, file=None) -> None:
    """Print a big rainbow-gradient title. Uses pyfiglet if available."""
    app_name = app_name or os.environ.get("APP_NAME") or "App"
    out = file or sys.stdout
    art = None
    try:
        import pyfiglet  # optional
        art = pyfiglet.figlet_format(app_name, font=font)
    except Exception:
        art = None

    if art:
        print(gradient(art.rstrip("\n"), stops), file=out)
    else:
        # Dependency-free fallback: a bordered, gradient title.
        title = f"  {app_name.upper()}  "
        bar = "\u2501" * len(title)
        block = f"\u250f{bar}\u2513\n\u2503{title}\u2503\n\u2517{bar}\u251b"
        print(gradient(block, stops), file=out)

    if subtitle:
        print("  " + colorize(subtitle, "#9a9a9a", italic=True), file=out)
    print("", file=out)


def print_check(status: str, label: str, detail: str = "", *,
                label_width: int = 28, file=None) -> None:
    """Print a single styled status row: <icon>  <label>  <detail>."""
    out = file or sys.stdout
    status = status.lower()
    label_str = label if len(label) >= label_width else label + " " * (label_width - len(label))
    line = (
        "  " + icon(status) + "  "
        + colorize(label_str, "#ffffff", bold=True)
        + ("  " + colorize(detail, "#9a9a9a") if detail else "")
    )
    print(line, file=out)


def print_rule(label: str = "", *, width: int = 60, file=None) -> None:
    """Print a horizontal gradient divider, optionally with a centered label."""
    out = file or sys.stdout
    if label:
        label = f" {label} "
        pad = max(width - len(label), 2)
        left = pad // 2
        right = pad - left
        line = "\u2500" * left + label + "\u2500" * right
    else:
        line = "\u2500" * width
    print(gradient(line), file=out)


def panel(lines, *, title: str = "", border_hex: str = "#b14aff",
          title_hex: str = "#00ffa3", min_width: int = 0, file=None) -> None:
    """Render a rounded box around the given (already-colored) lines."""
    out = file or sys.stdout
    if isinstance(lines, str):
        lines = lines.split("\n")
    inner = max([_visible_len(l) for l in lines] + [_visible_len(title) + 2, min_width])
    title_seg = (colorize(title, title_hex, bold=True) + " ") if title else ""
    title_vis = (_visible_len(title) + 1) if title else 0
    fill = (inner + 2) - 1 - title_vis  # interior width is inner+2; minus leading dash and title
    top = (colorize("\u256d", border_hex)
           + colorize("\u2500", border_hex)
           + title_seg
           + colorize("\u2500" * fill, border_hex)
           + colorize("\u256e", border_hex))
    print(top, file=out)
    for l in lines:
        pad = inner - _visible_len(l)
        print(colorize("\u2502", border_hex) + " " + l + " " * pad + " "
              + colorize("\u2502", border_hex), file=out)
    bottom = (colorize("\u2570", border_hex)
              + colorize("\u2500" * (inner + 2), border_hex)
              + colorize("\u256f", border_hex))
    print(bottom, file=out)


def print_server_online(url: str, data_root: str = "", *,
                        title: str = "SERVER ONLINE", file=None) -> None:
    """Render the 'server is online' panel with icons + a clickable-looking URL."""
    lines = [
        icon("net") + "  " + colorize("App UI", "#ffffff", bold=True)
        + "     " + colorize(url, "#00e5ff", underline=True),
    ]
    if data_root:
        lines.append(
            icon("folder") + "  " + colorize("Data root", "#ffffff", bold=True)
            + "  " + colorize(data_root, "#9a9a9a")
        )
    panel(lines, title=title, file=file)


# --------------------------------------------------------------------------- #
#  Manual demo
# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    name = sys.argv[1] if len(sys.argv) > 1 else "MyProject"
    print_banner(name, "A generic description of my project features")
    print_rule("diagnostics")
    print_check("pass", "Python version", "3.12.3")
    print_check("pass", "Package: PySide6", "import OK")
    print_check("warn", "Backend port 8080", "already listening")
    print_check("fail", "Package: some_dependency", "pip install some_dependency")
    print_rule()
    print_server_online("http://127.0.0.1:8080", "E:/Projects/MyProject/data")
