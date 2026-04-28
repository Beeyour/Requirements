# Project Management Commands


## 🛠️ Development Commands
This project is managed using `Docker` and a `Makefile`. To see all available commands, run:
```bash
make help

### 🐳 Docker Compose (Infrastructure)
Used for containerization and environment isolation.
- **Start Services:** `sudo docker compose up -d`
- **Rebuild & Start:** `sudo docker compose up -d --build`
- **Stop Services:** `sudo docker compose down`
- **Backend Logs:** `sudo docker compose logs -f backend`

### 🧪 Pytest (Testing Framework)
Used for running automated unit and integration tests.
- **Run Tests:** `sudo docker compose exec -e PYTHONPATH=/app backend pytest -v`

### 🌳 Tree (Filesystem Utility)
Used for visualizing the project structure.
- **Project Tree:** `tree -I 'node_modules|venv|__pycache__|.git|.pytest_cache'`

### ⚡ Uvicorn (ASGI Server)
The engine running the FastAPI application inside Docker.
- **Status Check:** Included in Docker logs.

## UML Storage Migration Note
After deploying the SSoT UML storage changes, new UML diagram tables are auto-created by `Base.metadata.create_all(engine)` on backend startup.

Legacy tables are no longer referenced by ORM models and should be dropped manually in PostgreSQL:


