import sys

import csv
import os
from datetime import datetime
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Load environment variables
load_dotenv()

# Get API key from .env
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

if not YOUTUBE_API_KEY:
    print("ERROR: YOUTUBE_API_KEY not found in .env file")
    exit(1)

# Output file
OUTPUT_FILE = "social_media/youtube.csv"

# Create directory if not exists
os.makedirs("social_media", exist_ok=True)

# Build YouTube client
yt_client = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)


def search_videos(client, query, max_results=3):
    """Search for videos by keyword"""
    try:
        response = client.search().list(
            part="snippet",
            q=query,
            type="video",
            maxResults=max_results
        ).execute()
        
        video_ids = []
        for item in response.get("items", []):
            video_ids.append(item["id"]["videoId"])
        
        return video_ids
    except HttpError as e:
        print(f"Error searching videos: {e.resp.status}")
        return []


def get_comments(client, video_id, max_results=1500):
    """Get comments from a video"""
    comments = []
    next_token = None
    
    try:
        while len(comments) < max_results:
            response = client.commentThreads().list(
                part="snippet",
                videoId=video_id,
                textFormat="plainText",
                maxResults=min(100, max_results - len(comments)),
                pageToken=next_token,
            ).execute()
            
            comments += response.get("items", [])
            next_token = response.get("nextPageToken")
            
            if not next_token:
                break
        
        return comments[:max_results]
    
    except HttpError as e:
        print(f"Error fetching comments: {e.resp.status}")
        return []


# Collect all comments
all_comments = []

# --- REVISI: Mengambil limit dari SCRAPING_LIMITS di keywords_config.py ---
from keywords_config import YOUTUBE_KEYWORDS, SCRAPING_LIMITS

# --- REVISI: Menambahkan keywords baru untuk mencapai target 1500 komentar ---
ADDITIONAL_YOUTUBE_KEYWORDS = [
    "seruan indonesia damai",
    "ajakan jaga kerukunan",
    "himbauan pasca pemilu",
    "diskusi kebangsaan",
    "peran pemuda untuk perdamaian",
    "menjaga keutuhan NKRI",
    "stop politik identitas",
    "narasi persatuan bangsa",
    "indonesia rukun dan damai",
    "pentingnya toleransi antar umat",
    "kolaborasi membangun negeri",
    "kontra narasi hoaks",
    "menuju indonesia emas damai"
]
# Menggabungkan keywords dari config dengan keywords tambahan
YOUTUBE_KEYWORDS.extend(ADDITIONAL_YOUTUBE_KEYWORDS)


YOUTUBE_VIDEOS_PER_KEYWORD = SCRAPING_LIMITS["youtube_videos_per_keyword"]
YOUTUBE_COMMENTS_PER_VIDEO = SCRAPING_LIMITS["youtube_comments_per_video"]

for keyword in YOUTUBE_KEYWORDS:
    print(f"\nSearching videos for keyword: '{keyword}'")
    
    # Search videos
    video_ids = search_videos(yt_client, keyword, max_results=YOUTUBE_VIDEOS_PER_KEYWORD) # Menggunakan limit dari config
    
    if not video_ids:
        print(f"   No videos found for '{keyword}'")
        continue
    
    print(f"   Found {len(video_ids)} videos")
    
    # Get comments from each video
    for vid_id in video_ids:
        print(f"   Fetching comments from video: {vid_id}")
        comments = get_comments(yt_client, vid_id, max_results=YOUTUBE_COMMENTS_PER_VIDEO) # Menggunakan limit dari config
        
        for comment in comments:
            snippet = comment["snippet"]["topLevelComment"]["snippet"]
            
            all_comments.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "keyword": keyword,
                "source": "YouTube",
                "video_url": f"https://www.youtube.com/watch?v={vid_id}",
                "commenter_name": snippet["authorDisplayName"],
                "comment_text": snippet["textDisplay"],
                "comment_date": snippet["publishedAt"]
            })
        
        print(f"     Collected {len(comments)} comments")

# Save to CSV
print(f"\nTotal comments collected: {len(all_comments)}")

if all_comments:
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as file:
        fieldnames = ["timestamp", "keyword", "source", "video_url", "commenter_name", "comment_text", "comment_date"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_comments)
    
    print(f"Saved to {OUTPUT_FILE}")
else:
    print("No comments collected")

