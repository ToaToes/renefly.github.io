# Authro: Tom
# Date: 2025-12-07
# Description: Public API for flight search with Firebase Authentication
# Production-ready with concurrency control & performance optimizations
"""
Firebase authentication with caching
Multiple airlines support (split requests per airline)
Dynamic microservice routing per airline
Async HTTP calls with connection pooling
Concurrency limiting with semaphore
Timeout and error handling
"""

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
from datetime import datetime
from typing import Union, List

# ==============================
# App Initialization
# ==============================

app = FastAPI()

# ==============================
# Firebase Token Cache (5 min)
# ==============================
from cachetools import TTLCache # Cache Verified Tokens (TTL)
token_cache = TTLCache(maxsize=10000, ttl=300)  # 5 minutes

# ==============================
# Concurrency Control
# ==============================
import asyncio # 10x throughput
MAX_CONCURRENT_REQUESTS = 100
request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


# Debug: Check if firebase_key.json exists and is valid
print(f"Current directory: {os.getcwd()}")
print(f"Files in directory: {os.listdir('.')}")


# ==============================
# Firebase Initialization
# ==============================
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

# Initialize Firebase Admin SDK
cred = credentials.Certificate("firebase_key.json")
# Initialize Firebase only once, even with reload
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)


# ==============================
# Airline → Microservice Mapping
# ==============================

AIRLINE_MICROSERVICES = {
    "CX": "http://192.168.1.101:10101/search",
    # Add other microservice routes here
}

http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(5.0),
    limits=httpx.Limits(
        max_connections=200,
        max_keepalive_connections=50
    )
)

@app.on_event("shutdown")
async def shutdown_event():
    await http_client.aclose()

# ==============================
# Define the expected JSON schema --- payload schema ---
# ==============================

class FlightSearch(BaseModel):
    airline: Optional[Union[str, List[str]]] = None  # single or multiple airlines
    origin: str
    destination: str
    depart_date: str
    cabin_class: Optional[str] = None
    stop_policy: str

"""
# For Test Only
# Allow CORS so HTML frontend (likely running on localhost) can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.renefly.com"],  # 明确指定来源
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)
"""


"""
# Dynamic CORS Middleware for multiple origins
class DynamicCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):

        origin = request.headers.get("Origin")

        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            response.status_code = 200
        else:
            response = await call_next(request)

        # Add dynamic CORS headers
        if origin:
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Vary"] = "Origin"
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
            response.headers["Access-Control-Allow-Headers"] = "Authorization, Content-Type"

        return response
    

app.add_middleware(DynamicCORSMiddleware)
"""

# ==============================
# Verify Firebase ID Token
# ==============================

async def verify_firebase_token(request: Request):

    id_token = request.headers.get("Authorization")
    # DEBUG
    print(f"Debug: Authorization header received: {id_token}")
    if not id_token or not id_token.startswith("Bearer "):
        print("Debug: No Bearer token found") # DEBUG
        raise HTTPException(status_code=401, detail="Authorization token missing")
    
    token = id_token.split(" ", 1)[1]

    # Cache hit
    if token in token_cache:
        return token_cache[token]
    # DEBUG
    print(f"Debug: Token extracted, length: {len(token)}")
    print(f"Debug: Token first 20 chars: {token[:20]}...")

    try:
        # Add clock tolerance to Firebase verification: Allow 24 hours of clock skew
        print("Debug: Attempting to verify token...")
        decoded_token = auth.verify_id_token(token)
        token_cache[token] = decoded_token
        print(f"✓ Token verified successfully")
        print(f"  UID: {decoded_token['uid']}")
        print(f"  Email: {decoded_token.get('email')}")
        print(f"  Issuer: {decoded_token.get('iss')}")
        print(f"  Audience: {decoded_token.get('aud')}")
        return decoded_token
    except ValueError as e:
        print(f"Debug: ValueError during verification: {e}")
        raise HTTPException(status_code=401, detail=f"Invalid token format: {str(e)}")
    except auth.ExpiredIdTokenError as e:
        print(f"Debug: Token expired: {e}")
        raise HTTPException(status_code=401, detail="Token expired")
    except auth.InvalidIdTokenError as e:
        print(f"Debug: Invalid token error: {e}")
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        print(f"Debug: Unexpected error type: {type(e).__name__}")
        print(f"Debug: Unexpected error details: {e}")
        raise HTTPException(status_code=401, detail=f"Authentication failed: {str(e)}")
    # For testing purposes, bypass token verification
    # return {"uid": "test_user"}
    


# ==============================
# Decide which internal microservice to call based on the flight request.
# ==============================
def choose_microservice_by_airline(airline_code: Optional[str]) -> str:

    return AIRLINE_MICROSERVICES.get(airline_code.upper())


# ==============================
# Async Call to Microservice
# ==============================
async def call_microservice(url: str, payload: dict):
    async with request_semaphore:
        try:
            resp = await http_client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()
        except httpx.TimeoutException:
            return {"error": f"Timeout calling {url}"}
        except httpx.HTTPError as e:
            return {"error": f"HTTP error calling {url}: {str(e)}"}



# ==============================
# Search Endpoint (Protected)
# ==============================

@app.post("/search")
async def search_flights(request: Request, flight_requests: FlightSearch):
    """
    Protected flight search endpoint with:
    - concurrency limiting
    - cached Firebase auth
    - pooled HTTP connections
    - downstream timeout protection
    """
    async with request_semaphore:

        # 1. Verify Firebase Token
        decoded = await verify_firebase_token(request)
        user_id = decoded.get("email", "unknown")

        # 2. Build request UUID
        # request time as uuid
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        # Append timestamp to uuid
        request_uuid = f"{user_id}_{timestamp}"
        print(f"User {user_id} is making a search request.")
    
        # For testing, just echo back what we received
        print("Received payload:", flight_requests.dict())
        print("Headers received:", dict(request.headers))
    

        # 3. Prepare airline list
        airlines = flight_requests.airline
        if not airlines:
            airlines = [None]
        elif isinstance(airlines, str):
            airlines = [airlines]


        """
        # Use fake results for testing
        from fake_flights import results as fake_results

        filtered = []

        for f in fake_results:
            # airline filter
            if payload.airline and f["airline"] != payload.airline:
                continue

            # origin filter
            if payload.origin and f["origin"] != payload.origin.split("(")[-1].replace(")", ""):
                continue

            # destination filter
            if payload.destination and f["destination"] != payload.destination.split("(")[-1].replace(")", ""):
                continue

            # date filter
            if payload.date and f["date"] != payload.date:
                continue

            # class filter
            if payload.cabin_class and f["class"] != payload.cabin_class:
                continue

            # direct filter
            if payload.DirectFlight is not None and f["direct"] != payload.DirectFlight:
                continue

            filtered.append(f)


        print("Forwarding payload to Frontend...")
        return {
            "message": "JSON received successfully",
            # "user_id": user_id,
            "results": filtered
        }

        """

        # 4. Prepare async tasks for each airline
        tasks = []
        for airline_code in airlines:
            target_url = choose_microservice_by_airline(airline_code)
            payload = {
                "version": "1.0",
                "type": "flight_search_request",
                "request_flights": {
                    **flight_requests.dict(),
                    "uuid": request_uuid # pass user info internally if needed
                }
            }

            tasks.append(call_microservice(target_url, payload))
            print("Sending payload to microservice:", payload)


        # 5. Execute all microservice calls concurrently
        results = await asyncio.gather(*tasks)
        

        # 6. Combine results
        combined_results = []
        for r in results:
            if isinstance(r, dict) and "results" in r:
                combined_results.extend(r["results"])
            else:
                combined_results.append(r)

        print("Combined results:", combined_results)
        return {"results": combined_results, "request_uuid": request_uuid}


# ==============================
# Run the app with Uvicorn
# ==============================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("public_api:app", host="0.0.0.0", port=53699, reload=False)
