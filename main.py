from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List

# Initialize FastAPI app
app = FastAPI()

# MongoDB Connection
MONGO_URI = "mongodb://mongodb:27017/"
client = MongoClient(MONGO_URI)

# Database & Collection
DB_NAME = "mydatabase"
COLLECTION_NAME = "users"

# Check if Database Exists
if DB_NAME in client.list_database_names():
    print(f"Database '{DB_NAME}' exists.")
else:
    print(f"Database '{DB_NAME}' does NOT exist. It will be created when data is inserted.")

db = client[DB_NAME]

# Check if Collection Exists
if COLLECTION_NAME in db.list_collection_names():
    print(f"Collection '{COLLECTION_NAME}' exists.")
else:
    print(f"Collection '{COLLECTION_NAME}' does NOT exist. It will be created when data is inserted.")

collection = db[COLLECTION_NAME]

# Pydantic Model for User
class User(BaseModel):
    name: str
    age: int
    city: str

# API Endpoints

@app.post("/users/", response_model=dict)
def create_user(user: User):
    """Insert a new user into MongoDB"""
    result = collection.insert_one(user.dict())
    return {"message": "User created", "id": str(result.inserted_id)}

@app.get("/users/", response_model=List[dict])
def get_all_users():
    """Retrieve all users from MongoDB"""
    users = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB's default _id field
    return users

@app.get("/users/{name}", response_model=dict)
def get_user(name: str):
    """Retrieve a specific user by name"""
    user = collection.find_one({"name": name}, {"_id": 0})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{name}", response_model=dict)
def update_user(name: str, user: User):
    """Update user details"""
    result = collection.update_one({"name": name}, {"$set": user.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated"}

@app.delete("/users/{name}", response_model=dict)
def delete_user(name: str):
    """Delete a user from MongoDB"""
    result = collection.delete_one({"name": name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted"}

# Run with: uvicorn filename:app --reload
