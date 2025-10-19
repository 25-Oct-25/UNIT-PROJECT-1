def start_report_scheduler_email(get_state, build_pdf_func, email_func, interval_sec: int = 30):
    """
    Generate weekly PDF at scheduled time/day, then email it as attachment.
    """
    import threading, time, datetime
    DAYS = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]

    def _now_hhmm():
        t = datetime.datetime.now().time()
        return f"{t.hour:02d}:{t.minute:02d}"
    def _today_day():
        return DAYS[datetime.datetime.today().weekday()]

    def loop():
        while True:
            try:
                st = get_state()
                to = getattr(st, "email_to", None)
                from_addr = getattr(st, "email_from", None)
                schedules = getattr(st, "report_schedules", [])
                if to and schedules:
                    now_hm = _now_hhmm(); today = _today_day()
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
                        except Exception as e:
                            job["last_error"] = str(e)
                time.sleep(interval_sec)
            except Exception:
                time.sleep(interval_sec)
    th = threading.Thread(target=loop, daemon=True); th.start(); return th
