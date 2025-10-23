import os
import json
from datetime import datetime
def save_analysis_json(video_title, data_cache:dict):
    """Save analysis results as JSON file inside /data folder."""
    os.makedirs("data", exist_ok=True)
    safe_title = "".join(c for c in video_title if c.isalnum() or c in (" ", "_")).strip()
    json_path = os.path.join("data", f"analysis_{safe_title}.json")

    data_cache["saved_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data_cache, f, ensure_ascii=False, indent=2)

    return json_path