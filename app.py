from flask import Flask, request, send_file, render_template_string
import zipfile
import os
import shutil
from AgnosticWallpaperScrapper import WallpaperDownloader

app = Flask(__name__)

HTML_TEMPLATE = """
<!doctype html>
<title>Agnostic Wallpaper Downloader</title>
<h1 style="text-align:center;">Agnostic Wallpaper Scraper & Downloader</h1>
<div style="text-align:center; padding-top: 20px;">
    
    <form method="POST" action="/" style="display: inline-block;">
        <label for="query" style="font-size: 18px; display: block; margin-bottom: 10px;">
            Enter Wallpaper Topic (e.g., 'Cyberpunk City', 'Mountain Landscape'):
        </label>
        <input type="text" id="query" name="query" required 
               placeholder="Enter your topic here..."
               style="padding: 10px; font-size: 16px; width: 300px; border: 1px solid #ccc; border-radius: 4px;">
        <button type="submit" 
                style="padding: 10px 20px; font-size: 16px; cursor: pointer; background-color: #3498db; color: #fff; border: none; border-radius: 4px; margin-left: 10px;">
            Scrape & Download ZIP
        </button>
    </form>

    <p style="margin-top: 20px;">
        ⚠️ **IMPORTANT:** Scraping and zipping may take **1-2 minutes** before the download starts.
    </p>
</div>
"""
# ----------------------------------------

@app.route('/', methods=['GET', 'POST'])
def index_or_download():
    # 1. Handle the GET request (Show the form)
    if request.method == 'GET':
        return render_template_string(HTML_TEMPLATE)

    # 2. Handle the POST request (Process the form and trigger download)
    if request.method == 'POST':
        # Get the user's input from the form field named 'query'
        user_query = request.form.get('query')
        
        if not user_query:
            return "Error: No wallpaper topic provided.", 400

        # Configuration & Cleanup
        # Use the query to create a unique and relevant folder/zip name
        safe_query = user_query.replace(' ', '_').replace('/', '').strip()
        TEMP_FOLDER = "temp_" + safe_query
        ZIP_FILENAME = safe_query + "_Wallpapers.zip"
        
        if os.path.exists(TEMP_FOLDER):
            shutil.rmtree(TEMP_FOLDER)

        try:
            # Run the Scraper
            downloader = WallpaperDownloader(output_folder=TEMP_FOLDER) 
            
            # Scrape from the two best public sources using the user's query
            downloader.download_from_reddit('wallpaper', user_query, limit=20) 
            downloader.download_from_reddit('Animewallpaper', user_query, limit=20) 

            if downloader.downloaded_count == 0:
                # IMPORTANT: Clean up the temp folder on failure
                if os.path.exists(TEMP_FOLDER):
                    shutil.rmtree(TEMP_FOLDER)
                return f"Sorry, no images were found for '{user_query}'. Try a different topic.", 404

            # Create the ZIP File on the server's disk
            with zipfile.ZipFile(ZIP_FILENAME, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for root, _, files in os.walk(TEMP_FOLDER):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # Add the file to the zip, naming it just by the file name
                        zipf.write(file_path, arcname=file)

            # Serve the ZIP file for download
            response = send_file(
                ZIP_FILENAME, 
                mimetype='application/zip', 
                as_attachment=True, 
                download_name=ZIP_FILENAME
            )
            
            return response
            
        except Exception as e:
            # Handle unexpected errors and ensure cleanup
            return f"An error occurred during scraping or zipping: {e}", 500
            
        finally:
            # Ensure cleanup runs after the response has been sent
            if os.path.exists(TEMP_FOLDER):
                shutil.rmtree(TEMP_FOLDER)
            if os.path.exists(ZIP_FILENAME):
                os.remove(ZIP_FILENAME)
                
# Standard entry point for local testing
if __name__ == '__main__':
    app.run(debug=True)
