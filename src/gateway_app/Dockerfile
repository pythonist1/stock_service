FROM python:3.12-slim

WORKDIR /app

ENV PARENT_DIR=".."

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Копируем wait-for-it.sh в контейнер
COPY ./wait-for-it.sh /usr/local/bin/wait-for-it.sh
RUN chmod +x /usr/local/bin/wait-for-it.sh

EXPOSE 8000

# Используем wait-for-it.sh для ожидания доступности зависимостей перед запуском приложения
CMD ["/usr/local/bin/wait-for-it.sh", "redis:6379", "postgres:5432", "rabbitmq:5672", "--", "python", "app/main.py"]
