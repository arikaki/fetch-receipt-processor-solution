import re
import math
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
receipts = {}

def validate_receipt(data):
    errors = []
    required_fields = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing field: {field}")
    if errors:
        return errors
    
    # Validate retailer name format (regex: ^[\w\s\-&]+$)
    retailer = data.get('retailer', '')
    retailer_pattern = re.compile(r'^[\w\s\-&]+$')
    if not isinstance(retailer, str) or not retailer_pattern.fullmatch(retailer):
        errors.append("Retailer name contains invalid characters. Allowed: letters, numbers, spaces, hyphens, and &.")
    
    # Validate purchaseDate (YYYY-MM-DD)
    purchase_date = data.get('purchaseDate', '')
    try:
        datetime.strptime(purchase_date, '%Y-%m-%d')
    except ValueError:
        errors.append("Invalid purchaseDate format. Expected YYYY-MM-DD.")
    
    # Validate purchaseTime (HH:MM)
    purchase_time = data.get('purchaseTime', '')
    try:
        datetime.strptime(purchase_time, '%H:%M')
    except ValueError:
        errors.append("Invalid purchaseTime format. Expected HH:MM.")
    
    # Validate items array
    items = data.get('items', [])
    if not isinstance(items, list) or len(items) < 1:
        errors.append("Items must be a non-empty array.")
    else:
        item_desc_pattern = re.compile(r'^[\w\s\-]+$')
        item_price_pattern = re.compile(r'^\d+\.\d{2}$')
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"Item {idx} is not an object.")
                continue
            if 'shortDescription' not in item or 'price' not in item:
                errors.append(f"Item {idx} missing required fields.")
                continue
            
            # Validate item shortDescription (regex: ^[\w\s\-]+$)
            desc = item['shortDescription']
            if not isinstance(desc, str) or not item_desc_pattern.fullmatch(desc.strip()):
                errors.append(f"Item {idx} shortDescription has invalid characters.")
            
            # Validate item price (regex: ^\d+\.\d{2}$)
            price = item['price']
            if not isinstance(price, str) or not item_price_pattern.fullmatch(price):
                errors.append(f"Item {idx} price must be a string with exactly two decimal places (e.g., 6.49).")
            else:
                try:
                    float(price)
                except ValueError:
                    errors.append(f"Item {idx} price is not a valid number.")
    
    # Validate total (regex: ^\d+\.\d{2}$)
    total = data.get('total', '')
    total_pattern = re.compile(r'^\d+\.\d{2}$')
    if not isinstance(total, str) or not total_pattern.fullmatch(total):
        errors.append("Total must be a string with exactly two decimal places (e.g., 9.00).")
    else:
        try:
            float(total)
        except ValueError:
            errors.append("Total is not a valid number.")
    
    return errors

def calculate_points(data):
    points = 0
    
    # Rule 1: Alphanumeric characters in retailer name
    retailer = data['retailer']
    alphanum_chars = re.sub(r'[^\w]', '', retailer)
    points += len(alphanum_chars)
    
    # Rule 2 & 3: Total is round dollar or multiple of 0.25
    total = float(data['total'])
    if total.is_integer():
        points += 50
    if (total * 100) % 25 == 0:
        points += 25
    
    # Rule 4: 5 points per two items
    num_items = len(data['items'])
    points += (num_items // 2) * 5
    
    # Rule 5: Item description trimmed length divisible by 3
    for item in data['items']:
        desc = item['shortDescription'].strip()
        if len(desc) % 3 == 0:
            price = float(item['price'])
            points += math.ceil(price * 0.2)
    
    # Rule 6: Odd purchase day
    purchase_date = datetime.strptime(data['purchaseDate'], '%Y-%m-%d')
    if purchase_date.day % 2 != 0:
        points += 6
    
    # Rule 7: Purchase time between 14:00 and 16:00
    purchase_time = datetime.strptime(data['purchaseTime'], '%H:%M').time()
    if 14 <= purchase_time.hour < 16:
        points += 10
    
    return points

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON"}), 400
    
    errors = validate_receipt(data)
    if errors:
        return jsonify({"message": "The receipt is invalid. Please verify input.", "errors": errors}), 400
    
    points = calculate_points(data)
    receipt_id = str(uuid.uuid4())
    receipts[receipt_id] = points
    
    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<string:id>/points', methods=['GET'])
def get_points(id):
    points = receipts.get(id)
    if points is None:
        return jsonify({"message": "No receipt found for that id"}), 404
    return jsonify({"points": points}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)