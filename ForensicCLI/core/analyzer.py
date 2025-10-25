# ForensicCLI/core/analyzer.py
import os
import pandas as pd
from core.file_loader import load_files_from_directory
from core.metadata_extractor import extract_metadata

# 🔹 Rules for detecting suspicious activity
SUSPICIOUS_ACTIONS = {"Delete", "Upload", "Privilege_Escalation"}

def analyze_files(directory, keyword):
    print(f"\n🔍 Scanning directory: {directory}")
    
    # Load files from the given directory
    files = load_files_from_directory(directory)
    print(f"📁 Found {len(files)} files to analyze.")

    # Main result structure
    summary = {
        "directory": directory,
        "files_scanned": len(files),
        "images_found": 0,
        "csv_found": False,
        "dataset_summary": {},
        "suspicious_rule_hits": 0,
        "rule_details": [],
        "matches": []  # Detailed results
    }

    # 🔍 Analyze each file depending on its type
    for file_path in files:
        metadata = extract_metadata(file_path)
        file_name = os.path.basename(file_path)

        # 🖼️ Image files
        if file_name.lower().endswith((".jpg", ".jpeg", ".png", ".gif", ".bmp")):
            summary["images_found"] += 1
            status = "IMAGE FILE"
            summary["matches"].append({
                "file": file_path,
                "metadata": metadata,
                "keyword_found": False,
                "status": status
            })
            print(f"✅ {file_path} → {status}")

        # 📊 CSV dataset analysis
        elif file_name.lower().endswith(".csv"):
            summary["csv_found"] = True
            print(f"🧾 Analyzing dataset: {file_name}")
            try:
                df = pd.read_csv(file_path)
                missing_values = int(df.isnull().sum().sum())
                label_counts = df["Label"].value_counts().to_dict() if "Label" in df.columns else {}

                # 🔸 Rule-based suspicious activity detection
                rule_hits = 0
                details = []

                # Rule 1: Too many login attempts
                if "Login_Attempts" in df.columns:
                    hits = df[df["Login_Attempts"].fillna(0) > 5]
                    rule_hits += len(hits)
                    if len(hits) > 0:
                        details.append(f"Login_Attempts > 5 : {len(hits)} rows")

                # Rule 2: Dangerous actions (Delete, Upload, Privilege_Escalation)
                if "Action" in df.columns:
                    hits2 = df[df["Action"].isin(SUSPICIOUS_ACTIONS)]
                    rule_hits += len(hits2)
                    if len(hits2) > 0:
                        details.append(f"Action in {list(SUSPICIOUS_ACTIONS)} : {len(hits2)} rows")

                summary["suspicious_rule_hits"] += rule_hits
                summary["rule_details"].extend(details)

                # Dataset summary
                summary["dataset_summary"] = {
                    "csv_path": file_path,
                    "rows": int(len(df)),
                    "columns": int(len(df.columns)),
                    "missing_values": missing_values,
                    "label_counts": label_counts
                }

                print(f"📊 Dataset analyzed: {len(df)} rows, {rule_hits} suspicious matches")

            except Exception as e:
                print(f"❌ Error analyzing {file_name}: {e}")

        # 📄 Other file types (e.g., text files)
        else:
            try:
                with open(file_path, "r", errors="ignore") as f:
                    content = f.read()
                contains_keyword = keyword.lower() in content.lower() if keyword else False
                status = "MATCH" if contains_keyword else "NO MATCH"
                summary["matches"].append({
                    "file": file_path,
                    "metadata": metadata,
                    "keyword_found": contains_keyword,
                    "status": status
                })
                print(f"✅ {file_path} → {status}")
            except Exception:
                print(f"⚠️ File format not recognized: {file_path}")

    print("\n📊 Analysis complete.\n")

    # ✅ Ensure all collected data are properly stored before returning
    if not summary["matches"]:
        print("⚠️ No detailed matches were found, but summary data saved.")
    else:
        print(f"🧩 {len(summary['matches'])} detailed records added to report.")

    return summary
