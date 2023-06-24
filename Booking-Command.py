import os
import uuid
from enum import Enum
import jwt

from boto3 import client
from boto3.dynamodb.conditions import Key

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

import uvicorn

class BookingStatus(str, Enum):
    Pending = "1"
    Confirmed = "2"
    Rejected = "3"

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"]
)

@app.post("/book")
def book(request):
    token = request.get("idToken")  # JWT Token
    if not token:
        raise HTTPException(status_code=400, detail="Missing idToken")
    
    id_token_details = jwt.decode(token, options={"verify_signature": False})

    booking = {
        "id": str(uuid.uuid4()),
        "hotel_id": request["HotelId"],
        "checkin_date": request["CheckinDate"],
        "checkout_date": request["CheckoutDate"],
        "user_id": id_token_details.get("sub"),
        "given_name": id_token_details.get("given_name"),
        "family_name": id_token_details.get("family_name"),
        "phone_number": id_token_details.get("phone_number"),
        "email": id_token_details.get("email"),
        "status": BookingStatus.Pending
    }

    table_name= os.getenv("tableName")
    dynamodb = client("dynamodb")
    table = client.Table(table_name)
    table.put_item(Item=booking)

@app.get("/health")
def health_check():
    return JSONResponse(status_code= 200, content="OK")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=80)