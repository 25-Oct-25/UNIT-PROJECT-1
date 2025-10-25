import os
import shutil
from pathlib import Path

SUPPORTED_EXTS = [".txt", ".pdf", ".jpg", ".jpeg", ".png"]

def collect_files(source_dir, dest_dir="data/samples/collected"):
    src = Path(source_dir)
    dst = Path(dest_dir)
    dst.mkdir(parents=True, exist_ok=True)

    if not src.exists():
        print(f"❌ Source path not found: {source_dir}")
        return

    count = 0
    for ext in SUPPORTED_EXTS:
        for file in src.rglob(f"*{ext}"):
            try:
                shutil.copy2(file, dst / file.name)
                count += 1
                print(f"📁 Copied: {file.name}")
            except Exception as e:
                print(f"⚠️ Could not copy {file}: {e}")

    print(f"✅ Collected {count} files into {dest_dir}")


if __name__ == "__main__":
    collect_files("/Users/hananaldayel/Desktop/Forensic_Test")
