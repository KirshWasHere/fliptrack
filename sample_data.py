"""
Generate sample data for testing the Reselling Profit Tracker
"""

from database import Database
import random

def generate_sample_data():
    """Generate sample items for demonstration"""
    
    db = Database()
    
    sample_items = [
        {
            'item_name': 'Nike Air Jordan 1 Retro High OG Chicago',
            'category': 'Sneakers',
            'purchase_price': 150.00,
            'shipping_cost': 10.00,
            'target_price': 300.00,
            'product_url': 'https://stockx.com/air-jordan-1-retro-high-og-chicago',
            'status': 'Sold',
            'final_sold_price': 280.00,
            'image_urls_cache': [],
            'selected_images': []
        },
        {
            'item_name': 'PlayStation 5 Console',
            'category': 'Electronics',
            'purchase_price': 450.00,
            'shipping_cost': 15.00,
            'target_price': 600.00,
            'product_url': 'https://www.ebay.com/itm/playstation-5',
            'status': 'Listed',
            'final_sold_price': None,
            'image_urls_cache': [],
            'selected_images': []
        },
        {
            'item_name': 'Adidas Yeezy Boost 350 V2 Zebra',
            'category': 'Sneakers',
            'purchase_price': 220.00,
            'shipping_cost': 12.00,
            'target_price': 400.00,
            'product_url': 'https://stockx.com/adidas-yeezy-boost-350-v2-zebra',
            'status': 'Listed',
            'final_sold_price': None,
            'image_urls_cache': [],
            'selected_images': []
        },
        {
            'item_name': 'Apple AirPods Pro 2nd Generation',
            'category': 'Electronics',
            'purchase_price': 180.00,
            'shipping_cost': 8.00,
            'target_price': 230.00,
            'product_url': 'https://www.ebay.com/itm/airpods-pro',
            'status': 'Draft',
            'final_sold_price': None,
            'image_urls_cache': [],
            'selected_images': []
        },
        {
            'item_name': 'Supreme Box Logo Hoodie Black',
            'category': 'General',
            'purchase_price': 500.00,
            'shipping_cost': 20.00,
            'target_price': 800.00,
            'product_url': 'https://www.grailed.com/listings/supreme-box-logo',
            'status': 'Sold',
            'final_sold_price': 750.00,
            'image_urls_cache': [],
            'selected_images': []
        },
        {
            'item_name': 'Nintendo Switch OLED',
            'category': 'Electronics',
            'purchase_price': 300.00,
            'shipping_cost': 10.00,
            'target_price': 380.00,
            'product_url': 'https://www.ebay.com/itm/nintendo-switch-oled',
            'status': 'Listed',
            'final_sold_price': None,
            'image_urls_cache': [],
            'selected_images': []
        },
        {
            'item_name': 'New Balance 550 White Green',
            'category': 'Sneakers',
            'purchase_price': 110.00,
            'shipping_cost': 8.00,
            'target_price': 180.00,
            'product_url': 'https://stockx.com/new-balance-550-white-green',
            'status': 'Sold',
            'final_sold_price': 165.00,
            'image_urls_cache': [],
            'selected_images': []
        },
        {
            'item_name': 'Vintage Pokemon Card Collection',
            'category': 'General',
            'purchase_price': 200.00,
            'shipping_cost': 5.00,
            'target_price': 450.00,
            'product_url': 'https://www.ebay.com/itm/pokemon-cards',
            'status': 'Draft',
            'final_sold_price': None,
            'image_urls_cache': [],
            'selected_images': []
        }
    ]
    
    print("Generating sample data...")
    print("=" * 60)
    
    for item in sample_items:
        item_id = db.add_item(item)
        potential_profit = item['target_price'] - item['purchase_price'] - item['shipping_cost']
        
        print(f"[{item['status']}] Added: {item['item_name']}")
        print(f"   ID: {item_id} | Potential Profit: ${potential_profit:.2f}")
        
        if item['status'] == 'Sold' and item['final_sold_price']:
            actual_profit = item['final_sold_price'] - item['purchase_price'] - item['shipping_cost']
            print(f"   Actual Profit: ${actual_profit:.2f}")
        print()
    
    print("=" * 60)
    stats = db.get_summary_stats()
    print(f"✅ Generated {stats['total_items']} sample items")
    print(f"💰 Total Potential Profit: ${stats['total_potential_profit']:.2f}")
    print(f"💵 Total Actual Profit: ${stats['total_actual_profit']:.2f}")
    print("=" * 60)
    print("\nRun 'python main.py' to view in the application!")

if __name__ == "__main__":
    generate_sample_data()
