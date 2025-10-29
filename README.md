# 🖼️ Agnostic Wallpaper Scraper

A Flask-based web application that downloads high-quality wallpapers from multiple sources (Reddit, Unsplash, Wallhaven) and delivers them as a convenient ZIP file directly to your Downloads folder.

## ✨ Features

- 🔍 **Multi-Source Scraping**: Downloads from Reddit, Unsplash, and Wallhaven
- 📦 **ZIP Download**: Automatically packages wallpapers into a single ZIP file
- 🎨 **Quality Filtering**: Only downloads images over 100KB to ensure high quality
- 🚀 **No API Keys Required**: Works out-of-the-box for Reddit, Unsplash, and Wallhaven
- 🎯 **Simple UI**: Clean, modern interface for easy searching
- 🐳 **Docker Support**: Fully containerized for easy deployment

## 📋 Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Docker (optional, for containerized deployment)

## 🚀 Quick Start (Local Development)

### 1. Clone the Repository

```bash
git clone https://github.com/Mr615-TN/Wallpaper_Scrapper
cd Wallpaper_Scrapper
```

### 2. Create a Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

## 🐳 Running with Docker

### Build the Docker Image

```bash
docker build -t wallpaper-scraper .
```

### Run the Container

```bash
docker run -p 5000:5000 wallpaper-scraper
```

Access the application at `http://localhost:5000`

### Using Docker Compose (Optional)

Create a `docker-compose.yml` file:

```yaml
version: '3.8'

services:
  wallpaper-scraper:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
```

Then run:

```bash
docker-compose up -d
```

## 📖 Usage

1. **Navigate to** `http://localhost:5000` in your web browser
2. **Enter a search term** (e.g., "Initial D", "Cyberpunk", "Nature")
3. **Select number of images** to download (1-50)
4. **Choose a source**:
   - **Reddit**: Searches wallpaper subreddits (r/wallpaper, r/wallpapers, r/WidescreenWallpaper)
   - **Unsplash**: High-quality photography
   - **Wallhaven**: Community-curated wallpapers
5. **Click "Start Download"** and wait for your ZIP file to download

## 📁 Project Structure

```
Wallpaper_Scrapper/
├── app.py                          # Flask application
├── AgnosticWallpaperScrapper.py    # Wallpaper scraping logic
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── render.yaml                     # Render deployment config
├── README.md                       # This file
├── templates/
│   └── download_page.html          # Web interface
└── static/
    └── style.css                   # Styling
```

## 🛠️ Configuration

### Environment Variables

- `PORT`: Server port (default: 5000)
- `FLASK_ENV`: Flask environment (development/production)

### Modifying Download Limits

Edit `app.py` line 26 to change the maximum download limit:

```python
count = min(count, 50)  # Change 50 to your desired max
```

### Adding More Sources

To add additional wallpaper sources:

1. Implement a new method in `AgnosticWallpaperScrapper.py`:
   ```python
   def search_newsource(self, query, limit=10):
       # Your scraping logic here
       pass
   ```

2. Add the source to `app.py` in the `/download` route:
   ```python
   elif source == 'NewSource':
       downloaded_count = scrapper.search_newsource(query, limit=count)
   ```

3. Update `templates/download_page.html` to include the new option:
   ```html
   <option value="NewSource">New Source (Description)</option>
   ```

## 🚨 Troubleshooting

### "No images found"
- Try a different search term
- Some sources may have rate limits
- Check your internet connection

### Download is slow
- Downloading many high-resolution images takes time
- Each source has rate limiting to be respectful
- Try reducing the image count

### Docker container won't start
```bash
# Check logs
docker logs <container-id>

# Rebuild without cache
docker build --no-cache -t wallpaper-scraper .
```

### Module not found errors
```bash
# Make sure you're in your virtual environment
pip install -r requirements.txt --upgrade
```

## 🌐 Deploying to Render

1. **Push your code to GitHub**

2. **Go to [Render Dashboard](https://dashboard.render.com/)**

3. **Create New Web Service**
   - Connect your GitHub repository
   - Choose "Python 3" environment
   - Set Build Command: `pip install -r requirements.txt`
   - Set Start Command: `gunicorn --bind 0.0.0.0:$PORT --timeout 120 app:app`
   - Choose "Free" instance type

4. **Deploy!**
   - Your app will be available at `https://your-app-name.onrender.com`

### ⚠️ Render Free Tier Limitations
- Service spins down after 15 minutes of inactivity
- First request after spin-down takes ~30 seconds
- 750 hours/month free (enough for hobby use)
- No persistent storage (perfect for this app since we use temp files)

## 📝 Dependencies

- **Flask** (3.0.0): Web framework
- **requests** (2.31.0): HTTP library for API calls
- **beautifulsoup4** (4.12.2): HTML parsing (for future scraping needs)
- **gunicorn** (21.2.0): Production WSGI server

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## ⚖️ Legal & Ethics

This scraper is designed to be **respectful** of source websites:

- ✅ Uses public APIs and endpoints
- ✅ Implements rate limiting delays
- ✅ Includes proper User-Agent headers
- ✅ Only downloads publicly available content
- ✅ Does not bypass paywalls or authentication

**Please use responsibly and respect the terms of service of each platform.**

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Reddit for their open JSON API
- Unsplash for their Source service
- Wallhaven for their public API
- All the amazing wallpaper creators!

## 📧 Support

If you encounter issues:

1. Check the [Troubleshooting](#-troubleshooting) section
2. Review existing GitHub Issues
3. Create a new issue with:
   - Python version
   - Operating system
   - Error message/logs
   - Steps to reproduce

---

**Made with ❤️ for wallpaper enthusiasts**

*Star ⭐ this repo if you find it useful!*
