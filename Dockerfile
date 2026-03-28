FROM python:3.12-slim

WORKDIR /app

COPY app.py .
COPY static/ static/
COPY blog/ blog/

RUN mkdir -p drops logs ops

EXPOSE 5060

CMD ["python3", "app.py"]
