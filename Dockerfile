FROM python:3.12-alpine3.20

WORKDIR /app

RUN python -m pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

COPY . /app

EXPOSE 8000

CMD poetry run alembic upgrade head && poetry run uvicorn main:app --host 0.0.0.0 --port 8000
