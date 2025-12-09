.PHONY: help build up down logs migrate shell test clean

help:
	@echo "Backend команды:"
	@echo "  make build     - Собрать контейнеры"
	@echo "  make up        - Запустить backend"
	@echo "  make down      - Остановить"
	@echo "  make logs      - Логи"
	@echo "  make migrate   - Применить миграции"
	@echo "  make shell     - Backend shell"
	@echo "  make test      - Тесты"
	@echo "  make clean     - Очистить все данные"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

logs:
	docker-compose logs -f backend celery-worker celery-beat

migrate:
	docker-compose exec backend alembic upgrade head

shell:
	docker-compose exec backend /bin/bash

test:
	docker-compose exec backend pytest

clean:
	docker-compose down -v
	rm -rf __pycache__
	rm -rf app/__pycache__
	find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete

restart:
	docker-compose restart

ps:
	docker-compose ps

backend-logs:
	docker-compose logs -f backend

celery-logs:
	docker-compose logs -f celery-worker celery-beat
