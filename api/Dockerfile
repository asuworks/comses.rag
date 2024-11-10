# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.11.10
FROM python:${PYTHON_VERSION}-slim as base

# Prevents Python from writing pyc files.
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr to avoid situations where
# the application crashes without emitting any logs due to buffering.
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Create a non-privileged user that the app will run under.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

# Install Poetry
ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.8.4
RUN pip install "poetry==$POETRY_VERSION"
ENV PATH="$POETRY_HOME/bin:$PATH"

# Configure Poetry to not create virtualenvs
ENV POETRY_VIRTUALENVS_CREATE=false

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install dependencies globally
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# Switch to the non-privileged user to run the application.
USER appuser

# Copy the source code into the container.
COPY . .

# Expose the port that the application listens on.
EXPOSE 8000

WORKDIR /app/api

# Run the application.
CMD ["poetry", "run", "uvicorn", "main:app", "--reload", "--host=0.0.0.0", "--port=8000"]