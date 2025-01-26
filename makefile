########################################################################################
######################################### TEMPORAL #####################################
########################################################################################

# start temporal services
t:
	cd temporal-server && docker compose -f docker-compose-postgres.yml up -d

# kill temporal services
kt:
	cd temporal-server && docker compose -f docker-compose-postgres.yml down


########################################################################################
####################################### MAIN SERVICES ##################################
########################################################################################

# start services for development (with source mapping and localhost port forwarding)
d:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# start services in production environment
p:
	docker compose up -d

# kill services
k:
	docker compose down

redeploy:
	git pull && docker compose up -d --force-recreate

rebuild:
	git pull && docker compose up -d --force-recreate --build


########################################################################################
###################################### TEMPORAL WORKERS  ###############################
########################################################################################
w:
	python src/ingest/workers/ingest_worker/run.py
	python src/shared/workers/minio_worker/run.py
	python src/shared/workers/ollama_embedding_worker/run.py
	python src/shared/workers/ollama_generate_worker/run.py
	python src/shared/workers/postgres_db_worker/run.py
	python src/shared/workers/vector_db_worker/run.py


########################################################################################
###################################### DATABASE ADMIN ##################################
########################################################################################

reset-models-db:
	cd admin && python reset_models_db.py

seed-models-db:
	cd admin && python seed_models_db.py
