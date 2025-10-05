import sys

import time
import os
import pandas as pd
import google.generativeai as genai
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# --- 📜 KONFIGURASI ---

# Konfigurasi kunci API Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ ERROR: GEMINI_API_KEY not found in .env file.")
    exit()

try:
    genai.configure(api_key=GEMINI_API_KEY)
except Exception as e:
    print(f"❌ ERROR: Failed to configure Gemini AI. Check your API key. Details: {e}")
    exit()

# <<< REVISI: Konfigurasi untuk setiap file yang akan diproses >>>
# Anda bisa menambahkan file baru di sini di masa depan (misal: instagram.csv)
FILE_CONFIGS = [
    {
        "name": "News Articles (Detik)",
        "input_file": "news_portal/news_detik.csv",
        "output_file": "news_portal/news_detik_cleaned.csv",
        "content_column": "content", # Kolom yang berisi teks untuk diproses
        "type": "news" # Tipe konten untuk memilih prompt yang tepat
    },
    {
        "name": "YouTube Comments",
        "input_file": "social_media/youtube.csv",
        "output_file": "social_media/youtube_cleaned.csv",
        "content_column": "comment_text",
        "type": "comment"
    }
]

# <<< REVISI: Template prompt yang berbeda untuk setiap tipe konten >>>
PROMPT_TEMPLATES = {
    "news": """
    Anda adalah asisten AI yang bertugas membersihkan dan merangkum artikel berita dari Indonesia.
    Tugas Anda adalah membaca konten artikel berita yang diberikan, mengabaikan teks non-berita seperti "SCROLL TO CONTINUE WITH CONTENT", "Tonton juga Video:", atau "[Gambas:Video 20detik]".
    
    Setelah itu, buatlah sebuah ringkasan berita yang netral, informatif, dan jelas dalam satu paragraf (sekitar 3-5 kalimat).
    
    Berikut adalah konten artikelnya:
    ---
    {content}
    ---
    
    Ringkasan:
    """,
    "comment": """
    Anda adalah asisten AI yang bertugas membersihkan dan memperbaiki tata bahasa komentar dari media sosial berbahasa Indonesia.
    Tugas Anda adalah membaca komentar yang diberikan, lalu menuliskannya kembali dengan ejaan dan tata bahasa yang benar. JANGAN mengubah makna atau sentimen asli dari komentar tersebut.
    Jika komentar menggunakan bahasa gaul atau singkatan (spt, yg, kpn, dll), ubah menjadi kata yang baku.
    Hapus semua emoji.
    Output harus berupa teks komentar yang sudah bersih saja, tanpa tambahan apa pun.

    Berikut adalah komentarnya:
    ---
    {content}
    ---

    Komentar yang sudah dibersihkan:
    """
}


def format_text_with_gemini(content: str, content_type: str) -> str:
    """
    Mengirim teks ke Gemini dan meminta pemformatan berdasarkan tipenya.
    """
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    # Pilih template prompt yang sesuai
    prompt_template = PROMPT_TEMPLATES.get(content_type, PROMPT_TEMPLATES["comment"])
    prompt = prompt_template.format(content=content)
    
    try:
        response = model.generate_content(prompt)
        time.sleep(1)  # Menghormati batas rate API
        return response.text.strip()
    except Exception as e:
        print(f"❌ An error occurred with the Gemini API: {e}")
        return "Error: Could not generate summary."


# --- 🚦 MAIN ORCHESTRATOR ---

if __name__ == "__main__":
    print("🚀 Memulai proses pembersihan dan pemformatan data dengan Gemini AI...")

    # Loop melalui setiap konfigurasi file
    for config in FILE_CONFIGS:
        print("\n" + "="*70)
        print(f"Processing: {config['name']}")
        print("="*70)
        
        input_file = config["input_file"]
        output_file = config["output_file"]
        content_column = config["content_column"]
        content_type = config["type"]

        # Periksa apakah file input ada
        if not os.path.exists(input_file):
            print(f"❌ ERROR: Input file not found at '{input_file}'. Skipping.")
            continue

        # Baca data menggunakan pandas
        print(f"📖 Membaca data dari {input_file}...")
        df = pd.read_csv(input_file)

        # Buat kolom baru untuk hasil yang sudah dibersihkan
        df['gemini_summary'] = ''

        print(f"🤖 Memproses {len(df)} baris dengan Gemini AI. Ini mungkin memakan waktu...")

        # Loop melalui setiap baris di DataFrame
        for index, row in df.iterrows():
            print(f"   -> Memproses baris {index + 1}/{len(df)}...")
            
            content = row[content_column]
            
            if pd.notna(content) and len(str(content)) > 10:
                summary = format_text_with_gemini(str(content), content_type)
                df.at[index, 'gemini_summary'] = summary
            else:
                df.at[index, 'gemini_summary'] = "Content too short or invalid."

        # Simpan DataFrame yang baru ke file CSV baru
        print(f"\n💾 Menyimpan data yang sudah dibersihkan ke {output_file}...")
        try:
            # Pindahkan kolom gemini_summary ke depan untuk visibilitas
            cols = df.columns.tolist()
            if 'gemini_summary' in cols:
                cols.insert(cols.index(content_column), cols.pop(cols.index('gemini_summary')))
                df = df[cols]

            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"✅ Selesai! Data bersih Anda ada di '{output_file}'.")
        except Exception as e:
            print(f"❌ Error saat menyimpan ke CSV: {e}")

    print("\n🏁 Semua proses selesai.")

