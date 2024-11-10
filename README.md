# comses.rag
> an API that exposes RAG funcitonality using local LLMs
# Develop, Test and Deploy
## Run locally with Docker (with  source mounting and port exposure)
1. `docker context use default`
2. `cp env.example .env` and adjust
3. `make t` - start temporal services
4. `make ds` - start development services
5. `make kds` - kill development services
6. `make kt` - kill temporal services

## Deploy to production
1. ssh into production server or use `docker context use ${PROD_SERVER_IP}`
2. `git clone https://github.com/asuworks/comses.rag`
3. adjust `.env` on the production server
4. `make t` - start temporal services
5. `make ds` - start development services
6. `make kds` - kill development services
7. `make kt` - kill temporal services

## FastApi Server
Listens on `:8000` with following routes:

- `/register` - register a client
- `/token` - get client bearer token
- `/chat` - send a chat request (auth with X-API-Key in header)
- `/spamcheck` - `{"text": "text to check for spam", "type": "event|job|codebase|user" }` (auth with X-API-Key in header)

## Import Bruno API collection
> https://www.usebruno.com/

Import from `/test/bruno_api_collection/comses.rag api.json`

# Operate
# Start JetStream instance with `OpenStack CLI`
```...```
