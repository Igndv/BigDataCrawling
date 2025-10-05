#Remove the example of Preview First Article

import csv
import os
from datetime import datetime

# --- 📜 CONFIGURATION ---

CSV_FILES = {
    "detik": "news_portal/news_detik.csv"
}

# --- 📊 PARSER FUNCTIONS ---

def load_csv_data(csv_file):
    """
    Loads data from a CSV file and returns a list of dictionaries.
    
    Args:
        csv_file (str): Path to CSV file
    
    Returns:
        list: List of article dictionaries
    """
    if not os.path.exists(csv_file):
        print(f"❌ File not found: {csv_file}")
        return []
    
    articles = []
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                articles.append(row)
        
        print(f"✅ Loaded {len(articles)} articles from {csv_file}")
        return articles
    
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return []


def get_statistics(articles):
    """
    Gets basic statistics from the articles.
    
    Args:
        articles (list): List of article dictionaries
    
    Returns:
        dict: Statistics dictionary
    """
    if not articles:
        return {}
    
    # Count by keyword
    keyword_counts = {}
    for article in articles:
        keyword = article.get('keyword', 'Unknown')
        keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    # Count by source
    source_counts = {}
    for article in articles:
        source = article.get('source', 'Unknown')
        source_counts[source] = source_counts.get(source, 0) + 1
    
    # Average content length
    total_length = sum(len(article.get('content', '')) for article in articles)
    avg_length = total_length / len(articles) if articles else 0
    
    # Average paragraph count
    total_paragraphs = sum(int(article.get('paragraph_count', 0)) for article in articles)
    avg_paragraphs = total_paragraphs / len(articles) if articles else 0
    
    return {
        "total_articles": len(articles),
        "keyword_counts": keyword_counts,
        "source_counts": source_counts,
        "avg_content_length": avg_length,
        "avg_paragraph_count": avg_paragraphs
    }


def filter_by_keyword(articles, keyword):
    """
    Filters articles by keyword.
    
    Args:
        articles (list): List of article dictionaries
        keyword (str): Keyword to filter by
    
    Returns:
        list: Filtered articles
    """
    filtered = [a for a in articles if a.get('keyword', '').lower() == keyword.lower()]
    print(f"🔍 Found {len(filtered)} articles for keyword: '{keyword}'")
    return filtered


def filter_by_source(articles, source):
    """
    Filters articles by source.
    
    Args:
        articles (list): List of article dictionaries
        source (str): Source to filter by
    
    Returns:
        list: Filtered articles
    """
    filtered = [a for a in articles if a.get('source', '').lower() == source.lower()]
    print(f"🔍 Found {len(filtered)} articles from source: '{source}'")
    return filtered


def get_article_by_index(articles, index):
    """
    Gets a specific article by index.
    
    Args:
        articles (list): List of article dictionaries
        index (int): Index of article
    
    Returns:
        dict: Article dictionary or None
    """
    if 0 <= index < len(articles):
        return articles[index]
    else:
        print(f"❌ Index {index} out of range (0-{len(articles)-1})")
        return None


def preview_article(article):
    """
    Prints a formatted preview of an article.
    
    Args:
        article (dict): Article dictionary
    """
    if not article:
        print("❌ No article to preview")
        return
    
    print("\n" + "="*70)
    print("📄 ARTICLE PREVIEW")
    print("="*70)
    print(f"Timestamp:    {article.get('timestamp', 'N/A')}")
    print(f"Keyword:      {article.get('keyword', 'N/A')}")
    print(f"Source:       {article.get('source', 'N/A')}")
    print(f"Title:        {article.get('title', 'N/A')}")
    print(f"URL:          {article.get('url', 'N/A')}")
    print(f"Paragraphs:   {article.get('paragraph_count', 'N/A')}")
    print(f"\nContent Preview (first 300 chars):")
    print("-" * 70)
    content = article.get('content', 'N/A')
    print(content[:300] + "..." if len(content) > 300 else content)
    print("="*70)


def print_statistics(stats):
    """
    Prints statistics in a formatted way.
    
    Args:
        stats (dict): Statistics dictionary
    """
    if not stats:
        print("❌ No statistics available")
        return
    
    print("\n" + "="*70)
    print("📊 STATISTICS")
    print("="*70)
    print(f"Total Articles:           {stats['total_articles']}")
    print(f"Avg Content Length:       {stats['avg_content_length']:.0f} characters")
    print(f"Avg Paragraph Count:      {stats['avg_paragraph_count']:.1f}")
    
    print("\n📋 Articles by Keyword:")
    for keyword, count in sorted(stats['keyword_counts'].items(), key=lambda x: x[1], reverse=True):
        print(f"  - {keyword}: {count}")
    
    print("\n📰 Articles by Source:")
    for source, count in stats['source_counts'].items():
        print(f"  - {source}: {count}")
    print("="*70)


# --- 🚦 MAIN ---

if __name__ == "__main__":
    print("🚀 CSV Data Parser for News Scraper")
    print("="*70)
    
    # Load data from Detik
    detik_articles = load_csv_data(CSV_FILES["detik"])
    
    if not detik_articles:
        print("\n❌ No data to parse. Run crawler_berita.py first!")
        exit(1)
    
    # Get and print statistics
    stats = get_statistics(detik_articles)
    print_statistics(stats)
    
    # Preview first article
    print("\n" + "#"*70)
    print("# SAMPLE ARTICLE (First One)")
    print("#"*70)
    first_article = get_article_by_index(detik_articles, 0)
    preview_article(first_article)
    
    # Example: Filter by a specific keyword
    print("\n" + "#"*70)
    print("# FILTERING EXAMPLE")
    print("#"*70)
    if detik_articles:
        sample_keyword = detik_articles[0].get('keyword', '')
        if sample_keyword:
            filtered = filter_by_keyword(detik_articles, sample_keyword)
            if filtered:
                print(f"\nShowing first article for keyword '{sample_keyword}':")
                preview_article(filtered[0])
    
    print("\n✅ Parsing complete!")
    print("\nYou can now import these functions in other scripts:")
    print("  from parse_csv import load_csv_data, get_statistics, filter_by_keyword")