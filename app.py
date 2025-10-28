# app.py (Minimal Flask example - Wallhaven, Reddit, Unsplash)
from flask import Flask, request, render_template_string, send_file
import os
import shutil
import time

# Ensure you save the code from section 1 as Agnostic_Scraper_Wallhaven.py
from AgnosticWallpaperScraper import WallpaperDownloader 

app = Flask(__name__)

# --- Core Web App Logic ---
def run_scraper_and_zip(query):
    """Initializes the scraper and zips the results using free sources."""
    
    downloader = WallpaperDownloader(query)
    
    # Run all free scraping methods
    downloader.search_wallhaven(pages=1) # Wallhaven is now included
    downloader.download_from_reddit('wallpaper', limit=15)
    downloader.search_unsplash(per_page=3)
    
    if downloader.downloaded_count > 0:
        # Create a ZIP file of the downloaded folder
        zip_filename = f"{downloader.output_folder}"
        shutil.make_archive(zip_filename, 'zip', downloader.output_folder)
        
        # Clean up the folder after zipping
        shutil.rmtree(downloader.output_folder)
        
        return f"{zip_filename}.zip"
    else:
        return None


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            return render_template_string(HTML_FORM, message="Please enter a search query.")

        # Simulate processing time for better user experience
        time.sleep(1) 
        
        zip_path = run_scraper_and_zip(query)

        if zip_path:
            # Send the generated ZIP file for download
            return send_file(zip_path, as_attachment=True, download_name=os.path.basename(zip_path))
        else:
            return render_template_string(HTML_FORM, message=f"No high-quality images found for '{query}'. Please try a different search term.")

    return render_template_string(HTML_FORM, message="")


# --- HTML Template ---
HTML_FORM = """
<!doctype html>
<title>Agnostic Wallpaper Scraper</title>
<style>
    body { font-family: sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #f4f4f9; }
    h1 { color: #333; text-align: center; }
    form { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    input[type="text"] { width: 100%; padding: 10px; margin-bottom: 10px; border: 1px solid #ccc; border-radius: 4px; box-sizing: border-box; }
    input[type="submit"] { background-color: #007bff; color: white; padding: 10px 15px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; width: 100%; }
    input[type="submit"]:hover { background-color: #0056b3; }
    .message { text-align: center; margin-top: 20px; padding: 10px; background-color: #e6f7ff; border: 1px solid #cce7ff; color: #004085; border-radius: 4px; }
    .info { margin-top: 15px; font-size: 0.9em; color: #666; text-align: center;}
</style>
<body>
    <h1>🖼️ Agnostic Wallpaper Scraper</h1>
    <p class="info">Scraping from **Wallhaven**, **Reddit**, and **Unsplash** for high-quality results.</p>
    {% if message %}<div class="message">{{ message }}</div>{% endif %}
    <form method="POST">
        <label for="query">Enter Wallpaper Type:</label>
        <input type="text" id="query" name="query" placeholder="e.g., Arch Linux, Initial D, Nature" required>
        <input type="submit" value="Scrape and Download ZIP">
    </form>
</body>
</html>
"""

if __name__ == '__main__':
    # To run: 'pip install flask requests beautifulsoup4' and 'python app.py'
    app.run(debug=True)
