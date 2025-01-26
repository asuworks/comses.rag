# comses.rag - RAG Pipeline for CoMSES
> an API that exposes RAG funcitonality using local LLMs

# Overview
https://www.figma.com/board/2UJjJii1LFyd6kdhxhyMRd/comses.rag?node-id=0-1&t=6td126XP4gCsTsDq-1
## Ingestion
## Retrieval
### Agentic RAG
### React Agent
#### Prompt
#### Tools
1. metadata_keyword_search_tool
2. metadata_vector_search_tool
3. metadata_text_to_sql_tool
4. docs_keyword_search
5. docs_vector_search
6. docs_summary_vector_search
7. summarize
8. compare
9. coder (answer questions about model's code)

## Workflows
### Simple Workflow
### Complex Workflow


# Develop, Test and Deploy
## Run locally with Docker (with  source mounting and port exposure)

0. Setup
```bash
    set -x PYTHONPATH /home/asuworks/work/repos/github.com/asuworks/comses.rag/src
```
```shell
    docker context use default
    cp env.example .env # and adjust
```
1. Temporal services
```shell
    make t # start temporal services
    make kt # kill temporal services
```
2. Main Services
```shell
    make d # start services with source mounting and localhost port forwarding
    make k # kill services        
```
3. Temporal Workers
```shell
    # for now use some terminal multiplexer like for example zellij or tmux
    # later workers will be separate docker containers
    
    python src/ingest/workers/ingest_worker/run.py
    python src/shared/workers/minio_worker/run.py
    python src/shared/workers/ollama_embedding_worker/run.py
    python src/shared/workers/ollama_generate_worker/run.py
    python src/shared/workers/postgres_db_worker/run.py
    python src/shared/workers/vector_db_worker/run.py
```
4. Start Temporal Workflows with `tctl`

```bash
cd ~/tmp/tctl

./temporal workflow start \
          --type IngestModelWorkflow \
          --workflow-id ingest-my_abm \
          --task-queue ingest-queue \
          --input '{"model_id": "4baf25b3-e800-4781-89ff-53201a8b446d", "model_slug": "my_abm", "original_file_path":"/local_folder/my_abm.pdf", "metadata_json_path": "/local_folder/codemeta.json"}'
```
```shell
./temporal workflow start \
          --type ComputeEmbeddingsWorkflow \
          --workflow-id compute-embeddings-test \
          --task-queue ingest-queue \
          --input '[
          "model_id 4baf25b3-e800-4781-89ff-53201a8b446d",
          "model_slug my_abm",
          "original_file_path /local_folder/my_abm.pdf",
          "metadata_json_path /local_folder/codemeta.json",
          "version 1.0",
          "author John Doe",
          "description An example ABM model",
          "created_at 2025-01-01T12:00:00Z",
          "updated_at 2025-01-10T12:00:00Z",
          "tags agent-based-modeling, simulation, AI",
          "license MIT",
          "source_url https://github.com/example/my_abm",
          "documentation_url https://example.com/my_abm_docs",
          "contact_email john.doe@example.com",
          "status active"
      ]'
```
5. Admin Database Tasks
```bash
    make reset-models-db
    make seed-models-db # seed fake data
```





## Build and Push Containers to `ghcr.io`
    export CR_PAT=YOUR_TOKEN
    echo $CR_PAT | docker login ghcr.io -u USERNAME --password-stdin

## Deploy to production
```shell
     # ssh into production server or use 
     docker context use ${PROD_SERVER_IP}
     git clone https://github.com/asuworks/comses.rag
     
     # adjust .env on the production server
     make t # start temporal services
     make kt # kill temporal services
     make p # start services
     make k # kill services
```

## FastApi Server
Listens on `:8000` with following routes:

- `/register` - register a client
- `/token` - get client bearer token
- `/chat` - send a chat request (auth with X-API-Key in header)
- `/spamcheck` - `{"text": "text to check for spam", "type": "event|job|codebase|user" }` (auth with X-API-Key in header)

## Import Bruno API collection
> https://www.usebruno.com/

Import from `/test/bruno_api_collection/comses.rag json`