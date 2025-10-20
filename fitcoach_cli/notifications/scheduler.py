# Path: fitcoach_cli/scheduler/reports_email.py
# Description: Background loop that builds a weekly PDF and emails it at a scheduled day/time.

def start_report_scheduler_email(get_state, build_pdf_func, email_func, interval_sec: int = 30):
    """Start a background scheduler for weekly PDF email.

    The loop checks the current day/time every `interval_sec` seconds.
    When it matches a job schedule, it builds the PDF and sends it by email,
    then records `last_sent_date` to avoid sending twice in the same day.

    Args:
        get_state (Callable[[], Any]): Function that returns the current app state.
            Expected fields on state:
              - email_to (str): Recipient address.
              - email_from (str|None): Sender address (optional).
              - report_schedules (list[dict]): Each job may include:
                    {
                        "active": bool,
                        "day": "Mon"|"Tue"|"Wed"|"Thu"|"Fri"|"Sat"|"Sun",
                        "time_hhmm": "HH:MM",
                        "days": int,                 # Days to include in the PDF (default 7)
                        "file": str,                 # Output filename (default "week_report.pdf")
                        "subject": str,              # Email subject
                        "text": str,                 # Email body
                        "last_sent_date": "YYYY-MM-DD",  # Auto-updated
                    }
        build_pdf_func (Callable[[Any, str, int], None]): Function to build the PDF:
            (state, output_path, days) -> None.
        email_func (Callable[[str, str, str, list[str], str|None], str]): Function to send email:
            (to, subject, body, attachments, from_addr) -> "OK".
        interval_sec (int): Sleep interval between checks.

    Returns:
        threading.Thread: The started daemon thread.
    """
    import threading, time, datetime
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    def _now_hhmm() -> str:
        t = datetime.datetime.now().time()
        return f"{t.hour:02d}:{t.minute:02d}"

    def _today_day() -> str:
        return DAYS[datetime.datetime.today().weekday()]

    def loop():
        while True:
            try:
                st = get_state()
                to = getattr(st, "email_to", None)
                from_addr = getattr(st, "email_from", None)
                schedules = getattr(st, "report_schedules", [])
                if to and schedules:
                    now_hm = _now_hhmm()
                    today = _today_day()
                    for job in schedules:
                        if not job.get("active", True):
                            continue
                        if today != job.get("day", "Sun") or now_hm != job.get("time_hhmm", "21:00"):
                            continue
                        today_iso = datetime.date.today().isoformat()
                        if job.get("last_sent_date") == today_iso:
                            continue
                        out_file = job.get("file", "week_report.pdf")
                        try:
                            build_pdf_func(st, out_file, days=int(job.get("days", 7)))
                            subject = job.get("subject", "FitCoach — Weekly Report")
                            body = job.get("text", "Your weekly report is attached.")
                            email_func(to, subject, body, attachments=[out_file], from_addr=from_addr)
                            job["last_sent_date"] = today_iso
                            job.pop("last_error", None)
                        except Exception as e:
                            job["last_error"] = str(e)
                time.sleep(interval_sec)
            except Exception:
                time.sleep(interval_sec)

    th = threading.Thread(target=loop, daemon=True)
    th.start()
    return th
