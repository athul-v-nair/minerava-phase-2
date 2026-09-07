.PHONY: up down logs api web test lint migrate

up:
	docker-compose up --build

down:
	docker-compose down

logs:
	docker-compose logs -f

migrate:
	cd api && alembic upgrade head

test:
	cd api && pytest -q

lint:
	ruff check api
	ruff check web 2>/dev/null || true

api:
	cd api && uvicorn app.main:app --reload --port 8000

web:
	cd web && npm run dev
