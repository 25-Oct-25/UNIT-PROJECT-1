import os
import pandas as pd
import sys

def analyze_dataset(path="."):
    print(f"📁 Checking folder: {path}")
    image_count = 0
    data_files = []
    csv_summary = []

    # نبحث في كل الملفات داخل المجلد المحدد
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.lower().endswith((".jpg", ".jpeg", ".png")):
                image_count += 1
            elif file.lower().endswith(".csv"):
                data_files.append(os.path.join(root, file))

    print(f"\n🖼️ Total Images Found: {image_count}")
    
    if data_files:
        for csv_file in data_files:
            print(f"\n📊 Found CSV file: {csv_file}")
            try:
                df = pd.read_csv(csv_file)
                print(f"   → Rows: {len(df)}, Columns: {len(df.columns)}")
                print(f"   → Missing values: {df.isnull().sum().sum()}")
                print(f"   → Columns: {list(df.columns)}")
                print("\n🔍 Preview of first 5 rows:")
                print(df.head())  # يعرض أول 5 صفوف من البيانات
            except Exception as e:
                print(f"   ⚠️ Could not read file: {e}")
    else:
        print("\n⚠️ No CSV data files found.")

    print("\n✅ Analysis completed.")

if __name__ == "__main__":
    # لو المسار جاي من argument
    if len(sys.argv) > 1:
        folder = sys.argv[1]
    else:
        folder = input("/Users/hananaldayel/Desktop/ForensicCLI_test") or "."
    analyze_dataset(folder)
