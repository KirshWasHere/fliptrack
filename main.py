from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import (
    Header, Footer, Button, DataTable, Static, Input, 
    Select, Label, RadioButton, RadioSet
)
from textual.screen import Screen, ModalScreen
from textual.binding import Binding
from rich.panel import Panel
from rich.table import Table as RichTable
from rich.text import Text
import os
from pathlib import Path
import shutil
import subprocess
import webbrowser
import time

from database import Database
from scraper import ImageScraper
from report_generator import ReportGenerator
from utils import validate_url, validate_price, validate_item_name, optimize_image
from export_utils import export_to_csv, create_full_backup



class ConfirmDialog(ModalScreen[bool]):
    """Confirmation dialog"""
    
    def __init__(self, message: str, title: str = "Confirm"):
        super().__init__()
        self.message = message
        self.title = title
    
    def compose(self) -> ComposeResult:
        yield Container(
            Static(f"[bold]{self.title}[/]", id="dialog-title"),
            Static(self.message, id="dialog-message"),
            Horizontal(
                Button("Yes", variant="error", id="yes-btn"),
                Button("No", variant="default", id="no-btn"),
                id="dialog-buttons"
            ),
            id="dialog"
        )
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "yes-btn":
            self.dismiss(True)
        else:
            self.dismiss(False)


class DashboardScreen(Screen):
    BINDINGS = [
        Binding("a", "add_item", "Add"),
        Binding("e", "edit_item", "Edit"),
        Binding("d", "delete_item", "Delete"),
        Binding("p", "providers", "Providers"),
        Binding("t", "analytics", "Analytics"),
        Binding("v", "view_report", "View Report"),
        Binding("ctrl+f", "focus_search", "Search"),
        Binding("q", "quit", "Quit"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Horizontal(
                Button("🌐 Web App", id="web-app-btn", variant="success"),
                Button("📊 Analytics", id="analytics-btn", variant="primary"),
                Button("💾 Export CSV", id="export-btn"),
                Button("🔄 Backup", id="backup-btn"),
                Button("📑 Master Index", id="master-btn"),
                Button("🗑️ Delete All", id="delete-all-btn", variant="error"),
                id="action-bar"
            ),
            Static(id="stats-panel"),
            Horizontal(
                Input(placeholder="Search items...", id="search-input"),
                Select(
                    [("All", "All"), ("Draft", "Draft"), ("Listed", "Listed"), ("Sold", "Sold")],
                    id="status-filter",
                    value="All"
                ),
                id="filter-bar"
            ),
            DataTable(id="items-table"),
            id="dashboard-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        self.refresh_dashboard()
    
    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "search-input":
            self.refresh_dashboard()
    
    def on_select_changed(self, event: Select.Changed):
        if event.select.id == "status-filter":
            self.refresh_dashboard()
    
    def action_focus_search(self):
        self.query_one("#search-input", Input).focus()
    
    def on_button_pressed(self, event: Button.Pressed):
        """Handle button clicks in action bar"""
        if event.button.id == "web-app-btn":
            self.action_launch_web_app()
        elif event.button.id == "analytics-btn":
            self.action_analytics()
        elif event.button.id == "export-btn":
            self.action_export_csv()
        elif event.button.id == "backup-btn":
            self.action_backup()
        elif event.button.id == "master-btn":
            self.action_master_index()
        elif event.button.id == "delete-all-btn":
            self.action_delete_all()
    
    def refresh_dashboard(self):
        try:
            db = Database()
            
            # Get filter values
            search_query = self.query_one("#search-input", Input).value
            status_filter = self.query_one("#status-filter", Select).value
            
            # Get filtered items
            items = db.get_all_items(search_query=search_query, status_filter=status_filter)
            stats = db.get_summary_stats()
            
            # Update stats panel with enhanced info
            stats_text = f"""Items: {stats['total_items']} (Draft: {stats['draft_count']}, Listed: {stats['listed_count']}, Sold: {stats['sold_count']}) | Showing: {len(items)}
Inventory Value: ${stats['inventory_value']:.2f} | Total Invested: ${stats['total_invested']:.2f}
Potential Profit: ${stats['total_potential_profit']:.2f} | Actual Profit: ${stats['total_actual_profit']:.2f}
ROI: {stats['roi']:.1f}%"""
            
            stats_panel = self.query_one("#stats-panel", Static)
            stats_panel.update(Panel(stats_text, title="Summary", border_style="cyan"))
            
            # Update items table
            table = self.query_one("#items-table", DataTable)
            table.clear(columns=True)
            table.add_columns("ID", "Item Name", "Status", "Purchase", "Target", "Potential Profit")
            
            for item in items:
                potential_profit = item['target_price'] - item['purchase_price'] - item['shipping_cost']
                table.add_row(
                    str(item['id']),
                    item['item_name'][:50],  # Truncate long names
                    item['status'],
                    f"${item['purchase_price']:.2f}",
                    f"${item['target_price']:.2f}",
                    f"${potential_profit:.2f}"
                )
            
            if items:
                table.cursor_type = "row"
        except Exception as e:
            self.app.notify(f"Error loading dashboard: {str(e)}", severity="error")
    
    def action_add_item(self):
        def check_refresh(result):
            self.refresh_dashboard()
        self.app.push_screen(ItemFormScreen(mode="add"), check_refresh)
    
    def action_edit_item(self):
        table = self.query_one("#items-table", DataTable)
        if table.row_count > 0:
            row_key = table.cursor_row
            if row_key is not None:
                item_id = int(table.get_row_at(row_key)[0])
                def check_refresh(result):
                    self.refresh_dashboard()
                self.app.push_screen(ItemFormScreen(mode="edit", item_id=item_id), check_refresh)
    
    def action_delete_item(self):
        table = self.query_one("#items-table", DataTable)
        if table.row_count > 0:
            row_key = table.cursor_row
            if row_key is not None:
                item_id = int(table.get_row_at(row_key)[0])
                item_name = table.get_row_at(row_key)[1]
                
                def handle_confirm(confirmed: bool):
                    if confirmed:
                        try:
                            db = Database()
                            
                            # Get item to delete images
                            item = db.get_item(item_id)
                            
                            # Delete from database
                            db.delete_item(item_id)
                            
                            # Delete images directory
                            if item:
                                item_dir = Path(f"./data/images/item_{item_id}")
                                if item_dir.exists():
                                    shutil.rmtree(item_dir)
                            
                            self.refresh_dashboard()
                            self.app.notify(f"Item {item_id} deleted successfully!")
                        except Exception as e:
                            self.app.notify(f"Error deleting item: {str(e)}", severity="error")
                
                self.app.push_screen(
                    ConfirmDialog(f"Delete '{item_name}'?\nThis cannot be undone.", "Confirm Delete"),
                    handle_confirm
                )
    
    def action_view_report(self):
        """View the HTML report for the selected item"""
        table = self.query_one("#items-table", DataTable)
        if table.row_count > 0:
            row_key = table.cursor_row
            if row_key is not None:
                item_id = int(table.get_row_at(row_key)[0])
                try:
                    db = Database()
                    item = db.get_item(item_id)
                    
                    if not item:
                        self.app.notify("Item not found", severity="error")
                        return
                    
                    # Generate report if it doesn't exist or is outdated
                    report_path = item.get('report_path')
                    if not report_path or not os.path.exists(report_path):
                        generator = ReportGenerator()
                        report_path = generator.generate_report(item)
                        db.update_report_path(item_id, report_path)
                    
                    # Open report
                    if os.name == 'nt':  # Windows
                        os.startfile(report_path)
                    elif os.name == 'posix':  # macOS/Linux
                        import subprocess
                        if os.uname().sysname == 'Darwin':  # macOS
                            subprocess.run(['open', report_path])
                        else:  # Linux
                            subprocess.run(['xdg-open', report_path])
                    self.app.notify(f"Opening report...")
                except Exception as e:
                    self.app.notify(f"Error: {str(e)}", severity="error")
    
    def action_master_index(self):
        try:
            db = Database()
            items = db.get_all_items()
            generator = ReportGenerator()
            
            # Generate missing reports first
            self.app.notify(f"Generating reports for {len(items)} items...")
            for item in items:
                if not item.get('report_path') or not os.path.exists(item.get('report_path', '')):
                    try:
                        report_path = generator.generate_report(item)
                        db.update_report_path(item['id'], report_path)
                    except Exception as e:
                        print(f"Failed to generate report for item {item['id']}: {e}")
            
            # Generate master index
            items = db.get_all_items()  # Refresh to get updated report paths
            index_path = generator.generate_master_index(items)
            
            # Automatically open the index
            try:
                if os.name == 'nt':  # Windows
                    os.startfile(index_path)
                elif os.name == 'posix':  # macOS/Linux
                    import subprocess
                    if os.uname().sysname == 'Darwin':  # macOS
                        subprocess.run(['open', index_path])
                    else:  # Linux
                        subprocess.run(['xdg-open', index_path])
                self.app.notify(f"Master index generated and opened!")
            except Exception as e:
                self.app.notify(f"Master index generated: {index_path}", severity="warning")
        except Exception as e:
            self.app.notify(f"Error generating master index: {str(e)}", severity="error")
    
    def action_generate_all_reports(self):
        """Generate reports for all items"""
        try:
            db = Database()
            items = db.get_all_items()
            
            if not items:
                self.app.notify("No items to generate reports for", severity="warning")
                return
            
            self.app.notify(f"Generating reports for {len(items)} items...")
            
            generator = ReportGenerator()
            success_count = 0
            error_count = 0
            
            for item in items:
                try:
                    report_path = generator.generate_report(item)
                    db.update_report_path(item['id'], report_path)
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    print(f"Failed to generate report for item {item['id']}: {e}")
            
            # Also generate master index
            try:
                index_path = generator.generate_master_index(items)
                self.app.notify(f"✓ Generated {success_count} reports + master index!")
                
                # Try to open the master index
                try:
                    if os.name == 'nt':
                        os.startfile(index_path)
                    elif os.name == 'posix':
                        import subprocess
                        if os.uname().sysname == 'Darwin':
                            subprocess.run(['open', index_path])
                        else:
                            subprocess.run(['xdg-open', index_path])
                except:
                    pass
            except Exception as e:
                self.app.notify(f"Generated {success_count} reports (master index failed)", severity="warning")
            
            if error_count > 0:
                self.app.notify(f"Warning: {error_count} reports failed", severity="warning")
            
            self.refresh_dashboard()
            
        except Exception as e:
            self.app.notify(f"Failed to generate reports: {str(e)}", severity="error")
    
    def action_export_csv(self):
        """Export all items to CSV"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"fliptrack_export_{timestamp}.csv"
            
            path = export_to_csv(output_path)
            self.app.notify(f"Exported to {path}")
            
            # Try to open the file location
            try:
                if os.name == 'nt':
                    os.startfile(os.path.dirname(os.path.abspath(path)))
            except:
                pass
        except Exception as e:
            self.app.notify(f"Export failed: {str(e)}", severity="error")
    
    def action_backup(self):
        """Create full backup"""
        try:
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_dir = f"backup_{timestamp}"
            
            path = create_full_backup(backup_dir)
            self.app.notify(f"Backup created: {path}")
            
            # Try to open the backup folder
            try:
                if os.name == 'nt':
                    os.startfile(path)
            except:
                pass
        except Exception as e:
            self.app.notify(f"Backup failed: {str(e)}", severity="error")
    
    def action_delete_all(self):
        """Delete all items from database"""
        db = Database()
        items = db.get_all_items()
        
        if not items:
            self.app.notify("No items to delete", severity="warning")
            return
        
        item_count = len(items)
        
        def handle_confirm(confirmed: bool):
            if confirmed:
                try:
                    db = Database()
                    items = db.get_all_items()
                    
                    deleted_count = 0
                    error_count = 0
                    
                    for item in items:
                        try:
                            item_id = item['id']
                            
                            # Delete from database
                            db.delete_item(item_id)
                            
                            # Delete images directory
                            item_dir = Path(f"./data/images/item_{item_id}")
                            if item_dir.exists():
                                shutil.rmtree(item_dir)
                            
                            deleted_count += 1
                        except Exception as e:
                            error_count += 1
                            print(f"Failed to delete item {item_id}: {e}")
                    
                    # Clear reports directory
                    try:
                        reports_dir = Path("./reports")
                        if reports_dir.exists():
                            for report_file in reports_dir.glob("*.html"):
                                report_file.unlink()
                    except Exception as e:
                        print(f"Failed to clear reports: {e}")
                    
                    self.refresh_dashboard()
                    
                    if error_count > 0:
                        self.app.notify(f"Deleted {deleted_count} items ({error_count} errors)", severity="warning")
                    else:
                        self.app.notify(f"✓ Deleted all {deleted_count} items")
                        
                except Exception as e:
                    self.app.notify(f"Error deleting items: {str(e)}", severity="error")
        
        self.app.push_screen(
            ConfirmDialog(
                f"Delete ALL {item_count} items?\n\nThis will delete:\n- All database records\n- All images\n- All reports\n\nThis CANNOT be undone!",
                "⚠️ DELETE ALL ITEMS"
            ),
            handle_confirm
        )
    
    def action_providers(self):
        """Open providers screen"""
        def check_refresh(result):
            self.refresh_dashboard()
        self.app.push_screen(ProvidersScreen(), check_refresh)
    
    def action_analytics(self):
        """Open analytics screen"""
        self.app.push_screen(AnalyticsScreen())
    
    def action_launch_web_app(self):
        """Launch the web application"""
        try:
            import subprocess
            import webbrowser
            import time
            
            self.app.notify("Starting web app...")
            
            # Start the web app in a subprocess
            if os.name == 'nt':  # Windows
                subprocess.Popen(['python', 'web_app.py'], 
                               creationflags=subprocess.CREATE_NEW_CONSOLE)
            else:  # macOS/Linux
                subprocess.Popen(['python3', 'web_app.py'])
            
            # Wait a moment for the server to start
            time.sleep(2)
            
            # Open browser
            webbrowser.open('http://127.0.0.1:5000')
            
            self.app.notify("Web app launched! Opening browser...")
        except Exception as e:
            self.app.notify(f"Failed to launch web app: {str(e)}", severity="error")
    
    def action_quit(self):
        self.app.exit()


class ItemFormScreen(Screen):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]
    
    def __init__(self, mode="add", item_id=None):
        super().__init__()
        self.mode = mode
        self.item_id = item_id
        self.scraped_images = []
        self.manual_images = []  # For manually added images
    
    def compose(self) -> ComposeResult:
        title = "Add New Item" if self.mode == "add" else f"Edit Item #{self.item_id}"
        
        yield Header()
        yield ScrollableContainer(
            Label(f"[bold cyan]{title}[/]"),
            Label("Item Name:"),
            Input(id="item_name", placeholder="Enter item name"),
            Label("Category:"),
            Select(
                [("General", "General"), ("Sneakers", "Sneakers"), ("Electronics", "Electronics"), ("Books", "Books")],
                id="category",
                value="General"
            ),
            Label("Provider (optional):"),
            Select(
                [("None", None)],
                id="provider",
                allow_blank=True
            ),
            Label("[bold]Additional Info:[/]"),
            Label("Tags (comma-separated):"),
            Input(id="tags", placeholder="e.g., vintage, rare, damaged"),
            Label("Condition:"),
            Select(
                [("", ""), ("New", "New"), ("Like New", "Like New"), ("Good", "Good"), 
                 ("Fair", "Fair"), ("Poor", "Poor")],
                id="condition",
                allow_blank=True
            ),
            Label("Storage Location:"),
            Input(id="storage_location", placeholder="e.g., Shelf A, Box 3"),
            Label("Notes:"),
            Input(id="notes", placeholder="Additional notes"),
            Horizontal(
                Button("Scrape Images", id="scrape-btn", variant="primary"),
                Button("Preview", id="preview-btn", variant="default", disabled=True),
                Button("Add Images", id="manual-btn", variant="default"),
                classes="button-row"
            ),
            Label("Purchase Price:"),
            Input(id="purchase_price", placeholder="0.00", type="number"),
            Label("Shipping Cost:"),
            Input(id="shipping_cost", placeholder="0.00", type="number"),
            Label("Target Selling Price:"),
            Input(id="target_price", placeholder="0.00", type="number"),
            Label("Product URL:"),
            Input(id="product_url", placeholder="https://..."),
            Label("[bold]Expenses:[/]"),
            Label("Listing Fee:"),
            Input(id="listing_fee", placeholder="0.00", type="number"),
            Label("Processing Fee (PayPal, Stripe, etc.):"),
            Input(id="processing_fee", placeholder="0.00", type="number"),
            Label("Storage Cost:"),
            Input(id="storage_cost", placeholder="0.00", type="number"),
            Label("Other Expenses:"),
            Input(id="other_expenses", placeholder="0.00", type="number"),
            Label("Status:"),
            RadioSet(
                RadioButton("Draft", id="status_draft", value=True),
                RadioButton("Listed", id="status_listed"),
                RadioButton("Sold", id="status_sold"),
                id="status"
            ),
            Label("Final Sold Price (if Sold):"),
            Input(id="final_sold_price", placeholder="0.00", type="number", disabled=True),
            Label("Sales Channel (if Sold):"),
            Select(
                [("None", ""), ("eBay", "eBay"), ("StockX", "StockX"), ("Grailed", "Grailed"), 
                 ("Local", "Local"), ("Facebook", "Facebook"), ("Mercari", "Mercari"), ("Other", "Other")],
                id="sales_channel",
                allow_blank=True,
                disabled=True
            ),
            Label("Listing URL (if Sold):"),
            Input(id="listing_url", placeholder="https://...", disabled=True),
            Static(id="profit-display"),
            Static(id="image-list"),
            Horizontal(
                Button("Save", id="save-btn", variant="success"),
                Button("Cancel", id="cancel-btn", variant="error"),
                classes="button-row"
            ),
            id="form-container"
        )
        yield Footer()
    
    def on_mount(self):
        self.load_providers()
        if self.mode == "edit" and self.item_id:
            self.load_item_data()
        self.update_profit_display()
    
    def load_providers(self):
        """Load providers into dropdown"""
        db = Database()
        providers = db.get_all_providers()
        provider_select = self.query_one("#provider", Select)
        
        # Build options list
        options = [("None", None)]
        for provider in providers:
            options.append((provider['name'], str(provider['id'])))
        
        provider_select.set_options(options)
    
    def load_item_data(self):
        db = Database()
        item = db.get_item(self.item_id)
        if item:
            self.query_one("#item_name", Input).value = item['item_name']
            self.query_one("#category", Select).value = item.get('category', 'General')
            self.query_one("#purchase_price", Input).value = str(item['purchase_price'])
            self.query_one("#shipping_cost", Input).value = str(item['shipping_cost'])
            self.query_one("#target_price", Input).value = str(item['target_price'])
            self.query_one("#product_url", Input).value = item.get('product_url', '')
            
            # Set provider
            if item.get('provider_id'):
                self.query_one("#provider", Select).value = str(item['provider_id'])
            
            # Set expenses
            self.query_one("#listing_fee", Input).value = str(item.get('listing_fee', 0))
            self.query_one("#processing_fee", Input).value = str(item.get('processing_fee', 0))
            self.query_one("#storage_cost", Input).value = str(item.get('storage_cost', 0))
            self.query_one("#other_expenses", Input).value = str(item.get('other_expenses', 0))
            
            if item.get('final_sold_price'):
                self.query_one("#final_sold_price", Input).value = str(item['final_sold_price'])
            
            # Set sales channel and listing URL
            if item.get('sales_channel'):
                self.query_one("#sales_channel", Select).value = item['sales_channel']
            if item.get('listing_url'):
                self.query_one("#listing_url", Input).value = item['listing_url']
            
            # Set notes/tags
            self.query_one("#tags", Input).value = item.get('tags', '')
            self.query_one("#notes", Input).value = item.get('notes', '')
            self.query_one("#storage_location", Input).value = item.get('storage_location', '')
            if item.get('condition'):
                self.query_one("#condition", Select).value = item['condition']
            
            # Set status
            status = item.get('status', 'Draft')
            if status == 'Draft':
                self.query_one("#status_draft", RadioButton).value = True
            elif status == 'Listed':
                self.query_one("#status_listed", RadioButton).value = True
            elif status == 'Sold':
                self.query_one("#status_sold", RadioButton).value = True
                self.query_one("#final_sold_price", Input).disabled = False
            
            # Load cached images
            if item.get('image_urls_cache'):
                self.scraped_images = item['image_urls_cache']
                self.update_image_list()
    
    def on_input_changed(self, event: Input.Changed):
        self.update_profit_display()
    
    def on_radio_set_changed(self, event: RadioSet.Changed):
        selected = event.pressed.id if event.pressed else None
        final_price_input = self.query_one("#final_sold_price", Input)
        sales_channel_select = self.query_one("#sales_channel", Select)
        listing_url_input = self.query_one("#listing_url", Input)
        
        if selected == "status_sold":
            final_price_input.disabled = False
            sales_channel_select.disabled = False
            listing_url_input.disabled = False
        else:
            final_price_input.disabled = True
            final_price_input.value = ""
            sales_channel_select.disabled = True
            listing_url_input.disabled = True
        
        self.update_profit_display()
    
    def update_profit_display(self):
        try:
            purchase = float(self.query_one("#purchase_price", Input).value or 0)
            shipping = float(self.query_one("#shipping_cost", Input).value or 0)
            listing_fee = float(self.query_one("#listing_fee", Input).value or 0)
            processing_fee = float(self.query_one("#processing_fee", Input).value or 0)
            storage_cost = float(self.query_one("#storage_cost", Input).value or 0)
            other_expenses = float(self.query_one("#other_expenses", Input).value or 0)
            target = float(self.query_one("#target_price", Input).value or 0)
            
            total_expenses = purchase + shipping + listing_fee + processing_fee + storage_cost + other_expenses
            potential_profit = target - total_expenses
            
            profit_text = f"Total Expenses: ${total_expenses:.2f}\n"
            profit_text += f"Potential: "
            if potential_profit >= 0:
                profit_text += f"[green]${potential_profit:.2f}[/]"
            else:
                profit_text += f"[red]${potential_profit:.2f}[/]"
            
            # Check if sold
            status_sold = self.query_one("#status_sold", RadioButton).value
            if status_sold:
                final_price = float(self.query_one("#final_sold_price", Input).value or 0)
                if final_price > 0:
                    actual_profit = final_price - total_expenses
                    profit_text += f"\nActual: "
                    if actual_profit >= 0:
                        profit_text += f"[green]${actual_profit:.2f}[/]"
                    else:
                        profit_text += f"[red]${actual_profit:.2f}[/]"
                    
                    # Show margin
                    margin = (actual_profit / final_price * 100) if final_price > 0 else 0
                    profit_text += f"\nMargin: {margin:.1f}%"
            
            self.query_one("#profit-display", Static).update(Panel(profit_text, title="Profit Analysis"))
        except:
            pass
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "scrape-btn":
            self.scrape_images()
        elif event.button.id == "preview-btn":
            self.preview_images()
        elif event.button.id == "manual-btn":
            self.add_manual_images()
        elif event.button.id == "save-btn":
            self.save_item()
        elif event.button.id == "cancel-btn":
            self.action_cancel()
    
    def scrape_images(self):
        item_name = self.query_one("#item_name", Input).value
        category = self.query_one("#category", Select).value
        
        if not item_name:
            self.app.notify("Please enter an item name first!", severity="warning")
            return
        
        self.app.notify("Scraping images... Please wait.")
        scraper = ImageScraper()
        self.scraped_images = scraper.scrape_images(item_name, category)
        
        if self.scraped_images:
            self.app.notify(f"Found {len(self.scraped_images)} images! First 3 will be used.")
            self.update_image_list()
            # Enable preview button
            self.query_one("#preview-btn", Button).disabled = False
        else:
            self.app.notify("No images found.", severity="warning")
    
    def add_manual_images(self):
        """Add images manually from file system"""
        self.app.notify("Opening file dialog... (Feature requires tkinter)")
        
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            file_paths = filedialog.askopenfilenames(
                title="Select Images",
                filetypes=[("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*")]
            )
            
            root.destroy()
            
            if file_paths:
                self.manual_images = list(file_paths)
                self.app.notify(f"Added {len(file_paths)} manual images!")
                
                # Update display
                image_text = "[bold]Manual Images:[/]\n\n"
                for i, path in enumerate(self.manual_images, 1):
                    filename = os.path.basename(path)
                    image_text += f"{i}. {filename}\n"
                image_text += f"\nThese will be used in report"
                self.query_one("#image-list", Static).update(Panel(image_text, title="Manual Images"))
        except ImportError:
            self.app.notify("tkinter not available. Place images in ./data/images/item_X/ manually", severity="warning")
        except Exception as e:
            self.app.notify(f"Error: {e}", severity="error")
    
    def preview_images(self):
        """Download and open first 3 images for preview"""
        if not self.scraped_images:
            self.app.notify("No images to preview!", severity="warning")
            return
        
        self.app.notify("Downloading images for preview...")
        
        import os
        import subprocess
        from pathlib import Path
        
        # Create temp preview directory
        preview_dir = Path("./temp_preview")
        preview_dir.mkdir(exist_ok=True)
        
        scraper = ImageScraper()
        downloaded = []
        
        # Download first 3 images
        for i, url in enumerate(self.scraped_images[:3], 1):
            preview_path = preview_dir / f"preview_{i}.jpg"
            if scraper.download_image(url, str(preview_path)):
                downloaded.append(str(preview_path))
        
        if downloaded:
            self.app.notify(f"Opening {len(downloaded)} images in your default viewer...")
            
            # Open images in default viewer
            for img_path in downloaded:
                try:
                    if os.name == 'nt':  # Windows
                        os.startfile(img_path)
                    elif os.name == 'posix':  # macOS/Linux
                        if os.uname().sysname == 'Darwin':  # macOS
                            subprocess.run(['open', img_path])
                        else:  # Linux
                            subprocess.run(['xdg-open', img_path])
                except Exception as e:
                    self.app.notify(f"Could not open image: {e}", severity="error")
        else:
            self.app.notify("Failed to download images for preview", severity="error")
    
    def update_image_list(self):
        if not self.scraped_images:
            return
        
        image_text = "[bold]Scraped Images:[/]\n\n"
        for i, url in enumerate(self.scraped_images[:3], 1):
            short_url = url[:60] + "..." if len(url) > 60 else url
            image_text += f"{i}. {short_url}\n"
        
        if len(self.scraped_images) > 3:
            image_text += f"\n+ {len(self.scraped_images) - 3} more found"
        
        image_text += "\n\nFirst 3 will be used"
        self.query_one("#image-list", Static).update(Panel(image_text, title="Images"))
    
    def save_item(self):
        try:
            # Validate item name
            item_name = self.query_one("#item_name", Input).value
            is_valid, error_msg = validate_item_name(item_name)
            if not is_valid:
                self.app.notify(error_msg, severity="error")
                self.query_one("#item_name", Input).focus()
                return
            
            # Validate prices
            purchase_str = self.query_one("#purchase_price", Input).value
            is_valid, purchase_price, error_msg = validate_price(purchase_str)
            if not is_valid:
                self.app.notify(f"Purchase price: {error_msg}", severity="error")
                self.query_one("#purchase_price", Input).focus()
                return
            
            shipping_str = self.query_one("#shipping_cost", Input).value
            is_valid, shipping_cost, error_msg = validate_price(shipping_str)
            if not is_valid:
                self.app.notify(f"Shipping cost: {error_msg}", severity="error")
                self.query_one("#shipping_cost", Input).focus()
                return
            
            target_str = self.query_one("#target_price", Input).value
            is_valid, target_price, error_msg = validate_price(target_str)
            if not is_valid:
                self.app.notify(f"Target price: {error_msg}", severity="error")
                self.query_one("#target_price", Input).focus()
                return
            
            # Validate URL
            product_url = self.query_one("#product_url", Input).value
            is_valid, error_msg = validate_url(product_url)
            if not is_valid:
                self.app.notify(error_msg, severity="error")
                self.query_one("#product_url", Input).focus()
                return
            
            category = self.query_one("#category", Select).value
            
            # Get provider
            provider_value = self.query_one("#provider", Select).value
            provider_id = int(provider_value) if provider_value and provider_value != "None" else None
            
            # Get status
            if self.query_one("#status_draft", RadioButton).value:
                status = "Draft"
            elif self.query_one("#status_listed", RadioButton).value:
                status = "Listed"
            else:
                status = "Sold"
            
            # Validate expenses
            listing_fee_str = self.query_one("#listing_fee", Input).value
            is_valid, listing_fee, error_msg = validate_price(listing_fee_str)
            if not is_valid:
                self.app.notify(f"Listing fee: {error_msg}", severity="error")
                return
            
            processing_fee_str = self.query_one("#processing_fee", Input).value
            is_valid, processing_fee, error_msg = validate_price(processing_fee_str)
            if not is_valid:
                self.app.notify(f"Processing fee: {error_msg}", severity="error")
                return
            
            storage_cost_str = self.query_one("#storage_cost", Input).value
            is_valid, storage_cost, error_msg = validate_price(storage_cost_str)
            if not is_valid:
                self.app.notify(f"Storage cost: {error_msg}", severity="error")
                return
            
            other_expenses_str = self.query_one("#other_expenses", Input).value
            is_valid, other_expenses, error_msg = validate_price(other_expenses_str)
            if not is_valid:
                self.app.notify(f"Other expenses: {error_msg}", severity="error")
                return
            
            final_sold_price = None
            sales_channel = ""
            listing_url = ""
            
            if status == "Sold":
                final_str = self.query_one("#final_sold_price", Input).value
                is_valid, final_sold_price, error_msg = validate_price(final_str)
                if not is_valid:
                    self.app.notify(f"Final sold price: {error_msg}", severity="error")
                    self.query_one("#final_sold_price", Input).focus()
                    return
                if final_sold_price == 0:
                    self.app.notify("Final sold price required for sold items", severity="error")
                    self.query_one("#final_sold_price", Input).focus()
                    return
                
                sales_channel = self.query_one("#sales_channel", Select).value or ""
                listing_url = self.query_one("#listing_url", Input).value.strip()
            
            # Get notes/tags
            tags = self.query_one("#tags", Input).value.strip()
            notes = self.query_one("#notes", Input).value.strip()
            condition = self.query_one("#condition", Select).value or ""
            storage_location = self.query_one("#storage_location", Input).value.strip()
            
            # Download and save images
            selected_images = []
            images_dir = Path("./data/images")
            
            # Create temp directory for now
            temp_id = self.item_id if self.item_id else "temp"
            item_dir = images_dir / f"item_{temp_id}"
            item_dir.mkdir(parents=True, exist_ok=True)
            
            # Use manual images if provided, otherwise scraped images
            if self.manual_images:
                # Copy manual images
                for i, img_path in enumerate(self.manual_images[:3], 1):
                    save_path = item_dir / f"image{i}.jpg"
                    try:
                        shutil.copy2(img_path, save_path)
                        # Optimize the image
                        optimize_image(str(save_path))
                        selected_images.append(str(save_path))
                    except Exception as e:
                        self.app.notify(f"Error copying image: {e}", severity="warning")
            elif self.scraped_images:
                # Download first 3 scraped images
                scraper = ImageScraper()
                for i, url in enumerate(self.scraped_images[:3], 1):
                    save_path = item_dir / f"image{i}.jpg"
                    if scraper.download_image(url, str(save_path)):
                        # Optimize the downloaded image
                        optimize_image(str(save_path))
                        selected_images.append(str(save_path))
            
            item_data = {
                'item_name': item_name,
                'category': category,
                'purchase_price': purchase_price,
                'shipping_cost': shipping_cost,
                'target_price': target_price,
                'product_url': product_url,
                'status': status,
                'final_sold_price': final_sold_price,
                'image_urls_cache': self.scraped_images,
                'selected_images': selected_images,
                'provider_id': provider_id,
                'listing_fee': listing_fee,
                'processing_fee': processing_fee,
                'storage_cost': storage_cost,
                'other_expenses': other_expenses,
                'sales_channel': sales_channel,
                'listing_url': listing_url,
                'tags': tags,
                'notes': notes,
                'condition': condition,
                'storage_location': storage_location
            }
            
            try:
                db = Database()
                if self.mode == "add":
                    item_id = db.add_item(item_data)
                    
                    # Rename temp directory to actual ID
                    if selected_images:
                        temp_dir = Path("./data/images/item_temp")
                        actual_dir = Path(f"./data/images/item_{item_id}")
                        if temp_dir.exists():
                            temp_dir.rename(actual_dir)
                            # Update paths in database
                            item_data['selected_images'] = [
                                str(actual_dir / f"image{i}.jpg") 
                                for i in range(1, len(selected_images) + 1)
                            ]
                            db.update_item(item_id, item_data)
                    
                    # Auto-generate report
                    try:
                        item = db.get_item(item_id)
                        generator = ReportGenerator()
                        report_path = generator.generate_report(item)
                        db.update_report_path(item_id, report_path)
                    except Exception as e:
                        print(f"Failed to generate report: {e}")
                    
                    self.app.notify(f"Item added! Press 'v' to view report.")
                else:
                    db.update_item(self.item_id, item_data)
                    
                    # Auto-regenerate report
                    try:
                        item = db.get_item(self.item_id)
                        generator = ReportGenerator()
                        report_path = generator.generate_report(item)
                        db.update_report_path(self.item_id, report_path)
                    except Exception as e:
                        print(f"Failed to generate report: {e}")
                    
                    self.app.notify(f"Item updated! Press 'v' to view report.")
                
                self.dismiss(True)
            except Exception as db_error:
                # Clean up images if database save failed
                if self.mode == "add" and item_dir.exists():
                    shutil.rmtree(item_dir)
                raise db_error
        
        except Exception as e:
            self.app.notify(f"Error saving item: {str(e)}", severity="error")
    
    def action_cancel(self):
        self.dismiss(False)
    
    def action_save(self):
        self.save_item()


class ProvidersScreen(Screen):
    BINDINGS = [
        Binding("a", "add_provider", "Add Provider"),
        Binding("e", "edit_provider", "Edit Provider"),
        Binding("d", "delete_provider", "Delete Provider"),
        Binding("v", "view_items", "View Items"),
        Binding("ctrl+d", "delete_all_providers", "Delete All Providers"),
        Binding("escape", "back", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(id="provider-stats-panel"),
            Input(placeholder="Search providers...", id="provider-search"),
            DataTable(id="providers-table"),
            id="providers-container"
        )
        yield Footer()
    
    def on_mount(self) -> None:
        self.refresh_providers()
    
    def on_input_changed(self, event: Input.Changed):
        if event.input.id == "provider-search":
            self.refresh_providers()
    
    def refresh_providers(self):
        try:
            db = Database()
            search_query = self.query_one("#provider-search", Input).value
            providers = db.get_all_providers(search_query=search_query)
            
            # Update stats
            stats_text = f"Total Providers: {len(providers)}"
            stats_panel = self.query_one("#provider-stats-panel", Static)
            stats_panel.update(Panel(stats_text, title="Providers", border_style="cyan"))
            
            # Update table
            table = self.query_one("#providers-table", DataTable)
            table.clear(columns=True)
            table.add_columns("ID", "Name", "Contact", "Phone", "Email", "Items")
            
            for provider in providers:
                items = db.get_provider_items(provider['id'])
                table.add_row(
                    str(provider['id']),
                    provider['name'][:30],
                    provider.get('contact_person', '')[:20],
                    provider.get('phone', '')[:15],
                    provider.get('email', '')[:25],
                    str(len(items))
                )
            
            if providers:
                table.cursor_type = "row"
        except Exception as e:
            self.app.notify(f"Error loading providers: {str(e)}", severity="error")
    
    def action_add_provider(self):
        def check_refresh(result):
            self.refresh_providers()
        self.app.push_screen(ProviderFormScreen(mode="add"), check_refresh)
    
    def action_edit_provider(self):
        table = self.query_one("#providers-table", DataTable)
        if table.row_count > 0:
            row_key = table.cursor_row
            if row_key is not None:
                provider_id = int(table.get_row_at(row_key)[0])
                def check_refresh(result):
                    self.refresh_providers()
                self.app.push_screen(ProviderFormScreen(mode="edit", provider_id=provider_id), check_refresh)
    
    def action_delete_provider(self):
        table = self.query_one("#providers-table", DataTable)
        if table.row_count > 0:
            row_key = table.cursor_row
            if row_key is not None:
                provider_id = int(table.get_row_at(row_key)[0])
                provider_name = table.get_row_at(row_key)[1]
                
                def handle_confirm(confirmed: bool):
                    if confirmed:
                        try:
                            db = Database()
                            db.delete_provider(provider_id)
                            self.refresh_providers()
                            self.app.notify(f"Provider deleted successfully!")
                        except Exception as e:
                            self.app.notify(f"Error deleting provider: {str(e)}", severity="error")
                
                self.app.push_screen(
                    ConfirmDialog(f"Delete provider '{provider_name}'?\nItems will not be deleted.", "Confirm Delete"),
                    handle_confirm
                )
    
    def action_view_items(self):
        """View items from selected provider"""
        table = self.query_one("#providers-table", DataTable)
        if table.row_count > 0:
            row_key = table.cursor_row
            if row_key is not None:
                provider_id = int(table.get_row_at(row_key)[0])
                provider_name = table.get_row_at(row_key)[1]
                self.app.push_screen(ProviderItemsScreen(provider_id, provider_name))
    
    def action_delete_all_providers(self):
        """Delete all providers"""
        db = Database()
        providers = db.get_all_providers()
        
        if not providers:
            self.app.notify("No providers to delete", severity="warning")
            return
        
        provider_count = len(providers)
        
        def handle_confirm(confirmed: bool):
            if confirmed:
                try:
                    db = Database()
                    providers = db.get_all_providers()
                    
                    deleted_count = 0
                    error_count = 0
                    
                    for provider in providers:
                        try:
                            db.delete_provider(provider['id'])
                            deleted_count += 1
                        except Exception as e:
                            error_count += 1
                            print(f"Failed to delete provider {provider['id']}: {e}")
                    
                    self.refresh_providers()
                    
                    if error_count > 0:
                        self.app.notify(f"Deleted {deleted_count} providers ({error_count} errors)", severity="warning")
                    else:
                        self.app.notify(f"✓ Deleted all {deleted_count} providers")
                        
                except Exception as e:
                    self.app.notify(f"Error deleting providers: {str(e)}", severity="error")
        
        self.app.push_screen(
            ConfirmDialog(
                f"Delete ALL {provider_count} providers?\n\nItems will NOT be deleted.\nProvider links will be removed from items.\n\nThis CANNOT be undone!",
                "⚠️ DELETE ALL PROVIDERS"
            ),
            handle_confirm
        )
    
    def action_back(self):
        self.dismiss(True)


class ProviderFormScreen(Screen):
    BINDINGS = [
        Binding("escape", "cancel", "Cancel"),
        Binding("ctrl+s", "save", "Save"),
    ]
    
    def __init__(self, mode="add", provider_id=None):
        super().__init__()
        self.mode = mode
        self.provider_id = provider_id
    
    def compose(self) -> ComposeResult:
        title = "Add New Provider" if self.mode == "add" else f"Edit Provider #{self.provider_id}"
        
        yield Header()
        yield ScrollableContainer(
            Label(f"[bold cyan]{title}[/]"),
            Label("Provider Name:"),
            Input(id="provider_name", placeholder="Enter provider name"),
            Label("Contact Person:"),
            Input(id="contact_person", placeholder="Contact name (optional)"),
            Label("Phone:"),
            Input(id="phone", placeholder="Phone number (optional)"),
            Label("Email:"),
            Input(id="email", placeholder="Email address (optional)"),
            Label("Website:"),
            Input(id="website", placeholder="https://... (optional)"),
            Label("Tags:"),
            Input(id="tags", placeholder="e.g., wholesale, liquidation (optional)"),
            Label("Notes:"),
            Input(id="notes", placeholder="Additional notes (optional)"),
            Horizontal(
                Button("Save", id="save-btn", variant="success"),
                Button("Cancel", id="cancel-btn", variant="error"),
                classes="button-row"
            ),
            id="provider-form-container"
        )
        yield Footer()
    
    def on_mount(self):
        if self.mode == "edit" and self.provider_id:
            self.load_provider_data()
    
    def load_provider_data(self):
        db = Database()
        provider = db.get_provider(self.provider_id)
        if provider:
            self.query_one("#provider_name", Input).value = provider['name']
            self.query_one("#contact_person", Input).value = provider.get('contact_person', '')
            self.query_one("#phone", Input).value = provider.get('phone', '')
            self.query_one("#email", Input).value = provider.get('email', '')
            self.query_one("#website", Input).value = provider.get('website', '')
            self.query_one("#tags", Input).value = provider.get('tags', '')
            self.query_one("#notes", Input).value = provider.get('notes', '')
    
    def on_button_pressed(self, event: Button.Pressed):
        if event.button.id == "save-btn":
            self.save_provider()
        elif event.button.id == "cancel-btn":
            self.action_cancel()
    
    def save_provider(self):
        try:
            provider_name = self.query_one("#provider_name", Input).value
            
            if not provider_name or provider_name.strip() == "":
                self.app.notify("Provider name is required!", severity="error")
                self.query_one("#provider_name", Input).focus()
                return
            
            provider_data = {
                'name': provider_name.strip(),
                'contact_person': self.query_one("#contact_person", Input).value.strip(),
                'phone': self.query_one("#phone", Input).value.strip(),
                'email': self.query_one("#email", Input).value.strip(),
                'website': self.query_one("#website", Input).value.strip(),
                'tags': self.query_one("#tags", Input).value.strip(),
                'notes': self.query_one("#notes", Input).value.strip()
            }
            
            db = Database()
            if self.mode == "add":
                provider_id = db.add_provider(provider_data)
                self.app.notify(f"Provider added successfully! ID: {provider_id}")
            else:
                db.update_provider(self.provider_id, provider_data)
                self.app.notify(f"Provider updated successfully!")
            
            self.dismiss(True)
        except Exception as e:
            self.app.notify(f"Error saving provider: {str(e)}", severity="error")
    
    def action_cancel(self):
        self.dismiss(False)
    
    def action_save(self):
        self.save_provider()


class ProviderItemsScreen(Screen):
    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]
    
    def __init__(self, provider_id: int, provider_name: str):
        super().__init__()
        self.provider_id = provider_id
        self.provider_name = provider_name
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static(id="provider-items-stats"),
            DataTable(id="provider-items-table"),
            id="provider-items-container"
        )
        yield Footer()
    
    def on_mount(self):
        self.refresh_items()
    
    def refresh_items(self):
        try:
            db = Database()
            items = db.get_provider_items(self.provider_id)
            stats = db.get_provider_stats(self.provider_id)
            
            # Update stats
            stats_text = f"""Provider: {self.provider_name}
Total Items: {stats['total_items']} | Sold: {stats['sold_count']}
Total Spent: ${stats['total_spent']:.2f}
Potential Profit: ${stats['total_potential_profit']:.2f}
Actual Profit: ${stats['total_actual_profit']:.2f}"""
            
            stats_panel = self.query_one("#provider-items-stats", Static)
            stats_panel.update(Panel(stats_text, title="Provider Stats", border_style="cyan"))
            
            # Update table
            table = self.query_one("#provider-items-table", DataTable)
            table.clear(columns=True)
            table.add_columns("ID", "Item Name", "Status", "Purchase", "Target", "Profit")
            
            for item in items:
                potential_profit = item['target_price'] - item['purchase_price'] - item['shipping_cost']
                table.add_row(
                    str(item['id']),
                    item['item_name'][:40],
                    item['status'],
                    f"${item['purchase_price']:.2f}",
                    f"${item['target_price']:.2f}",
                    f"${potential_profit:.2f}"
                )
            
            if items:
                table.cursor_type = "row"
        except Exception as e:
            self.app.notify(f"Error loading items: {str(e)}", severity="error")
    
    def action_back(self):
        self.dismiss()


class AnalyticsScreen(Screen):
    BINDINGS = [
        Binding("escape", "back", "Back"),
    ]
    
    def compose(self) -> ComposeResult:
        yield Header()
        yield ScrollableContainer(
            Static(id="analytics-summary"),
            Static(id="tax-report"),
            Static(id="channel-breakdown"),
            Static(id="provider-breakdown"),
            id="analytics-container"
        )
        yield Footer()
    
    def on_mount(self):
        self.refresh_analytics()
    
    def refresh_analytics(self):
        try:
            db = Database()
            items = db.get_all_items()
            stats = db.get_summary_stats()
            
            # Summary
            summary_text = f"""Total Items: {stats['total_items']}
Inventory Value: ${stats['inventory_value']:.2f}
Total Invested: ${stats['total_invested']:.2f}
Total Revenue: ${stats['total_revenue']:.2f}
Total Profit: ${stats['total_actual_profit']:.2f}
ROI: {stats['roi']:.1f}%"""
            
            self.query_one("#analytics-summary", Static).update(
                Panel(summary_text, title="📊 Summary", border_style="cyan")
            )
            
            # Tax Report
            from datetime import datetime
            current_year = datetime.now().year
            
            # Calculate quarterly
            quarters = {1: [], 2: [], 3: [], 4: []}
            for item in items:
                if item['status'] == 'Sold' and item.get('date_sold'):
                    try:
                        date_sold = datetime.fromisoformat(item['date_sold'])
                        if date_sold.year == current_year:
                            quarter = (date_sold.month - 1) // 3 + 1
                            total_expenses = (
                                item['purchase_price'] + item['shipping_cost'] +
                                item.get('listing_fee', 0) + item.get('processing_fee', 0) +
                                item.get('storage_cost', 0) + item.get('other_expenses', 0)
                            )
                            profit = item['final_sold_price'] - total_expenses
                            quarters[quarter].append(profit)
                    except:
                        pass
            
            tax_text = f"Year: {current_year}\n\n"
            for q in range(1, 5):
                q_profit = sum(quarters[q])
                tax_text += f"Q{q}: ${q_profit:.2f} ({len(quarters[q])} items)\n"
            tax_text += f"\nAnnual Profit: ${stats['total_actual_profit']:.2f}"
            
            self.query_one("#tax-report", Static).update(
                Panel(tax_text, title="💰 Tax Report", border_style="green")
            )
            
            # Sales Channel Breakdown
            channels = {}
            for item in items:
                if item['status'] == 'Sold' and item.get('sales_channel'):
                    channel = item['sales_channel']
                    if channel not in channels:
                        channels[channel] = {'count': 0, 'revenue': 0, 'profit': 0}
                    
                    channels[channel]['count'] += 1
                    channels[channel]['revenue'] += item['final_sold_price']
                    
                    total_expenses = (
                        item['purchase_price'] + item['shipping_cost'] +
                        item.get('listing_fee', 0) + item.get('processing_fee', 0) +
                        item.get('storage_cost', 0) + item.get('other_expenses', 0)
                    )
                    channels[channel]['profit'] += item['final_sold_price'] - total_expenses
            
            channel_text = ""
            for channel, data in sorted(channels.items(), key=lambda x: x[1]['profit'], reverse=True):
                channel_text += f"{channel}: {data['count']} items | ${data['revenue']:.2f} revenue | ${data['profit']:.2f} profit\n"
            
            if not channel_text:
                channel_text = "No sales data yet"
            
            self.query_one("#channel-breakdown", Static).update(
                Panel(channel_text, title="📱 Sales Channels", border_style="blue")
            )
            
            # Provider Breakdown
            providers = db.get_all_providers()
            provider_text = ""
            
            for provider in providers[:10]:  # Top 10
                provider_stats = db.get_provider_stats(provider['id'])
                provider_text += f"{provider['name']}: {provider_stats['total_items']} items | ${provider_stats['total_actual_profit']:.2f} profit\n"
            
            if not provider_text:
                provider_text = "No providers yet"
            
            self.query_one("#provider-breakdown", Static).update(
                Panel(provider_text, title="🏪 Top Providers", border_style="magenta")
            )
            
        except Exception as e:
            self.app.notify(f"Error loading analytics: {str(e)}", severity="error")
    
    def action_back(self):
        self.dismiss()


class ResellingTrackerApp(App):
    CSS = """
    Screen {
        background: $surface;
    }
    
    #dashboard-container {
        height: 100%;
        padding: 1;
    }
    
    #action-bar {
        height: auto;
        padding: 1;
        background: $surface;
        border-bottom: solid $primary;
    }
    
    #action-bar Button {
        margin: 0 1;
        min-width: 12;
    }
    
    #stats-panel {
        height: auto;
        margin-bottom: 1;
    }
    
    #filter-bar {
        height: auto;
        margin-bottom: 1;
        padding: 0 1;
    }
    
    #search-input {
        width: 3fr;
        margin-right: 1;
    }
    
    #status-filter {
        width: 1fr;
    }
    
    #items-table {
        height: 1fr;
        border: solid $primary;
    }
    
    #form-container {
        width: 100%;
        height: 100%;
        padding: 2;
    }
    
    .button-row {
        height: auto;
        width: 100%;
        margin: 1 0;
        padding: 1;
    }
    
    Label {
        margin-top: 1;
        color: $text;
    }
    
    Input {
        margin-bottom: 1;
    }
    
    Button {
        margin: 0 1;
        min-width: 16;
        width: 1fr;
    }
    
    #profit-display {
        margin: 2 0;
    }
    
    #image-list {
        margin-top: 2;
        min-height: 10;
    }
    
    RadioSet {
        height: auto;
        margin: 1 0;
    }
    
    /* Confirmation Dialog */
    #dialog {
        width: 50;
        height: auto;
        background: $surface;
        border: thick $primary;
        padding: 2;
    }
    
    #dialog-title {
        text-align: center;
        margin-bottom: 1;
        color: $primary;
    }
    
    #dialog-message {
        text-align: center;
        margin-bottom: 2;
        padding: 1;
    }
    
    #dialog-buttons {
        height: auto;
        align: center middle;
    }
    
    #dialog-buttons Button {
        min-width: 10;
    }
    
    /* Providers Screen */
    #providers-container {
        height: 100%;
        padding: 1;
    }
    
    #provider-stats-panel {
        height: auto;
        margin-bottom: 1;
    }
    
    #provider-search {
        margin-bottom: 1;
    }
    
    #providers-table {
        height: 1fr;
        border: solid $primary;
    }
    
    #provider-form-container {
        width: 100%;
        height: 100%;
        padding: 2;
    }
    
    #provider-items-container {
        height: 100%;
        padding: 1;
    }
    
    #provider-items-stats {
        height: auto;
        margin-bottom: 1;
    }
    
    #provider-items-table {
        height: 1fr;
        border: solid $primary;
    }
    
    /* Analytics Screen */
    #analytics-container {
        width: 100%;
        height: 100%;
        padding: 2;
    }
    
    #analytics-summary, #tax-report, #channel-breakdown, #provider-breakdown {
        margin-bottom: 2;
    }
    """
    
    TITLE = "Reselling Profit Tracker"
    
    def on_mount(self):
        self.push_screen(DashboardScreen())


if __name__ == "__main__":
    app = ResellingTrackerApp()
    app.run()
