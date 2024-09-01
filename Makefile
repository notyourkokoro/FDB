database_name  = main
DOCKER_COMP    = docker compose -f docker-compose.yml
EXEC	       = $(DOCKER_COMP) exec
UV			   = $(EXEC)
DEFAULT_IMAGES = fdb-auth_service

up:
	@$(DOCKER_COMP) up --detach --wait

down:
	@$(DOCKER_COMP) down --remove-orphans

full-clean:
	@$(DOCKER_COMP) down --volumes
	@docker rmi $(DEFAULT_IMAGES) || exit 0;

# ---------- Database ----------
# revision:
# 	@$(UV) run alembic revision --autogenerate -m "Initial User table"
# head:
# 	alembic upgrade head