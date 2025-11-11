"""
FlipTrack Web Dashboard
Run with: python web_app.py
Access at: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, send_file, flash
from werkzeug.utils import secure_filename
from database import Database
from report_generator import ReportGenerator
from utils import optimize_image
import os
from datetime import datetime
from pathlib import Path
import shutil

app = Flask(__name__)
app.config['SECRET_KEY'] = 'fliptrack-secret-key-change-in-production'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = 'data/images'

# Initialize database
db = Database()

# Ensure upload folder exists
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)


@app.route('/')
def index():
    """Dashboard home"""
    stats = db.get_summary_stats()
    items = db.get_all_items()
    recent_items = items[:10]  # Last 10 items
    
    return render_template('dashboard.html', 
                         stats=stats, 
                         recent_items=recent_items)


@app.route('/items')
def items_list():
    """All items list"""
    search = request.args.get('search', '')
    status = request.args.get('status', 'All')
    
    items = db.get_all_items(search_query=search, status_filter=status)
    
    return render_template('items.html', 
                         items=items, 
                         search=search, 
                         status=status)


@app.route('/item/<int:item_id>')
def item_detail(item_id):
    """Item detail view"""
    item = db.get_item(item_id)
    if not item:
        return "Item not found", 404
    
    # Get provider if exists
    provider = None
    if item.get('provider_id'):
        provider = db.get_provider(item['provider_id'])
    
    return render_template('item_detail.html', 
                         item=item, 
                         provider=provider)


@app.route('/item/add', methods=['GET', 'POST'])
def add_item():
    """Add new item"""
    if request.method == 'POST':
        try:
            # Get form data
            item_data = {
                'item_name': request.form.get('item_name'),
                'category': request.form.get('category', ''),
                'purchase_price': float(request.form.get('purchase_price', 0)),
                'shipping_cost': float(request.form.get('shipping_cost', 0)),
                'target_price': float(request.form.get('target_price', 0)),
                'product_url': request.form.get('product_url', ''),
                'status': request.form.get('status', 'Draft'),
                'final_sold_price': float(request.form.get('final_sold_price')) if request.form.get('final_sold_price') else None,
                'listing_fee': float(request.form.get('listing_fee', 0)),
                'processing_fee': float(request.form.get('processing_fee', 0)),
                'storage_cost': float(request.form.get('storage_cost', 0)),
                'other_expenses': float(request.form.get('other_expenses', 0)),
                'sales_channel': request.form.get('sales_channel', ''),
                'listing_url': request.form.get('listing_url', ''),
                'provider_id': int(request.form.get('provider_id')) if request.form.get('provider_id') else None,
                'tags': request.form.get('tags', ''),
                'notes': request.form.get('notes', ''),
                'condition': request.form.get('condition', ''),
                'storage_location': request.form.get('storage_location', ''),
                'image_urls_cache': [],
                'selected_images': []
            }
            
            # Add item first to get ID
            item_id = db.add_item(item_data)
            
            # Handle image uploads
            if 'images' in request.files:
                files = request.files.getlist('images')
                item_dir = Path(app.config['UPLOAD_FOLDER']) / f'item_{item_id}'
                item_dir.mkdir(exist_ok=True)
                
                selected_images = []
                for i, file in enumerate(files):
                    if file and file.filename:
                        filename = secure_filename(file.filename)
                        filepath = item_dir / f'image_{i+1}_{filename}'
                        file.save(filepath)
                        
                        # Optimize image
                        try:
                            optimize_image(str(filepath), str(filepath))
                        except:
                            pass
                        
                        # Store relative path
                        selected_images.append(str(filepath.relative_to('.')))
                
                # Update item with images
                if selected_images:
                    item_data['selected_images'] = selected_images
                    db.update_item(item_id, item_data)
            
            # Generate report
            item = db.get_item(item_id)
            generator = ReportGenerator()
            report_path = generator.generate_report(item)
            db.update_report_path(item_id, report_path)
            
            return redirect(url_for('item_detail', item_id=item_id))
        
        except Exception as e:
            return f"Error: {str(e)}", 400
    
    # GET request - show form
    providers = db.get_all_providers()
    return render_template('add_item.html', providers=providers)


@app.route('/providers')
def providers_list():
    """Providers list"""
    providers = db.get_all_providers()
    
    # Get stats for each provider
    provider_stats = []
    for provider in providers:
        stats = db.get_provider_stats(provider['id'])
        provider_stats.append({
            'provider': provider,
            'stats': stats
        })
    
    return render_template('providers.html', provider_stats=provider_stats)


@app.route('/item/<int:item_id>/edit', methods=['GET', 'POST'])
def edit_item(item_id):
    """Edit item"""
    item = db.get_item(item_id)
    if not item:
        return "Item not found", 404
    
    if request.method == 'POST':
        try:
            # Get form data
            item_data = {
                'item_name': request.form.get('item_name'),
                'category': request.form.get('category', ''),
                'purchase_price': float(request.form.get('purchase_price', 0)),
                'shipping_cost': float(request.form.get('shipping_cost', 0)),
                'target_price': float(request.form.get('target_price', 0)),
                'product_url': request.form.get('product_url', ''),
                'status': request.form.get('status', 'Draft'),
                'final_sold_price': float(request.form.get('final_sold_price')) if request.form.get('final_sold_price') else None,
                'listing_fee': float(request.form.get('listing_fee', 0)),
                'processing_fee': float(request.form.get('processing_fee', 0)),
                'storage_cost': float(request.form.get('storage_cost', 0)),
                'other_expenses': float(request.form.get('other_expenses', 0)),
                'sales_channel': request.form.get('sales_channel', ''),
                'listing_url': request.form.get('listing_url', ''),
                'provider_id': int(request.form.get('provider_id')) if request.form.get('provider_id') else None,
                'tags': request.form.get('tags', ''),
                'notes': request.form.get('notes', ''),
                'condition': request.form.get('condition', ''),
                'storage_location': request.form.get('storage_location', ''),
                'image_urls_cache': item.get('image_urls_cache', []),
                'selected_images': item.get('selected_images', [])
            }
            
            # Update item
            db.update_item(item_id, item_data)
            
            # Regenerate report
            item = db.get_item(item_id)
            generator = ReportGenerator()
            report_path = generator.generate_report(item)
            db.update_report_path(item_id, report_path)
            
            return redirect(url_for('item_detail', item_id=item_id))
        
        except Exception as e:
            return f"Error: {str(e)}", 400
    
    # GET request - show form
    providers = db.get_all_providers()
    return render_template('edit_item.html', item=item, providers=providers)


@app.route('/item/<int:item_id>/delete', methods=['POST'])
def delete_item(item_id):
    """Delete item"""
    try:
        item = db.get_item(item_id)
        if not item:
            return jsonify({'error': 'Item not found'}), 404
        
        # Delete from database
        db.delete_item(item_id)
        
        # Delete images directory
        item_dir = Path(app.config['UPLOAD_FOLDER']) / f'item_{item_id}'
        if item_dir.exists():
            shutil.rmtree(item_dir)
        
        # Delete report
        if item.get('report_path') and os.path.exists(item['report_path']):
            os.remove(item['report_path'])
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/analytics')
def analytics():
    """Analytics dashboard"""
    stats = db.get_summary_stats()
    items = db.get_all_items()
    
    # Sales channels
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
    
    return render_template('analytics.html', 
                         stats=stats, 
                         channels=channels)


@app.route('/export/csv')
def export_csv():
    """Export items to CSV"""
    try:
        from export_utils import export_to_csv
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"fliptrack_export_{timestamp}.csv"
        path = export_to_csv(output_path)
        return send_file(path, as_attachment=True)
    except Exception as e:
        return f"Export failed: {str(e)}", 500


@app.route('/export/tax-report')
def tax_report():
    """Generate tax report"""
    try:
        items = db.get_all_items(status_filter='Sold')
        stats = db.get_summary_stats()
        
        # Calculate tax info
        total_revenue = sum(item['final_sold_price'] for item in items if item.get('final_sold_price'))
        total_expenses = sum(
            item['purchase_price'] + item['shipping_cost'] +
            item.get('listing_fee', 0) + item.get('processing_fee', 0) +
            item.get('storage_cost', 0) + item.get('other_expenses', 0)
            for item in items
        )
        
        return render_template('tax_report.html', 
                             items=items, 
                             total_revenue=total_revenue,
                             total_expenses=total_expenses,
                             net_profit=total_revenue - total_expenses)
    except Exception as e:
        return f"Error: {str(e)}", 500


@app.route('/reports/master')
def master_report():
    """Generate and view master index"""
    try:
        items = db.get_all_items()
        generator = ReportGenerator()
        
        # Generate missing reports
        for item in items:
            if not item.get('report_path') or not os.path.exists(item.get('report_path', '')):
                report_path = generator.generate_report(item)
                db.update_report_path(item['id'], report_path)
        
        # Generate master index
        items = db.get_all_items()
        index_path = generator.generate_master_index(items)
        
        return send_file(index_path)
    except Exception as e:
        return f"Error: {str(e)}", 500


if __name__ == '__main__':
    print("=" * 60)
    print("FlipTrack Web Dashboard")
    print("=" * 60)
    print(f"Starting server...")
    print(f"Access at: http://localhost:5000")
    print(f"Press Ctrl+C to stop")
    print("=" * 60)
    app.run(debug=True, host='0.0.0.0', port=5000)
