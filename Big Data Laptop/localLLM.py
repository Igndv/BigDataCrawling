import sys
import time
import os
import pandas as pd
import requests
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# --- KONFIGURASI ---

# Konfigurasi untuk LM Studio (local LLM)
LM_STUDIO_URL = "http://127.0.0.1:1234/v1/chat/completions"
MODEL_NAME = "google/gemma-3-12b"  # Sesuaikan dengan model yang Anda load di LM Studio

# Konfigurasi file yang akan diproses
FILE_CONFIGS = [
    {
        "name": "News Articles (Detik)",
        "input_file": "news_portal/news_detik.csv",
        "output_file": "news_portal/news_detik_cleaned.csv",
        "content_column": "content",
        "type": "news"
    },
    {
        "name": "YouTube Comments",
        "input_file": "social_media/youtube.csv",
        "output_file": "social_media/youtube_cleaned.csv",
        "content_column": "comment_text",
        "type": "comment"
    }
]

# Template prompt
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


def format_text_with_local_llm(content: str, content_type: str) -> str:
    """
    Mengirim teks ke LM Studio (local LLM) dan meminta pemformatan berdasarkan tipenya.
    Fungsi ini dilengkapi dengan mekanisme retry jika terjadi kegagalan.
    """
    # Pilih template prompt yang sesuai
    prompt_template = PROMPT_TEMPLATES.get(content_type, PROMPT_TEMPLATES["comment"])
    prompt = prompt_template.format(content=content)
    
    # Buat request body untuk OpenAI-compatible API
    payload = {
        "model": MODEL_NAME,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
        "stream": False
    }
    
    max_retries = 3
    retry_delay = 1  # <<< CHANGE: Wait time is now 1 second >>>

    for attempt in range(max_retries):
        try:
            response = requests.post(
                LM_STUDIO_URL,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60  # Timeout per request
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content'].strip()
            else:
                # Error dari server, akan coba lagi
                print(f"      Attempt {attempt + 1}/{max_retries} failed with HTTP {response.status_code}: {response.text}")

        except requests.exceptions.RequestException as e:
            # Error koneksi, akan coba lagi
            print(f"      Attempt {attempt + 1}/{max_retries} failed: Could not connect to LM Studio. Error: {e}")
        
        except Exception as e:
            # Error tak terduga lainnya, akan coba lagi
            print(f"      Attempt {attempt + 1}/{max_retries} failed with an unexpected error: {e}")

        # Tunggu sebelum mencoba lagi, kecuali ini adalah percobaan terakhir
        if attempt < max_retries - 1:
            print(f"      Retrying in {retry_delay} second(s)...")
            time.sleep(retry_delay)

    # Jika semua percobaan gagal
    print(f"      Skipping row after {max_retries} failed attempts.")
    return "Error: Failed to process after multiple retries."


# --- MAIN ORCHESTRATOR ---

if __name__ == "__main__":
    print("Starting data cleaning with Local LLM (LM Studio)...")
    print(f"Connecting to: {LM_STUDIO_URL}")
    print(f"Model: {MODEL_NAME}")
    print("="*70)
    
    # Loop melalui setiap konfigurasi file
    for config in FILE_CONFIGS:
        print(f"\nProcessing: {config['name']}")
        print("="*70)
        
        input_file = config["input_file"]
        output_file = config["output_file"]
        content_column = config["content_column"]
        content_type = config["type"]

        # Periksa apakah file input ada
        if not os.path.exists(input_file):
            print(f"ERROR: Input file not found at '{input_file}'. Skipping.")
            continue

        # Baca data menggunakan pandas
        print(f"Reading data from {input_file}...")
        df = pd.read_csv(input_file)

        # Buat kolom baru untuk hasil yang sudah dibersihkan
        df['gemini_summary'] = ''

        print(f"Processing {len(df)} rows with Local LLM...")

        # Loop melalui setiap baris di DataFrame
        for index, row in df.iterrows():
            print(f"    -> Processing row {index + 1}/{len(df)}...")
            
            content = row[content_column]
            
            if pd.notna(content) and len(str(content)) > 10:
                summary = format_text_with_local_llm(str(content), content_type)
                df.at[index, 'gemini_summary'] = summary
            else:
                df.at[index, 'gemini_summary'] = "Content too short or invalid."

        # Simpan DataFrame yang baru ke file CSV baru
        print(f"\nSaving cleaned data to {output_file}...")
        try:
            # Pindahkan kolom gemini_summary ke depan untuk visibilitas
            cols = df.columns.tolist()
            if 'gemini_summary' in cols:
                cols.insert(cols.index(content_column), cols.pop(cols.index('gemini_summary')))
                df = df[cols]

            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Done! Clean data saved to '{output_file}'.")
        except Exception as e:
            print(f"Error saving to CSV: {e}")

    print("\nAll processes complete.")