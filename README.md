# Receipt Processor

A REST API to process receipts and calculate reward points based on predefined rules.

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/arikaki/fetch-receipt-processor-solution.git
   cd fetch-receipt-processor-solution.git
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   flask run --port=5000
   ```

4. Docker: [Optional]

   Build and run the container:
   ```bash
   docker build -t receipt-processor .
   docker run -p 5000:5000 receipt-processor
   ```

## Endpoint

### 1. **Process reciept**

   POST ``` /receipts/process ```

   Submits a receipt for processing and returns a unique ID.

   Request Body

   ```bash
   {
      "retailer": "Target",
      "purchaseDate": "2022-01-01",
      "purchaseTime": "13:01",
      "items": [
         {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
         {"shortDescription": "Dasani", "price": "1.40"}
               ],
      "total": "2.65"
   }
   ```

   #### Response
   - **Success (200):**
   ```bash
   {
      "id": "adb6b560-0eef-42bc-9d16-df48f30e89b2"
   }
   ```

   - **Error (400):**
   ```bash
   {
      "message": "The receipt is invalid. Please verify input.", "errors": ["Missing field: retailer"]
   }
   ```


### 2. **Get points**

   GET ``` /receipts/{id}/points```

   Retrieves the points awarded for a receipt by its ID.

   #### Response
   - **Success (200):**
   ```bash
   {
      "points": 28
   }
   ```

   - **Error (400):**
   ```bash
   {
      "message": "No receipt found for that id"
   }
   ```


### 3. **Testing**

   ### Run Unit Tests

   ```bash
   pytest test_app.py -v
   ```

   #### Example Test Cases

   - **Valid Receipt:**
   ```bash
   curl -X POST http://localhost:5000/receipts/process \
   -H "Content-Type: application/json" \
   -d '{
      "retailer": "Target",
      "purchaseDate": "2022-01-01",
      "purchaseTime": "13:01",
      "items": [
         {"shortDescription": "Pepsi - 12-oz", "price": "1.25"},
         {"shortDescription": "Dasani", "price": "1.40"}
      ],
      "total": "2.65"
   }'
   ```

   - **Invalid Receipt:**
   ```bash
   curl -X POST http://localhost:5000/receipts/process \
   -H "Content-Type: application/json" \
   -d '{
      "retailer": "Target!",
      "purchaseDate": "2022-01-01",
      "purchaseTime": "13:01",
      "items": [{"shortDescription": "Pepsi", "price": "1.25"}],
      "total": "2.6"
   }'
   ```

### 4. **Docker Support**  [optional]

   #### Build and Run
   ```bash
   docker build -t receipt-processor .
   docker run -p 5000:5000 receipt-processor
   ```

   #### Test with Docker
   ```bash
   curl -X POST http://localhost:5000/receipts/process \
   -H "Content-Type: application/json" \
   -d '{
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
   }'
   ```








   





   

