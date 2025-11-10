# 📦 FlipTrack - Reselling Profit Tracker

A powerful terminal-based profit tracking application for resellers. Track inventory, calculate profits, scrape product images, and generate professional HTML reports.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## ✨ Features

- 🖥️ **Terminal UI** - Full-screen interactive interface with keyboard shortcuts
- 💰 **Profit Tracking** - Automatic calculation of potential and actual profits
- 📊 **Item Management** - Add, edit, delete items with status tracking (Draft/Listed/Sold)
- 🖼️ **Image Scraping** - Automatic image discovery from product sites
- 📄 **HTML Reports** - Self-contained reports with embedded images and QR codes
- 🌙 **Dark Mode** - Professional dark-themed reports
- 🔍 **Search & Filter** - Find items quickly by name or status
- ✅ **Data Validation** - Input validation prevents errors
- 🗜️ **Image Optimization** - Automatic compression of downloaded images
- 📤 **Export** - CSV export and full backup functionality
- 🧪 **Tested** - Comprehensive test suite included

## 🚀 Quick Start

### Installation

**Windows:**
```bash
# Clone the repository
git clone https://github.com/yourusername/fliptrack.git
cd fliptrack

# Run the launcher (installs dependencies automatically)
run.bat
```

**macOS/Linux:**
```bash
# Clone the repository
git clone https://github.com/yourusername/fliptrack.git
cd fliptrack

# Install dependencies
pip install -r requirements.txt

# Run the application
python main.py
```

### Requirements

- Python 3.8 or higher
- Internet connection (for image scraping)

## 📖 Usage

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `a` | Add new item |
| `e` | Edit selected item |
| `d` | Delete selected item (with confirmation) |
| `r` | Generate HTML report for selected item |
| `o` | Open report in browser |
| `m` | Generate master index of all items |
| `Ctrl+R` | Generate reports for ALL items + master index |
| `Ctrl+D` | Delete ALL items (with confirmation) |
| `Ctrl+F` | Focus search bar |
| `Ctrl+E` | Export all items to CSV |
| `Ctrl+B` | Create full backup (database + images + reports) |
| `q` | Quit application |

### Adding Items

1. Press `a` to open the add item form
2. Fill in required fields:
   - **Item Name**: Product name (required, 2-200 characters)
   - **Category**: General, Sneakers, Electronics, or Books
   - **Purchase Price**: What you paid (required)
   - **Shipping Cost**: Shipping/handling fees
   - **Target Price**: Your selling price goal
   - **Product URL**: Link to product page (optional)
   - **Status**: Draft, Listed, or Sold
3. **Add Images** (optional):
   - Click "Scrape Images" to auto-find images online
   - Click "Preview" to view scraped images
   - Click "Add Images" to select local files
   - First 3 images will be used in reports
4. Click "Save" or press `Ctrl+S`

### Searching & Filtering

- Use the search bar to find items by name
- Use the status dropdown to filter by Draft/Listed/Sold
- Results update in real-time

### Generating Reports

**Single Item:**
1. Select an item from the table
2. Press `r` to generate HTML report
3. Press `o` to open in your default browser

**All Items:**
- Press `Ctrl+R` to generate reports for ALL items at once
- Automatically generates master index and opens it
- Perfect for batch processing your entire inventory

Reports include:
- Item details and pricing breakdown
- Profit calculations (potential and actual)
- Product images (embedded, no internet required)
- QR code for product URL
- Professional dark mode styling

### Master Index

Press `m` to generate a master index HTML file with:
- All items in a sortable table
- Links to individual reports
- Profit summaries
- Status badges

## 📁 Project Structure

```
fliptrack/
├── main.py              # Main application (TUI)
├── database.py          # SQLite database operations
├── scraper.py           # Image scraping logic
├── report_generator.py  # HTML report generation
├── utils.py             # Utility functions
├── config.py            # Configuration settings
├── export_utils.py      # Export and backup utilities
├── tests.py             # Test suite
├── requirements.txt     # Python dependencies
├── run.bat              # Windows launcher
├── tracker.db           # SQLite database (created on first run)
├── data/
│   └── images/          # Downloaded product images
│       └── item_[ID]/   # Images organized by item
└── reports/             # Generated HTML reports
    ├── index.html       # Master index
    └── item_[ID]_report.html
```

## 🛠️ Technology Stack

- **Textual** - Terminal UI framework
- **Rich** - Terminal styling and formatting
- **SQLite** - Local database
- **BeautifulSoup4** - Web scraping
- **httpx** - HTTP client for image downloads
- **Jinja2** - HTML templating
- **qrcode** - QR code generation
- **Pillow** - Image processing and optimization

## 📊 Data Validation

The application validates all inputs:

- **Item names**: 2-200 characters, required
- **Prices**: Non-negative numbers, max $1,000,000
- **URLs**: Must start with http:// or https://
- **Sold items**: Must have final sold price

Invalid data is rejected with clear error messages.

## 💾 Export & Backup

### From the Application

- **CSV Export**: Press `Ctrl+E` to export all items to a timestamped CSV file
- **Full Backup**: Press `Ctrl+B` to create a complete backup (database, images, reports, CSV, JSON)

### Command Line

```bash
# Export to CSV
python export_utils.py csv [output.csv]

# Export to JSON
python export_utils.py json [output.json]

# Create full backup
python export_utils.py backup [backup_dir]

# Restore from JSON backup
python export_utils.py restore backup.json
```

### Manual Backup

```bash
# Copy database file
copy tracker.db tracker_backup.db

# Copy entire data folder
xcopy /E /I data data_backup
```

## 🧪 Testing

Run the test suite to verify everything works:

```bash
python tests.py
```

Tests cover:
- Database operations (CRUD)
- Search and filtering
- Input validation
- Profit calculations
- Report generation
- CSV export

### Generate Test Data

```bash
# Generate 25 random test items
python generate_test_data.py 25

# Add placeholder images to 15 items
python add_test_images.py 15
```

## 💡 Tips & Best Practices

1. **Use descriptive item names** - Makes searching easier
2. **Add images early** - Harder to find later
3. **Update status regularly** - Keep inventory accurate
4. **Generate reports before selling** - Professional presentation
5. **Backup your database** - Press `Ctrl+B` regularly
6. **Use search and filters** - Faster than scrolling

## ⚠️ Dangerous Operations

### Delete All Items (Ctrl+D)
- Deletes **ALL** items from database
- Removes **ALL** images
- Clears **ALL** reports
- **CANNOT be undone**
- **Always backup first!** (Press `Ctrl+B` before `Ctrl+D`)

This is useful for:
- Clearing test data
- Starting fresh
- Resetting the application

**Recommended workflow:**
1. Press `Ctrl+B` to create backup
2. Press `Ctrl+D` to delete all
3. Confirm the deletion
4. Start adding new items

## 🐛 Troubleshooting

**"Python is not installed"**
- Install Python 3.8+ from [python.org](https://python.org)
- Ensure Python is added to PATH

**"Failed to install dependencies"**
- Run: `pip install --upgrade pip`
- Then: `pip install -r requirements.txt`

**"No images found" when scraping**
- Try manual image selection instead
- Check internet connection
- Some sites block scrapers (expected behavior)

**Images not showing in reports**
- Ensure images were downloaded (check data/images/)
- Try re-generating the report

**Database locked error**
- Close any other instances of the app
- Delete `tracker.db` to start fresh (loses all data)

See [INSTALL.md](INSTALL.md) for detailed troubleshooting.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Areas for improvement:
- Additional scraping sources
- UI enhancements
- Performance optimization
- Export formats (PDF)
- Bulk operations
- Charts and analytics

## 📄 License

MIT License - Free to use for personal and commercial purposes.

You can:
- ✅ Use the software for any purpose
- ✅ Modify and distribute the software
- ✅ Use it commercially to track your reselling business

You cannot:
- ❌ Sell the software itself as a product
- ❌ Hold the author liable

See [LICENSE](LICENSE) for full details.

## 📚 Documentation

- [README.md](README.md) - Main documentation (you are here)
- [INSTALL.md](INSTALL.md) - Installation and troubleshooting
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Keyboard shortcuts and tips
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guide
- [CHANGELOG.md](CHANGELOG.md) - Version history
- [ARCHITECTURE.md](ARCHITECTURE.md) - Technical architecture
- [TEST_DATA_GUIDE.md](TEST_DATA_GUIDE.md) - Testing guide

## 🙏 Acknowledgments

Built with:
- [Textual](https://github.com/Textualize/textual) - Amazing TUI framework
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - Reliable web scraping
- [Jinja2](https://jinja.palletsprojects.com/) - Powerful templating

## 📞 Support

- Check [README.md](README.md) for common issues
- Review error messages carefully
- Run `python tests.py` to verify installation
- Check [INSTALL.md](INSTALL.md) for troubleshooting

---

**Built for resellers, by resellers** 📦💰

**Star ⭐ this repo if you find it useful!**
