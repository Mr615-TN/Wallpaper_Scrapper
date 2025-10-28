import os
import requests
from pathlib import Path
import time
import re
from bs4 import BeautifulSoup
import shutil

class WallpaperDownloader:
    """
    Agnostic downloader for high-quality wallpapers from free, open sources 
    (Reddit, Unsplash, Wallhaven).
    """
    def __init__(self, query, output_folder_suffix="Wallpapers"):
        # Sanitize query for folder name
        safe_query = re.sub(r'[^\w\-_\. ]', '', query).replace(' ', '_')
        self.query = query
        self.output_folder = f"{safe_query}_{output_folder_suffix}"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.downloaded_count = 0
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
    
    def download_image(self, url, filename_prefix):
        """Download a single image and enforce minimum quality (size)"""
        try:
            filename = f"{filename_prefix}_{self.downloaded_count + 1}.jpg"
            print(f"Downloading: {filename}...", end=" ")
            
            response = requests.get(url, headers=self.headers, timeout=20, stream=True)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                print(f"✗ Not an image (Content-Type: {content_type})")
                return False
            
            filepath = os.path.join(self.output_folder, filename)
            
            file_size_bytes = 0
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
                    file_size_bytes += len(chunk)
            
            # QUALITY CHECK: File size must be at least 100KB (102400 bytes)
            file_size_kb = file_size_bytes / 1024
            if file_size_bytes < 102400: 
                os.remove(filepath)
                print(f"✗ Too small ({file_size_kb:.0f}KB) - Removed")
                return False
            
            self.downloaded_count += 1
            print(f"✓ ({file_size_kb:.0f}KB) - URL: {url[:50]}...")
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    # --- NEW: Wallhaven Scraper (Free) ---
    def search_wallhaven(self, pages=2):
        """Scrape Wallhaven using its search endpoint and high-res filter."""
        print(f"\n{'='*60}\n🔍 Searching Wallhaven for: {self.query}\n{'='*60}\n")
        
        for page in range(1, pages + 1):
            url = "https://wallhaven.cc/api/v1/search"
            params = {
                'q': self.query,
                'categories': '111', # General, Anime, People
                'purity': '100',     # SFW, Sketchy (excludes NSFW)
                'resolutions': '1920x1080', # Minimum 1080p
                'sorting': 'toplist', 
                'order': 'desc',
                'page': page
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params)
                response.raise_for_status()
                data = response.json()
                
                wallpapers = data.get('data', [])
                if not wallpapers:
                    print(f"No more results found on page {page}.")
                    break
                    
                for w in wallpapers:
                    # Wallhaven provides direct download URL for the original image size
                    img_url = w.get('path') 
                    self.download_image(img_url, "wallhaven")
                    time.sleep(0.5)
            
            except Exception as e:
                print(f"❌ Error with Wallhaven API on page {page}: {e}")
                
    # --- Reddit Scraper (Free) ---
    def download_from_reddit(self, subreddit, limit=50):
        """Download from Reddit's wallpaper subreddits (NO API KEY REQUIRED)"""
        print(f"\n{'='*60}\n🔍 Searching Reddit r/{subreddit} for: {self.query}\n{'='*60}\n")
        
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': self.query,
            'restrict_sr': 'on',
            'limit': limit,
            'sort': 'top'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            for post in data.get('data', {}).get('children', []):
                post_data = post['data']
                img_url = post_data.get('url_overridden_by_dest') or post_data.get('url')
                
                if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', 'i.redd.it']):
                    self.download_image(img_url, "reddit")
                    time.sleep(1)
                        
        except Exception as e:
            print(f"❌ Error with Reddit: {e}")

    # --- Unsplash Scraper (Free) ---
    def search_unsplash(self, per_page=5):
        """Search Unsplash (NO API KEY NEEDED)"""
        print(f"\n{'='*60}\n🔍 Searching Unsplash Source for: {self.query}\n{'='*60}\n")
        images_found = 0
        queries = [self.query, self.query.replace(" ", "-")]
        
        for q in queries:
            if images_found >= per_page: break
                
            for i in range(1, per_page + 1):
                if images_found >= per_page: break
                    
                # Forces 1920x1080 resolution for high quality
                url = f"https://source.unsplash.com/1920x1080/?{q},{i}"
                
                if self.download_image(url, "unsplash"):
                    images_found += 1
                
                time.sleep(1) # Be respectful

def main_scraper_cli():
    print("--- Agnostic Wallpaper Downloader (Wallhaven, Reddit, Unsplash) ---")
    
    search_term = input("❓ Enter the type of wallpaper you want (e.g., 'Arch Linux' or 'Initial D'): ")
    if not search_term.strip():
        print("Search term cannot be empty. Exiting.")
        return
        
    downloader = WallpaperDownloader(search_term)

    # --- Run Scrapers ---
    downloader.search_wallhaven(pages=2) # Wallhaven
    downloader.download_from_reddit('wallpaper', limit=20) # Reddit
    downloader.search_unsplash(per_page=5) # Unsplash
    
    # --- Summary ---
    print(f"\n{'='*60}")
    print(f"🎉 Download Complete!")
    print(f"✓ Total images downloaded: **{downloader.downloaded_count}**")
    print(f"✓ Location: **{os.path.abspath(downloader.output_folder)}**")
    print(f"{'='*60}\n")
    

if __name__ == "__main__":
    main_scraper_cli()
