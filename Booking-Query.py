import jwt
import boto3
from boto3.dynamodb.conditions import Key
from fastapi import FastAPI

class BookingDto:
    # HotelName and CityName attributes are used to be displayed in the website only. Not part of the booking table.
    HotelName: str = None
    CityName: str = None
    HotelId: str = None
    CheckinDate: str = None
    CheckoutDate: str = None
    UserId: str = None
    Id: str = None
    GivenName: str = None
    FamilyName: str = None
    PhoneNumber: str = None
    Email: str = None
    Status: int = 0

class Hotel:
    Id: str = None
    UserId: str = None
    Name: str = None
    CityName: str = None

app = FastAPI()

dynamodb = boto3.resource('dynamodb')
table_booking = dynamodb.Table('Booking')
table_hotel = dynamodb.Table('Hotels_Order_Domain')

@app.get("/query")
async def query(idToken: str = None):
    idTokenDetails = jwt.decode(idToken, verify=False)
    userId = idTokenDetails.get('sub', '')
    groups = idTokenDetails.get('cognito:groups', '')

    result = []

    if not groups: # ordinary user
        response = table_booking.query(
            KeyConditionExpression=Key('UserId').eq(userId),
            IndexName='UserId-index'
        )
        result.extend([BookingDto(**item) for item in response['Items']])
    elif 'HotelManager' in groups: # hotel admin
        response = table_booking.query(
            IndexName='Status-index',
            KeyConditionExpression=Key('Status').eq(1)
        )
        result.extend([BookingDto(**item) for item in response['Items']])

    # this code has been added to display extra information. Not part of the lecture.
    for booking in result:
        hotelId = booking.HotelId
        response = table_hotel.query(
            KeyConditionExpression=Key('Id').eq(hotelId),
            IndexName='Id-index'
        )
        hotel = response['Items'][0] if response['Items'] else None
        booking.HotelName = hotel['Name'] if hotel else ""
        booking.CityName = hotel['CityName'] if hotel else ""

    return result

@app.get("/")
async def index():
    return True
