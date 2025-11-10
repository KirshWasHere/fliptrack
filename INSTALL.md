# Installation Guide

## Prerequisites

- **Python 3.8 or higher** - [Download here](https://www.python.org/downloads/)
- **pip** (included with Python)
- **Internet connection** (for image scraping)

## Windows Installation

### Method 1: Automatic (Recommended)

1. Download or clone the project
2. Navigate to the project folder
3. Double-click `run.bat`
4. The script will:
   - Check Python installation
   - Install dependencies automatically
   - Create necessary directories
   - Launch the application

### Method 2: Manual

```cmd
# Navigate to project folder
cd fliptrack

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## macOS/Linux Installation

### Using Terminal

```bash
# Navigate to project folder
cd fliptrack

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

### Optional: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Verifying Installation

Run the test script to verify everything is installed correctly:

```bash
python test_setup.py
```

This will check:
- All required packages are installed
- Modules can be imported
- Database can be created
- Reports can be generated

## Dependencies

The following packages will be installed:

- `textual>=0.47.0` - Terminal UI framework
- `rich>=13.7.0` - Terminal styling
- `beautifulsoup4>=4.12.0` - Web scraping
- `httpx>=0.25.0` - HTTP client
- `jinja2>=3.1.2` - HTML templating
- `qrcode[pil]>=7.4.2` - QR code generation
- `pillow>=10.1.0` - Image processing

## Troubleshooting

### "Python is not recognized"

**Problem:** Python not in system PATH

**Solution:**
1. Reinstall Python
2. Check "Add Python to PATH" during installation
3. Or manually add Python to PATH:
   - Windows: System Properties → Environment Variables → Path
   - Add: `C:\Python3X\` and `C:\Python3X\Scripts\`

### "pip is not recognized"

**Problem:** pip not installed or not in PATH

**Solution:**
```bash
# Download get-pip.py
python get-pip.py

# Or reinstall Python with pip included
```

### "Failed to install dependencies"

**Problem:** Outdated pip or permission issues

**Solution:**
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install with user flag (no admin required)
pip install --user -r requirements.txt

# Or use virtual environment (recommended)
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### "Permission denied" errors

**Problem:** Insufficient permissions

**Solution:**
- Run terminal as administrator (Windows)
- Use `sudo` on macOS/Linux (not recommended)
- Or use virtual environment (recommended)

### "Module not found" after installation

**Problem:** Multiple Python versions or wrong pip

**Solution:**
```bash
# Use python -m pip instead
python -m pip install -r requirements.txt

# Check Python version
python --version

# Check pip is for correct Python
pip --version
```

### "Database is locked"

**Problem:** Another instance is running

**Solution:**
- Close all instances of the application
- Delete `tracker.db` if corrupted (loses data)

### Images not downloading

**Problem:** Network issues or blocked by websites

**Solution:**
- Check internet connection
- Use manual image selection instead
- Some sites block scrapers (expected)

## Uninstallation

To remove the application:

1. Delete the project folder
2. (Optional) Uninstall dependencies:
   ```bash
   pip uninstall textual rich beautifulsoup4 httpx jinja2 qrcode pillow
   ```

## Updating

To update to a new version:

1. Backup your data:
   ```bash
   copy tracker.db tracker_backup.db
   xcopy /E /I data data_backup
   ```

2. Download new version

3. Copy your old `tracker.db` and `data/` folder to new version

4. Run the application

## System Requirements

**Minimum:**
- Python 3.8+
- 100 MB free disk space
- 256 MB RAM
- Terminal with 80x24 character display

**Recommended:**
- Python 3.10+
- 500 MB free disk space (for images)
- 512 MB RAM
- Terminal with 120x30+ character display
- Internet connection for image scraping

## Platform Support

- ✅ Windows 10/11
- ✅ macOS 10.14+
- ✅ Linux (Ubuntu, Debian, Fedora, etc.)
- ✅ Windows Subsystem for Linux (WSL)

## Getting Help

If installation fails:

1. Check error messages carefully
2. Run `python test_setup.py` to diagnose
3. Verify Python version: `python --version`
4. Verify pip works: `pip --version`
5. Try virtual environment method
6. Check GitHub issues (if applicable)

---

**Need more help?** Check the main [README.md](README.md) for usage instructions.
