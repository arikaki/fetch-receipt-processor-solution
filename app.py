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
    
    if not isinstance(data['retailer'], str):
        errors.append("Retailer must be a string")
    
    try:
        datetime.strptime(data['purchaseDate'], '%Y-%m-%d')
    except ValueError:
        errors.append("Invalid purchaseDate format. Expected YYYY-MM-DD.")
    
    try:
        datetime.strptime(data['purchaseTime'], '%H:%M')
    except ValueError:
        errors.append("Invalid purchaseTime format. Expected HH:MM.")
    
    items = data.get('items', [])
    if not isinstance(items, list) or len(items) < 1:
        errors.append("Items must be a non-empty array")
    else:
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"Item {idx} is not an object")
                continue
            if 'shortDescription' not in item or 'price' not in item:
                errors.append(f"Item {idx} missing required fields")
            else:
                if not isinstance(item['shortDescription'], str):
                    errors.append(f"Item {idx} shortDescription must be a string")
                if not isinstance(item['price'], str):
                    errors.append(f"Item {idx} price must be a string")
                else:
                    try:
                        float(item['price'])
                    except ValueError:
                        errors.append(f"Item {idx} price is not a valid number")
    
    total = data.get('total', '')
    if not isinstance(total, str):
        errors.append("Total must be a string")
    else:
        try:
            float(total)
        except ValueError:
            errors.append("Total is not a valid number")
    
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