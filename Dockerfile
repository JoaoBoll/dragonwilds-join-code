FROM python:3.13-alpine

RUN addgroup -S app && adduser -S -D -H -u 10001 -G app app

WORKDIR /app

COPY --chown=app:app app.py ./
COPY --chown=app:app web ./web

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    JOIN_CODE_HOST=0.0.0.0 \
    JOIN_CODE_PORT=8787 \
    JOIN_CODE_LOG_FILE=/logs/dragonwilds.log

USER app

EXPOSE 8787

CMD ["python", "app.py"]
