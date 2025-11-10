import os
import base64
import qrcode
from io import BytesIO
from jinja2 import Template
from typing import Dict, List
from pathlib import Path

class ReportGenerator:
    def __init__(self):
        self.reports_dir = Path("./reports")
        self.reports_dir.mkdir(exist_ok=True)
    
    def generate_report(self, item: Dict) -> str:
        """Generate a self-contained HTML report for an item"""
        try:
            # Calculate profits
            potential_profit = item['target_price'] - item['purchase_price'] - item['shipping_cost']
            actual_profit = 0
            if item['status'] == 'Sold' and item.get('final_sold_price'):
                actual_profit = item['final_sold_price'] - item['purchase_price'] - item['shipping_cost']
            
            # Generate QR code for product URL
            qr_code_base64 = ""
            if item.get('product_url') and item['product_url'].strip():
                try:
                    qr_code_base64 = self._generate_qr_code(item['product_url'])
                except Exception as e:
                    print(f"Warning: Failed to generate QR code: {e}")
            
            # Embed images as base64
            embedded_images = []
            if item.get('selected_images'):
                for img_path in item['selected_images']:
                    if os.path.exists(img_path):
                        try:
                            img_base64 = self._image_to_base64(img_path)
                            if img_base64:
                                embedded_images.append(img_base64)
                        except Exception as e:
                            print(f"Warning: Failed to embed image {img_path}: {e}")
            
            # Render template
            template_str = self._get_template()
            template = Template(template_str)
            html_content = template.render(
                item=item,
                potential_profit=potential_profit,
                actual_profit=actual_profit,
                qr_code=qr_code_base64,
                images=embedded_images
            )
            
            # Save report
            report_path = self.reports_dir / f"item_{item['id']}_report.html"
            with open(report_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(report_path)
        except Exception as e:
            raise Exception(f"Failed to generate report: {str(e)}")
    
    def generate_master_index(self, items: List[Dict]) -> str:
        """Generate a master index HTML file linking to all item reports"""
        try:
            template_str = self._get_index_template()
            template = Template(template_str)
            
            # Calculate profits for each item
            items_with_profits = []
            for item in items:
                potential_profit = item['target_price'] - item['purchase_price'] - item['shipping_cost']
                actual_profit = 0
                if item['status'] == 'Sold' and item.get('final_sold_price'):
                    actual_profit = item['final_sold_price'] - item['purchase_price'] - item['shipping_cost']
                
                items_with_profits.append({
                    **item,
                    'potential_profit': potential_profit,
                    'actual_profit': actual_profit
                })
            
            html_content = template.render(items=items_with_profits)
            
            index_path = self.reports_dir / "index.html"
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return str(index_path)
        except Exception as e:
            raise Exception(f"Failed to generate master index: {str(e)}")
    
    def _generate_qr_code(self, url: str) -> str:
        """Generate QR code and return as base64 string"""
        qr = qrcode.QRCode(version=1, box_size=10, border=2)
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        return base64.b64encode(buffer.read()).decode()
    
    def _image_to_base64(self, image_path: str) -> str:
        """Convert image file to base64 string"""
        try:
            with open(image_path, 'rb') as f:
                return base64.b64encode(f.read()).decode()
        except:
            return ""
    
    def _get_template(self) -> str:
        """Return the HTML template for individual item reports"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ item.item_name }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #0a0a0a;
            padding: 20px;
            color: #e0e0e0;
            line-height: 1.6;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: #1a1a1a;
            border-radius: 8px;
            border: 1px solid #2a2a2a;
        }
        .header {
            padding: 30px;
            border-bottom: 1px solid #2a2a2a;
        }
        .header h1 { 
            font-size: 1.8em; 
            margin-bottom: 10px;
            color: #ffffff;
            font-weight: 600;
        }
        .header .status {
            display: inline-block;
            padding: 4px 12px;
            background: #2a2a2a;
            border-radius: 4px;
            font-size: 0.85em;
            color: #a0a0a0;
        }
        .content { padding: 30px; }
        .section {
            margin-bottom: 30px;
        }
        .section h2 {
            color: #ffffff;
            margin-bottom: 15px;
            font-size: 1.1em;
            font-weight: 600;
        }
        .info-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
            gap: 12px;
            margin-bottom: 20px;
        }
        .info-item {
            background: #0f0f0f;
            padding: 15px;
            border-radius: 6px;
            border: 1px solid #2a2a2a;
        }
        .info-item label {
            display: block;
            font-size: 0.75em;
            color: #808080;
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .info-item .value {
            font-size: 1.3em;
            font-weight: 600;
            color: #ffffff;
        }
        .profit-box {
            background: #1a3a1a;
            color: #4ade80;
            padding: 20px;
            border-radius: 6px;
            text-align: center;
            margin: 15px 0;
            border: 1px solid #2a4a2a;
        }
        .profit-box.negative { 
            background: #3a1a1a;
            color: #f87171;
            border: 1px solid #4a2a2a;
        }
        .profit-box h3 { 
            font-size: 0.9em; 
            margin-bottom: 8px;
            opacity: 0.8;
            font-weight: 500;
        }
        .profit-box .amount { 
            font-size: 2em; 
            font-weight: 700;
        }
        .images-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 12px;
        }
        .images-grid img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 6px;
            border: 1px solid #2a2a2a;
        }
        .qr-section {
            text-align: center;
            padding: 20px;
            background: #0f0f0f;
            border-radius: 6px;
            border: 1px solid #2a2a2a;
        }
        .qr-section img {
            max-width: 160px;
            margin: 15px auto;
            display: block;
            padding: 10px;
            background: white;
            border-radius: 6px;
        }
        .url-link {
            display: inline-block;
            padding: 10px 20px;
            background: #2a2a2a;
            color: #e0e0e0;
            text-decoration: none;
            border-radius: 4px;
            margin-top: 10px;
            font-size: 0.9em;
            border: 1px solid #3a3a3a;
            transition: background 0.2s;
        }
        .url-link:hover { 
            background: #3a3a3a;
        }
        .footer {
            text-align: center;
            padding: 20px;
            color: #606060;
            font-size: 0.8em;
            border-top: 1px solid #2a2a2a;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ item.item_name }}</h1>
            <div class="status">{{ item.status }}</div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>Financial Details</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <label>Purchase Price</label>
                        <div class="value">${{ "%.2f"|format(item.purchase_price) }}</div>
                    </div>
                    <div class="info-item">
                        <label>Shipping Cost</label>
                        <div class="value">${{ "%.2f"|format(item.shipping_cost) }}</div>
                    </div>
                    <div class="info-item">
                        <label>Target Price</label>
                        <div class="value">${{ "%.2f"|format(item.target_price) }}</div>
                    </div>
                    {% if item.final_sold_price %}
                    <div class="info-item">
                        <label>Sold Price</label>
                        <div class="value">${{ "%.2f"|format(item.final_sold_price) }}</div>
                    </div>
                    {% endif %}
                </div>
                
                <div class="profit-box {% if potential_profit < 0 %}negative{% endif %}">
                    <h3>Potential Profit</h3>
                    <div class="amount">${{ "%.2f"|format(potential_profit) }}</div>
                </div>
                
                {% if item.status == 'Sold' and item.final_sold_price %}
                <div class="profit-box {% if actual_profit < 0 %}negative{% endif %}">
                    <h3>Actual Profit</h3>
                    <div class="amount">${{ "%.2f"|format(actual_profit) }}</div>
                </div>
                {% endif %}
            </div>
            
            {% if images %}
            <div class="section">
                <h2>Product Images</h2>
                <div class="images-grid">
                    {% for img in images %}
                    <img src="data:image/jpeg;base64,{{ img }}" alt="Product">
                    {% endfor %}
                </div>
            </div>
            {% endif %}
            
            {% if item.product_url %}
            <div class="section">
                <h2>Product Link</h2>
                <div class="qr-section">
                    {% if qr_code %}
                    <img src="data:image/png;base64,{{ qr_code }}" alt="QR Code">
                    {% endif %}
                    <a href="{{ item.product_url }}" class="url-link" target="_blank">View Online</a>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="footer">
            <p>FlipTrack - Item #{{ item.id }}</p>
        </div>
    </div>
</body>
</html>
"""
    
    def _get_index_template(self) -> str:
        """Return the HTML template for master index"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FlipTrack - All Items</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
            background: #0a0a0a;
            padding: 20px;
            color: #e0e0e0;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: #1a1a1a;
            border-radius: 8px;
            border: 1px solid #2a2a2a;
        }
        .header {
            padding: 30px;
            border-bottom: 1px solid #2a2a2a;
        }
        .header h1 { 
            font-size: 1.8em; 
            margin-bottom: 5px;
            color: #ffffff;
            font-weight: 600;
        }
        .header p {
            color: #808080;
            font-size: 0.9em;
        }
        .content { padding: 30px; }
        table {
            width: 100%;
            border-collapse: collapse;
        }
        thead {
            background: #0f0f0f;
            border-bottom: 2px solid #2a2a2a;
        }
        th {
            padding: 12px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85em;
            color: #a0a0a0;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        td {
            padding: 12px;
            border-bottom: 1px solid #2a2a2a;
            color: #e0e0e0;
        }
        tbody tr {
            transition: background 0.2s;
        }
        tbody tr:hover { 
            background: #0f0f0f;
        }
        .item-link {
            color: #60a5fa;
            text-decoration: none;
            font-size: 0.9em;
        }
        .item-link:hover { 
            text-decoration: underline;
        }
        .status-badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 500;
        }
        .status-draft { 
            background: #3a3a1a; 
            color: #fbbf24;
            border: 1px solid #4a4a2a;
        }
        .status-listed { 
            background: #1a2a3a; 
            color: #60a5fa;
            border: 1px solid #2a3a4a;
        }
        .status-sold { 
            background: #1a3a1a; 
            color: #4ade80;
            border: 1px solid #2a4a2a;
        }
        .profit-positive { color: #4ade80; font-weight: 600; }
        .profit-negative { color: #f87171; font-weight: 600; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FlipTrack</h1>
            <p>All Items</p>
        </div>
        
        <div class="content">
            <table>
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Item</th>
                        <th>Status</th>
                        <th>Purchase</th>
                        <th>Target</th>
                        <th>Potential</th>
                        <th>Actual</th>
                        <th>Report</th>
                    </tr>
                </thead>
                <tbody>
                    {% for item in items %}
                    <tr>
                        <td>{{ item.id }}</td>
                        <td>{{ item.item_name }}</td>
                        <td>
                            <span class="status-badge status-{{ item.status.lower() }}">
                                {{ item.status }}
                            </span>
                        </td>
                        <td>${{ "%.2f"|format(item.purchase_price) }}</td>
                        <td>${{ "%.2f"|format(item.target_price) }}</td>
                        <td class="{% if item.potential_profit >= 0 %}profit-positive{% else %}profit-negative{% endif %}">
                            ${{ "%.2f"|format(item.potential_profit) }}
                        </td>
                        <td class="{% if item.actual_profit >= 0 %}profit-positive{% else %}profit-negative{% endif %}">
                            {% if item.status == 'Sold' %}
                                ${{ "%.2f"|format(item.actual_profit) }}
                            {% else %}
                                -
                            {% endif %}
                        </td>
                        <td>
                            {% if item.report_path %}
                            <a href="./item_{{ item.id }}_report.html" class="item-link">View</a>
                            {% else %}
                            -
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</body>
</html>
"""
