# app.py

from flask import Flask, render_template, request
# Import the renamed file and class as requested
from AgnosticWallpaperScrapper import WallpaperDownloader 
import os

app = Flask(__name__)
# Define the default output folder
OUTPUT_DIR = "AgnosticWallpapers" 

@app.route('/', methods=['GET'])
def index():
    """Renders the initial, stylish download form."""
    # Set defaults for the form
    return render_template('download_page.html', 
                           status_message="Ready to begin...", 
                           current_query="AE86", 
                           current_source="Reddit")

@app.route('/download', methods=['POST'])
def download():
    """Handles the form submission and runs the WallpaperScrapper method."""
    
    # 1. Get user input from the form
    query = request.form.get('query', 'AE86')
    source = request.form.get('source', 'Reddit') 
    try:
        count = int(request.form.get('count', 10))
    except ValueError:
        count = 10 

    # 2. Initialize the Scrapper
    scrapper = WallpaperDownloader(output_folder=OUTPUT_DIR)
    downloaded_count = 0
    status_msg = ""
    
    # 3. Call the appropriate method based on the selected source
    try:
        if source == 'Reddit':
            downloaded_count = scrapper.search_reddit(query, limit=count)
        elif source == 'Unsplash':
            downloaded_count = scrapper.search_unsplash(query, limit=count)
        elif source == 'Pixabay':
            # --- NOTE: You MUST pass your actual API key here if needed ---
            status_msg = f"⚠ Download from **{source}** requires a valid API Key."
            
        elif source == 'Pexels':
            # --- NOTE: You MUST pass your actual API key here if needed ---
            status_msg = f"⚠ Download from **{source}** requires a valid API Key."
        else:
            status_msg = f"⚠ Source **{source}** is not a valid option."

        # If a specific status message wasn't set (e.g., API key warning)
        if not status_msg:
            if downloaded_count > 0:
                status_msg = f"✅ Success! **{downloaded_count} images** saved from **{source}**."
            else:
                 status_msg = f"⚠️ Downloaded 0 images from **{source}**. Try a new query."

    except Exception as e:
        status_msg = f"❌ Error during download from {source}: {str(e)}"
        
    # 4. Re-render the page with the updated status
    return render_template(
        'download_page.html',
        status_message=status_msg,
        output_folder=scrapper.get_output_path(),
        current_query=query,
        current_count=count,
        current_source=source
    )

if __name__ == '__main__':
    # Run the server: Navigate to http://127.0.0.1:5000
    app.run(debug=True)
