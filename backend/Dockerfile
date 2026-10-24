FROM python:3.12-slim

# Prevent Python from buffering stdout/stderr and creating .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Install system dependencies needed for compiling C-extensions like psycopg2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, reliable dependency installation
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Copy dependencies first to leverage Docker layer caching
COPY requirements.txt .

# Install dependencies into system Python inside the container
RUN uv pip install --system --no-cache -r requirements.txt

# Copy application code and Alembic configurations
COPY . .

# Expose FastAPI default port
EXPOSE 8000

# Run FastAPI with uvicorn (0.0.0.0 allows traffic from outside the container / AWS ALB)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
