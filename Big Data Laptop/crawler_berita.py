import requests
from bs4 import BeautifulSoup
import time
import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from keywords_config import NEWS_KEYWORDS, SCRAPING_LIMITS

# Load environment variables from .env file
load_dotenv()

# Create directories if they don't exist
os.makedirs("news_portal", exist_ok=True)
os.makedirs("social_media", exist_ok=True)

# --- 📜 CONFIGURATION ---

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Cache-Control': 'max-age=0'
}

# Scraping limits - adjust these to control article collection
MAX_ARTICLES_PER_KEYWORD = 30  # Increase to 30 per keyword per site
MAX_LINKS_TO_SCRAPE = 100  # Maximum links to try per search
TARGET_TOTAL_ARTICLES = 1000  # Overall target - 1000 articles

# News site configurations with search URL and selectors
NEWS_SITES = {
    "detik": {
        "search_url": "https://www.detik.com/search/searchall?query={}&page={}",  # Added pagination
        "article_selector": "article",
        "link_selector": "a",
        "title_in_article": "h2",
        "full_title_selector": {"tag": "h1", "class": "detail__title"},
        "content_selector": {"tag": "div", "class": "detail__body-text"},
        "paragraph_selector": "p",
        "csv_file": "news_portal/news_detik.csv",
        "max_pages": 5  # Scrape multiple pages of search results
    }
}

def save_to_csv(articles, csv_file):
    """
    Saves scraped articles to CSV file (overwrites existing file).
    """
    if not articles:
        print(f"⚠️  No articles to save for {csv_file}")
        return
    
    # CSV headers
    fieldnames = ['timestamp', 'keyword', 'source', 'title', 'url', 'content', 'paragraph_count']
    
    try:
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for article in articles:
                writer.writerow({
                    'timestamp': article.get('timestamp', ''),
                    'keyword': article.get('keyword', ''),
                    'source': article.get('source', ''),
                    'title': article.get('title', ''),
                    'url': article.get('url', ''),
                    'content': article.get('content', ''),
                    'paragraph_count': article.get('paragraph_count', 0)
                })
        
        print(f"💾 Saved {len(articles)} articles to {csv_file}")
    
    except Exception as e:
        print(f"❌ Error saving to CSV: {e}")


def get_article_links_paginated(keyword, site_name, site_config, articles_needed):
    """
    Gets article links from search results with pagination support.
    Continues scraping pages until we have enough articles.
    """
    print(f"\n--- [Step 1] Getting article links from {site_name} for '{keyword}' ---")
    print(f"   Target: {articles_needed} articles")
    
    all_links = []
    max_pages = site_config.get("max_pages", 5)
    
    for page in range(1, max_pages + 1):
        if len(all_links) >= articles_needed * 2:  # Get extra links as backup
            break
            
        try:
            # Format search URL with pagination
            if '{}' in site_config["search_url"]:
                # Check if URL has two placeholders (keyword and page)
                if site_config["search_url"].count('{}') == 2:
                    search_url = site_config["search_url"].format(
                        keyword.replace(' ', '+'), 
                        page
                    )
                else:
                    # Only keyword placeholder
                    search_url = site_config["search_url"].format(keyword.replace(' ', '+'))
            else:
                search_url = site_config["search_url"]
            
            print(f"   📄 Page {page}/{max_pages}: {search_url[:80]}...")
            
            response = requests.get(search_url, headers=HEADERS, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            articles = soup.find_all(site_config["article_selector"].split('[')[0])
            
            if not articles:
                print(f"   ⚠️  No articles found on page {page}")
                break

            page_links = []
            for article in articles:
                link_tag = article.find(site_config["link_selector"])
                if link_tag and link_tag.get('href'):
                    url = link_tag['href']
                    # Make sure URL is absolute
                    if url.startswith('/'):
                        base_domain = f"https://www.{site_name}"
                        url = base_domain + url
                    elif not url.startswith('http'):
                        url = f"https://www.{site_name}/{url}"
                    
                    # Avoid duplicates
                    if url not in all_links:
                        page_links.append(url)
            
            all_links.extend(page_links)
            print(f"   ✓ Found {len(page_links)} new links (total: {len(all_links)})")
            
            # Small delay between pages
            time.sleep(2)

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error on page {page}: {e}")
            break
    
    # Limit to what we need
    all_links = all_links[:articles_needed]
    print(f"✅ Total links collected: {len(all_links)}")
    return all_links


def scrape_article_content(url, site_name, site_config):
    """
    Scrapes full content (title and paragraphs) from an article URL.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract title
        title_config = site_config["full_title_selector"]
        title_tag = None
        
        if "id" in title_config:
            title_tag = soup.find(title_config["tag"], id=title_config["id"])
        elif "class" in title_config:
            title_tag = soup.find(title_config["tag"], class_=title_config["class"])
        else:
            title_tag = soup.find(title_config["tag"])
            
        title = title_tag.get_text(strip=True) if title_tag else "No title found"

        # Extract content paragraphs
        content_config = site_config["content_selector"]
        content_div = None
        
        if "id" in content_config:
            content_div = soup.find(content_config["tag"], id=content_config["id"])
        elif "class" in content_config:
            content_div = soup.find(content_config["tag"], class_=content_config["class"])
        else:
            content_div = soup.find(content_config["tag"])
        
        paragraphs = []
        if content_div:
            para_config = site_config["paragraph_selector"]
            if isinstance(para_config, dict):
                para_tags = content_div.find_all(para_config["tag"], class_=para_config.get("class"))
            else:
                para_tags = content_div.find_all(para_config)
            
            paragraphs = [p.get_text(strip=True) for p in para_tags if p.get_text(strip=True)]

        # Combine all paragraphs into full content
        full_content = "\n".join(paragraphs) if paragraphs else "No content found"

        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "title": title,
            "url": url,
            "content": full_content,
            "paragraph_count": len(paragraphs),
            "source": site_name
        }

    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Error scraping article: {e}")
        return None
    except Exception as e:
        print(f"   ⚠️  Parsing error: {e}")
        return None


def scrape_news_site(keyword, site_name, site_config, articles_needed):
    """
    Main function to scrape a news site: get links, then scrape each article.
    """
    print(f"\n{'='*70}")
    print(f"🔍 Scraping {site_name} for keyword: '{keyword}'")
    print(f"   Target: {articles_needed} articles")
    print(f"{'='*70}")
    
    # Step 1: Get article links with pagination
    article_links = get_article_links_paginated(keyword, site_name, site_config, articles_needed)
    
    if not article_links:
        return []
    
    # Step 2: Scrape each article
    scraped_articles = []
    for i, link in enumerate(article_links, 1):
        print(f"\n[Article {i}/{len(article_links)}] {link[:60]}...")
        article_data = scrape_article_content(link, site_name, site_config)
        if article_data:
            article_data["keyword"] = keyword
            scraped_articles.append(article_data)
            print(f"   ✅ Title: {article_data['title'][:60]}...")
            print(f"   📝 Paragraphs: {article_data['paragraph_count']}")
        
        # Polite delay between articles
        time.sleep(1)  # Reduced from 1.5 to 1 second for faster scraping
        
        # Stop if we've reached our target for this keyword
        if len(scraped_articles) >= articles_needed:
            break
    
    return scraped_articles


# --- 🚦 MAIN ORCHESTRATOR ---

if __name__ == "__main__":
    print("🚀 Starting Enhanced News Web Scraper...")
    print(f"📋 Total keywords to process: {len(NEWS_KEYWORDS)}")
    print(f"📰 News sites: {', '.join(NEWS_SITES.keys())}")
    print(f"🎯 Target: {TARGET_TOTAL_ARTICLES} total articles")
    print(f"📊 Strategy: {MAX_ARTICLES_PER_KEYWORD} articles per keyword per site\n")
    
    # Dictionary to store articles per site
    articles_by_site = {site: [] for site in NEWS_SITES.keys()}
    
    # Calculate distribution
    total_keywords = len(NEWS_KEYWORDS)
    total_sites = len(NEWS_SITES)
    articles_per_keyword_site = MAX_ARTICLES_PER_KEYWORD
    
    print(f"📐 Calculation:")
    print(f"   {total_keywords} keywords × {total_sites} sites × {articles_per_keyword_site} articles")
    print(f"   = ~{total_keywords * total_sites * articles_per_keyword_site} maximum articles\n")
    
    total_scraped = 0
    
    for keyword_idx, keyword in enumerate(NEWS_KEYWORDS, 1):
        print(f"\n\n{'#'*70}")
        print(f"# Keyword {keyword_idx}/{total_keywords}: '{keyword}'")
        print(f"# Progress: {total_scraped}/{TARGET_TOTAL_ARTICLES} articles collected")
        print(f"{'#'*70}")
        
        # Check if we've reached target
        if total_scraped >= TARGET_TOTAL_ARTICLES:
            print(f"\n🎉 Target of {TARGET_TOTAL_ARTICLES} articles reached! Stopping.")
            break
        
        # Scrape each news site
        for site_name, site_config in NEWS_SITES.items():
            # Calculate how many more articles we need
            remaining_target = TARGET_TOTAL_ARTICLES - total_scraped
            articles_to_get = min(articles_per_keyword_site, remaining_target)
            
            if articles_to_get <= 0:
                break
                
            articles = scrape_news_site(keyword, site_name, site_config, articles_to_get)
            articles_by_site[site_name].extend(articles)
            total_scraped += len(articles)
            
            print(f"\n   📊 Site summary: {len(articles)} articles scraped")
            print(f"   🎯 Overall progress: {total_scraped}/{TARGET_TOTAL_ARTICLES}")
            
            time.sleep(3)  # Delay between sites
    
    print("\n\n" + "="*70)
    print(f"✅ Web Scraping Complete!")
    print("="*70)
    
    # Save each site's articles to its respective CSV file
    for site_name, site_config in NEWS_SITES.items():
        articles = articles_by_site[site_name]
        csv_file = site_config['csv_file']
        save_to_csv(articles, csv_file)
        print(f"   {site_name}: {len(articles)} articles → {csv_file}")
    
    # Calculate total
    total_articles = sum(len(articles) for articles in articles_by_site.values())
    print(f"\n📊 Total articles scraped: {total_articles}")
    print(f"🎯 Target achievement: {(total_articles/TARGET_TOTAL_ARTICLES*100):.1f}%")
    print("="*70)
    
    # Show statistics per keyword
    print("\n📈 Statistics by keyword:")
    keyword_stats = {}
    for articles in articles_by_site.values():
        for article in articles:
            kw = article['keyword']
            if kw not in keyword_stats:
                keyword_stats[kw] = 0
            keyword_stats[kw] += 1
    
    for kw, count in sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True):
        print(f"   {kw}: {count} articles")
    
    # Preview first article
    first_article = None
    for articles in articles_by_site.values():
        if articles:
            first_article = articles[0]
            break
    
    if first_article:
        print("\n📄 Sample Article (first one):")
        print(f"   Source: {first_article['source']}")
        print(f"   Keyword: {first_article['keyword']}")
        print(f"   Title: {first_article['title'][:100]}...")
        print(f"   Content length: {len(first_article['content'])} characters")
        print(f"   Paragraphs: {first_article['paragraph_count']}")