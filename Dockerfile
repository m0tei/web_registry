FROM python:3.9-slim-bullseye

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP run.py
ENV DEBUG False

WORKDIR /app

ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

USER appuser
EXPOSE 5000

COPY . .

# gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "-w", "1", "--access-logfile", "-", "--log-level", "debug", "--capture-output", "--enable-stdio-inheritance", "-k", "eventlet", "run:app"]

