
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List

app = FastAPI()

# Allow CORS so HTML frontend (likely running on localhost) can call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the expected JSON schema
class FlightSearch(BaseModel):
    date: str
    origin: str
    destination: str
    airline: Optional[str] = None
    cabin_class: Optional[str] = None
    DirectFlight: Optional[bool] = False

@app.post("/search")
async def search_flights(payload: FlightSearch):
    # For testing, just echo back what we received
    print("Received payload:", payload.dict())
    return {
        "message": "JSON received successfully",
        "results": [
            {
                "flight": "TEST123",
                "origin": payload.origin,
                "destination": payload.destination,
                "date": payload.date,
                "airline": payload.airline,
                "class": payload.cabin_class,
                "direct": payload.DirectFlight
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend:app", host="127.0.0.1", port=8001, reload=True)
