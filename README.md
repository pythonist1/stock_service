## Gateway App

Gateway App представляет собой сервис, включающий три ключевых асинхронных задачи, которые работают в рамках одного event loop:

1. **Веб-сервер (Uvicorn с FastAPI)**: Обрабатывает входящие HTTP-запросы и предоставляет API для взаимодействия с другими частями системы. Поддерживает WebSocket для двустороннего общения в реальном времени, что позволяет клиентам получать обновления без необходимости повторных запросов.
2. **Актуализатор данных**: Асинхронная задача, которая периодически проверяет данные в Redis и обновляет фронтенд, чтобы поддерживать актуальность показателей.
3. **RabbitMQ Consumer**: Отвечает за получение сообщений из RabbitMQ и их распределение между пользователями, обеспечивая обработку и доставку данных в реальном времени.

Эти задачи функционируют в рамках одного event loop, что позволяет эффективно управлять асинхронными операциями и ресурсами.

## Task Service

**Функционал**: Выполнение фоновых задач и распределённых вычислений.

**Компоненты**:
- **Celery Worker**: Обрабатывает задачи, поставленные в очередь.
- **RabbitMQ**: Управляет очередями задач, распределяет их между worker-ами и отправляет сообщения в Gateway App для пользователей.
- **Redis**: Хранит актуальные данные и результаты выполнения задач.
- **Celery Beat (опционально)**: Периодически собирает данные по установленному расписанию из сторонних сервисов.


URL для доступа: После запуска приложения, интерфейс будет доступен по адресу http://localhost:8080.

# Запуск проекта с Docker Compose

## Шаги для запуска

1. **Убедитесь, что Docker и Docker Compose установлены на вашем компьютере.**
   - [Скачать Docker](https://docs.docker.com/get-docker/)
   - [Скачать Docker Compose](https://docs.docker.com/compose/install/)

2. **Клонируйте репозиторий проекта (если еще не сделано):**

   ```bash
   git clone https://github.com/pythonist1/stock_service.git

3 **Запустите Docker Compose для создания и запуска контейнеров:**

    ```bash
        docker-compose up --build