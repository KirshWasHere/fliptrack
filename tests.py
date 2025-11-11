"""
Test suite for FlipTrack
Run with: python tests.py
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Test results
tests_passed = 0
tests_failed = 0
test_errors = []


def test(name):
    """Decorator for test functions"""
    def decorator(func):
        def wrapper():
            global tests_passed, tests_failed, test_errors
            try:
                print(f"Testing {name}...", end=" ")
                func()
                print("[PASS]")
                tests_passed += 1
            except AssertionError as e:
                print(f"[FAIL]: {e}")
                tests_failed += 1
                test_errors.append((name, str(e)))
            except Exception as e:
                print(f"[ERROR]: {e}")
                tests_failed += 1
                test_errors.append((name, f"Error: {e}"))
        return wrapper
    return decorator


@test("Import core modules")
def test_imports():
    """Test that all core modules can be imported"""
    import database
    import scraper
    import report_generator
    import utils
    import config
    import export_utils
    assert True


@test("Database initialization")
def test_database_init():
    """Test database creation"""
    from database import Database
    
    # Use temp database
    temp_db = tempfile.mktemp(suffix=".db")
    try:
        db = Database(temp_db)
        assert os.path.exists(temp_db), "Database file not created"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


@test("Add item to database")
def test_add_item():
    """Test adding an item"""
    from database import Database
    
    temp_db = tempfile.mktemp(suffix=".db")
    try:
        db = Database(temp_db)
        item_data = {
            'item_name': 'Test Item',
            'purchase_price': 100.0,
            'shipping_cost': 10.0,
            'target_price': 150.0,
            'status': 'Draft',
            'category': 'General'
        }
        item_id = db.add_item(item_data)
        assert item_id > 0, "Item ID should be positive"
        
        # Verify item was added
        item = db.get_item(item_id)
        assert item is not None, "Item not found"
        assert item['item_name'] == 'Test Item', "Item name mismatch"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


@test("Update item in database")
def test_update_item():
    """Test updating an item"""
    from database import Database
    
    temp_db = tempfile.mktemp(suffix=".db")
    try:
        db = Database(temp_db)
        item_data = {
            'item_name': 'Test Item',
            'purchase_price': 100.0,
            'shipping_cost': 10.0,
            'target_price': 150.0,
            'status': 'Draft',
            'category': 'General'
        }
        item_id = db.add_item(item_data)
        
        # Update item
        item_data['item_name'] = 'Updated Item'
        item_data['status'] = 'Listed'
        db.update_item(item_id, item_data)
        
        # Verify update
        item = db.get_item(item_id)
        assert item['item_name'] == 'Updated Item', "Item name not updated"
        assert item['status'] == 'Listed', "Status not updated"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


@test("Delete item from database")
def test_delete_item():
    """Test deleting an item"""
    from database import Database
    
    temp_db = tempfile.mktemp(suffix=".db")
    try:
        db = Database(temp_db)
        item_data = {
            'item_name': 'Test Item',
            'purchase_price': 100.0,
            'shipping_cost': 10.0,
            'target_price': 150.0,
            'status': 'Draft',
            'category': 'General'
        }
        item_id = db.add_item(item_data)
        
        # Delete item
        db.delete_item(item_id)
        
        # Verify deletion
        item = db.get_item(item_id)
        assert item is None, "Item should be deleted"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


@test("Search and filter items")
def test_search_filter():
    """Test search and filter functionality"""
    from database import Database
    
    temp_db = tempfile.mktemp(suffix=".db")
    try:
        db = Database(temp_db)
        
        # Add test items
        db.add_item({
            'item_name': 'Nike Shoes',
            'purchase_price': 100.0,
            'shipping_cost': 10.0,
            'target_price': 150.0,
            'status': 'Draft',
            'category': 'Sneakers'
        })
        db.add_item({
            'item_name': 'Adidas Shoes',
            'purchase_price': 90.0,
            'shipping_cost': 10.0,
            'target_price': 140.0,
            'status': 'Listed',
            'category': 'Sneakers'
        })
        db.add_item({
            'item_name': 'iPhone',
            'purchase_price': 500.0,
            'shipping_cost': 20.0,
            'target_price': 700.0,
            'status': 'Sold',
            'category': 'Electronics'
        })
        
        # Test search
        results = db.get_all_items(search_query="Nike")
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0]['item_name'] == 'Nike Shoes'
        
        # Test filter
        results = db.get_all_items(status_filter="Listed")
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
        assert results[0]['status'] == 'Listed'
        
        # Test combined
        results = db.get_all_items(search_query="Shoes", status_filter="Draft")
        assert len(results) == 1, f"Expected 1 result, got {len(results)}"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)


@test("Profit calculations")
def test_profit_calculations():
    """Test profit calculation functions"""
    from utils import calculate_potential_profit, calculate_actual_profit
    
    potential = calculate_potential_profit(100.0, 10.0, 150.0)
    assert potential == 40.0, f"Expected 40.0, got {potential}"
    
    actual = calculate_actual_profit(100.0, 10.0, 160.0)
    assert actual == 50.0, f"Expected 50.0, got {actual}"


@test("Input validation - prices")
def test_validate_price():
    """Test price validation"""
    from utils import validate_price
    
    # Valid prices
    valid, value, msg = validate_price("100.50")
    assert valid, "Valid price rejected"
    assert value == 100.50
    
    valid, value, msg = validate_price("0")
    assert valid, "Zero price rejected"
    
    # Invalid prices
    valid, value, msg = validate_price("-10")
    assert not valid, "Negative price accepted"
    
    valid, value, msg = validate_price("abc")
    assert not valid, "Non-numeric price accepted"
    
    valid, value, msg = validate_price("9999999")
    assert not valid, "Excessive price accepted"


@test("Input validation - URLs")
def test_validate_url():
    """Test URL validation"""
    from utils import validate_url
    
    # Valid URLs
    valid, msg = validate_url("https://example.com")
    assert valid, "Valid HTTPS URL rejected"
    
    valid, msg = validate_url("http://example.com")
    assert valid, "Valid HTTP URL rejected"
    
    valid, msg = validate_url("")
    assert valid, "Empty URL rejected (should be optional)"
    
    # Invalid URLs
    valid, msg = validate_url("not-a-url")
    assert not valid, "Invalid URL accepted"
    
    valid, msg = validate_url("ftp://example.com")
    assert not valid, "FTP URL accepted"


@test("Input validation - item names")
def test_validate_item_name():
    """Test item name validation"""
    from utils import validate_item_name
    
    # Valid names
    valid, msg = validate_item_name("Nike Shoes")
    assert valid, "Valid name rejected"
    
    valid, msg = validate_item_name("AB")
    assert valid, "2-char name rejected"
    
    # Invalid names
    valid, msg = validate_item_name("")
    assert not valid, "Empty name accepted"
    
    valid, msg = validate_item_name("A")
    assert not valid, "1-char name accepted"
    
    valid, msg = validate_item_name("A" * 201)
    assert not valid, "Excessive length name accepted"


@test("Report generation")
def test_report_generation():
    """Test HTML report generation"""
    from database import Database
    from report_generator import ReportGenerator
    
    temp_db = tempfile.mktemp(suffix=".db")
    temp_reports = tempfile.mkdtemp()
    
    try:
        db = Database(temp_db)
        item_data = {
            'item_name': 'Test Item',
            'purchase_price': 100.0,
            'shipping_cost': 10.0,
            'target_price': 150.0,
            'status': 'Draft',
            'category': 'General',
            'product_url': 'https://example.com'
        }
        item_id = db.add_item(item_data)
        item = db.get_item(item_id)
        
        # Generate report
        generator = ReportGenerator()
        generator.reports_dir = Path(temp_reports)
        report_path = generator.generate_report(item)
        
        assert os.path.exists(report_path), "Report file not created"
        
        # Check report content
        with open(report_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test Item' in content, "Item name not in report"
            assert '$100.00' in content, "Purchase price not in report"
    finally:
        if os.path.exists(temp_db):
            os.remove(temp_db)
        if os.path.exists(temp_reports):
            shutil.rmtree(temp_reports)


@test("CSV export")
def test_csv_export():
    """Test CSV export functionality"""
    import database
    import export_utils
    
    temp_db = tempfile.mktemp(suffix=".db")
    temp_csv = tempfile.mktemp(suffix=".csv")
    
    # Temporarily replace the default database path
    original_db_init = database.Database.__init__
    
    def temp_db_init(self, db_path=None):
        original_db_init(self, temp_db)
    
    try:
        database.Database.__init__ = temp_db_init
        
        db = database.Database()
        db.add_item({
            'item_name': 'Test Item',
            'purchase_price': 100.0,
            'shipping_cost': 10.0,
            'target_price': 150.0,
            'status': 'Draft',
            'category': 'General'
        })
        
        # Export to CSV
        path = export_utils.export_to_csv(temp_csv)
        assert os.path.exists(path), "CSV file not created"
        
        # Check CSV content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'Test Item' in content, "Item not in CSV"
            assert 'ID' in content, "CSV header missing"
    finally:
        database.Database.__init__ = original_db_init
        if os.path.exists(temp_db):
            os.remove(temp_db)
        if os.path.exists(temp_csv):
            os.remove(temp_csv)


def run_tests():
    """Run all tests"""
    print("=" * 60)
    print("FlipTrack Test Suite")
    print("=" * 60)
    print()
    
    # Run all test functions
    test_imports()
    test_database_init()
    test_add_item()
    test_update_item()
    test_delete_item()
    test_search_filter()
    test_profit_calculations()
    test_validate_price()
    test_validate_url()
    test_validate_item_name()
    test_report_generation()
    test_csv_export()
    
    # Print summary
    print()
    print("=" * 60)
    print(f"Tests Passed: {tests_passed}")
    print(f"Tests Failed: {tests_failed}")
    print("=" * 60)
    
    if test_errors:
        print("\nFailed Tests:")
        for name, error in test_errors:
            print(f"  - {name}: {error}")
    
    return tests_failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
