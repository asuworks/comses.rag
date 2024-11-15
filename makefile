
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
d:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

# kill develop services
kd:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml down


######################################
################## PROD ##############
######################################

# prod services
p:
	docker compose up -d

# kill prod services
kp:
	docker compose down

redeploy:
	git pull && docker compose up -d --force-recreate

rebuild:
	git pull && docker compose up -d --force-recreate --build