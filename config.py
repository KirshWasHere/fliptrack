"""
Configuration settings for Reselling Profit Tracker
"""

from pathlib import Path

# Application Info
APP_NAME = "Reselling Profit Tracker"
APP_VERSION = "1.0.0"

# Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
IMAGES_DIR = DATA_DIR / "images"
REPORTS_DIR = BASE_DIR / "reports"
DATABASE_PATH = BASE_DIR / "tracker.db"

# Database Settings
DB_TIMEOUT = 30  # seconds

# Scraping Settings
SCRAPE_TIMEOUT = 10  # seconds
MAX_IMAGES_TO_SCRAPE = 15
MAX_IMAGES_TO_DOWNLOAD = 3
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Image Settings
IMAGE_QUALITY = 85  # JPEG quality (1-100)
MAX_IMAGE_SIZE = (1920, 1920)  # Max dimensions for downloaded images

# Report Settings
REPORT_TEMPLATE_ENCODING = "utf-8"
EMBED_IMAGES_AS_BASE64 = True

# Categories for scraping
CATEGORIES = {
    'Sneakers': {
        'sites': ['stockx.com', 'goat.com'],
        'search_url': 'https://stockx.com/search?s={query}'
    },
    'Electronics': {
        'sites': ['ebay.com', 'amazon.com'],
        'search_url': 'https://www.ebay.com/sch/i.html?_nkw={query}'
    },
    'Books': {
        'sites': ['amazon.com', 'ebay.com'],
        'search_url': 'https://www.amazon.com/s?k={query}'
    },
    'General': {
        'sites': ['google.com'],
        'search_url': 'https://www.google.com/search?q={query}&tbm=isch'
    }
}

# UI Settings
TABLE_CURSOR_TYPE = "row"
NOTIFICATION_TIMEOUT = 3  # seconds

# Status Options
STATUS_OPTIONS = ["Draft", "Listed", "Sold"]
STATUS_COLORS = {
    "Draft": "yellow",
    "Listed": "cyan",
    "Sold": "green"
}

def ensure_directories():
    """Create necessary directories if they don't exist"""
    DATA_DIR.mkdir(exist_ok=True)
    IMAGES_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

def get_item_image_dir(item_id: int) -> Path:
    """Get the image directory for a specific item"""
    item_dir = IMAGES_DIR / f"item_{item_id}"
    item_dir.mkdir(exist_ok=True)
    return item_dir

# Initialize directories on import
ensure_directories()
