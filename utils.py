"""
Utility functions for Reselling Profit Tracker
"""

import os
import subprocess
from pathlib import Path
from typing import Optional
from PIL import Image
import config

def calculate_potential_profit(purchase_price: float, shipping_cost: float, target_price: float) -> float:
    """Calculate potential profit"""
    return target_price - purchase_price - shipping_cost

def calculate_actual_profit(purchase_price: float, shipping_cost: float, final_sold_price: float) -> float:
    """Calculate actual profit"""
    return final_sold_price - purchase_price - shipping_cost

def format_currency(amount: float) -> str:
    """Format amount as currency"""
    return f"${amount:.2f}"

def format_profit(profit: float) -> str:
    """Format profit with color indicator"""
    if profit >= 0:
        return f"[green]{format_currency(profit)}[/green]"
    else:
        return f"[red]{format_currency(profit)}[/red]"

def optimize_image(image_path: str, max_size: tuple = None, quality: int = None) -> bool:
    """Optimize image file size and dimensions"""
    try:
        if max_size is None:
            max_size = config.MAX_IMAGE_SIZE
        if quality is None:
            quality = config.IMAGE_QUALITY
        
        img = Image.open(image_path)
        
        # Convert RGBA to RGB if necessary
        if img.mode == 'RGBA':
            img = img.convert('RGB')
        
        # Resize if larger than max size
        if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # Save with optimization
        img.save(image_path, 'JPEG', quality=quality, optimize=True)
        return True
    except Exception as e:
        print(f"Error optimizing image: {e}")
        return False

def preview_image_in_terminal(image_path: str, width: int = 40) -> bool:
    """Display image preview in terminal using timg or viu"""
    if not os.path.exists(image_path):
        return False
    
    # Try timg first
    try:
        subprocess.run(['timg', '-g', f'{width}x{width}', image_path], 
                      check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    # Try viu as fallback
    try:
        subprocess.run(['viu', '-w', str(width), image_path], 
                      check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    
    return False

def get_file_size(file_path: str) -> str:
    """Get human-readable file size"""
    try:
        size = os.path.getsize(file_path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return "Unknown"

def validate_url(url: str) -> tuple[bool, str]:
    """Basic URL validation
    Returns: (is_valid, error_message)
    """
    if not url or url.strip() == "":
        return True, ""  # Empty URL is valid (optional field)
    
    url = url.strip()
    if not url.startswith(('http://', 'https://')):
        return False, "URL must start with http:// or https://"
    
    if len(url) > 2000:
        return False, "URL too long"
    
    return True, ""

def validate_price(price_str: str) -> tuple[bool, Optional[float], str]:
    """Validate and convert price string to float
    Returns: (is_valid, value, error_message)
    """
    if not price_str or price_str.strip() == "":
        return True, 0.0, ""
    
    try:
        price = float(price_str)
        if price < 0:
            return False, None, "Price cannot be negative"
        if price > 1000000:
            return False, None, "Price too large"
        return True, price, ""
    except (ValueError, TypeError):
        return False, None, "Invalid number format"

def sanitize_filename(filename: str) -> str:
    """Remove invalid characters from filename"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    # Remove leading/trailing spaces and dots
    filename = filename.strip('. ')
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    return filename if filename else "unnamed"

def validate_item_name(name: str) -> tuple[bool, str]:
    """Validate item name
    Returns: (is_valid, error_message)
    """
    if not name or name.strip() == "":
        return False, "Item name is required"
    
    if len(name.strip()) < 2:
        return False, "Item name too short (min 2 characters)"
    
    if len(name) > 200:
        return False, "Item name too long (max 200 characters)"
    
    return True, ""

def get_status_emoji(status: str) -> str:
    """Get emoji for status"""
    # Emojis removed for cleaner output
    return ''

def truncate_text(text: str, max_length: int = 50) -> str:
    """Truncate text with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def open_file_in_browser(file_path: str) -> bool:
    """Open HTML file in default browser"""
    try:
        if os.name == 'nt':  # Windows
            os.startfile(file_path)
        elif os.name == 'posix':  # macOS/Linux
            subprocess.run(['open' if os.uname().sysname == 'Darwin' else 'xdg-open', file_path])
        return True
    except Exception as e:
        print(f"Error opening file: {e}")
        return False

def get_database_stats(db_path: str) -> dict:
    """Get database file statistics"""
    try:
        size = os.path.getsize(db_path)
        return {
            'exists': True,
            'size': get_file_size(db_path),
            'size_bytes': size
        }
    except:
        return {
            'exists': False,
            'size': 'N/A',
            'size_bytes': 0
        }

def cleanup_temp_files(directory: str, pattern: str = "temp_*"):
    """Clean up temporary files"""
    try:
        path = Path(directory)
        for file in path.glob(pattern):
            if file.is_file():
                file.unlink()
            elif file.is_dir():
                import shutil
                shutil.rmtree(file)
        return True
    except Exception as e:
        print(f"Error cleaning up temp files: {e}")
        return False
