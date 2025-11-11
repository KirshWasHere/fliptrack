"""
Generate complete test data: providers, items, and images
Run with: python generate_full_test_data.py [count]
"""

import random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from database import Database

# Provider data
PROVIDER_NAMES = [
    "Wholesale Direct",
    "Liquidation Depot",
    "StockX Marketplace",
    "eBay Seller Pro",
    "Amazon Returns",
    "Local Thrift Store",
    "Estate Sale Finds",
    "Retail Arbitrage Co",
    "Bulk Buyers Inc",
    "Discount Warehouse"
]

PROVIDER_CONTACTS = ["John Smith", "Sarah Johnson", "Mike Chen", "Lisa Anderson", "David Brown"]
PROVIDER_TAGS = ["wholesale", "liquidation", "retail arbitrage", "thrift", "online", "local"]

# Item data
SNEAKER_ITEMS = [
    "Nike Air Jordan 1 Retro High",
    "Adidas Yeezy Boost 350 V2",
    "Nike Dunk Low Panda",
    "New Balance 550 White Green",
    "Air Jordan 4 Military Black",
    "Nike SB Dunk Low Travis Scott",
    "Adidas Forum Low Bad Bunny",
    "Nike Air Max 1 Patta",
    "Jordan 1 Low Golf Midnight Navy",
    "Yeezy Slide Bone"
]

ELECTRONICS_ITEMS = [
    "iPhone 14 Pro Max 256GB",
    "PlayStation 5 Disc Edition",
    "Xbox Series X Console",
    "Apple AirPods Pro 2nd Gen",
    "Samsung Galaxy S23 Ultra",
    "Nintendo Switch OLED",
    "iPad Air 5th Generation",
    "Sony WH-1000XM5 Headphones",
    "Apple Watch Series 8",
    "MacBook Air M2 13-inch",
    "Steam Deck 512GB",
    "DJI Mini 3 Pro Drone"
]

GENERAL_ITEMS = [
    "Supreme Box Logo Hoodie",
    "Louis Vuitton Neverfull MM",
    "Canada Goose Expedition Parka",
    "The North Face Nuptse Jacket",
    "Patagonia Better Sweater",
    "Lululemon Align Leggings",
    "Ray-Ban Aviator Sunglasses",
    "Yeti Rambler 30oz Tumbler",
    "Carhartt WIP Detroit Jacket",
    "Stussy 8 Ball Hoodie"
]

BOOK_ITEMS = [
    "Harry Potter Complete Collection",
    "The Lord of the Rings Box Set",
    "First Edition To Kill a Mockingbird",
    "Signed Stephen King IT",
    "Game of Thrones Leather Bound Set",
    "Pokemon Card Base Set Booster Box",
    "Magic: The Gathering Black Lotus",
    "Vintage National Geographic Collection"
]

STATUSES = ["Draft", "Listed", "Sold"]

SAMPLE_URLS = [
    "https://stockx.com/product",
    "https://www.ebay.com/itm/12345",
    "https://www.goat.com/sneakers",
    "https://www.amazon.com/dp/B0ABC123",
    "https://www.grailed.com/listings/12345"
]

COLORS = [
    ("#1a1a1a", "#4ade80"),
    ("#1a1a1a", "#60a5fa"),
    ("#1a1a1a", "#f87171"),
    ("#1a1a1a", "#fbbf24"),
    ("#1a1a1a", "#a78bfa"),
]


def create_placeholder_image(item_name, image_number, save_path):
    """Create a placeholder image"""
    bg_color, text_color = random.choice(COLORS)
    img = Image.new('RGB', (800, 800), color=bg_color)
    draw = ImageDraw.Draw(img)
    
    try:
        font_large = ImageFont.truetype("arial.ttf", 50)
        font_small = ImageFont.truetype("arial.ttf", 35)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Draw text
    text = item_name[:30]
    bbox = draw.textbbox((0, 0), text, font=font_small)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (800 - text_width) // 2
    y = (800 - text_height) // 2 - 50
    
    draw.text((x, y), text, fill=text_color, font=font_small)
    
    # Draw image number
    number_text = f"Image {image_number}"
    bbox = draw.textbbox((0, 0), number_text, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (800 - text_width) // 2
    y = y + 100
    
    draw.text((x, y), number_text, fill=text_color, font=font_small)
    
    # Draw border
    draw.rectangle([50, 50, 750, 750], outline=text_color, width=3)
    
    img.save(save_path, 'JPEG', quality=85)


def generate_providers(count=10):
    """Generate random providers"""
    db = Database()
    provider_ids = []
    
    print("=" * 80)
    print("GENERATING PROVIDERS")
    print("=" * 80)
    
    for i in range(count):
        provider_data = {
            'name': random.choice(PROVIDER_NAMES),
            'contact_person': random.choice(PROVIDER_CONTACTS) if random.random() > 0.3 else "",
            'phone': f"({random.randint(200,999)}) {random.randint(200,999)}-{random.randint(1000,9999)}" if random.random() > 0.2 else "",
            'email': f"contact{i}@{random.choice(['wholesale', 'liquidation', 'supplier'])}.com" if random.random() > 0.3 else "",
            'website': random.choice(SAMPLE_URLS) if random.random() > 0.4 else "",
            'notes': random.choice([
                "Fast shipping, reliable",
                "Good prices but slow",
                "Best for bulk orders",
                "Local pickup available",
                "Excellent customer service"
            ]) if random.random() > 0.5 else "",
            'tags': ", ".join(random.sample(PROVIDER_TAGS, random.randint(1, 3)))
        }
        
        try:
            provider_id = db.add_provider(provider_data)
            provider_ids.append(provider_id)
            print(f"✓ Created provider: {provider_data['name']:<30} | ID: {provider_id}")
        except Exception as e:
            print(f"✗ Failed to create provider: {e}")
    
    print(f"\n✓ Created {len(provider_ids)} providers\n")
    return provider_ids


def generate_items(count=30, provider_ids=None):
    """Generate random items with optional provider links"""
    db = Database()
    
    print("=" * 80)
    print("GENERATING ITEMS")
    print("=" * 80)
    
    all_items = {
        'Sneakers': SNEAKER_ITEMS,
        'Electronics': ELECTRONICS_ITEMS,
        'General': GENERAL_ITEMS,
        'Books': BOOK_ITEMS
    }
    
    created_items = []
    
    for i in range(count):
        category = random.choice(list(all_items.keys()))
        item_list = all_items[category]
        item_name = random.choice(item_list)
        
        # Generate prices based on category
        if category == 'Electronics':
            purchase_price = round(random.uniform(200, 800), 2)
        elif category == 'Sneakers':
            purchase_price = round(random.uniform(80, 300), 2)
        elif category == 'Books':
            purchase_price = round(random.uniform(20, 150), 2)
        else:
            purchase_price = round(random.uniform(50, 500), 2)
        
        shipping_cost = round(random.uniform(5, 25), 2)
        profit_margin = random.uniform(1.15, 1.5)
        target_price = round(purchase_price * profit_margin, 2)
        
        status = random.choice(STATUSES)
        final_sold_price = None
        if status == "Sold":
            variance = random.uniform(0.9, 1.15)
            final_sold_price = round(target_price * variance, 2)
        
        # Link to random provider (70% chance)
        provider_id = None
        if provider_ids and random.random() > 0.3:
            provider_id = random.choice(provider_ids)
        
        product_url = random.choice(SAMPLE_URLS) if random.random() > 0.3 else ""
        
        item_data = {
            'item_name': item_name,
            'category': category,
            'purchase_price': purchase_price,
            'shipping_cost': shipping_cost,
            'target_price': target_price,
            'product_url': product_url,
            'status': status,
            'final_sold_price': final_sold_price,
            'image_urls_cache': [],
            'selected_images': [],
            'provider_id': provider_id
        }
        
        try:
            item_id = db.add_item(item_data)
            created_items.append(item_id)
            
            potential_profit = target_price - purchase_price - shipping_cost
            provider_text = f" | Provider: {provider_id}" if provider_id else ""
            print(f"✓ {item_name[:40]:<40} | {status:<7} | ${potential_profit:>7.2f}{provider_text}")
        except Exception as e:
            print(f"✗ Failed to create {item_name}: {e}")
    
    print(f"\n✓ Created {len(created_items)} items\n")
    return created_items


def add_images_to_items(item_ids, percentage=0.6):
    """Add placeholder images to a percentage of items"""
    db = Database()
    
    # Select random items to add images to
    items_to_image = random.sample(item_ids, int(len(item_ids) * percentage))
    
    print("=" * 80)
    print("GENERATING IMAGES")
    print("=" * 80)
    
    for item_id in items_to_image:
        item = db.get_item(item_id)
        if not item:
            continue
        
        item_name = item['item_name']
        item_dir = Path(f"./data/images/item_{item_id}")
        item_dir.mkdir(parents=True, exist_ok=True)
        
        # Create 3 images
        image_paths = []
        for i in range(1, 4):
            image_path = item_dir / f"image{i}.jpg"
            create_placeholder_image(item_name, i, str(image_path))
            image_paths.append(str(image_path))
        
        # Update database
        item['selected_images'] = image_paths
        db.update_item(item_id, item)
        
        print(f"✓ Added 3 images to: {item_name[:50]}")
    
    print(f"\n✓ Added images to {len(items_to_image)} items\n")


def generate_summary():
    """Print summary statistics"""
    db = Database()
    stats = db.get_summary_stats()
    items = db.get_all_items()
    providers = db.get_all_providers()
    
    print("=" * 80)
    print("DATABASE SUMMARY")
    print("=" * 80)
    print(f"Total Providers: {len(providers)}")
    print(f"Total Items: {stats['total_items']}")
    print(f"Total Potential Profit: ${stats['total_potential_profit']:.2f}")
    print(f"Total Actual Profit: ${stats['total_actual_profit']:.2f}")
    
    # Count by status
    draft_count = len([i for i in items if i['status'] == 'Draft'])
    listed_count = len([i for i in items if i['status'] == 'Listed'])
    sold_count = len([i for i in items if i['status'] == 'Sold'])
    
    print(f"\nItems by Status:")
    print(f"  Draft: {draft_count}")
    print(f"  Listed: {listed_count}")
    print(f"  Sold: {sold_count}")
    
    # Count by category
    categories = {}
    for item in items:
        cat = item.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nItems by Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    # Items with providers
    items_with_providers = len([i for i in items if i.get('provider_id')])
    print(f"\nItems linked to providers: {items_with_providers}")
    
    # Items with images
    items_with_images = len([i for i in items if i.get('selected_images')])
    print(f"Items with images: {items_with_images}")
    
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("FlipTrack Complete Test Data Generator")
    print("=" * 80)
    print()
    
    # Get counts from command line
    item_count = 30
    provider_count = 10
    
    if len(sys.argv) > 1:
        try:
            item_count = int(sys.argv[1])
        except ValueError:
            print("Invalid count, using default of 30 items")
    
    if len(sys.argv) > 2:
        try:
            provider_count = int(sys.argv[2])
        except ValueError:
            print("Invalid count, using default of 10 providers")
    
    print(f"Generating {provider_count} providers and {item_count} items...\n")
    
    # Generate everything
    provider_ids = generate_providers(provider_count)
    item_ids = generate_items(item_count, provider_ids)
    add_images_to_items(item_ids, percentage=0.6)
    
    generate_summary()
    
    print("\nYou can now:")
    print("  1. Run the app: python main.py")
    print("  2. Press 'p' to view providers")
    print("  3. Press 'v' on a provider to see their items")
    print("  4. Generate reports (press 'r' or Ctrl+R)")
    print("  5. Export to CSV (Ctrl+E)")
    print("  6. Create backup (Ctrl+B)")
