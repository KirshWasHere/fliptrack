"""
Test script to verify the Reselling Profit Tracker setup
"""

import sys
import os

def test_imports():
    """Test if all required packages are installed"""
    print("Testing package imports...")
    
    packages = {
        'textual': 'Textual',
        'rich': 'Rich',
        'bs4': 'BeautifulSoup4',
        'httpx': 'httpx',
        'jinja2': 'Jinja2',
        'qrcode': 'qrcode',
        'PIL': 'Pillow'
    }
    
    failed = []
    for package, name in packages.items():
        try:
            __import__(package)
            print(f"  ✓ {name}")
        except ImportError:
            print(f"  ✗ {name} - NOT INSTALLED")
            failed.append(name)
    
    if failed:
        print(f"\n❌ Missing packages: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All packages installed successfully!")
        return True

def test_modules():
    """Test if custom modules can be imported"""
    print("\nTesting custom modules...")
    
    modules = ['database', 'scraper', 'report_generator']
    failed = []
    
    for module in modules:
        try:
            __import__(module)
            print(f"  ✓ {module}.py")
        except Exception as e:
            print(f"  ✗ {module}.py - ERROR: {e}")
            failed.append(module)
    
    if failed:
        print(f"\n❌ Module errors: {', '.join(failed)}")
        return False
    else:
        print("\n✅ All modules loaded successfully!")
        return True

def test_database():
    """Test database creation"""
    print("\nTesting database...")
    
    try:
        from database import Database
        db = Database("test_tracker.db")
        
        # Test adding an item
        test_item = {
            'item_name': 'Test Item',
            'purchase_price': 50.0,
            'shipping_cost': 5.0,
            'target_price': 100.0,
            'product_url': 'https://example.com',
            'status': 'Draft',
            'category': 'General'
        }
        
        item_id = db.add_item(test_item)
        print(f"  ✓ Created test item (ID: {item_id})")
        
        # Test retrieving
        item = db.get_item(item_id)
        if item and item['item_name'] == 'Test Item':
            print(f"  ✓ Retrieved test item")
        
        # Test stats
        stats = db.get_summary_stats()
        print(f"  ✓ Stats: {stats['total_items']} items, ${stats['total_potential_profit']:.2f} potential profit")
        
        # Cleanup
        db.delete_item(item_id)
        os.remove("test_tracker.db")
        print(f"  ✓ Cleaned up test database")
        
        print("\n✅ Database operations working!")
        return True
        
    except Exception as e:
        print(f"\n❌ Database error: {e}")
        return False

def test_report_generation():
    """Test report generation"""
    print("\nTesting report generation...")
    
    try:
        from report_generator import ReportGenerator
        
        generator = ReportGenerator()
        
        test_item = {
            'id': 999,
            'item_name': 'Test Product',
            'purchase_price': 50.0,
            'shipping_cost': 5.0,
            'target_price': 100.0,
            'product_url': 'https://example.com/product',
            'status': 'Listed',
            'final_sold_price': None,
            'selected_images': []
        }
        
        report_path = generator.generate_report(test_item)
        
        if os.path.exists(report_path):
            print(f"  ✓ Generated test report: {report_path}")
            
            # Check file size
            size = os.path.getsize(report_path)
            print(f"  ✓ Report size: {size} bytes")
            
            # Cleanup
            os.remove(report_path)
            print(f"  ✓ Cleaned up test report")
            
            print("\n✅ Report generation working!")
            return True
        else:
            print(f"\n❌ Report file not created")
            return False
            
    except Exception as e:
        print(f"\n❌ Report generation error: {e}")
        return False

def main():
    print("=" * 60)
    print("Reselling Profit Tracker - Setup Test")
    print("=" * 60)
    
    results = []
    
    results.append(test_imports())
    results.append(test_modules())
    results.append(test_database())
    results.append(test_report_generation())
    
    print("\n" + "=" * 60)
    if all(results):
        print("🎉 All tests passed! You're ready to run the application.")
        print("\nRun: python main.py")
    else:
        print("⚠️  Some tests failed. Please fix the issues above.")
        print("\nCommon fixes:")
        print("  - Install dependencies: pip install -r requirements.txt")
        print("  - Check Python version: python --version (need 3.8+)")
    print("=" * 60)

if __name__ == "__main__":
    main()
