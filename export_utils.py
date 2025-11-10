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
        'ID', 'Item Name', 'Category', 'Status',
        'Purchase Price', 'Shipping Cost', 'Target Price', 'Final Sold Price',
        'Potential Profit', 'Actual Profit',
        'Product URL', 'Report Path', 'Image Count'
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
                'Purchase Price': f"{item['purchase_price']:.2f}",
                'Shipping Cost': f"{item['shipping_cost']:.2f}",
                'Target Price': f"{item['target_price']:.2f}",
                'Final Sold Price': f"{item['final_sold_price']:.2f}" if item.get('final_sold_price') else '',
                'Potential Profit': f"{potential_profit:.2f}",
                'Actual Profit': f"{actual_profit:.2f}" if item['status'] == 'Sold' else '',
                'Product URL': item.get('product_url', ''),
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
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "csv":
            output = sys.argv[2] if len(sys.argv) > 2 else None
            path = export_to_csv(output)
            print(f"✓ CSV exported to: {path}")
        
        elif command == "json":
            output = sys.argv[2] if len(sys.argv) > 2 else None
            path = export_to_json(output)
            print(f"✓ JSON exported to: {path}")
        
        elif command == "backup":
            backup_dir = sys.argv[2] if len(sys.argv) > 2 else None
            path = create_full_backup(backup_dir)
            print(f"✓ Full backup created: {path}")
        
        elif command == "restore":
            if len(sys.argv) < 3:
                print("Error: JSON file path required")
                sys.exit(1)
            count = restore_from_json(sys.argv[2])
            print(f"✓ Restored {count} items")
        
        else:
            print(f"Error: Unknown command '{command}'")
            sys.exit(1)
    
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)
