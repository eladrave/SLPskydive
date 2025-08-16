SHELL := /bin/bash

export COMPOSE_PROJECT_NAME=slpskydive

.PHONY: up down logs migrate seed backend-test frontend-test e2e fmt lint

up:
	docker-compose up --build -d

down:
	docker-compose down -v

logs:
	docker-compose logs -f --tail=200

migrate:
	docker-compose run --rm backend alembic -c app/backend/db/migrations/alembic.ini upgrade head || true

seed:
	docker-compose run --rm backend python -m app.backend.db.seed || true

backend-test:
	docker-compose run --rm backend pytest -q

frontend-test:
	docker-compose run --rm frontend pnpm test

e2e:
	docker-compose run --rm frontend pnpm exec playwright test

fmt:
	docker-compose run --rm backend bash -lc "black app && isort app" || true
	docker-compose run --rm frontend pnpm exec prettier --write . || true

lint:
	docker-compose run --rm backend flake8 app || true
	docker-compose run --rm frontend pnpm run lint || true
