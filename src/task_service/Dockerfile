FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Копируем wait-for-it.sh в контейнер
COPY ./wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

# Запускаем wait-for-it.sh и затем Celery
CMD ["/usr/local/bin/wait-for-it.sh", "redis:6379", "postgres:5432", "rabbitmq:5672", "--", "celery", "-A", "tasks", "worker", "--loglevel=info"]