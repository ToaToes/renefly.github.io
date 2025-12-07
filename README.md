# renefly.github.io
Flight Tickets Book


Schema:

***1. User → Public API Server<br>***
User sends request with Firebase ID token + Payload<br>
FastAPI verifies token and extracts UID

***2. Public API Server → Private Microservices<br>***
Public server sends requests (HTTP or gRPC or message queue) to private servers<br>
Private servers perform the actual flight search tasks<br>
Private servers return results

***3. Public API Server → User<br>***
Public server aggregates results from all private servers<br>
Sends final response to the user<br>

This ensures only one publicly exposed endpoint, and all internal services stay isolated and protected.


```
Structure:

project/
│
├── public_api/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
├── search_service/
│   ├── app.py
│   ├── requirements.txt
│   └── Dockerfile
│
└── docker-compose.yml

```


### USING Docker

```
# Build docker image
docker build -t public-api:latest .
# run actual as server
docker run -d -p 8001:8001 public-api:latest  # Use -d for detached mode
```

When you run with -it, the container attaches to your terminal<br>
```
docker run -it -p 8001:8001 public_api:latest
```
After processing one request, if there's an issue or the script completes, it exits<br>
Using -d (detached) mode runs it in the background as a proper server<br>

MUST MUST Match the app names!!
```
#in python

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("public_api:app", host="192.168.1.81", port=8001, reload=True)
```
```
# in docker file

# Run the server
CMD ["uvicorn", "public_api:app", "--host", "0.0.0.0", "--port", "8001"]
```
