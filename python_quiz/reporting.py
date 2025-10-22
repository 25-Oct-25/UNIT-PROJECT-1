import os
from datetime import datetime
from typing import List, Tuple, Optional

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

REPORTS_DIR = os.path.join(os.path.dirname(__file__), "reports")


def _ensure_reports_dir() -> None:
    """Ensure the 'reports' folder exists."""
    os.makedirs(REPORTS_DIR, exist_ok=True)


def wrap_text(text: str, width: int) -> List[str]:
    """Simple word-wrap for PDF paragraph text."""
    words = text.split()
    lines, cur = [], []
    length = 0
    for w in words:
        if length + len(w) + (1 if cur else 0) > width:
            lines.append(" ".join(cur))
            cur = [w]
            length = len(w)
        else:
            if cur:
                cur.append(w)
                length += len(w) + 1
            else:
                cur = [w]
                length = len(w)
    if cur:
        lines.append(" ".join(cur))
    return lines


def make_session_pdf(
    players: List[str],
    sorted_results: List[Tuple[str, float, float, str, str, str]],
    source_label: str,
    winners: List[str],
    is_tie: bool,
    timestamp: Optional[str] = None
) -> str:
    """
    Create a PDF summary for one quiz session.
    sorted_results tuple: (name, score, avg_time, label, message, dev_plan)
    Returns: full file path to the PDF.
    """
    _ensure_reports_dir()
    ts = timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_ts = ts.replace(":", "").replace(" ", "-")
    filename = f"session-{file_ts}.pdf"
    path = os.path.join(REPORTS_DIR, filename)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    x_margin, y_margin = 3 * cm, 3 * cm
    y = height - y_margin

    def write_line(text: str, size=12, bold=False, leading=16):
        """Helper: write one line of text and handle pagination."""
        nonlocal y
        if y < y_margin + 2 * cm:  # new page if near bottom
            c.showPage()
            y = height - y_margin
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(x_margin, y, text)
        y -= leading

    # Header
    write_line("Python Challenge – Session Report", size=16, bold=True, leading=22)
    write_line(f"Timestamp: {ts}")
    write_line(f"Question source: {source_label}")
    write_line(f"Players: {', '.join(players)}")
    if winners:
        if is_tie:
            write_line(f"Winners (tie): {', '.join(winners)}", bold=True)
        else:
            write_line(f"Champion: {winners[0]}", bold=True)
    write_line("-" * 92)

    # Table header
    write_line("Rank | Name        | Score  | Avg Time | Result", bold=True)
    write_line("-" * 92)

    # Table rows
    for i, (name, score, avg, label, _msg, _plan) in enumerate(sorted_results, 1):
        write_line(f"{i:>4} | {name:<10} | {score:>6.1f}% | {avg:.2f}s   | {label}")

    write_line("-" * 92)

    # Per-player details
    for i, (name, score, avg, label, message, dev_plan) in enumerate(sorted_results, 1):
        write_line(f"{i}. {name}", size=14, bold=True, leading=20)
        write_line(f"Score: {score:.1f}%   Avg time: {avg:.2f}s   Result: {label}")
        write_line("-" * 92)
        write_line("Message:", bold=True)
        # handle manual newlines in message
        for section in message.splitlines():
            if section.strip():
                for line in wrap_text(section.strip(), 110):
                    write_line(f"  {line}")

        write_line("-" * 92)
        write_line("Development plan:", bold=True)
        # handle manual newlines in dev_plan
        for section in dev_plan.splitlines():
            if section.strip():
                for line in wrap_text(section.strip(), 110):
                    write_line(f"  {line}")

        write_line("-" * 92)

    c.save()
    return path


# -----------------------------------------------------------
# Generate a PDF for all-time leaderboard
# -----------------------------------------------------------

def make_leaderboard_pdf(stats: List[Tuple[str, float, float, int]]) -> str:
    """
    Create a PDF for the all-time leaderboard across all sessions.

    Args:
        stats: list of tuples (name, avg_score, avg_time, appearances)

    Returns:
        str: full file path to the generated PDF
    """
    _ensure_reports_dir()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    file_ts = ts.replace(":", "").replace(" ", "-")
    filename = f"leaderboard-{file_ts}.pdf"
    path = os.path.join(REPORTS_DIR, filename)

    c = canvas.Canvas(path, pagesize=A4)
    width, height = A4
    x_margin, y_margin = 2 * cm, 2 * cm
    y = height - y_margin

    def write_line(text: str, size=12, bold=False, leading=16):
        """Helper to write lines and handle page breaks."""
        nonlocal y
        if y < y_margin + 2 * cm:
            c.showPage()
            y = height - y_margin
        c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
        c.drawString(x_margin, y, text)
        y -= leading

    # Header
    write_line("Python Challenge – All-Time Leaderboard", size=16, bold=True, leading=22)
    write_line(f"Generated at: {ts}")
    write_line("-" * 92, leading=14)
    write_line("Rank | Name           | Avg Score | Avg Time | Games", bold=True)
    write_line("-" * 92, leading=14)

    # Table rows
    for i, (name, avg_s, avg_t, n) in enumerate(stats, 1):
        row = f"{i:<4} | {name:<14} | {avg_s:>8.1f}% | {avg_t:.2f}s   | {n}"
        write_line(row)

    c.save()
    return path
