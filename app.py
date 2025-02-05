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

