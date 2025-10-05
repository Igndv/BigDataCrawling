# Big Data By Ignasius Deva
# NRP : 5024231003

Topik : #WujudkanIndonesiaDamai

Metode : Crawling Data portal berita dengan BS4 dan Youtube dengan Youtube Data V3 API

--------------------------------------------------------------------------------------
### Keywords ### (Bisa di cek di keywords_config.py) :

Keywords Berita :

    # Kategori 1: Kata Kunci Utama
    "Wujudkan Indonesia Damai",
    "Indonesia Damai",
    "Kampanye Damai",
    "Gerakan Indonesia Damai",
    
    # Kategori 2: Persatuan dan Anti-Perpecahan
    "jaga persatuan bangsa",
    "persatuan dan kesatuan",
    "rekonsiliasi nasional",
    "anti provokasi",
    "stop adu domba",
    
    # Kategori 2: Toleransi dan Kerukunan
    "toleransi beragama",
    "kerukunan umat beragama",
    "dialog lintas agama",
    "moderasi beragama",
    
    # Kategori 2: Anti-Hoax dan Suasana Kondusif
    "anti hoax",
    "anti berita bohong",
    "ciptakan suasana sejuk",
    "pemilu damai",
    "pendinginan pasca pemilu",
    
    # Kategori 3: Kombinasi dengan Institusi
    "Wujudkan Indonesia Damai Polri",
    "kerukunan umat beragama Kemenag",
    "deklarasi damai tokoh masyarakat",
    "pemilu damai KPU Bawaslu",
    "kampanye anti hoax Kominfo"

Keywords Youtube :

    "Webinar Wujudkan Indonesia Damai",
    "Deklarasi kampanye damai",
    "Pesan damai dari tokoh agama",
    "Polri ajak masyarakat jaga persatuan",
    "Liputan berita Indonesia Damai",
    "Podcast tentang toleransi di Indonesia",
    "Dialog kerukunan umat beragama",
    "Kampanye anti hoax Indonesia",
--------------------------------------------------------------------------------------

1. Install to Run :
  The requirements.txt have all of the required dependencies to install

          pip install -r requirements.txt

  dependencies included : request, bs4, python-dotenv, google-api-python-client, pandas, torch, transformers, google-generativeai #On final Product, unused because I am using a local LLM

2. File and Folder Structure :
    Folders :
    - combined_data/                     -   Contains merged and final analysis results
      - combined_all_sources_cleaned.csv - All cleaned data from news + social media
      - final_sentiment_results.csv      - Final output with sentiment analysis
    
    - news_portal/                       - News scraping results
      - news_detik.csv                   - Raw scraped news from Detik
      - news_detik_cleaned.csv           - Gemini-cleaned summaries
    
    - social_media/                      - Social media scraping results
      - youtube.csv                      - Raw YouTube comments
      - youtube_cleaned.csv              - Gemini-cleaned comments
    
    Files:
    - .env                                 - Contains API keys and credentials (Instagram, YouTube API, Gemini API)
    - .gitignore                           - Prevents sensitive files from being committed to git
    - crawler_berita.py                    - Scrapes Detik news articles (title + content)
    - crawler_sosmedYT.py                  - Scrapes YouTube comments using API
    - csv_combiner.py                      - Merges all *_cleaned.csv files into one
    - indobert_process.py                  - Performs sentiment analysis (positive/neutral/negative)
    - keywords_config.py                   - Central configuration for keywords and scraping limits
   
    - gemini.py                            - Cleans and summarizes text using Gemini AI #Before update, because got limited by free tier API
    - localLLM.py                          - NEW : Cleans and summarizes text using --- AI #Before update, because got limited by free tier API
    
4. Workflow :
   - crawler_berita.py → news_portal/news_detik.csv
   - crawler_sosmedYT.py → social_media/youtube.csv

   - localLLM.py (previously gemini.py) → Processes both CSVs:
     - news_detik.csv → news_detik_cleaned.csv
     - youtube.csv → youtube_cleaned.csv

   - csv_combiner.py → Merges all *_cleaned.csv files:
     - combined_data/combined_all_sources_cleaned.csv

   - indobert_process.py → Sentiment analysis:
     - combined_data/final_sentiment_results.csv
    
   - Convert from csv to excel untuk mempermudah pengaksesan oleh tableu

   - dashboard and visualize data with tableu (browser)

5.  Process Visualization :
    1. Crawl Data Berita
       
       ![Start Process](photo/crawler_berita_1.jpg)

       ![Hasil Process](photo/crawler_berita_2.jpg)
    3. Crawl Sosmed Youtube

       ![Start Process](photo/crawler_sosmedYT_1.jpg)

       ![Hasil Process](photo/crawler_sosmedYT_2.jpg)
       
    5. Menggunakan LocalLLM yaitu google/gemma-3-12b untuk memberihkan dan merangkum data
       
       ![Start Process](photo/localLLM_1.jpg)

       ![Local LLM Process recieving and sending data](photo/localLLM_2.jpg)

       ![Hasil Process](photo/localLLM_3.jpg)
       
    7. Combine CSV setelah clean dan dirangkum ke combined data from all source
       
       ![Hasil Process](photo/csv_combiner.jpg)

    9. Dilakukan sentiment analysis oleh Indobert Model
        
        ![Start Process](photo/final_sentiment_result_1.jpg)
       
    11. Convert from csv to excel from website (manually)
        
        ![Ganti nanti](photo/final_sentiment_result_1.jpg)
        
    13. Dashboard and visualize data with Tableu
        
        ![Ganti Nanti](photo/final_sentiment_result_1.jpg)
