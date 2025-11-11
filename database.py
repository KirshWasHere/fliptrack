import sqlite3
import json
from typing import List, Dict, Optional
from contextlib import contextmanager

class Database:
    def __init__(self, db_path: str = "tracker.db"):
        self.db_path = db_path
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        with self.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS items (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    purchase_price REAL NOT NULL,
                    shipping_cost REAL NOT NULL,
                    target_price REAL NOT NULL,
                    product_url TEXT,
                    status TEXT DEFAULT 'Draft',
                    final_sold_price REAL,
                    report_path TEXT,
                    image_urls_cache TEXT,
                    category TEXT,
                    selected_images TEXT,
                    provider_id INTEGER,
                    listing_fee REAL DEFAULT 0,
                    processing_fee REAL DEFAULT 0,
                    storage_cost REAL DEFAULT 0,
                    other_expenses REAL DEFAULT 0,
                    sales_channel TEXT,
                    listing_url TEXT,
                    date_added TEXT,
                    date_listed TEXT,
                    date_sold TEXT
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS providers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    website TEXT,
                    notes TEXT,
                    tags TEXT
                )
            """)
    
    def add_item(self, item_data: Dict) -> int:
        try:
            from datetime import datetime
            with self.get_connection() as conn:
                date_added = datetime.now().isoformat()
                date_listed = datetime.now().isoformat() if item_data.get('status') == 'Listed' else None
                date_sold = datetime.now().isoformat() if item_data.get('status') == 'Sold' else None
                
                cursor = conn.execute("""
                    INSERT INTO items (
                        item_name, purchase_price, shipping_cost, target_price,
                        product_url, status, final_sold_price, category,
                        image_urls_cache, selected_images, provider_id,
                        listing_fee, processing_fee, storage_cost, other_expenses,
                        sales_channel, listing_url, date_added, date_listed, date_sold
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_data['item_name'],
                    item_data['purchase_price'],
                    item_data['shipping_cost'],
                    item_data['target_price'],
                    item_data.get('product_url', ''),
                    item_data.get('status', 'Draft'),
                    item_data.get('final_sold_price'),
                    item_data.get('category', ''),
                    json.dumps(item_data.get('image_urls_cache', [])),
                    json.dumps(item_data.get('selected_images', [])),
                    item_data.get('provider_id'),
                    item_data.get('listing_fee', 0),
                    item_data.get('processing_fee', 0),
                    item_data.get('storage_cost', 0),
                    item_data.get('other_expenses', 0),
                    item_data.get('sales_channel', ''),
                    item_data.get('listing_url', ''),
                    date_added,
                    date_listed,
                    date_sold
                ))
                return cursor.lastrowid
        except Exception as e:
            raise Exception(f"Failed to add item: {str(e)}")
    
    def update_item(self, item_id: int, item_data: Dict):
        try:
            from datetime import datetime
            with self.get_connection() as conn:
                # Get current item to check status changes
                current = self.get_item(item_id)
                date_listed = item_data.get('date_listed', current.get('date_listed'))
                date_sold = item_data.get('date_sold', current.get('date_sold'))
                
                # Update dates based on status changes
                if item_data.get('status') == 'Listed' and current.get('status') != 'Listed' and not date_listed:
                    date_listed = datetime.now().isoformat()
                if item_data.get('status') == 'Sold' and current.get('status') != 'Sold' and not date_sold:
                    date_sold = datetime.now().isoformat()
                
                conn.execute("""
                    UPDATE items SET
                        item_name = ?,
                        purchase_price = ?,
                        shipping_cost = ?,
                        target_price = ?,
                        product_url = ?,
                        status = ?,
                        final_sold_price = ?,
                        category = ?,
                        image_urls_cache = ?,
                        selected_images = ?,
                        provider_id = ?,
                        listing_fee = ?,
                        processing_fee = ?,
                        storage_cost = ?,
                        other_expenses = ?,
                        sales_channel = ?,
                        listing_url = ?,
                        date_listed = ?,
                        date_sold = ?
                    WHERE id = ?
                """, (
                    item_data['item_name'],
                    item_data['purchase_price'],
                    item_data['shipping_cost'],
                    item_data['target_price'],
                    item_data.get('product_url', ''),
                    item_data.get('status', 'Draft'),
                    item_data.get('final_sold_price'),
                    item_data.get('category', ''),
                    json.dumps(item_data.get('image_urls_cache', [])),
                    json.dumps(item_data.get('selected_images', [])),
                    item_data.get('provider_id'),
                    item_data.get('listing_fee', 0),
                    item_data.get('processing_fee', 0),
                    item_data.get('storage_cost', 0),
                    item_data.get('other_expenses', 0),
                    item_data.get('sales_channel', ''),
                    item_data.get('listing_url', ''),
                    date_listed,
                    date_sold,
                    item_id
                ))
        except Exception as e:
            raise Exception(f"Failed to update item: {str(e)}")
    
    def delete_item(self, item_id: int):
        try:
            with self.get_connection() as conn:
                conn.execute("DELETE FROM items WHERE id = ?", (item_id,))
        except Exception as e:
            raise Exception(f"Failed to delete item: {str(e)}")
    
    def get_item(self, item_id: int) -> Optional[Dict]:
        try:
            with self.get_connection() as conn:
                row = conn.execute("SELECT * FROM items WHERE id = ?", (item_id,)).fetchone()
                if row:
                    return self._row_to_dict(row)
                return None
        except Exception as e:
            raise Exception(f"Failed to get item: {str(e)}")
    
    def get_all_items(self, search_query: str = None, status_filter: str = None) -> List[Dict]:
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM items WHERE 1=1"
                params = []
                
                if search_query:
                    query += " AND item_name LIKE ?"
                    params.append(f"%{search_query}%")
                
                if status_filter and status_filter != "All":
                    query += " AND status = ?"
                    params.append(status_filter)
                
                query += " ORDER BY id DESC"
                
                rows = conn.execute(query, params).fetchall()
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Failed to get items: {str(e)}")
    
    def update_report_path(self, item_id: int, report_path: str):
        with self.get_connection() as conn:
            conn.execute("UPDATE items SET report_path = ? WHERE id = ?", (report_path, item_id))
    
    def _row_to_dict(self, row) -> Dict:
        data = dict(row)
        if data.get('image_urls_cache'):
            data['image_urls_cache'] = json.loads(data['image_urls_cache'])
        else:
            data['image_urls_cache'] = []
        if data.get('selected_images'):
            data['selected_images'] = json.loads(data['selected_images'])
        else:
            data['selected_images'] = []
        return data
    
    def get_summary_stats(self) -> Dict:
        with self.get_connection() as conn:
            items = self.get_all_items()
            total_items = len(items)
            
            # Calculate total expenses per item
            def get_total_expenses(item):
                return (
                    item['purchase_price'] + 
                    item['shipping_cost'] + 
                    item.get('listing_fee', 0) + 
                    item.get('processing_fee', 0) + 
                    item.get('storage_cost', 0) + 
                    item.get('other_expenses', 0)
                )
            
            # Potential profit (for unsold items)
            total_potential_profit = sum(
                (item['target_price'] - get_total_expenses(item))
                for item in items if item['status'] != 'Sold'
            )
            
            # Actual profit (for sold items)
            total_actual_profit = sum(
                (item['final_sold_price'] - get_total_expenses(item))
                for item in items if item['status'] == 'Sold' and item['final_sold_price']
            )
            
            # Inventory value (unsold items)
            inventory_value = sum(
                get_total_expenses(item)
                for item in items if item['status'] != 'Sold'
            )
            
            # Total invested
            total_invested = sum(get_total_expenses(item) for item in items)
            
            # ROI calculation
            total_revenue = sum(
                item['final_sold_price']
                for item in items if item['status'] == 'Sold' and item['final_sold_price']
            )
            roi = ((total_revenue - total_invested) / total_invested * 100) if total_invested > 0 else 0
            
            return {
                'total_items': total_items,
                'total_potential_profit': total_potential_profit,
                'total_actual_profit': total_actual_profit,
                'inventory_value': inventory_value,
                'total_invested': total_invested,
                'total_revenue': total_revenue,
                'roi': roi,
                'sold_count': len([i for i in items if i['status'] == 'Sold']),
                'listed_count': len([i for i in items if i['status'] == 'Listed']),
                'draft_count': len([i for i in items if i['status'] == 'Draft'])
            }
    
    # Provider methods
    def add_provider(self, provider_data: Dict) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO providers (name, contact_person, phone, email, website, notes, tags)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    provider_data['name'],
                    provider_data.get('contact_person', ''),
                    provider_data.get('phone', ''),
                    provider_data.get('email', ''),
                    provider_data.get('website', ''),
                    provider_data.get('notes', ''),
                    provider_data.get('tags', '')
                ))
                return cursor.lastrowid
        except Exception as e:
            raise Exception(f"Failed to add provider: {str(e)}")
    
    def update_provider(self, provider_id: int, provider_data: Dict):
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    UPDATE providers SET
                        name = ?,
                        contact_person = ?,
                        phone = ?,
                        email = ?,
                        website = ?,
                        notes = ?,
                        tags = ?
                    WHERE id = ?
                """, (
                    provider_data['name'],
                    provider_data.get('contact_person', ''),
                    provider_data.get('phone', ''),
                    provider_data.get('email', ''),
                    provider_data.get('website', ''),
                    provider_data.get('notes', ''),
                    provider_data.get('tags', ''),
                    provider_id
                ))
        except Exception as e:
            raise Exception(f"Failed to update provider: {str(e)}")
    
    def delete_provider(self, provider_id: int):
        try:
            with self.get_connection() as conn:
                # Set provider_id to NULL for items using this provider
                conn.execute("UPDATE items SET provider_id = NULL WHERE provider_id = ?", (provider_id,))
                # Delete provider
                conn.execute("DELETE FROM providers WHERE id = ?", (provider_id,))
        except Exception as e:
            raise Exception(f"Failed to delete provider: {str(e)}")
    
    def get_provider(self, provider_id: int) -> Optional[Dict]:
        try:
            with self.get_connection() as conn:
                row = conn.execute("SELECT * FROM providers WHERE id = ?", (provider_id,)).fetchone()
                if row:
                    return dict(row)
                return None
        except Exception as e:
            raise Exception(f"Failed to get provider: {str(e)}")
    
    def get_all_providers(self, search_query: str = None) -> List[Dict]:
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM providers WHERE 1=1"
                params = []
                
                if search_query:
                    query += " AND (name LIKE ? OR tags LIKE ?)"
                    params.extend([f"%{search_query}%", f"%{search_query}%"])
                
                query += " ORDER BY name ASC"
                
                rows = conn.execute(query, params).fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Failed to get providers: {str(e)}")
    
    def get_provider_items(self, provider_id: int) -> List[Dict]:
        """Get all items from a specific provider"""
        try:
            with self.get_connection() as conn:
                query = "SELECT * FROM items WHERE provider_id = ? ORDER BY id DESC"
                rows = conn.execute(query, (provider_id,)).fetchall()
                return [self._row_to_dict(row) for row in rows]
        except Exception as e:
            raise Exception(f"Failed to get provider items: {str(e)}")
    
    def get_days_listed(self, item: Dict) -> int:
        """Calculate days an item has been listed"""
        from datetime import datetime
        
        if item.get('date_listed'):
            try:
                date_listed = datetime.fromisoformat(item['date_listed'])
                if item['status'] == 'Sold' and item.get('date_sold'):
                    date_sold = datetime.fromisoformat(item['date_sold'])
                    return (date_sold - date_listed).days
                else:
                    return (datetime.now() - date_listed).days
            except:
                return 0
        return 0
    
    def get_provider_stats(self, provider_id: int) -> Dict:
        """Get statistics for a provider"""
        items = self.get_provider_items(provider_id)
        total_items = len(items)
        total_spent = sum(item['purchase_price'] + item['shipping_cost'] for item in items)
        total_potential_profit = sum(
            (item['target_price'] - item['purchase_price'] - item['shipping_cost'])
            for item in items
        )
        total_actual_profit = sum(
            (item['final_sold_price'] - item['purchase_price'] - item['shipping_cost'])
            for item in items if item['status'] == 'Sold' and item['final_sold_price']
        )
        sold_count = len([i for i in items if i['status'] == 'Sold'])
        
        return {
            'total_items': total_items,
            'total_spent': total_spent,
            'total_potential_profit': total_potential_profit,
            'total_actual_profit': total_actual_profit,
            'sold_count': sold_count,
            'avg_profit_per_item': total_actual_profit / sold_count if sold_count > 0 else 0
        }
