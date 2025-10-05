import sys

import pandas as pd
import glob
import os

# --- 📜 CONFIGURATION ---

# Folder tempat file-file CSV yang sudah dibersihkan oleh gemini.py berada
# Script ini akan mencari file di dalam folder 'news_portal' dan 'social_media'
INPUT_FOLDERS = ["news_portal", "social_media"]

# File output master yang akan berisi gabungan semua data
OUTPUT_FOLDER = "combined_data"
COMBINED_CSV_FILE = os.path.join(OUTPUT_FOLDER, "combined_all_sources_cleaned.csv")

# --- 🚦 MAIN SCRIPT ---

if __name__ == "__main__":
    print("🚀 Starting CSV combination process...")

    # Buat folder output jika belum ada
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    
    all_files_to_combine = []
    # Cari semua file yang berakhiran '_cleaned.csv' di setiap folder input
    for folder in INPUT_FOLDERS:
        if os.path.exists(folder):
            search_pattern = os.path.join(folder, "*_cleaned.csv")
            found_files = glob.glob(search_pattern)
            all_files_to_combine.extend(found_files)
            print(f"📁 Found {len(found_files)} cleaned files in '{folder}'.")
        else:
            print(f"⚠️  Warning: Folder '{folder}' not found, skipping.")

    if not all_files_to_combine:
        print("❌ ERROR: No '*_cleaned.csv' files found to combine.")
        print("Please run gemini.py on your raw data files first.")
        exit()

    # Buat list untuk menampung semua dataframe
    list_of_dataframes = []

    # Baca setiap file dan tambahkan ke dalam list
    for f in all_files_to_combine:
        try:
            df = pd.read_csv(f)
            list_of_dataframes.append(df)
        except Exception as e:
            print(f"❌ Error reading {f}: {e}")

    # Gabungkan semua dataframe menjadi satu
    if list_of_dataframes:
        print("\n🖇️  Combining all dataframes into a single master file...")
        combined_df = pd.concat(list_of_dataframes, ignore_index=True)

        # Simpan file master
        try:
            combined_df.to_csv(COMBINED_CSV_FILE, index=False, encoding='utf-8')
            print(f"\n✅ Success! All data has been combined.")
            print(f"📊 Total rows combined: {len(combined_df)}")
            print(f"💾 Master file saved to: '{COMBINED_CSV_FILE}'")
        except Exception as e:
            print(f"❌ Error saving combined file: {e}")
    else:
        print("No dataframes were loaded. Cannot combine.")
