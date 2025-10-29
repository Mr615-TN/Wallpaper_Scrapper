from flask import Flask, render_template, request, send_file
from AgnosticWallpaperScrapper import WallpaperDownloader 
import os

app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    """Renders the initial, stylish download form."""
    return render_template('download_page.html', 
                           status_message="Ready to begin...", 
                           current_query="AE86", 
                           current_source="Reddit",
                           current_count=10)

@app.route('/download', methods=['POST'])
def download():
    """Handles the form submission, scrapes wallpapers, and returns a ZIP file."""
    
    query = request.form.get('query', 'AE86')
    source = request.form.get('source', 'Reddit') 
    try:
        count = int(request.form.get('count', 10))
        count = min(count, 50)  # Cap at 50
    except ValueError:
        count = 10 

    # Initialize the Scrapper - it will create its own temp folder
    scrapper = WallpaperDownloader()
    downloaded_count = 0
    zip_path = None
    
    try:
        # Call the appropriate method based on the selected source
        if source == 'Reddit':
            downloaded_count = scrapper.search_reddit(query, limit=count)
        elif source == 'Unsplash':
            downloaded_count = scrapper.search_unsplash(query, limit=count)
        elif source == 'Wallhaven':
            downloaded_count = scrapper.search_wallhaven(query, limit=count)
        elif source == 'Pixabay':
            scrapper.cleanup()
            return render_template(
                'download_page.html',
                status_message=f"⚠️ {source} requires an API Key (not implemented yet).",
                current_query=query,
                current_count=count,
                current_source=source
            )
        elif source == 'Pexels':
            scrapper.cleanup()
            return render_template(
                'download_page.html',
                status_message=f"⚠️ {source} requires an API Key (not implemented yet).",
                current_query=query,
                current_count=count,
                current_source=source
            )
        else:
            scrapper.cleanup()
            return render_template(
                'download_page.html',
                status_message=f"⚠️ Invalid source selected.",
                current_query=query,
                current_count=count,
                current_source=source
            )

        # If we got images, create ZIP and send it
        if downloaded_count > 0:
            zip_path = scrapper.create_zip(query)
            
            if zip_path and os.path.exists(zip_path):
                # Get the filename for download
                import re
                safe_query = re.sub(r'[^\w\-_\. ]', '', query).replace(' ', '_')
                download_name = f"{safe_query}_wallpapers.zip"
                
                # Send the file and cleanup after
                response = send_file(
                    zip_path,
                    as_attachment=True,
                    download_name=download_name,
                    mimetype='application/zip'
                )
                
                # Register cleanup function to run after response is sent
                @response.call_on_close
                def cleanup_temp_files():
                    scrapper.cleanup()
                
                return response
            else:
                scrapper.cleanup()
                return render_template(
                    'download_page.html',
                    status_message=f"❌ Error creating ZIP file.",
                    current_query=query,
                    current_count=count,
                    current_source=source
                )
        else:
            scrapper.cleanup()
            return render_template(
                'download_page.html',
                status_message=f"⚠️ No images found for '{query}' from {source}. Try a different query!",
                current_query=query,
                current_count=count,
                current_source=source
            )

    except Exception as e:
        scrapper.cleanup()
        return render_template(
            'download_page.html',
            status_message=f"❌ Error: {str(e)}",
            current_query=query,
            current_count=count,
            current_source=source
        )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
