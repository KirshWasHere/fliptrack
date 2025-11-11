"""
Export and backup utilities for FlipTrack
"""

import csv
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from database import Database


def export_to_csv(output_path: str = None) -> str:
    """Export all items to CSV file
    
    Args:
        output_path: Optional custom output path
        
    Returns:
        Path to created CSV file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"fliptrack_export_{timestamp}.csv"
    
    db = Database()
    items = db.get_all_items()
    
    if not items:
        raise Exception("No items to export")
    
    # Define CSV columns
    fieldnames = [
        'ID', 'Item Name', 'Category', 'Status', 'Condition',
        'Purchase Price', 'Shipping Cost', 'Listing Fee', 'Processing Fee', 
        'Storage Cost', 'Other Expenses', 'Target Price', 'Final Sold Price',
        'Potential Profit', 'Actual Profit',
        'Sales Channel', 'Product URL', 'Listing URL',
        'Tags', 'Notes', 'Storage Location',
        'Report Path', 'Image Count'
    ]
    
    with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for item in items:
            potential_profit = item['target_price'] - item['purchase_price'] - item['shipping_cost']
            actual_profit = 0
            if item['status'] == 'Sold' and item.get('final_sold_price'):
                actual_profit = item['final_sold_price'] - item['purchase_price'] - item['shipping_cost']
            
            image_count = len(item.get('selected_images', []))
            
            writer.writerow({
                'ID': item['id'],
                'Item Name': item['item_name'],
                'Category': item.get('category', ''),
                'Status': item['status'],
                'Condition': item.get('condition', ''),
                'Purchase Price': f"{item['purchase_price']:.2f}",
                'Shipping Cost': f"{item['shipping_cost']:.2f}",
                'Listing Fee': f"{item.get('listing_fee', 0):.2f}",
                'Processing Fee': f"{item.get('processing_fee', 0):.2f}",
                'Storage Cost': f"{item.get('storage_cost', 0):.2f}",
                'Other Expenses': f"{item.get('other_expenses', 0):.2f}",
                'Target Price': f"{item['target_price']:.2f}",
                'Final Sold Price': f"{item['final_sold_price']:.2f}" if item.get('final_sold_price') else '',
                'Potential Profit': f"{potential_profit:.2f}",
                'Actual Profit': f"{actual_profit:.2f}" if item['status'] == 'Sold' else '',
                'Sales Channel': item.get('sales_channel', ''),
                'Product URL': item.get('product_url', ''),
                'Listing URL': item.get('listing_url', ''),
                'Tags': item.get('tags', ''),
                'Notes': item.get('notes', ''),
                'Storage Location': item.get('storage_location', ''),
                'Report Path': item.get('report_path', ''),
                'Image Count': image_count
            })
    
    return output_path


def export_to_json(output_path: str = None) -> str:
    """Export all items to JSON file (full backup)
    
    Args:
        output_path: Optional custom output path
        
    Returns:
        Path to created JSON file
    """
    if output_path is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"fliptrack_backup_{timestamp}.json"
    
    db = Database()
    items = db.get_all_items()
    
    backup_data = {
        'export_date': datetime.now().isoformat(),
        'version': '1.0',
        'item_count': len(items),
        'items': items
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(backup_data, f, indent=2, ensure_ascii=False)
    
    return output_path


def create_full_backup(backup_dir: str = None) -> str:
    """Create full backup including database and images
    
    Args:
        backup_dir: Optional custom backup directory
        
    Returns:
        Path to backup directory
    """
    if backup_dir is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup_{timestamp}"
    
    backup_path = Path(backup_dir)
    backup_path.mkdir(exist_ok=True)
    
    # Backup database
    db_path = Path("tracker.db")
    if db_path.exists():
        shutil.copy2(db_path, backup_path / "tracker.db")
    
    # Backup images
    images_dir = Path("data/images")
    if images_dir.exists():
        shutil.copytree(images_dir, backup_path / "images", dirs_exist_ok=True)
    
    # Backup reports
    reports_dir = Path("reports")
    if reports_dir.exists():
        shutil.copytree(reports_dir, backup_path / "reports", dirs_exist_ok=True)
    
    # Create JSON export
    export_to_json(str(backup_path / "items_export.json"))
    
    # Create CSV export
    export_to_csv(str(backup_path / "items_export.csv"))
    
    # Create backup info file
    info = {
        'backup_date': datetime.now().isoformat(),
        'database_included': db_path.exists(),
        'images_included': images_dir.exists(),
        'reports_included': reports_dir.exists()
    }
    
    with open(backup_path / "backup_info.json", 'w') as f:
        json.dump(info, f, indent=2)
    
    return str(backup_path)


def restore_from_json(json_path: str) -> int:
    """Restore items from JSON backup
    
    Args:
        json_path: Path to JSON backup file
        
    Returns:
        Number of items restored
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        backup_data = json.load(f)
    
    items = backup_data.get('items', [])
    
    db = Database()
    restored_count = 0
    
    for item in items:
        try:
            # Remove id to let database auto-generate
            item_data = {k: v for k, v in item.items() if k != 'id'}
            db.add_item(item_data)
            restored_count += 1
        except Exception as e:
            print(f"Warning: Failed to restore item {item.get('item_name')}: {e}")
    
    return restored_count


def import_from_csv(csv_path: str) -> tuple[int, int]:
    """Import items from CSV file
    
    Args:
        csv_path: Path to CSV file
        
    Returns:
        Tuple of (success_count, error_count)
    """
    db = Database()
    success_count = 0
    error_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        
        for row in reader:
            try:
                item_data = {
                    'item_name': row.get('Item Name', ''),
                    'category': row.get('Category', ''),
                    'purchase_price': float(row.get('Purchase Price', 0)),
                    'shipping_cost': float(row.get('Shipping Cost', 0)),
                    'target_price': float(row.get('Target Price', 0)),
                    'product_url': row.get('Product URL', ''),
                    'status': row.get('Status', 'Draft'),
                    'final_sold_price': float(row['Final Sold Price']) if row.get('Final Sold Price') else None,
                    'listing_fee': float(row.get('Listing Fee', 0)),
                    'processing_fee': float(row.get('Processing Fee', 0)),
                    'storage_cost': float(row.get('Storage Cost', 0)),
                    'other_expenses': float(row.get('Other Expenses', 0)),
                    'sales_channel': row.get('Sales Channel', ''),
                    'listing_url': row.get('Listing URL', ''),
                    'tags': row.get('Tags', ''),
                    'notes': row.get('Notes', ''),
                    'condition': row.get('Condition', ''),
                    'storage_location': row.get('Storage Location', ''),
                    'image_urls_cache': [],
                    'selected_images': []
                }
                
                # Validate required fields
                if not item_data['item_name']:
                    print(f"Skipping row: Missing item name")
                    error_count += 1
                    continue
                
                db.add_item(item_data)
                success_count += 1
                
            except Exception as e:
                print(f"Error importing row: {e}")
                error_count += 1
    
    return success_count, error_count


if __name__ == "__main__":
    # CLI interface for export utilities
    import sys
    
    if len(sys.argv) < 2:
        print("FlipTrack Export Utilities")
        print("\nUsage:")
        print("  python export_utils.py csv [output.csv]")
        print("  python export_utils.py json [output.json]")
        print("  python export_utils.py backup [backup_dir]")
        print("  python export_utils.py restore <backup.json>")
        print("  python export_utils.py import <items.csv>")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "csv":
            output = sys.argv[2] if len(sys.argv) > 2 else None
            path = export_to_csv(output)
            print(f"CSV exported to: {path}")
        
        elif command == "json":
            output = sys.argv[2] if len(sys.argv) > 2 else None
            path = export_to_json(output)
            print(f"JSON exported to: {path}")
        
        elif command == "backup":
            backup_dir = sys.argv[2] if len(sys.argv) > 2 else None
            path = create_full_backup(backup_dir)
            print(f"Full backup created: {path}")
        
        elif command == "restore":
            if len(sys.argv) < 3:
                print("Error: JSON file path required")
                sys.exit(1)
            count = restore_from_json(sys.argv[2])
            print(f"Restored {count} items")
        
        elif command == "import":
            if len(sys.argv) < 3:
                print("Error: CSV file path required")
                sys.exit(1)
            success, errors = import_from_csv(sys.argv[2])
            print(f"Imported {success} items ({errors} errors)")
        
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)
    
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
