"""
Check downloaded images and show where they are
"""

import os
from pathlib import Path
from database import Database

def check_images():
    print("=" * 70)
    print("IMAGE STORAGE CHECK")
    print("=" * 70)
    
    # Check if images directory exists
    images_dir = Path("./data/images")
    if not images_dir.exists():
        print("\n❌ No images directory found yet.")
        print("   Images will be created when you save an item with scraped images.")
        return
    
    print(f"\n✅ Images directory exists: {images_dir}")
    
    # List all item directories
    item_dirs = [d for d in images_dir.iterdir() if d.is_dir()]
    
    if not item_dirs:
        print("\n📁 No item image folders yet.")
        print("   Add an item, scrape images, and save to create image folders.")
        return
    
    print(f"\n📁 Found {len(item_dirs)} item folders:\n")
    
    # Check each item's images
    db = Database()
    
    for item_dir in sorted(item_dirs):
        item_id = item_dir.name.replace("item_", "")
        
        # Get item info from database
        try:
            item_id_int = int(item_id)
            item = db.get_item(item_id_int)
            item_name = item['item_name'] if item else "Unknown"
        except:
            item_name = "Unknown"
        
        print(f"📦 {item_dir.name}/")
        print(f"   Item: {item_name}")
        
        # List images in this folder
        images = list(item_dir.glob("*.jpg")) + list(item_dir.glob("*.png"))
        
        if images:
            print(f"   Images: {len(images)}")
            for img in images:
                size = img.stat().st_size
                size_kb = size / 1024
                print(f"      • {img.name} ({size_kb:.1f} KB)")
        else:
            print(f"   ⚠️  No images found")
        
        print()
    
    print("=" * 70)
    print("HOW TO VIEW IMAGES:")
    print("=" * 70)
    print("\n1. IN FILE EXPLORER:")
    print("   Navigate to: ./data/images/item_X/")
    print("   Double-click any .jpg file to view")
    
    print("\n2. IN HTML REPORTS:")
    print("   - Select an item in the dashboard")
    print("   - Press 'r' to generate report")
    print("   - Open the HTML file in your browser")
    print("   - Images will be embedded and visible!")
    
    print("\n3. IN TERMINAL (Optional):")
    print("   Install timg or viu for terminal image preview")
    print("   Windows: scoop install timg")
    print("   Then images can preview in the TUI")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    check_images()
