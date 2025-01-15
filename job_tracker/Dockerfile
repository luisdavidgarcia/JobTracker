FROM python:3.11-slim-bullseye

WORKDIR /app

COPY ../project.toml ../poetry.lock ./

RUN pip install poetry
RUN poetry install --no-root

COPY . .

CMD ["python", "main.py"]