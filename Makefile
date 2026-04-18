# Define phony targets to avoid conflicts with files of the same name
.PHONY: help up down build test logs tree db-revision db-upgrade

# Display help message by default
.DEFAULT_GOAL := help


help: ## 📌 Show this help message
	@echo "Usage: make [command]"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

up: ## 🚀 Start all docker containers in background
	sudo docker compose up -d

build: ## 🏗️ Rebuild docker images and start containers
	sudo docker compose up -d --build

down: ## 🛑 Stop and remove all docker containers
	sudo docker compose down

test: ## 🧪 Run backend tests using Pytest
	sudo docker compose exec -e PYTHONPATH=/app backend pytest -v

logs: ## 📡 Follow real-time backend logs
	sudo docker compose logs -f backend

tree: ## 📁 Display a clean project structure tree
	tree -I 'node_modules|venv|__pycache__|.git|.pytest_cache|.alembic'

treeBackend: ## Display a clean project structure tree fo backend
	tree -I 'node_modules|frontend|venv|__pycache__|.git|.pytest_cache'

db-revision: ## 📝 Generate a new database migration (Alembic)
	sudo docker compose exec backend alembic revision --autogenerate -m "Update DB schema"

db-upgrade: ## ⚙️ Apply pending database migrations to PostgreSQL
	sudo docker compose exec backend alembic upgrade head

prod-up:
	sudo docker compose -f docker-compose.yml up -d --build