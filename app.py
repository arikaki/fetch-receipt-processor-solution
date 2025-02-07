import re
import math
import uuid
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)
receipts_data = {}

def validate_receipt_data(receipt):
    """Validates the structure and content of a receipt submission."""
    errors = []
    required_keys = ['retailer', 'purchaseDate', 'purchaseTime', 'items', 'total']
    
    for key in required_keys:
        if key not in receipt:
            errors.append(f"Missing required field: {key}")
    
    if errors:
        return errors
    
    # Define regex patterns for validation
    retailer_regex = re.compile(r'^[\w\s\-&]+$')
    item_desc_regex = re.compile(r'^[\w\s\-]+$')
    price_format_regex = re.compile(r'^\d+\.\d{2}$')
    
    # Validate retailer name
    if not retailer_regex.match(receipt.get('retailer', '')):
        errors.append("Invalid retailer name. Allowed: alphanumerics, spaces, hyphens, &.")
    
    # Validate purchase date format
    try:
        datetime.strptime(receipt['purchaseDate'], '%Y-%m-%d')
    except ValueError:
        errors.append("Invalid purchaseDate format. Expected YYYY-MM-DD.")
    
    # Validate purchase time format
    try:
        datetime.strptime(receipt['purchaseTime'], '%H:%M')
    except ValueError:
        errors.append("Invalid purchaseTime format. Expected HH:MM.")
    
    # Validate items list
    items = receipt.get('items', [])
    if not items:
        errors.append("Receipt must contain at least one item.")
    else:
        for index, item in enumerate(items):
            if not isinstance(item, dict) or 'shortDescription' not in item or 'price' not in item:
                errors.append(f"Item {index} is missing required fields or is not an object.")
                continue
            if not item_desc_regex.match(item['shortDescription'].strip()):
                errors.append(f"Item {index} has an invalid description format.")
            if not price_format_regex.match(item['price']):
                errors.append(f"Item {index} price must be a valid monetary value (e.g., 12.00).")
    
    # Validate total price format
    if not price_format_regex.match(receipt.get('total', '')):
        errors.append("Invalid total price format. Expected string with two decimal places (e.g., 35.35).")
    
    return errors

def compute_points(receipt):
    """Computes points for a receipt based on predefined rules."""
    points = 0
    
    # Rule 1: Count alphanumeric characters in retailer name
    retailer_cleaned = re.sub(r'[^a-zA-Z0-9]', '', receipt['retailer'])
    points += len(retailer_cleaned)
    
    # Rule 2: 50 points if total is a whole dollar amount
    total_amount = float(receipt['total'])
    if total_amount.is_integer():
        points += 50
    
    # Rule 3: 25 points if total is a multiple of 0.25
    if (total_amount * 100) % 25 == 0:
        points += 25
    
    # Rule 4: 5 points per pair of items
    points += (len(receipt['items']) // 2) * 5
    
    # Rule 5: If item description length is divisible by 3, add 20% of price (rounded up)
    for item in receipt['items']:
        if len(item['shortDescription'].strip()) % 3 == 0:
            points += math.ceil(float(item['price']) * 0.2)
    
    # Rule 6: 6 points if purchase date is an odd-numbered day
    if int(receipt['purchaseDate'].split('-')[-1]) % 2 != 0:
        points += 6
    
    # Rule 7: 10 points if purchase time is between 2:00 PM and 4:00 PM
    purchase_time = datetime.strptime(receipt['purchaseTime'], '%H:%M').time()
    if 14 <= purchase_time.hour < 16:
        points += 10
    
    return points

@app.route('/receipts/process', methods=['POST'])
def process_receipt():
    """Handles receipt processing, validation, and point calculation."""
    receipt_data = request.get_json()
    if not receipt_data:
        return jsonify({"message": "Invalid JSON payload."}), 400
    
    validation_errors = validate_receipt_data(receipt_data)
    if validation_errors:
        return jsonify({"message": "Receipt validation failed.", "errors": validation_errors}), 400
    
    receipt_id = str(uuid.uuid4())
    receipts_data[receipt_id] = compute_points(receipt_data)
    
    return jsonify({"id": receipt_id}), 200

@app.route('/receipts/<string:receipt_id>/points', methods=['GET'])
def retrieve_points(receipt_id):
    """Retrieves the points associated with a given receipt ID."""
    if receipt_id not in receipts_data:
        return jsonify({"message": "No receipt found for the given ID."}), 404
    return jsonify({"points": receipts_data[receipt_id]}), 200

if __name__ == '__main__':
    app.run(port=5000, debug=True)
