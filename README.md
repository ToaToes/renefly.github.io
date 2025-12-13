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

To Check Logs
```
docker logs -f public-api 
```


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

### NOTE: CMD COMMAND will overide the python code:
```
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("public_api:app", host="192.168.1.81", port=8001, reload=True)
```
_remember to change when environment altered_


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

5. Firebase auth 401 unauthorized <br>
Docker containers by default use UTC time and don't sync with host time. When Firebase checks token expiration, it uses container time, which thinks it's already tomorrow, making valid tokens appear expired. <br>
Add clock_tolerance=86400 to auth.verify_id_token() call.<br>
```
# Clock skew:
# Docker container time might be off:

# Check container time
docker exec public-api date
# Compare with host time
date
```


6. TO TEST backend alone
```
# in terminal
TOKEN="eyJhbGciOiJSUzI1NiIsImtpZCI6Ijk1MTg5MTkxMTA3NjA1NDM0NGUxNWUyNTY0MjViYjQyNWVlYjNhNWMiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOiJodHRwczovL3NlY3VyZXRva2VuLmdvb2dsZS5jb20vbG9naW5hdXRoLTg2NjJlIiwiYXVkIjoibG9naW5hdXRoLTg2NjJlIiwiYXV0aF90aW1lIjoxNzY1MTc4NDMzLCJ1c2VyX2lkIjoiU2s3SjU5SUJNaVF0SUdscG1nekhQR0RCMUtJMyIsInN1YiI6IlNrN0o1OUlCTWlRdElHbHBtZ3pIUEdEQjFLSTMiLCJpYXQiOjE3NjUxNzg0NjIsImV4cCI6MTc2NTE4MjA2MiwiZW1haWwiOiJleHJpdmVpdkBnbWFpbC5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZSwiZmlyZWJhc2UiOnsiaWRlbnRpdGllcyI6eyJlbWFpbCI6WyJleHJpdmVpdkBnbWFpbC5jb20iXX0sInNpZ25faW5fcHJvdmlkZXIiOiJwYXNzd29yZCJ9fQ.J7SOA4uS-4DAHzHyHPnFGgPDE4xIT-1Fa3F8-gmeFgbIzU8LSZmKGuuw5ropxhj5_a3TkaS8Me2iakYhUWrvlctqQdqzkxaQ3JdpnilZ_S2yT1rnsl0c0ZkWdnSg5rAZh3lRbP_Un9R4k3Q7cEVzd_eY_B3VMvhyk9LRTwOPKUByczkjC689mKpJfHINWi7jLWwucqfdpFRxRaZSzZ1oITjFXZy8rBohjs0SOvLahQcHAxT-CvxVgS7Rj9YWMe3YNJJT7xMeZpyhbao9Se5ajP0VVq3zpjL-50VBI9-s7ZcK_DOnXpVTVwXiKAWDHGWM3T1JZeMSZIdfPKJduGOkow"

curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"date":"2026-01-10","origin":"LAX","destination":"HKG","airline":"UA","cabin_class":"business","DirectFlight":true}' \
  -s | python3 -m json.tool

```

7. Handle large amount of Flows

FastAPI itself is async, but Python is still CPU-bound. <br>
Use multiple Uvicorn/Gunicorn workers:
```
gunicorn public_api:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:53699
```
Rule of thumb:
```
workers = (CPU cores × 2) + 1
```

Command:
public_api:app	public_api.py file, variable app<br>
-k uvicorn.workers.UvicornWorker	Use Uvicorn worker for async FastAPI<br>
--workers 4	Number of worker processes (adjust to CPU cores)<br>
--bind 0.0.0.0:53699	Listen on all interfaces on port 53699<br>
```
gunicorn public_api:app \
  -k uvicorn.workers.UvicornWorker \
  --workers 4 \
  --bind 0.0.0.0:53699
```
Adjust workers based on CPU cores:
```
workers = (CPU cores × 2) + 1
```
Run in background:
```
gunicorn public_api:app -k uvicorn.workers.UvicornWorker --workers 4 --bind 0.0.0.0:53699 &
```
Stop the server:
```
pkill -f "gunicorn public_api:app"
```
Use Docker (optional) — same command is in the Dockerfile.
