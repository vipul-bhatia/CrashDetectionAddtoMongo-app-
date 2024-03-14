import datetime
from typing import List, Optional  
from http.client import HTTPException
from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel, conint
from bson.objectid import ObjectId

app = FastAPI()

# Connect to MongoDB
client = MongoClient("mongodb+srv://priyam:pqrs.123@cluster0.1uefwpt.mongodb.net/")
db = client['car_crash']
collection = db['user_login']


class UserInitial(BaseModel):
    fcm: str

class UserEmailPasswordUpdate(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None

class UserContactsUpdate(BaseModel):
    contact_numbers: List[str] = []
    email_ids: List[str] = []

class UserLocation(BaseModel):
    latitude: float
    longitude: float
    timestamp: datetime.datetime = datetime.datetime.now()

@app.get("/")
async def root():
    return {"message": "Welcome to your FastAPI application"}

@app.get("/request-location")
async def request_location():
    # Instead of returning location data directly, send a specific message
    # For example, you can send a JSON response with a message
    response_message = {"message": "give location"}
    return response_message

@app.post("/location")
async def store_location(location: UserLocation):
    location_dict = location.dict()
    result = collection.insert_one(location_dict)
    return {"_id": str(result.inserted_id)}

@app.post("/user")
async def create_user(user: UserInitial):
    existing_user = collection.find_one({"fcm": user.fcm})
    if existing_user:
        return {"message": "User with the same FCM token already exists"}

    user_dict = user.dict()
    user_dict['email'] = ''  # Initialize empty "email" field
    user_dict["password"] = ""  # Initialize empty "password" field
    user_dict['location_latitude'] = float
    user_dict['location_longitude'] = float
    user_dict["contact_numbers"] = []  # Initialize empty "contact_numbers" field
    user_dict["email_ids"] = []  # Initialize empty "email_ids" field
    user_dict['contact_fcm'] = []
    result = collection.insert_one(user_dict)
    return {"_id": str(result.inserted_id)}

@app.patch("/user/{user_id}/location")
async def update_user_location(user_id: str, location: UserLocation):
    user = collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user["location_latitude"] = location.latitude
    user["location_longitude"] = location.longitude
    return {"updated": 1}

@app.patch("/user/{user_id}/email-password")
async def update_user_email_password(user_id: str, user_update: UserEmailPasswordUpdate):
    user = collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user_update.email:
        user["email"] = user_update.email
    if user_update.password:
        user["password"] = user_update.password
    result = collection.replace_one({"_id": ObjectId(user_id)}, user)
    return {"updated": result.modified_count}

@app.patch("/user/{user_id}/contacts")
async def update_user_contacts(user_id: str, user_update: UserContactsUpdate):
    user = collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user["contact_numbers"].extend(user_update.contact_numbers)
    user["email_ids"].extend(user_update.email_ids)
    result = collection.replace_one({"_id": ObjectId(user_id)}, user)
    return {"updated": result.modified_count}

@app.get("/user/{user_id}")
async def get_user(user_id: str):
    user = collection.find_one({"_id": ObjectId(user_id)})
    if user:
        user['_id'] = str(user['_id'])
        return user
    else:
        return {"message": "User not found"}

@app.delete("/user/{user_id}")
async def delete_user(user_id: str):
    result = collection.delete_one({"_id": ObjectId(user_id)})
    return {"deleted": result.deleted_count}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
