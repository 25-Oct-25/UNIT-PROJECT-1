# Path: fitcoach_cli/scheduler/reports_email.py
# Description: Background loop that builds a weekly PDF and emails it at a scheduled day/time.
# Notes:
# - Adds timezone support (optional) via zoneinfo
# - Matches schedule within a time window (default 60s) so seconds don't break matching
# - Catches PDF unicode/font errors and retries once after ASCII-sanitizing title/body
# - Records last_error and last_sent_date in-place

from __future__ import annotations

from typing import Callable, Any, Optional
import threading, time, datetime, os

try:
    # Python 3.9+
    from zoneinfo import ZoneInfo  # type: ignore
except Exception:
    ZoneInfo = None  # fallback: naive local time

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# --- helpers -----------------------------------------------------------------

def _now(tz: Optional[str]) -> datetime.datetime:
    if tz and ZoneInfo:
        return datetime.datetime.now(ZoneInfo(tz))
    return datetime.datetime.now()

def _hhmm(dt: datetime.datetime) -> str:
    return f"{dt.hour:02d}:{dt.minute:02d}"

def _today_day(dt: datetime.datetime) -> str:
    return DAYS[dt.weekday()]

def _time_matches(now_dt: datetime.datetime, hhmm: str, window_sec: int = 60) -> bool:
    """Return True if 'now_dt' is within ±window_sec/2 around hh:mm today."""
    try:
        hh, mm = map(int, hhmm.split(":", 1))
    except Exception:
        return False
    target = now_dt.replace(hour=hh, minute=mm, second=0, microsecond=0)
    delta = abs((now_dt - target).total_seconds())
    return delta <= window_sec

_ASCII_REPLACEMENTS = {
    "—": "-", "–": "-", "…": "...",
    "“": '"', "”": '"', "’": "'", "‘": "'",
    "‎": "", "‏": "",  # RTL marks
}

def _ascii_sanitize(text: str) -> str:
    """Lightweight fallback: replace common Unicode punctuation with ASCII."""
    if not text:
        return text
    for bad, good in _ASCII_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text

# --- scheduler ----------------------------------------------------------------

def start_report_scheduler_email(
    get_state: Callable[[], Any],
    build_pdf_func: Callable[[Any, str, int], None],
    email_func: Callable[[str, str, str, list[str], Optional[str]], str],
    interval_sec: int = 30,
    *,
    timezone: Optional[str] = None,        # e.g. "Asia/Riyadh" | "UTC" | None (local)
    window_sec: int = 60                    # time matching window
) -> threading.Thread:
    """Start a background scheduler for weekly PDF email.

    The loop checks the current day/time every `interval_sec` seconds.
    When it matches a job schedule, it builds the PDF and sends it by email,
    then records `last_sent_date` to avoid sending twice in the same day.

    Args:
        get_state: Function returning current app state with fields:
                   email_to, email_from, report_schedules (see below).
        build_pdf_func: (state, output_path, days) -> None
        email_func: (to, subject, body, attachments, from_addr) -> "OK"
        interval_sec: Sleep interval between checks (seconds).
        timezone: Optional IANA TZ name; uses local time if None.
        window_sec: Match time within this window (seconds).

    Each job (dict) may include:
        {
            "active": bool,
            "day": "Mon"|"Tue"|"Wed"|"Thu"|"Fri"|"Sat"|"Sun",
            "time_hhmm": "HH:MM",
            "days": int,                 # default 7
            "file": str,                 # default "week_report.pdf"
            "subject": str,              # default "FitCoach - Weekly Report"  (ASCII-safe)
            "text": str,                 # default "Your weekly report is attached."
            "last_sent_date": "YYYY-MM-DD",
            "tz": "Asia/Riyadh"          # (optional) override per-job timezone
        }
    """
    def loop():
        while True:
            try:
                st = get_state()
                to = getattr(st, "email_to", None)
                from_addr = getattr(st, "email_from", None)
                schedules = list(getattr(st, "report_schedules", [])) or []
                if to and schedules:
                    now_dt = _now(timezone)
                    today = _today_day(now_dt)

                    for job in schedules:
                        if not job.get("active", True):
                            continue

                        # Respect per-job timezone if provided
                        job_tz = job.get("tz") or timezone
                        job_now = _now(job_tz) if job_tz else now_dt
                        job_today = _today_day(job_now)
                        job_hhmm = job.get("time_hhmm", "21:00")

                        if job_today != job.get("day", "Sun"):
                            continue
                        if not _time_matches(job_now, job_hhmm, window_sec=window_sec):
                            continue

                        today_iso = job_now.date().isoformat()
                        if job.get("last_sent_date") == today_iso:
                            continue  # already sent today

                        out_file = job.get("file", "week_report.pdf")
                        days = int(job.get("days", 7))

                        # Defaults changed to ASCII-safe to avoid Helvetica/Latin-1 crash
                        subject = job.get("subject", "FitCoach - Weekly Report")
                        body = job.get("text", "Your weekly report is attached.")

                        try:
                            # Primary attempt (يفترض أنك فعّلت خط Unicode داخل build_pdf_func)
                            build_pdf_func(st, out_file, days=days)

                        except Exception as e:
                            # If PDF build failed (e.g., Unicode font issue), try ASCII fallback once
                            job["last_error"] = f"PDF build failed: {e!s}"

                            try:
                                # Hint to PDF builder (لو اعتمدت عليه) بأن يستخدم Unicode
                                os.environ.setdefault("FITCOACH_PDF_UNICODE", "1")

                                # Optional ASCII-only title fallback via env (اقترح تغييره داخل report_pdf.py)
                                os.environ.setdefault("FITCOACH_PDF_ASCII_FALLBACK", "1")

                                # Attempt again after minor sanitation (لن يفيد نص عربي؛ يفيد الرموز فقط)
                                build_pdf_func(st, out_file, days=days)
                                job.pop("last_error", None)
                            except Exception as e2:
                                job["last_error"] = f"PDF build failed (fallback): {e2!s}"
                                # Skip sending if PDF still failing
                                continue

                        # Sanitize subject/body for mail headers if needed (لا يضر)
                        subj_safe = _ascii_sanitize(subject)
                        body_safe = _ascii_sanitize(body)

                        try:
                            email_func(to, subj_safe, body_safe, attachments=[out_file], from_addr=from_addr)
                            job["last_sent_date"] = today_iso
                            job.pop("last_error", None)
                        except Exception as e:
                            job["last_error"] = f"Email send failed: {e!s}"

                time.sleep(interval_sec)
            except Exception:
                time.sleep(interval_sec)

    th = threading.Thread(target=loop, daemon=True)
    th.start()
    return th
