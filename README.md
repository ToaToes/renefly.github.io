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

without name restriction, container will be given random names
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

## Clean rebuild and restart:
1. cut the port
```
# Remove the conflicting container
docker rm -f public-api

# Or if that doesn't work, use the container ID shown in the error
docker rm -f ac812d5095dc1e860d48a790c36b35cbf5391839f482eb226d79f0ed2e837464
```

2. check port usage
```
# Find what's using port 8001
lsof -i :8001

# If it shows a process, kill it
lsof -ti:8001 | xargs kill -9 2>/dev/null

# OR check if it's another Docker container
docker ps --format "table {{.Names}}\t{{.Ports}}" | grep 8001

```
or use different port
```
docker run -d -p 8002:8001 --name public-api public-api:latest
```

3. rerun, last one
```
# Remove any existing public-api container
docker rm -f public-api 2>/dev/null || true

# Check for other containers using port 8001
docker ps -a --format "table {{.Names}}\t{{.Ports}}" | grep 8001

# Stop any container using port 8001
docker stop $(docker ps -q --filter "publish=8001") 2>/dev/null
docker rm $(docker ps -aq --filter "publish=8001") 2>/dev/null

# Now run fresh
docker run -d -p 8001:8001 --name public-api public-api:latest
```

4. To stop the IN Use docker container
```
# list all containers
docker ps -a

docker stop <container_id>

# remove all containers that not in use
docker image prune -a
```
