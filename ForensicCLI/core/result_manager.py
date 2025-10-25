import json
import os
from datetime import datetime
import pathlib

def _convert_paths_to_str(obj):
    """Recursively convert PosixPath objects to strings for JSON serialization."""
    if isinstance(obj, dict):
        return {k: _convert_paths_to_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_paths_to_str(i) for i in obj]
    elif isinstance(obj, pathlib.PurePath):
        return str(obj)
    else:
        return obj


def save_results(data, secure=False):
    """
    Save analysis results into a JSON file.
    If secure=True, the JSON will later be encrypted.
    """
    os.makedirs("output", exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = f"output/results_{timestamp}.json"

    try:
        # ✅ convert all PosixPath to strings BEFORE saving
        clean_data = _convert_paths_to_str(data)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(clean_data, f, indent=4, ensure_ascii=False)

        print(f"✅ Results saved successfully at: {output_path}")

        if secure:
            print("🔒 Secure mode enabled — results will be encrypted later.")
            return output_path
        return output_path

    except Exception as e:
        print(f"❌ Failed to save results: {e}")
        return None
