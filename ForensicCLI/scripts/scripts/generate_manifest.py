import csv
from pathlib import Path

def generate_manifest(data_dir="data/samples/collected", output_file="data/manifest.csv"):
    src = Path(data_dir)
    files = list(src.glob("*"))
    
    if not files:
        print("❌ No files found in the collected folder.")
        return
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["File Name", "File Type", "Size (KB)", "Path"])
        
        for file in files:
            writer.writerow([
                file.name,
                file.suffix,
                round(file.stat().st_size / 1024, 2),
                str(file)
            ])

    print(f"✅ Manifest generated with {len(files)} files → {output_file}")


if __name__ == "__main__":
    generate_manifest()
