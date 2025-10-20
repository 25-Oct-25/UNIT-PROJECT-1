def save_subtitles(translated_text, output_path="subtitles.srt", duration_per_line=4):
    """
    Save translated Arabic text into a timed .srt subtitle file
    showing each line for a few seconds sequentially.
    """
    lines = translated_text.split("。")  
    if len(lines) == 1:
        lines = translated_text.split("،")
    if len(lines) == 1:
        lines = translated_text.split(".")
        
    srt_content = ""
    start_time = 0.0

    for i, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue

        end_time = start_time + duration_per_line

        def fmt(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int((t - int(t)) * 1000)
            return f"{h:02}:{m:02}:{s:02},{ms:03}"

        srt_content += f"{i}\n{fmt(start_time)} --> {fmt(end_time)}\n{line}\n\n"
        start_time = end_time

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    print(f"Subtitles saved to {output_path}")
    return output_path

