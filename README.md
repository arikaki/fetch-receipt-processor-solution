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

## Docker

   Build and run the container:
   ```bash
   docker build -t receipt-processor .
   docker run -p 5000:5000 receipt-processor
   ```

## Endpoint

1. **Process reciept**

   POST ``` /receipts/process ```

   





   

