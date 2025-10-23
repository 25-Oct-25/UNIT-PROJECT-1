# fitcoach_cli/cli/console.py
# -*- coding: utf-8 -*-
"""
Console helpers for colored, well-formatted CLI output.

This module wraps `colorama`, terminal width detection, and text wrapping
to provide a small toolkit for building readable CLIs.

Functions (12):
  - set_color_enabled(enabled): Enable/disable ANSI colors programmatically.
  - set_theme(**kwargs): Override theme colors (primary/success/warning/danger/muted).
  - info(msg), success(msg), warn(msg), error(msg): Shorthand colored messages.
  - ask(prompt): Colored input prompt.
  - wrap(text, width=None, indent=""): Fill text to terminal width while keeping blank lines.
  - banner(text, subtitle=None): Primary-colored banner.
  - heading(title, color=None, *, wide=True, bright=True): Wide section heading.
  - section(title, body, color=None, bright=True, *, wide=True, box=False): Full section printer.
  - _term_width(min_w=50, max_w=120): Safe terminal width detection.
  - _colorize(s, color, bright=False): Internal color application.

Key features:
  * Works on Windows and VS Code terminal (Colorama init with convert=True).
  * Honors NO_COLOR / FORCE_COLOR env vars + manual toggle via set_color_enabled().
  * Wide headings and optional boxed sections with **accurate visible width** (wcwidth).
"""

from colorama import init, Fore, Style
import os, sys, shutil, textwrap, re

# Enable ANSI colors on Windows / VS Code; autoreset style after every print.
init(autoreset=True, convert=True, strip=False)

# Global color switch (reads FORCE_COLOR / NO_COLOR from environment).
_COLOR_ENABLED = (os.getenv("FORCE_COLOR") == "1") or (
    sys.stdout.isatty() and os.getenv("NO_COLOR") is None
)

def set_color_enabled(enabled: bool) -> None:
    """Enable/disable colorized output at runtime."""
    global _COLOR_ENABLED
    _COLOR_ENABLED = bool(enabled)

# ------------------------------ Theme -----------------------------------------

_THEME = {
    "primary": Fore.CYAN,
    "success": Fore.GREEN,
    "warning": Fore.YELLOW,
    "danger":  Fore.RED,
    "muted":   Fore.WHITE,
}

def set_theme(**kwargs) -> None:
    """Override theme colors selectively (primary/success/warning/danger/muted)."""
    for k, v in kwargs.items():
        if k in _THEME:
            _THEME[k] = v

def _colorize(s: str, color: str, bright: bool = False) -> str:
    """Apply color and optional bright style if colors are enabled."""
    if not _COLOR_ENABLED:
        return s
    return (Style.BRIGHT if bright else "") + color + s + Style.RESET_ALL

# ----------------------- Shorthand message helpers ----------------------------

def info(msg: str) -> None:
    print(_colorize(f"› {msg}", _THEME["primary"], True))

def success(msg: str) -> None:
    print(_colorize(f"✔ {msg}", _THEME["success"], True))

def warn(msg: str) -> None:
    print(_colorize(f"⚠ {msg}", _THEME["warning"], True))

def error(msg: str) -> None:
    print(_colorize(f"✖ {msg}", _THEME["danger"], True))

def ask(prompt: str) -> str:
    return input(_colorize(prompt, _THEME["primary"], True))

# ----------------------------- Layout utils -----------------------------------

def _term_width(min_w: int = 50, max_w: int = 120) -> int:
    """Return a safe terminal width within [min_w, max_w]."""
    try:
        w = shutil.get_terminal_size((80, 20)).columns
    except Exception:
        w = 80
    return max(min_w, min(max_w, w))

def wrap(text: str, width: int | None = None, indent: str = "") -> str:
    """Wrap text to the given width while preserving blank lines."""
    if width is None:
        width = _term_width()
    out: list[str] = []
    for para in text.rstrip("\n").split("\n"):
        if not para.strip():
            out.append("")
            continue
        out.extend(
            textwrap.fill(
                para,
                width=width,
                initial_indent=indent,
                subsequent_indent=indent,
                replace_whitespace=False,
                drop_whitespace=False,
            ).split("\n")
        )
    return "\n".join(out)

# -------- Visible-length helpers (ANSI/bidi aware using wcwidth) --------------

try:
    from wcwidth import wcwidth  # accurate terminal cell width
except Exception:
    wcwidth = None  # fallback to len()

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
# bidi/zero-width control chars (LRM/RLM + embedding/override/isolate range)
_ZW_RE   = re.compile(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]")

def _cells(s: str) -> int:
    """Number of terminal cells after stripping ANSI and bidi controls."""
    clean = _ZW_RE.sub("", _ANSI_RE.sub("", s.replace("\t", "    ")))
    if wcwidth:
        w = 0
        for ch in clean:
            cw = wcwidth(ch)
            if cw is None:
                cw = 0
            w += max(cw, 0)
        return w
    return len(clean)

def _clip_visible(s: str, width: int) -> str:
    """Clip string to <= width terminal cells without breaking ANSI sequences."""
    if width <= 0:
        return ""
    out = []
    w = 0
    i = 0
    while i < len(s) and w < width:
        # pass ANSI escape sequences through untouched
        if s[i] == "\x1b":
            m = _ANSI_RE.match(s, i)
            if m:
                out.append(m.group(0))
                i = m.end()
                continue
        ch = s[i]
        if ch == "\t":
            ch = "    "
        # keep zero-width/bidi controls but don't count them
        if _ZW_RE.match(ch):
            out.append(ch)
            i += 1
            continue
        cw = wcwidth(ch) if wcwidth else 1
        if cw is None:
            cw = 0
        if w + max(cw, 0) > width:
            break
        out.append(ch)
        w += max(cw, 0)
        i += 1
    return "".join(out)

def _pad_visible(s: str, width: int, align: str = "left") -> str:
    """Pad spaces based on terminal cells. Clips first, then pads."""
    s = _clip_visible(s, width)
    vis = _cells(s)
    if vis >= width:
        return s
    pad = width - vis
    if align == "left":
        return s + " " * pad
    elif align == "right":
        return " " * pad + s
    else:  # center
        left = pad // 2
        right = pad - left
        return " " * left + s + " " * right

# --------------------------- High-level renderers ------------------------------

def banner(text: str, subtitle: str | None = None) -> None:
    print(_colorize(text, _THEME["primary"], True))
    if subtitle:
        print(_colorize(subtitle, _THEME["primary"], False))

def heading(
    title: str,
    color: str | None = None,
    *,
    wide: bool = True,
    bright: bool = True,
) -> None:
    """Print a wide section heading with an underline."""
    if color is None:
        color = _THEME["primary"]
    W = _term_width()
    text = title.strip()
    print(_colorize(text, color, bright))
    line_len = W if wide else max(1, len(text))
    print(_colorize("─" * line_len, color, False))

def section(
    title: str,
    body: str,
    color: str | None = None,
    bright: bool = True,
    *,
    wide: bool = True,
    box: bool = False,
) -> None:
    """Print a titled section with optional full box.

    When ``box`` is ``False`` (default), prints a wide heading followed by wrapped
    body text. When ``box`` is ``True``, draws a framed box around the title and
    content with visible-length padding (wcwidth) to keep borders aligned.
    """
    if color is None:
        color = _THEME["primary"]

    W = _term_width()
    text = title.strip()
    inner_w = W - (4 if box else 0)
    body_wrapped = wrap(body.rstrip(), width=inner_w)

    if not box:
        heading(text, color=color, wide=wide, bright=bright)
        print(_colorize(body_wrapped, color, False), end="\n\n")
        return

    # Boxed style (accurate cell width so borders never overflow).
    inner = W - 2
    top    = "╔" + "═" * inner + "╗"
    sep    = "╟" + "─" * inner + "╢"
    bottom = "╚" + "═" * inner + "╝"

    print(_colorize(top, color, bright))

    # Title centered inside box with visible padding
    title_field = _pad_visible(text, W - 4, align="center")
    print(_colorize("║ " + title_field + " ║", color, bright))

    print(_colorize(sep, color, False))

    for ln in body_wrapped.splitlines():
        line_field = _pad_visible(ln, W - 4, align="left")
        print(_colorize("║ " + line_field + " ║", color, False))

    print(_colorize(bottom, color, False))
    print()  # trailing spacer
