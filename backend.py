
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import firebase_admin
from firebase_admin import credentials, auth
import httpx
import os
import json
from fastapi.responses import JSONResponse
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware


# Debug: Check if firebase_key.json exists and is valid
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")

if os.path.exists("firebase_key.json"):
    print("✓ firebase_key.json found")
    try:
        with open("firebase_key.json") as f:
            data = json.load(f)
            print(f"✓ File is valid JSON, type: {data.get('type')}")
    except Exception as e:
        print(f"✗ Error reading JSON: {e}")
else:
    print("✗ firebase_key.json NOT found!")


app = FastAPI()

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase_key.json")
firebase_admin.initialize_app(cred)

"""
# For Test Only
# Allow CORS so HTML frontend (likely running on localhost) can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["Authorization", "Content-Type"],
)
"""

# Dynamic CORS Middleware for multiple origins
class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        origin = request.headers.get("Origin")

        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
        else:
            response = await call_next(request)

        # Add dynamic CORS headers
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization,Content-Type"

        return response
    

app.add_middleware(DynamicCORSMiddleware)


#Verify Firebase ID Token
async def verify_firebase_token(request: Request):
    
    id_token = request.headers.get("Authorization")
    if not id_token or not id_token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization token missing")
    
    token = id_token.split(" ")[1]

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid token") from e
    
    # For testing purposes, bypass token verification
    # return {"uid": "test_user"}
    

# Define the expected JSON schema --- payload schema ---
class FlightSearch(BaseModel):
    date: str
    origin: str
    destination: str
    airline: Optional[str] = None
    cabin_class: Optional[str] = None
    DirectFlight: Optional[bool] = False

# Search Endpoint (Protected)
@app.post("/search")
async def search_flights(request: Request, payload: FlightSearch):
    
    # 1. Verify Firebase Token
    decoded = await verify_firebase_token(request)
    user_id = decoded["uid"]

    print(f"User {decoded.get('email')} is making a search request.")
    
    # For testing, just echo back what we received
    print("Received payload:", payload.dict())
    print("Headers received:", dict(request.headers))

    results = [
        {
            "airline": payload.airline,
            "flight": "TEST123",
            "origin": payload.origin,
            "destination": payload.destination,
            "date": payload.date,
            "class": payload.cabin_class,
            "direct": payload.DirectFlight,
            "price": 199.99
        }
    ]
    

    return {
        "message": "JSON received successfully",
        "user_id": user_id,
        "results": results
    }


    """

    # 2. Forward payload to private microservices
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://private-microservice.local/search", # private services URL
            json={
                **payload.dict(),
                "user_id": user_id # pass user info internally if needed
            }
        )

    internal_results = response.json()
    return internal_results

    """



# Run the app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("public_api:app", host="192.168.1.81", port=8001, reload=True)
