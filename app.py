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

    # Regex patterns from api.yml
    retailer_pattern = re.compile(r'^[\w\s\-&]+$')
    item_desc_pattern = re.compile(r'^[\w\s\-]+$')
    price_pattern = re.compile(r'^\d+\.\d{2}$')
    total_pattern = re.compile(r'^\d+\.\d{2}$')

    # Validate retailer
    retailer = data.get('retailer', '')
    if not retailer_pattern.match(retailer):
        errors.append("Retailer contains invalid characters. Only alphanumerics, spaces, hyphens, and & are allowed.")

    # Validate purchaseDate
    try:
        datetime.strptime(data['purchaseDate'], '%Y-%m-%d')
    except ValueError:
        errors.append("Invalid purchaseDate. Expected format: YYYY-MM-DD.")

    # Validate purchaseTime
    try:
        datetime.strptime(data['purchaseTime'], '%H:%M')
    except ValueError:
        errors.append("Invalid purchaseTime. Expected format: HH:MM.")

    # Validate items
    items = data.get('items', [])
    if len(items) < 1:
        errors.append("Receipt must contain at least one item.")
    else:
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                errors.append(f"Item {idx} is not an object.")
                continue
            if 'shortDescription' not in item or 'price' not in item:
                errors.append(f"Item {idx} is missing required fields.")
                continue
            desc = item['shortDescription']
            price = item['price']
            if not item_desc_pattern.match(desc.strip()):
                errors.append(f"Item {idx} description contains invalid characters.")
            if not price_pattern.match(price):
                errors.append(f"Item {idx} price must be a string with exactly two decimal places (e.g., 12.00).")
            else:
                try:
                    float(price)
                except ValueError:
                    errors.append(f"Item {idx} price is not a valid number.")

    # Validate total
    total = data.get('total', '')
    if not total_pattern.match(total):
        errors.append("Total must be a string with exactly two decimal places (e.g., 35.35).")
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
    alphanum = re.sub(r'[^a-zA-Z0-9]', '', retailer)
    points += len(alphanum)

    # Rule 2: Total is a round dollar amount
    total = float(data['total'])
    if total.is_integer():
        points += 50

    # Rule 3: Total is a multiple of 0.25
    total_cents = round(total * 100)
    if total_cents % 25 == 0:
        points += 25

    # Rule 4: 5 points per two items
    num_items = len(data['items'])
    points += (num_items // 2) * 5

    # Rule 5: Trimmed description length divisible by 3 → ceil(price * 0.2)
    for item in data['items']:
        desc = item['shortDescription'].strip()
        if len(desc) % 3 == 0:
            price = float(item['price'])
            points += math.ceil(price * 0.2)

    # Rule 6: Odd purchase day
    purchase_date = datetime.strptime(data['purchaseDate'], '%Y-%m-%d')
    if purchase_date.day % 2 != 0:
        points += 6

    # Rule 7: Purchase time between 2:00 PM and 4:00 PM
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
        return jsonify({
            "message": "The receipt is invalid. Please verify input.",
            "errors": errors
        }), 400

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
