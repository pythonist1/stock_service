import pathlib
from pydantic_settings import BaseSettings


project_path = pathlib.Path(__file__).parent
env_path = str(project_path) + '/.env'


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
    rabbitmq_queue: str = 'test_queue'
    redis_password: str = ''
    rabbitmq_user: str = 'guest'
    rabbitmq_password: str = 'guest'
    parent_dir: str = '../../'
    nasdaq_stocks: list = [
                "AAPL",  # Apple Inc.
                "MSFT",  # Microsoft Corporation
                "GOOGL", # Alphabet Inc.
                "AMZN",  # Amazon.com, Inc.
                "NVDA",  # NVIDIA Corporation
                "META",  # Meta Platforms, Inc.
                "TSLA",  # Tesla, Inc.
                "ADBE",  # Adobe Inc.
                "PYPL",  # PayPal Holdings, Inc.
                "INTC",  # Intel Corporation
                "CSCO",  # Cisco Systems, Inc.
                "NFLX",  # Netflix, Inc.
                "QCOM",  # Qualcomm Incorporated
                "AVGO",  # Broadcom Inc.
                "NOW",   # ServiceNow, Inc.
                "CRM",   # Salesforce, Inc.
                "PANW",  # Palo Alto Networks, Inc.
                "ZM",    # Zoom Video Communications, Inc.
                "UBER",  # Uber Technologies, Inc.
                "DOCU"   # DocuSign, Inc.
            ]
    API_KEY: str = ""


config = Config(_env_file=env_path)
