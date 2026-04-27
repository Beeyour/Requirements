FROM python:3.11-slim
WORKDIR /app

# System dependencies for SVG/PNG rendering (svglib + reportlab)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libcairo2-dev \
    libffi-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . ./backend

ENV PYTHONPATH=/app
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]