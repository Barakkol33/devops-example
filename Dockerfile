# The recipe for the game's image - in three stages.

# 1. base: Python, the libraries the game needs, and the game's code
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY main.py board.py ./
COPY static/ static/

# 2. test: base + the test tools and the tests - the pipeline runs this one: docker run <image>
FROM base AS test
COPY requirements-dev.txt pyproject.toml ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY tests/ tests/
CMD ["python", "-m", "pytest", "-q"]

# 3. the game itself - what players get (the last stage is the default)
FROM base AS app
ARG VERSION=dev
ARG COLOR=#8250df
ENV VERSION=$VERSION COLOR=$COLOR HOST=0.0.0.0
EXPOSE 8000
CMD ["python", "main.py"]
