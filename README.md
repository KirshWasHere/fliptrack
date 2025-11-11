# FlipTrack

A terminal-based profit tracking application for resellers. Track inventory, calculate profits, and generate HTML reports.

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Demo

https://github.com/KirshWasHere/fliptrack/assets/demo.mp4

## Features

- Terminal UI with keyboard shortcuts
- Profit tracking with automatic calculations
- Item management (add, edit, delete)
- Image scraping from product sites
- HTML report generation with dark mode
- Search and filter functionality
- Data validation
- CSV export and backup system
- Comprehensive test suite

## Installation

**Windows:**
```bash
git clone https://github.com/KirshWasHere/fliptrack.git
cd fliptrack
run.bat
```

**macOS/Linux:**
```bash
git clone https://github.com/KirshWasHere/fliptrack.git
cd fliptrack
pip install -r requirements.txt
python main.py
```

**Requirements:**
- Python 3.8+
- Internet connection for image scraping

## Usage

### Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `a` | Add new item |
| `e` | Edit selected item |
| `d` | Delete selected item |
| `r` | Generate HTML report |
| `o` | Open report in browser |
| `m` | Generate master index |
| `Ctrl+R` | Generate all reports |
| `Ctrl+D` | Delete all items |
| `Ctrl+F` | Focus search bar |
| `Ctrl+E` | Export to CSV |
| `Ctrl+B` | Create backup |
| `q` | Quit |

### Adding Items

1. Press `a` to open form
2. Fill in item details (name, prices, category, status)
3. Optionally scrape or add images
4. Save with `Ctrl+S` or click Save

### Generating Reports

**Single item:** Select item and press `r`

**All items:** Press `Ctrl+R` to batch generate

Reports include item details, profit calculations, embedded images, and QR codes.

## Project Structure

```
fliptrack/
├── main.py              # Main application
├── database.py          # Database operations
├── scraper.py           # Image scraping
├── report_generator.py  # HTML generation
├── utils.py             # Utilities
├── config.py            # Configuration
├── export_utils.py      # Export/backup
├── tests.py             # Test suite
├── requirements.txt     # Dependencies
└── run.bat              # Windows launcher
```

## Technology

- Textual - Terminal UI
- SQLite - Database
- BeautifulSoup4 - Web scraping
- Jinja2 - HTML templating
- Pillow - Image processing
- qrcode - QR generation

## Testing

```bash
python tests.py
```

Generate test data:
```bash
python generate_test_data.py 25
python add_test_images.py 15
```

## Export & Backup

**From app:**
- `Ctrl+E` - Export to CSV
- `Ctrl+B` - Full backup

**Command line:**
```bash
python export_utils.py csv [output.csv]
python export_utils.py backup [backup_dir]
python export_utils.py restore backup.json
```

## Documentation

- [INSTALL.md](INSTALL.md) - Installation guide
- [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Shortcuts and tips
- [CONTRIBUTING.md](CONTRIBUTING.md) - Developer guide
- [CHANGELOG.md](CHANGELOG.md) - Version history

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
