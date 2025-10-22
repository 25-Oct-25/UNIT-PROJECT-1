import json
import os
from datetime import datetime

JSON_PATH = os.path.join("data", "user_files.json")

def save_file_record(email, file_type, video_title, file_name, path):
    record = {
        "user_email": email,
        "file_type": file_type,
        "video_title": video_title, 
        "file_name": file_name,
        "path": path,
        "date_created": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    data = []
    if os.path.exists(JSON_PATH):
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []

    data.append(record)

    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
