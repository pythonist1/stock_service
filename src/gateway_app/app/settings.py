from pydantic_settings import BaseSettings


class Config(BaseSettings):
    redis_host: str = 'localhost'
    redis_port: int = 6379
    postgres_user: str = ''
    postgres_password: str = ''
    postgres_server: str = 'localhost'
    postgres_port: int = 5432
    postgres_db: str = ''
    rabbitmq_host: str = '127.0.0.1'
    rabbitmq_port: int = 5672
    rabbitmq_queue: str = ""
    parent_dir: str = '../../'
    redis_password: str = ''
    rabbitmq_user: str = 'guest'
    rabbitmq_password: str = 'guest'

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


config = Config()
