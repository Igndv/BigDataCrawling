# ========================================
# KEYWORDS CONFIGURATION
# Tema: #WujudkanIndonesiaDamai
# ========================================

# --- KEYWORDS FOR NEWS PORTALS (BBC, Detik, Hukumonline) ---
# Use these with requests + BeautifulSoup
NEWS_KEYWORDS = [
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
    "kampanye anti hoax Kominfo",
]

# --- KEYWORDS FOR INSTAGRAM ---
# Use these with Selenium (hashtag search)
INSTAGRAM_HASHTAGS = [
    "WujudkanIndonesiaDamai",
    "IndonesiaDamai",
    "JagaPersatuan",
    "KerukunanBangsa",
    "TolakProvokasi",
    "PemiluDamai2024",
    "Toleransi",
    "StopHoax",
]

# --- KEYWORDS FOR YOUTUBE ---
# Use these with Selenium (search queries)
YOUTUBE_KEYWORDS = [
    "Webinar Wujudkan Indonesia Damai",
    "Deklarasi kampanye damai",
    "Pesan damai dari tokoh agama",
    "Polri ajak masyarakat jaga persatuan",
    "Liputan berita Indonesia Damai",
    "Podcast tentang toleransi di Indonesia",
    "Dialog kerukunan umat beragama",
    "Kampanye anti hoax Indonesia",
]

# --- SCRAPING LIMITS CONFIGURATION ---
# Adjust these values to control how much data to collect
SCRAPING_LIMITS = {
    # Instagram limits
    "instagram_posts_per_hashtag": 5,         # How many posts to scrape per hashtag
    "instagram_comments_per_post": 50,        # How many comments to collect per post
    "instagram_max_scroll_attempts": 3,       # How many times to scroll on hashtag page
    
    # YouTube limits
    "youtube_videos_per_keyword": 3,          # How many videos to scrape per keyword
    "youtube_comments_per_video": 50,         # How many comments to collect per video
    "youtube_max_scroll_attempts": 10,        # How many times to scroll for comments
    
    # News portal limits
    "news_articles_per_keyword": 5,           # How many articles to scrape per keyword
}

# --- KEYWORD LIMITS FOR TESTING ---
# You can limit how many keywords to process for testing
LIMIT_NEWS_KEYWORDS = None  # Set to a number (e.g., 5) to limit, or None for all
LIMIT_INSTAGRAM_HASHTAGS = None
LIMIT_YOUTUBE_KEYWORDS = None

# Apply limits if set
if LIMIT_NEWS_KEYWORDS:
    NEWS_KEYWORDS = NEWS_KEYWORDS[:LIMIT_NEWS_KEYWORDS]
if LIMIT_INSTAGRAM_HASHTAGS:
    INSTAGRAM_HASHTAGS = INSTAGRAM_HASHTAGS[:LIMIT_INSTAGRAM_HASHTAGS]
if LIMIT_YOUTUBE_KEYWORDS:
    YOUTUBE_KEYWORDS = YOUTUBE_KEYWORDS[:LIMIT_YOUTUBE_KEYWORDS]