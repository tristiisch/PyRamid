COMPOSE_SERVICE					:=	discord
VENV_NAME						:=	.venv
DOCKER_COMPOSE_FILE_DEV			:=	./.docker/docker-compose.dev.yml
DOCKER_COMPOSE_FILE_PREPROD		:=	./.docker/docker-compose.preprod.yml
DOCKER_SERVICE_PREPROD			:=	pyramid_preprod_pyramid
DOCKER_CONTEXT_PREPROD			:=	cookie-pulsheberg

# Basics

all: up-b logs

build:
	@docker compose build --pull

build-c:
	@docker compose build --pull

up:
	@docker compose up -d --remove-orphans

up-f:
	@docker compose up -d --remove-orphans --force-recreate

up-b:
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

# Other envs

exec-pp:
	@scripts/docker_service_exec.sh $(DOCKER_SERVICE_PREPROD) $(DOCKER_CONTEXT_PREPROD)

dev:
	@docker compose -f $(DOCKER_COMPOSE_FILE_DEV) up -d --remove-orphans --pull always --force-recreate

tests:
	@docker build -f ./.docker/Dockerfile --target tests -t pyramid:tests .
	@mkdir -p ./coverage && chmod 777 ./coverage
	@docker run --rm --env-file ./.env -v ./coverage:/app/coverage -it pyramid:tests

healthcheck:
	@docker compose exec $(COMPOSE_SERVICE) sh -c "python ./src/startup_cli.py health"

healthcheck-dev:
	@docker compose exec $(COMPOSE_SERVICE) sh -c "python -Xfrozen_modules=off ./src/startup_cli_dev.py health"

# Pythons scripts

img-b:
	@python scripts/environnement.py --build

img-ba:
	@python scripts/environnement.py --build-archs

img-c:
	@python scripts/environnement.py --images-purge

clean:
	@python scripts/environnement.py --clean

# Other

.PHONY: build tests logs
