SERVICE := pyramid
VENV_NAME := .venv

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

logs:
	@docker compose logs -f -n 100

exec:
	@docker compose exec $(SERVICE) sh

env-setup:
	@python3 -m venv $(VENV_NAME)
	@make env
	@pip install -r requirements.txt

dev: start-f logs
