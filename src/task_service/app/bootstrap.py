import os
import sys
import pika

from celery import Celery
from .settings import config
import redis

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from .request_aggregator.request_aggregator import RequestAggregator
from .handler import TaskHandler

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), config.parent_dir))
sys.path.insert(0, project_root)

from database_schema.models import create_tables
from database_schema import models as db_tables


def bootstrap_celery_app():
    RABBITMQ_URL = f'pyamqp://{config.rabbitmq_user}:{config.rabbitmq_password}@{config.rabbitmq_host}'

    app = Celery(
        'tasks'
    )

    app.conf.update(
        broker_url=RABBITMQ_URL
    )
    return app

def bootstrap_db_session():
    username = config.postgres_user
    password = config.postgres_password
    host = config.postgres_server
    port = config.postgres_port
    db_name = config.postgres_db

    DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{db_name}"
    engine = create_engine(DATABASE_URL)
    create_tables(engine)

    db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    return db_session


def bootstrap_handler(db_session):
    redis_client = redis.Redis(
        host=config.redis_host,
        port=config.redis_port,
        decode_responses=True
    )
    rabbit_channel = bootstrap_rabbit_connection()
    handler = TaskHandler(db_session, redis_client, config, db_tables, rabbit_channel)
    return handler


def bootstrap_rabbit_connection():
    rabbit_url = f"amqp://{config.rabbitmq_user}:{config.rabbitmq_password}@{config.rabbitmq_host}:{config.rabbitmq_port}/"

    params = pika.URLParameters(rabbit_url)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    queue_name = 'test_queue'
    channel.queue_declare(queue=queue_name, durable=False, auto_delete=True)  # Убедитесь, что параметры совпадают

    return channel
