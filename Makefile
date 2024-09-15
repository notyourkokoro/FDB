database_name  = main
DOCKER_COMP    = docker compose -f docker-compose.yml
EXEC	       = $(DOCKER_COMP) exec
CORE		   = @$(EXEC) core uv
DEFAULT_IMAGES = fdb-auth_service fdb-storage_service fdb-data_service core

# ---------- Docker containers ----------
up:
	@$(DOCKER_COMP) up --detach --wait

down:
	@$(DOCKER_COMP) down --remove-orphans

full-clean:
	@$(DOCKER_COMP) down --volumes
	@docker rmi $(DEFAULT_IMAGES) || exit 0;

# ---------- Database ----------
migrations:
	@$(CORE) run alembic revision --autogenerate -m "$(comment)"

migrate:
	@$(CORE) run alembic upgrade head

downgrade:
	@$(CORE) run alembic downgrade -1
