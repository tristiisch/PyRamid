COMPOSE_SERVICE					:=	pyramid
VENV_NAME						:=	.venv
DOCKER_COMPOSE_FILE_PREPROD		:=	docker-compose.preprod.yml
DOCKER_SERVICE_PREPROD			:=	pyramid_preprod_pyramid
DOCKER_CONTEXT_PREPROD			:=	cookie-pulsheberg

# ifeq ($(OS),Windows_NT)
# else
# endif

start:
	@docker compose up -d --remove-orphans

start-f:
	@docker compose up -d --remove-orphans --force-recreate

start-b:
	@docker compose up -d --remove-orphans --build

stop:
	@docker compose stop

down:
	@docker compose down

down-v:
	@docker compose down -v

config:
	@docker compose config

config-pp:
	@docker compose -f $(DOCKER_COMPOSE_FILE_PREPROD) config

logs:
	@docker compose logs -f -n 100

exec:
	@docker compose exec $(COMPOSE_SERVICE) sh

exec-pp:
	@scripts/docker_service_exec.sh $(DOCKER_SERVICE_PREPROD) $(DOCKER_CONTEXT_PREPROD)

env-setup:
	@python3 -m venv $(VENV_NAME)
	@make env
	@pip install -r requirements.txt

dev: start-f logs
