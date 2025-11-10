"""
Add placeholder images to test items
Run with: python add_test_images.py
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random
from database import Database

COLORS = [
    ("#1a1a1a", "#4ade80"),  # Dark with green
    ("#1a1a1a", "#60a5fa"),  # Dark with blue
    ("#1a1a1a", "#f87171"),  # Dark with red
    ("#1a1a1a", "#fbbf24"),  # Dark with yellow
    ("#1a1a1a", "#a78bfa"),  # Dark with purple
]


def create_placeholder_image(item_name, image_number, save_path):
    """Create a placeholder image with item name"""
    # Create image
    img = Image.new('RGB', (800, 800), color=random.choice(COLORS)[0])
    draw = ImageDraw.Draw(img)
    
    # Try to use a nice font, fallback to default
    try:
        font_large = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 40)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Get random color
    bg_color, text_color = random.choice(COLORS)
    img = Image.new('RGB', (800, 800), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    # Draw text
    text = item_name[:30]  # Truncate long names
    
    # Calculate text position (centered)
    bbox = draw.textbbox((0, 0), text, font=font_small)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (800 - text_width) // 2
    y = (800 - text_height) // 2 - 50
    
    # Draw item name
    draw.text((x, y), text, fill=text_color, font=font_small)
    
    # Draw image number
    number_text = f"Image {image_number}"
    bbox = draw.textbbox((0, 0), number_text, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (800 - text_width) // 2
    y = y + 100
    
    draw.text((x, y), number_text, fill=text_color, font=font_small)
    
    # Draw decorative elements
    draw.rectangle([50, 50, 750, 750], outline=text_color, width=3)
    
    # Save
    img.save(save_path, 'JPEG', quality=85)


def add_images_to_items(item_count=10):
    """Add placeholder images to random items"""
    db = Database()
    items = db.get_all_items()
    
    if not items:
        print("No items in database. Run generate_test_data.py first.")
        return
    
    # Select random items
    selected_items = random.sample(items, min(item_count, len(items)))
    
    print(f"Adding images to {len(selected_items)} items...\n")
    
    for item in selected_items:
        item_id = item['id']
        item_name = item['item_name']
        
        # Create images directory
        item_dir = Path(f"./data/images/item_{item_id}")
        item_dir.mkdir(parents=True, exist_ok=True)
        
        # Create 3 placeholder images
        image_paths = []
        for i in range(1, 4):
            image_path = item_dir / f"image{i}.jpg"
            create_placeholder_image(item_name, i, str(image_path))
            image_paths.append(str(image_path))
        
        # Update database
        item['selected_images'] = image_paths
        db.update_item(item_id, item)
        
        print(f"✓ Added 3 images to: {item_name[:50]}")
    
    print(f"\n✓ Successfully added images to {len(selected_items)} items")
    print("\nYou can now:")
    print("  1. Run the app: python main.py")
    print("  2. Select an item and press 'r' to generate report")
    print("  3. Press 'o' to open the report in browser")
    print("  4. Press 'm' to generate master index")


if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("FlipTrack Test Image Generator")
    print("=" * 80)
    print()
    
    # Check if user wants to specify count
    count = 10
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Invalid count, using default of 10")
    
    add_images_to_items(count)
