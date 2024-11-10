
######################################
############## TEMPORAL ##############
######################################

# start temporal services
t:
	cd temporal-server && docker compose -f docker-compose-postgres.yml up -d

# kill temporal services
kt:
	cd temporal-server && docker compose -f docker-compose-postgres.yml down


######################################
################# DEV ################
######################################

# develop services
ds:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# kill develop services
kds:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down


######################################
################## PROD ##############
######################################

# prod services
ps:
	docker compose up -d

# kill prod services
kps:
	docker compose down

redeploy:
	git pull && docker compose up -d --force-recreate

rebuild:
	git pull && docker compose up -d --force-recreate --build