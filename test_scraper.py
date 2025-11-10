"""
Test script to demonstrate image scraping
"""

from scraper import ImageScraper
import os

def test_scraping():
    print("=" * 60)
    print("IMAGE SCRAPING DEMONSTRATION")
    print("=" * 60)
    
    scraper = ImageScraper()
    
    # Test 1: Scrape sneaker images
    print("\n1. Scraping sneaker images...")
    print("   Item: Nike Air Jordan 1")
    print("   Category: Sneakers")
    print("   Target: StockX")
    
    urls = scraper.scrape_images("Nike Air Jordan 1", "Sneakers")
    
    if urls:
        print(f"\n   ✅ Found {len(urls)} images!")
        print("\n   First 5 URLs:")
        for i, url in enumerate(urls[:5], 1):
            short_url = url[:70] + "..." if len(url) > 70 else url
            print(f"   {i}. {short_url}")
    else:
        print("   ❌ No images found")
    
    # Test 2: Download an image
    print("\n" + "=" * 60)
    print("2. Downloading first image...")
    
    if urls:
        test_dir = "./test_images"
        os.makedirs(test_dir, exist_ok=True)
        
        test_path = os.path.join(test_dir, "test_image.jpg")
        success = scraper.download_image(urls[0], test_path)
        
        if success and os.path.exists(test_path):
            size = os.path.getsize(test_path)
            print(f"   ✅ Downloaded successfully!")
            print(f"   Path: {test_path}")
            print(f"   Size: {size:,} bytes ({size/1024:.1f} KB)")
            
            # Cleanup
            os.remove(test_path)
            os.rmdir(test_dir)
            print("   🧹 Cleaned up test files")
        else:
            print("   ❌ Download failed")
    
    # Test 3: Different categories
    print("\n" + "=" * 60)
    print("3. Testing different categories...")
    
    test_items = [
        ("iPhone 15 Pro", "Electronics"),
        ("Harry Potter Book", "Books"),
        ("Vintage Camera", "General")
    ]
    
    for item_name, category in test_items:
        print(f"\n   Item: {item_name}")
        print(f"   Category: {category}")
        urls = scraper.scrape_images(item_name, category)
        print(f"   Result: {len(urls)} images found")
    
    print("\n" + "=" * 60)
    print("DEMONSTRATION COMPLETE")
    print("=" * 60)
    print("\nHow it works:")
    print("1. User enters item name and selects category")
    print("2. Scraper chooses appropriate website")
    print("3. Fetches and parses HTML")
    print("4. Extracts image URLs")
    print("5. Returns list of URLs")
    print("6. App downloads first 3 images")
    print("7. Stores locally in ./data/images/item_X/")
    print("8. Saves URLs to database as JSON")
    print("9. When generating report, converts to Base64")
    print("10. Embeds in self-contained HTML")

if __name__ == "__main__":
    test_scraping()
