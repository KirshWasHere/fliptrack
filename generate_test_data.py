"""
Generate random test data for FlipTrack
Run with: python generate_test_data.py
"""

import random
from database import Database

# Sample data
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
    "DJI Mini 3 Pro Drone",
    "GoPro Hero 11 Black",
    "Bose QuietComfort 45",
    "Meta Quest 3 VR Headset"
]

GENERAL_ITEMS = [
    "Supreme Box Logo Hoodie",
    "Louis Vuitton Neverfull MM",
    "Rolex Submariner Date",
    "Canada Goose Expedition Parka",
    "The North Face Nuptse Jacket",
    "Patagonia Better Sweater",
    "Lululemon Align Leggings",
    "Ray-Ban Aviator Sunglasses",
    "Yeti Rambler 30oz Tumbler",
    "Hydro Flask 32oz Wide Mouth",
    "Carhartt WIP Detroit Jacket",
    "Stussy 8 Ball Hoodie",
    "Palace Tri-Ferg T-Shirt",
    "KITH Box Logo Crewneck",
    "Bape Shark Hoodie Full Zip"
]

BOOK_ITEMS = [
    "Harry Potter Complete Collection",
    "The Lord of the Rings Box Set",
    "First Edition To Kill a Mockingbird",
    "Signed Stephen King IT",
    "Game of Thrones Leather Bound Set",
    "Marvel Comics Amazing Spider-Man #1",
    "Pokemon Card Base Set Booster Box",
    "Magic: The Gathering Black Lotus",
    "Vintage National Geographic Collection",
    "Signed J.K. Rowling Harry Potter"
]

STATUSES = ["Draft", "Listed", "Sold"]

URLS = [
    "https://stockx.com/product",
    "https://www.ebay.com/itm/12345",
    "https://www.goat.com/sneakers",
    "https://www.amazon.com/dp/B0ABC123",
    "https://www.grailed.com/listings/12345",
    ""  # Some items without URLs
]


def generate_random_items(count=20):
    """Generate random test items"""
    db = Database()
    
    # Combine all items
    all_items = {
        'Sneakers': SNEAKER_ITEMS,
        'Electronics': ELECTRONICS_ITEMS,
        'General': GENERAL_ITEMS,
        'Books': BOOK_ITEMS
    }
    
    created_items = []
    
    for i in range(count):
        # Pick random category
        category = random.choice(list(all_items.keys()))
        item_list = all_items[category]
        
        # Pick random item name
        item_name = random.choice(item_list)
        
        # Generate random prices
        if category == 'Electronics':
            purchase_price = round(random.uniform(200, 800), 2)
        elif category == 'Sneakers':
            purchase_price = round(random.uniform(80, 300), 2)
        elif category == 'Books':
            purchase_price = round(random.uniform(20, 150), 2)
        else:  # General
            purchase_price = round(random.uniform(50, 500), 2)
        
        shipping_cost = round(random.uniform(5, 25), 2)
        
        # Target price with some profit margin
        profit_margin = random.uniform(1.15, 1.5)  # 15-50% markup
        target_price = round(purchase_price * profit_margin, 2)
        
        # Random status
        status = random.choice(STATUSES)
        
        # If sold, generate final price (might be higher or lower than target)
        final_sold_price = None
        if status == "Sold":
            variance = random.uniform(0.9, 1.15)  # -10% to +15% of target
            final_sold_price = round(target_price * variance, 2)
        
        # Random URL (some items won't have one)
        product_url = random.choice(URLS)
        
        # Create item data
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
            'selected_images': []
        }
        
        try:
            item_id = db.add_item(item_data)
            created_items.append(item_id)
            
            # Calculate profit for display
            potential_profit = target_price - purchase_price - shipping_cost
            actual_profit = ""
            if final_sold_price:
                actual_profit = f" | Actual: ${final_sold_price - purchase_price - shipping_cost:.2f}"
            
            print(f"[OK] Created: {item_name[:40]:<40} | {status:<7} | Potential: ${potential_profit:.2f}{actual_profit}")
        except Exception as e:
            print(f"[FAIL] Failed to create {item_name}: {e}")
    
    return created_items


def generate_summary():
    """Print summary of database"""
    db = Database()
    stats = db.get_summary_stats()
    items = db.get_all_items()
    
    print("\n" + "=" * 80)
    print("DATABASE SUMMARY")
    print("=" * 80)
    print(f"Total Items: {stats['total_items']}")
    print(f"Total Potential Profit: ${stats['total_potential_profit']:.2f}")
    print(f"Total Actual Profit: ${stats['total_actual_profit']:.2f}")
    
    # Count by status
    draft_count = len([i for i in items if i['status'] == 'Draft'])
    listed_count = len([i for i in items if i['status'] == 'Listed'])
    sold_count = len([i for i in items if i['status'] == 'Sold'])
    
    print(f"\nBy Status:")
    print(f"  Draft: {draft_count}")
    print(f"  Listed: {listed_count}")
    print(f"  Sold: {sold_count}")
    
    # Count by category
    categories = {}
    for item in items:
        cat = item.get('category', 'Unknown')
        categories[cat] = categories.get(cat, 0) + 1
    
    print(f"\nBy Category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print("=" * 80)


if __name__ == "__main__":
    import sys
    
    print("=" * 80)
    print("FlipTrack Test Data Generator")
    print("=" * 80)
    print()
    
    # Check if user wants to specify count
    count = 20
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            print("Invalid count, using default of 20")
    
    print(f"Generating {count} random test items...\n")
    
    created = generate_random_items(count)
    
    print(f"\n[OK] Successfully created {len(created)} items")
    
    generate_summary()
    
    print("\nYou can now:")
    print("  1. Run the app: python main.py")
    print("  2. Test search and filters")
    print("  3. Generate reports (press 'r' on any item)")
    print("  4. Export to CSV (Ctrl+E)")
    print("  5. Create backup (Ctrl+B)")
