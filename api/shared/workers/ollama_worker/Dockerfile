FROM python:3.12-slim-bookworm as builder

ARG ENVIRONMENT

ENV ENVIRONMENT=${ENVIRONMENT} \
    PYTHONFAULTHANDLER=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=random \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    # Poetry's configuration:
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR='/var/cache/pypoetry' \
    POETRY_HOME='/usr/local' \
    PYTHONPATH="/app"

RUN pip3 install poetry==1.8.4

WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN touch README.md

# Project initialization:
RUN poetry config virtualenvs.in-project true && \
    poetry install $(test "$ENVIRONMENT" == production && echo "--only=main") --no-interaction --no-ansi

# The runtime image, used to just run the code provided its virtual environment
FROM python:3.12-slim-bookworm as runtime

ENV PATH="/app/.venv/bin:$PATH"    
ENV PYTHONPATH="/app"

COPY --from=builder /app/.venv /app/.venv

WORKDIR /app

COPY . .

# Generate Prisma client
# RUN python -m prisma generate --schema=/app/shared/databases/gfs_db/gfs-db-schema.prisma

CMD [ "python", "/app/shared/workers/ollama_worker/run.py" ]