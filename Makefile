run:
	sudo docker compose up -d

build:
	sudo docker compose up -d --build

test:
	sudo docker compose exec -e PYTHONPATH=/app backend pytest -v

tree:
	tree -I 'node_modules|venv|__pycache__|.git|.pytest_cache'