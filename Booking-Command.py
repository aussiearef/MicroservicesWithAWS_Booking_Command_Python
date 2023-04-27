from uuid import uuid4
from typing import Optional
from enum import Enum

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from jose import jwt

from boto3 import client
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.types import TypeDeserializer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    expose_headers=["Custom-Header"],
)

dynamodb = client("dynamodb")


class BookingStatus(str, Enum):
    Pending = "1"
    Confirmed = "2"
    Rejected = "3"


class BookingDto:
    def __init__(
        self,
        id: str,
        hotel_id: str,
        checkin_date: str,
        checkout_date: str,
        user_id: str,
        given_name: Optional[str] = None,
        family_name: Optional[str] = None,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        status: BookingStatus = BookingStatus.Pending,
    ):
        self.id = id
        self.hotel_id = hotel_id
        self.checkin_date = checkin_date
        self.checkout_date = checkout_date
        self.user_id = user_id
        self.given_name = given_name
        self.family_name = family_name
        self.phone_number = phone_number
        self.email = email
        self.status = status.value

    def to_dict(self):
        return {
            "id": {"S": self.id},
            "hotel_id": {"S": self.hotel_id},
            "checkin_date": {"S": self.checkin_date},
            "checkout_date": {"S": self.checkout_date},
            "user_id": {"S": self.user_id},
            "given_name": {"S": self.given_name} if self.given_name else {"NULL": True},
            "family_name": {"S": self.family_name} if self.family_name else {"NULL": True},
            "phone_number": {"S": self.phone_number} if self.phone_number else {"NULL": True},
            "email": {"S": self.email} if self.email else {"NULL": True},
            "status": {"N": str(self.status)},
        }

    @classmethod
    def from_dict(cls, data):
        deserializer = TypeDeserializer()
        return cls(
            id=data["id"]["S"],
            hotel_id=data["hotel_id"]["S"],
            checkin_date=data["checkin_date"]["S"],
            checkout_date=data["checkout_date"]["S"],
            user_id=data["user_id"]["S"],
            given_name=deserializer.deserialize(data["given_name"]),
            family_name=deserializer.deserialize(data["family_name"]),
            phone_number=deserializer.deserialize(data["phone_number"]),
            email=deserializer.deserialize(data["email"]),
            status=BookingStatus(int(data["status"]["N"])),
        )


@app.post("/book")
async def book(request: dict):
    token = request.get("idToken")  # JWT Token
    if not token:
        raise HTTPException(status_code=400, detail="Missing idToken")
    try:
        id_token_details = jwt.decode(token, verify=False)
    except jwt.JWTError:
        raise HTTPException(status_code=400, detail="Invalid idToken")

    user_id = id_token_details.get("sub", "")
    given_name = id_token_details.get("given_name", "")
    family_name = id_token_details.get("family
