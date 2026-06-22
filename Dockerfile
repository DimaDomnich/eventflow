FROM python:3.12-slim AS base

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .


FROM base AS development

CMD ["flask", "--app", "run", "run", "--host=0.0.0.0", "--debug"]


FROM base AS production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "run:app"]