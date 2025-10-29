import os
import requests
from pathlib import Path
import time
import re

class WallpaperDownloader:
    """
    Agnostic downloader for high-quality wallpapers from free, open sources 
    (Reddit, Unsplash, Wallhaven).
    """
    def __init__(self, output_folder="AgnosticWallpapers"):
        self.output_folder = output_folder
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.downloaded_count = 0
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
    
    def get_output_path(self):
        """Return the absolute path to the output folder"""
        return os.path.abspath(self.output_folder)
    
    def download_image(self, url, filename_prefix, query=""):
        """Download a single image and enforce minimum quality (size)"""
        try:
            # Sanitize query for filename
            safe_query = re.sub(r'[^\w\-_\. ]', '', query).replace(' ', '_')
            filename = f"{filename_prefix}_{safe_query}_{self.downloaded_count + 1}.jpg"
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
            print(f"✓ ({file_size_kb:.0f}KB)")
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False

    def search_wallhaven(self, query, limit=10):
        """Scrape Wallhaven using its search endpoint and high-res filter."""
        print(f"\n{'='*60}\n🔎 Searching Wallhaven for: {query}\n{'='*60}\n")
        
        pages = (limit // 24) + 1  # Wallhaven returns ~24 per page
        downloaded = 0
        
        for page in range(1, pages + 1):
            if downloaded >= limit:
                break
                
            url = "https://wallhaven.cc/api/v1/search"
            params = {
                'q': query,
                'categories': '111',
                'purity': '100',
                'resolutions': '1920x1080',
                'sorting': 'toplist', 
                'order': 'desc',
                'page': page
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                wallpapers = data.get('data', [])
                if not wallpapers:
                    break
                    
                for w in wallpapers:
                    if downloaded >= limit:
                        break
                    img_url = w.get('path')
                    if self.download_image(img_url, "wallhaven", query):
                        downloaded += 1
                    time.sleep(0.5)
            
            except Exception as e:
                print(f"❌ Error with Wallhaven API on page {page}: {e}")
                break
        
        return downloaded

    def search_reddit(self, query, limit=10):
        """Download from Reddit's wallpaper subreddits (NO API KEY REQUIRED)"""
        print(f"\n{'='*60}\n🔎 Searching Reddit for: {query}\n{'='*60}\n")
        
        subreddits = ['wallpaper', 'wallpapers', 'WidescreenWallpaper']
        downloaded = 0
        
        for subreddit in subreddits:
            if downloaded >= limit:
                break
                
            url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                'q': query,
                'restrict_sr': 'on',
                'limit': min(25, limit - downloaded),
                'sort': 'top',
                't': 'all'
            }
            
            try:
                response = requests.get(url, headers=self.headers, params=params, timeout=10)
                response.raise_for_status()
                data = response.json()
                
                for post in data.get('data', {}).get('children', []):
                    if downloaded >= limit:
                        break
                        
                    post_data = post['data']
                    img_url = post_data.get('url_overridden_by_dest') or post_data.get('url')
                    
                    if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png', 'i.redd.it']):
                        if self.download_image(img_url, "reddit", query):
                            downloaded += 1
                        time.sleep(1)
                            
            except Exception as e:
                print(f"❌ Error with Reddit r/{subreddit}: {e}")
        
        return downloaded

    def search_unsplash(self, query, limit=10):
        """Search Unsplash (NO API KEY NEEDED)"""
        print(f"\n{'='*60}\n🔎 Searching Unsplash Source for: {query}\n{'='*60}\n")
        
        downloaded = 0
        query_variants = [query, query.replace(" ", "-"), query.replace(" ", "+")]
        
        for q in query_variants:
            if downloaded >= limit:
                break
                
            for i in range(1, limit + 1):
                if downloaded >= limit:
                    break
                    
                url = f"https://source.unsplash.com/1920x1080/?{q},{i}"
                
                if self.download_image(url, "unsplash", query):
                    downloaded += 1
                
                time.sleep(1)
        
        return downloaded


def main_scraper_cli():
    print("--- Agnostic Wallpaper Downloader (Wallhaven, Reddit, Unsplash) ---")
    
    search_term = input("➤ Enter the type of wallpaper you want (e.g., 'Arch Linux' or 'Initial D'): ")
    if not search_term.strip():
        print("Search term cannot be empty. Exiting.")
        return
        
    downloader = WallpaperDownloader(f"{search_term}_Wallpapers")

    # Run Scrapers
    downloader.search_wallhaven(search_term, limit=10)
    downloader.search_reddit(search_term, limit=10)
    downloader.search_unsplash(search_term, limit=5)
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 Download Complete!")
    print(f"✓ Total images downloaded: **{downloader.downloaded_count}**")
    print(f"✓ Location: **{downloader.get_output_path()}**")
    print(f"{'='*60}\n")
    

if __name__ == "__main__":
    main_scraper_cli()
