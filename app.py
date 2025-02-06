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
    
    # Validate retailer name
    retailer = data['retailer']
    retailer_pattern = re.compile(r'^[\w\s\-&]+$')
    if not isinstance(retailer, str) or not retailer_pattern.match(retailer):
        errors.append("Retailer must be a string with allowed characters: letters, numbers, spaces, hyphens, and &.")
    
    # Validate purchaseDate format (YYYY-MM-DD)
    try:
        datetime.strptime(data['purchaseDate'], '%Y-%m-%d')
    except ValueError:
        errors.append("Invalid purchaseDate format. Expected YYYY-MM-DD.")
    
    # Validate purchaseTime format (HH:MM)
    try:
        datetime.strptime(data['purchaseTime'], '%H:%M')
    except ValueError:
        errors.append("Invalid purchaseTime format. Expected HH:MM.")
    
    # Validate items
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
            else:
                desc = item['shortDescription']
                price = item['price']
                if not isinstance(desc, str) or not item_desc_pattern.match(desc):
                    errors.append(f"Item {idx} shortDescription has invalid characters.")
                if not isinstance(price, str) or not item_price_pattern.match(price):
                    errors.append(f"Item {idx} price must be a string with exactly two decimal places (e.g., 6.49).")
                else:
                    try:
                        float(price)
                    except ValueError:
                        errors.append(f"Item {idx} price is not a valid number.")
    
    # Validate total format
    total = data.get('total', '')
    total_pattern = re.compile(r'^\d+\.\d{2}$')
    if not isinstance(total, str) or not total_pattern.match(total):
        errors.append("Total must be a string with exactly two decimal places (e.g., 9.00).")
    else:
        try:
            float(total)
        except ValueError:
            errors.append("Total is not a valid number.")
    
    return errors

def calculate_points(data):
    points = 0
    
    retailer = data['retailer']
    alphanum_chars = re.sub(r'[^a-zA-Z0-9]', '', retailer)
    points += len(alphanum_chars)
    
    total = float(data['total'])
    if total.is_integer():
        points += 50
    
    total_cents = round(total * 100)
    if total_cents % 25 == 0:
        points += 25
    
    num_items = len(data['items'])
    points += (num_items // 2) * 5
    
    for item in data['items']:
        desc = item['shortDescription'].strip()
        if len(desc) % 3 == 0:
            price = float(item['price'])
            points += math.ceil(price * 0.2)
    
    purchase_date = datetime.strptime(data['purchaseDate'], '%Y-%m-%d')
    if purchase_date.day % 2 != 0:
        points += 6
    
    purchase_time = datetime.strptime(data['purchaseTime'], '%H:%M').time()
    time_min = purchase_time.hour * 60 + purchase_time.minute
    if 14 * 60 <= time_min <= 16 * 60:
        points += 10

    return points

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    data = request.get_json()
    if not data:
        return jsonify({"message": "Invalid JSON"}), 400
    
    errors = validate_receipt(data)
    if errors:
        return jsonify({"message": "The receipt is invalid", "errors": errors}), 400
    
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