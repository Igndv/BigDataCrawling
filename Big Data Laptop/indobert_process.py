import sys

import pandas as pd
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import os


# Model IndoBERT yang telah di-fine-tune khusus untuk analisis sentimen 3 kelas (positive, neutral, negative)
MODEL_NAME = "mdhugol/indonesia-bert-sentiment-classification"

# File input (output dari combine_csv.py)
INPUT_CSV_FILE = "combined_data/combined_all_sources_cleaned.csv"
# File output akhir dengan hasil sentimen
OUTPUT_CSV_FILE = "combined_data/final_sentiment_results.csv"

# Kolom yang akan dianalisis
TEXT_COLUMN_TO_ANALYZE = "gemini_summary"

# --- FUNGSI HELPER ---

def map_label_to_readable(label):
    """
    Maps model output labels (LABEL_0, LABEL_1, LABEL_2) to readable sentiment names.
    Model mdhugol/indonesia-bert-sentiment-classification outputs:
    - LABEL_0 = positive
    - LABEL_1 = neutral
    - LABEL_2 = negative
    """
    label_map = {
        'LABEL_0': 'positive',
        'LABEL_1': 'neutral',
        'LABEL_2': 'negative',
        'positive': 'positive',
        'neutral': 'neutral',
        'negative': 'negative'
    }
    return label_map.get(label, label)

# --- FUNGSI UNTUK PREDIKSI SENTIMEN ---

def predict_sentiment(texts, model, tokenizer):
    """
    Menerima daftar teks dan mengembalikan daftar label sentimen dan skor kepercayaan.
    """
    results = []
    # Menggunakan 'no_grad' untuk mempercepat proses karena kita tidak melakukan training
    with torch.no_grad():
        for i, text in enumerate(texts):
            # Memberi tahu pengguna tentang progres
            if (i + 1) % 10 == 0:
                print(f"   Processing text {i+1}/{len(texts)}...")
            
            try:
                # Tokenisasi: mengubah teks menjadi format yang dimengerti model
                inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
                
                # Prediksi: memasukkan input ke model
                outputs = model(**inputs)
                
                # Mendapatkan probabilitas sentimen dengan softmax
                scores = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
                # Mendapatkan label dengan skor tertinggi
                predicted_class_id = torch.argmax(scores).item()
                confidence_score = scores[0][predicted_class_id].item()
                
                # Mendapatkan nama label dari ID (e.g., 0 -> 'LABEL_0')
                raw_label = model.config.id2label[predicted_class_id]
                
                # Map ke format yang mudah dibaca (positive/neutral/negative)
                label = map_label_to_readable(raw_label)
                
                results.append({"sentiment_label": label, "sentiment_score": confidence_score})
            except Exception as e:
                print(f"   ⚠️  Skipping text due to error: {e}")
                results.append({"sentiment_label": "error", "sentiment_score": 0.0})

    return results

# --- 🚦 SKRIP UTAMA ---

if __name__ == "__main__":
    print("🚀 Memulai proses analisis sentimen dengan IndoBERT...")
    print(f"MODEL: {MODEL_NAME}")

    # 1. Cek apakah file input ada
    if not os.path.exists(INPUT_CSV_FILE):
        print(f"❌ KESALAHAN: File input tidak ditemukan di '{INPUT_CSV_FILE}'.")
        print("Silakan jalankan combine_csv.py terlebih dahulu untuk menggabungkan data.")
        exit()

    # 2. Muat data yang sudah digabungkan
    print(f"📖 Membaca data dari '{INPUT_CSV_FILE}'...")
    df = pd.read_csv(INPUT_CSV_FILE)

    # Pastikan kolom teks ada
    if TEXT_COLUMN_TO_ANALYZE not in df.columns:
        print(f"❌ KESALAHAN: Kolom '{TEXT_COLUMN_TO_ANALYZE}' tidak ditemukan di CSV.")
        exit()
        
    # Hapus baris dengan ringkasan yang kosong atau tidak valid
    df.dropna(subset=[TEXT_COLUMN_TO_ANALYZE], inplace=True)

    # 3. Muat model dan tokenizer IndoBERT dari Hugging Face
    print("🤖 Memuat model dan tokenizer IndoBERT... (Mungkin perlu waktu saat pertama kali)")
    try:
        tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
        model.eval()  # Set model ke mode evaluasi
    except Exception as e:
        print(f"❌ KESALAHAN: Tidak bisa memuat model. Periksa koneksi internet atau nama model. Detail: {e}")
        exit()

    # 4. Lakukan prediksi sentimen
    print(f"\n✍️  Menganalisis sentimen pada kolom '{TEXT_COLUMN_TO_ANALYZE}'...")
    
    texts_to_analyze = df[TEXT_COLUMN_TO_ANALYZE].tolist()
    sentiment_results = predict_sentiment(texts_to_analyze, model, tokenizer)
    
    # Buat DataFrame baru dari hasil sentimen
    sentiment_df = pd.DataFrame(sentiment_results)
    
    # Gabungkan DataFrame asli dengan hasil sentimen
    # Pastikan indexnya sesuai
    df.reset_index(drop=True, inplace=True)
    sentiment_df.reset_index(drop=True, inplace=True)
    df_final = pd.concat([df, sentiment_df], axis=1)

    # 5. Simpan hasil akhir
    print(f"\n💾 Menyimpan hasil akhir ke '{OUTPUT_CSV_FILE}'...")
    try:
        df_final.to_csv(OUTPUT_CSV_FILE, index=False, encoding='utf-8')
        print("✅ Proses analisis sentimen selesai!")
        print(f"📊 Total baris yang diproses: {len(df_final)}")
        print(f"💾 File hasil akhir Anda siap di: '{OUTPUT_CSV_FILE}'")
    except Exception as e:
        print(f"❌ Kesalahan saat menyimpan file CSV akhir: {e}")

    # --- TAMBAHAN: Tampilkan Ringkasan Sentimen ---
    print("\n" + "="*50)
    print("📊 Ringkasan Hasil Analisis Sentimen:")
    print("="*50)

    # Hitung jumlah setiap label sentimen
    sentiment_counts = df_final['sentiment_label'].value_counts()

    positive_count = sentiment_counts.get('positive', 0)
    neutral_count = sentiment_counts.get('neutral', 0)
    negative_count = sentiment_counts.get('negative', 0)
    error_count = sentiment_counts.get('error', 0)

    print(f"👍 Positive : {positive_count} berita")
    print(f"😐 Neutral  : {neutral_count} berita")
    print(f"👎 Negative : {negative_count} berita")
    
    if error_count > 0:
        print(f"⚠️  Error   : {error_count} berita (gagal diproses)")

    print("="*50)