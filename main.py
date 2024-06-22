from fastapi import FastAPI, Request
import mysql.connector
import json

app = FastAPI()

# Database connection details
db_config = {
    'user': 'root',
    'password': '********',
    'host': 'localhost',
    'database': 'hackOn',
}

# Function to get the minimum discount for a given product ID
def get_max_discount(prod_id: int):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT prodId, prodName, prodDesc,
               LEAST(SBI, Axis, ICICI, MasterCard, HDFC) AS max_discount
        FROM product
        WHERE prodId = %s
    """
    cursor.execute(query, (prod_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

@app.post("/webhook")
async def webhook(request: Request):
    req = await request.json()
    
    # Extract intent and parameters from the Dialogflow request
    intent_name = req['queryResult']['intent']['displayName']
    parameters = req['queryResult']['parameters']
    
    if intent_name == 'max.discount':
        prod_id = parameters.get('prodId')
        if prod_id:
            discount_info = get_max_discount(prod_id)
            if discount_info:
                response = {
                    "fulfillmentText": f"The maximum discount for {discount_info['prodName']} is {discount_info['max_discount']}%",
                }
            else:
                response = {
                    "fulfillmentText": "Product not found.",
                }
        else:
            response = {
                "fulfillmentText": "Product ID not provided.",
            }
    else:
        response = {
            "fulfillmentText": "Intent not recognized.",
        }
    
    return json.dumps(response)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
