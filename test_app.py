import pytest
from app import app, calculate_points

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_process_receipt_valid(client):
    receipt = {
        "retailer": "Target",
        "purchaseDate": "2022-01-01",
        "purchaseTime": "13:01",
        "items": [
            {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
            {"shortDescription": "Dasani", "price": "1.40"}
        ],
        "total": "2.65"
    }
    response = client.post('/receipts/process', json=receipt)
    assert response.status_code == 200
    assert 'id' in response.get_json()

def test_get_points(client):
    receipt = {
        "retailer": "M&M Corner Market",
        "purchaseDate": "2022-03-20",
        "purchaseTime": "14:33",
        "items": [
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Gatorade", "price": "2.25"},
            {"shortDescription": "Pink Lemonade Britvic", "price": "5.40"}
        ],
        "total": "9.00"
    }
    process_response = client.post('/receipts/process', json=receipt)
    receipt_id = process_response.get_json()['id']
    points_response = client.get(f'/receipts/{receipt_id}/points')
    assert points_response.status_code == 200
    assert points_response.get_json()['points'] == 109

def test_invalid_receipt(client):
    receipt = {"retailer": "Test"}
    response = client.post('/receipts/process', json=receipt)
    assert response.status_code == 400