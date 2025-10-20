# fitcoach_cli/cli/console.py
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
  * Wide headings and optional boxed sections for better scannability.
"""

from colorama import init, Fore, Style
import os, sys, shutil, textwrap

# Enable ANSI colors on Windows / VS Code; autoreset style after every print.
init(autoreset=True, convert=True, strip=False)

# Global color switch (reads FORCE_COLOR / NO_COLOR from environment).
_COLOR_ENABLED = (os.getenv("FORCE_COLOR") == "1") or (
    sys.stdout.isatty() and os.getenv("NO_COLOR") is None
)

def set_color_enabled(enabled: bool) -> None:
    """Enable/disable colorized output at runtime.

    Intended to be toggled by a CLI flag like ``--no-color``.

    Args:
        enabled: ``True`` to enable ANSI colors, ``False`` to disable.
    """
    global _COLOR_ENABLED
    _COLOR_ENABLED = bool(enabled)

# Default theme.
_THEME = {
    "primary": Fore.CYAN,
    "success": Fore.GREEN,
    "warning": Fore.YELLOW,
    "danger":  Fore.RED,
    "muted":   Fore.WHITE,
}

def set_theme(**kwargs) -> None:
    """Override theme colors selectively.

    Recognized keys: ``primary``, ``success``, ``warning``, ``danger``, ``muted``.

    Example:
        >>> set_theme(primary=Fore.MAGENTA, muted=Fore.WHITE)

    Args:
        **kwargs: Color values (Colorama constants) keyed by theme name.
    """
    for k, v in kwargs.items():
        if k in _THEME:
            _THEME[k] = v

def _colorize(s: str, color: str, bright: bool = False) -> str:
    """Apply color and optional bright style if colors are enabled.

    Args:
        s: Text to colorize.
        color: A Colorama foreground color (e.g., ``Fore.CYAN``).
        bright: If ``True``, applies ``Style.BRIGHT``.

    Returns:
        The possibly colorized string (plain text if colors are disabled).
    """
    if not _COLOR_ENABLED:
        return s
    return (Style.BRIGHT if bright else "") + color + s + Style.RESET_ALL

# ---- Shorthand message helpers ------------------------------------------------

def info(msg: str) -> None:
    """Print an informational message (primary color)."""
    print(_colorize(f"› {msg}", _THEME["primary"], True))

def success(msg: str) -> None:
    """Print a success message (green check)."""
    print(_colorize(f"✔ {msg}", _THEME["success"], True))

def warn(msg: str) -> None:
    """Print a warning message (yellow triangle)."""
    print(_colorize(f"⚠ {msg}", _THEME["warning"], True))

def error(msg: str) -> None:
    """Print an error message (red cross)."""
    print(_colorize(f"✖ {msg}", _THEME["danger"], True))

def ask(prompt: str) -> str:
    """Prompt the user for input using the primary color.

    Args:
        prompt: Prompt text to display.

    Returns:
        The user input string (without trailing newline).
    """
    return input(_colorize(prompt, _THEME["primary"], True))

# ---- Layout utilities ----------------------------------------------------------

def _term_width(min_w: int = 50, max_w: int = 120) -> int:
    """Return a safe terminal width within [min_w, max_w].

    Args:
        min_w: Minimum width to use if the terminal is very small.
        max_w: Maximum width to avoid overly long lines.

    Returns:
        An integer width clamped to the provided bounds.
    """
    try:
        w = shutil.get_terminal_size((80, 20)).columns
    except Exception:
        w = 80
    return max(min_w, min(max_w, w))

def wrap(text: str, width: int | None = None, indent: str = "") -> str:
    """Wrap text to the given width while preserving blank lines.

    Args:
        text: The multi-line string to wrap.
        width: Target width; if ``None``, uses detected terminal width.
        indent: Indentation applied to the first and subsequent lines.

    Returns:
        A string with lines wrapped and indentation applied.
    """
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

# ---- High-level renderers ------------------------------------------------------

def banner(text: str, subtitle: str | None = None) -> None:
    """Print a primary-colored banner (optionally with a subtitle).

    Args:
        text: Main banner text.
        subtitle: Optional secondary line rendered in a dimmer style.
    """
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
    """Print a wide section heading with an underline.

    Args:
        title: Heading text.
        color: Colorama color to use; defaults to theme ``primary``.
        wide: If ``True``, underline spans the terminal width; otherwise, the title length.
        bright: If ``True``, applies bold (bright) style to the title.
    """
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
    content to improve visual separation.

    Args:
        title: Section title.
        body: Section body text (can be multi-line).
        color: Colorama color to use; defaults to theme ``primary``.
        bright: If ``True``, applies bold (bright) style to the title.
        wide: If ``True``, underline/box content spans terminal width.
        box: If ``True``, render a full bordered box around the section.
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

    # Boxed style.
    top    = "╔" + "═" * (W - 2) + "╗"
    tline  = "║ " + text.center(W - 4) + " ║"
    sep    = "╟" + "─" * (W - 2) + "╢"
    bottom = "╚" + "═" * (W - 2) + "╝"

    print(_colorize(top, color, bright))
    print(_colorize(tline, color, bright))
    print(_colorize(sep, color, False))
    for ln in body_wrapped.splitlines():
        print(_colorize("║ " + ln.ljust(W - 4) + " ║", color, False))
    print(_colorize(bottom, color, False))
    print()  # trailing spacer
