# renefly.github.io
Flight Tickets Book


Schema:

**1. User → Public API Server<br>**
User sends request with Firebase ID token + Payload<br>
FastAPI verifies token and extracts UID

**2. Public API Server → Private Microservices<br>**
Public server sends requests (HTTP or gRPC or message queue) to private servers<br>
Private servers perform the actual flight search tasks<br>
Private servers return results

**3. Public API Server → User<br>**
Public server aggregates results from all private servers<br>
Sends final response to the user<br>

This ensures only one publicly exposed endpoint, and all internal services stay isolated and protected.
