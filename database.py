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
                    selected_images TEXT
                )
            """)
    
    def add_item(self, item_data: Dict) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("""
                    INSERT INTO items (
                        item_name, purchase_price, shipping_cost, target_price,
                        product_url, status, final_sold_price, category,
                        image_urls_cache, selected_images
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                    json.dumps(item_data.get('selected_images', []))
                ))
                return cursor.lastrowid
        except Exception as e:
            raise Exception(f"Failed to add item: {str(e)}")
    
    def update_item(self, item_id: int, item_data: Dict):
        try:
            with self.get_connection() as conn:
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
                        selected_images = ?
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
            total_potential_profit = sum(
                (item['target_price'] - item['purchase_price'] - item['shipping_cost'])
                for item in items
            )
            total_actual_profit = sum(
                (item['final_sold_price'] - item['purchase_price'] - item['shipping_cost'])
                for item in items if item['status'] == 'Sold' and item['final_sold_price']
            )
            return {
                'total_items': total_items,
                'total_potential_profit': total_potential_profit,
                'total_actual_profit': total_actual_profit
            }
