import os
import requests
from pathlib import Path
import time
import json

class InitialDWallpaperDownloader:
    def __init__(self, output_folder="InitialDWallpapers"):
        self.output_folder = output_folder
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.downloaded_count = 0
        Path(self.output_folder).mkdir(parents=True, exist_ok=True)
    
    def download_image(self, url, filename):
        """Download a single image"""
        try:
            print(f"Downloading: {filename}...", end=" ")
            response = requests.get(url, headers=self.headers, timeout=20)
            response.raise_for_status()
            
            # Check if it's actually an image
            content_type = response.headers.get('content-type', '')
            if 'image' not in content_type.lower():
                print(f"✗ Not an image (Content-Type: {content_type})")
                return False
            
            filepath = os.path.join(self.output_folder, filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            # Check file size (should be at least 100KB for quality wallpaper)
            file_size = os.path.getsize(filepath) / 1024  # KB
            if file_size < 100:
                os.remove(filepath)
                print(f"✗ Too small ({file_size:.0f}KB)")
                return False
            
            self.downloaded_count += 1
            print(f"✓ ({file_size:.0f}KB)")
            return True
            
        except Exception as e:
            print(f"✗ Error: {e}")
            return False
    
    def search_unsplash(self, query, per_page=30):
        """Search Unsplash for images (no API key needed for basic search)"""
        print(f"\n{'='*60}")
        print(f"Searching Unsplash for: {query}")
        print(f"{'='*60}\n")
        
        # Unsplash source URL format (for random images by topic)
        images_found = 0
        
        # Try multiple variations
        queries = [query, query.replace(" ", "-"), query.replace(" ", "+")]
        
        for q in queries:
            # Unsplash Source API (free, no key required)
            for i in range(1, per_page + 1):
                if images_found >= per_page:
                    break
                    
                # Use Unsplash random with query
                url = f"https://source.unsplash.com/1920x1080/?{q},{i}"
                filename = f"initiald_{images_found + 1}.jpg"
                
                if self.download_image(url, filename):
                    images_found += 1
                
                time.sleep(1)  # Be respectful
    
    def search_pixabay(self, api_key, query, per_page=50):
        """Search Pixabay (requires free API key from pixabay.com/api/docs/)"""
        print(f"\n{'='*60}")
        print(f"Searching Pixabay for: {query}")
        print(f"{'='*60}\n")
        
        url = "https://pixabay.com/api/"
        params = {
            'key': api_key,
            'q': query,
            'image_type': 'photo',
            'min_width': 1920,
            'min_height': 1080,
            'per_page': per_page
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data['totalHits'] == 0:
                print("No images found.")
                return
            
            print(f"Found {data['totalHits']} images\n")
            
            for idx, hit in enumerate(data['hits'], 1):
                # Get the large image URL
                img_url = hit.get('largeImageURL') or hit.get('webformatURL')
                filename = f"initiald_pixabay_{idx}.jpg"
                
                self.download_image(img_url, filename)
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error with Pixabay API: {e}")
    
    def search_pexels(self, api_key, query, per_page=30):
        """Search Pexels (requires free API key from pexels.com/api/)"""
        print(f"\n{'='*60}")
        print(f"Searching Pexels for: {query}")
        print(f"{'='*60}\n")
        
        url = "https://api.pexels.com/v1/search"
        headers = {
            'Authorization': api_key
        }
        params = {
            'query': query,
            'per_page': per_page,
            'orientation': 'landscape'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data.get('photos'):
                print("No images found.")
                return
            
            print(f"Found {len(data['photos'])} images\n")
            
            for idx, photo in enumerate(data['photos'], 1):
                # Get the original or large2x image
                img_url = photo['src'].get('original') or photo['src'].get('large2x')
                filename = f"initiald_pexels_{idx}.jpg"
                
                self.download_image(img_url, filename)
                time.sleep(0.5)
                
        except Exception as e:
            print(f"Error with Pexels API: {e}")
    
    def download_from_reddit(self, subreddit, query, limit=50):
        """Download from Reddit (no API key needed for basic access)"""
        print(f"\n{'='*60}")
        print(f"Searching Reddit r/{subreddit} for: {query}")
        print(f"{'='*60}\n")
        
        # Reddit JSON endpoint (works without API key)
        url = f"https://www.reddit.com/r/{subreddit}/search.json"
        params = {
            'q': query,
            'restrict_sr': 'on',
            'limit': limit,
            'sort': 'top'
        }
        
        try:
            response = requests.get(url, headers=self.headers, params=params)
            response.raise_for_status()
            data = response.json()
            
            posts = data['data']['children']
            print(f"Found {len(posts)} posts\n")
            
            for idx, post in enumerate(posts, 1):
                post_data = post['data']
                
                # Check if post has image
                if post_data.get('post_hint') == 'image':
                    img_url = post_data.get('url')
                    if img_url and any(ext in img_url.lower() for ext in ['.jpg', '.jpeg', '.png']):
                        filename = f"initiald_reddit_{idx}.jpg"
                        self.download_image(img_url, filename)
                        time.sleep(1)
                        
        except Exception as e:
            print(f"Error with Reddit: {e}")


def main():
    print("""
╔══════════════════════════════════════════════════════════╗
║         Initial D Wallpaper Downloader v2.0             ║
╚══════════════════════════════════════════════════════════╝
    """)
    
    downloader = InitialDWallpaperDownloader()
    
    # Method 1: Reddit (NO API KEY REQUIRED - works immediately)
    print("\n[Method 1] Downloading from Reddit...")
    downloader.download_from_reddit('Animewallpaper', 'Initial D', limit=30)
    downloader.download_from_reddit('wallpaper', 'Initial D', limit=30)
    
    # Method 2: Unsplash Source (NO API KEY REQUIRED)
    # Note: Generic car/anime images, not specifically Initial D
    # downloader.search_unsplash('initial d anime', per_page=10)
    
    # Method 3: Pixabay (FREE API KEY REQUIRED)
    # Get free API key at: https://pixabay.com/api/docs/
    pixabay_key = ""  # Add your key here
    if pixabay_key:
        downloader.search_pixabay(pixabay_key, 'Initial D', per_page=20)
    
    # Method 4: Pexels (FREE API KEY REQUIRED)
    # Get free API key at: https://www.pexels.com/api/
    pexels_key = ""  # Add your key here
    if pexels_key:
        downloader.search_pexels(pexels_key, 'Initial D anime', per_page=20)
    
    print(f"\n{'='*60}")
    print(f"✓ Download Complete!")
    print(f"✓ Total images downloaded: {downloader.downloaded_count}")
    print(f"✓ Location: {os.path.abspath(downloader.output_folder)}")
    print(f"{'='*60}\n")
    
    if downloader.downloaded_count == 0:
        print("\n⚠ No images were downloaded. Try these options:")
        print("1. Check your internet connection")
        print("2. The Reddit method works without API keys - it should find images")
        print("3. Get free API keys from Pixabay or Pexels for more sources")
        print("4. Visit these sites directly:")
        print("   - https://wallhaven.cc (search: Initial D)")
        print("   - https://www.reddit.com/r/Animewallpaper")
        print("   - https://wall.alphacoders.com")


if __name__ == "__main__":
    main()
