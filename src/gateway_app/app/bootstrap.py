import os
import sys
import time
import asyncio
import aio_pika
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine
from celery import Celery
from redis import asyncio as aioredis

from services import GatewayService, MessageConsumerService, DataSyncService
from endpoints.api import router
from websocket_manager import WebsocketManager
from settings import config
from authorization import AuthHandler, UserRepository
from adapters import ActualDataManager, CeleryWorkerManager
from message_processor import MessageProcessor, MessageUseCases


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), config.parent_dir))
sys.path.insert(0, project_root)

from database_schema.models import create_tables
from database_schema import models as db_tables


async def process_message(
    message: aio_pika.abc.AbstractIncomingMessage,
) -> None:
    async with message.process():
        print(message.body)
        await asyncio.sleep(1)


def bootstrap_database_engine():
    username = config.postgres_user
    password = config.postgres_password
    host = config.postgres_server
    port = config.postgres_port
    db_name = config.postgres_db

    postgres_url = f"postgresql+asyncpg://{username}:{password}@{host}:{port}/{db_name}"

    async_engine = create_async_engine(postgres_url)

    from sqlalchemy import create_engine
    DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(DATABASE_URL)
    create_tables(engine)

    return async_engine


def bootstrap_gateway_service():
    app = FastAPI(docs_url='/api/docs')
    app.include_router(router)
    service = GatewayService(app, '0.0.0.0', 8000)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return service, app

def bootstrap_message_consumer_service():
    message_queue_service = MessageConsumerService(
        f"amqp://{config.rabbitmq_user}:{config.rabbitmq_password}@{config.rabbitmq_host}:{config.rabbitmq_port}/",
        config.rabbitmq_queue,
    )

    return message_queue_service


def bootstrap_websocket_manager():
    websocket_manager = WebsocketManager()
    return websocket_manager


def bootstrap_auth_handler(engine):
    repository = UserRepository(engine, db_tables)
    auth_handler = AuthHandler(repository)

    return auth_handler


def bootstrap_celery_worker_manager():
    RABBITMQ_URL = f'pyamqp://{config.rabbitmq_user}:{config.rabbitmq_password}@{config.rabbitmq_host}'

    app = Celery(
        'gateway_app',
        broker=RABBITMQ_URL
    )

    worker_manager = CeleryWorkerManager(celery_app=app)
    return worker_manager


def bootstrap_actual_data_manager():
    redis_client = aioredis.from_url(
        url=f'redis://{config.redis_host}:{config.redis_port}',
        max_connections=1
    )

    actual_data_manager = ActualDataManager(redis_client)
    return actual_data_manager


def bootstrap_message_processor(websocket_manager, worker_manager, actual_data_manager):
    use_cases = MessageUseCases(websocket_manager, worker_manager, actual_data_manager)
    message_processor = MessageProcessor(use_cases)
    return message_processor


def bootstrap_data_sync_service():
    actual_data_sender = DataSyncService()
    return actual_data_sender
