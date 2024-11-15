# comses.rag
> an API that exposes RAG funcitonality using local LLMs
# Develop, Test and Deploy
## Run locally with Docker (with  source mounting and port exposure)
1. `docker context use default`
2. `cp env.example .env` and adjust
3. `make t` - start `t`emporal services
4. `make kt` - `k`ill `t`emporal services
5. `make d` - start `d`evelopment services
6. `make kd` - `k`ill `d`evelopment services 

## Build and Push Containers to `ghcr.io`
    export CR_PAT=YOUR_TOKEN
    echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin


## Deploy to production
1. ssh into production server or use `docker context use ${PROD_SERVER_IP}`
2. `git clone https://github.com/asuworks/comses.rag`
3. adjust `.env` on the production server
4. `make t` - start `t`emporal services
5. `make kt` - `k`ill `t`emporal services
6. `make ps` - start `p`roduction services
7. `make kp` - `k`ill `p`roduction services 

## FastApi Server
Listens on `:8000` with following routes:

- `/register` - register a client
- `/token` - get client bearer token
- `/chat` - send a chat request (auth with X-API-Key in header)
- `/spamcheck` - `{"text": "text to check for spam", "type": "event|job|codebase|user" }` (auth with X-API-Key in header)

## Import Bruno API collection
> https://www.usebruno.com/

Import from `/test/bruno_api_collection/comses.rag json`

# Operate
## Start JetStream instance with `OpenStack CLI`
```...```

## Temporal Workflows
## Install Dependencies

    poetry install
    
This will start worker:
 
    poetry run python worker.py

In another terminal, run the following to execute a workflow:

    poetry run python starter.py

Then, in another terminal, run the following command to translate a phrase:

    curl -X POST "http://localhost:8000/translate?phrase=hello%20world&language=Spanish"

Which should produce some output like:

    {"translation":"Hola mundo"}
