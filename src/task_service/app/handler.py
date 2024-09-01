import json
import requests
import pika
from datetime import datetime, timedelta
from amqp import Channel
from kombu import Connection, Exchange, Queue, Producer

from .request_aggregator import RequestAggregator
from .storage.repository import StocksRepository

from enum import Enum

class AggregationInterval(Enum):
    HOUR = "1h"
    FOUR_HOURS = "4h"
    DAY = "1d"
    THREE_DAYS = "3d"
    TEN_DAYS = "10d"


class TaskHandler:
    def __init__(self, db_session, redis_client, config, db_tables, rabbit_channel: Producer):
        self._config = config
        self._redis_client = redis_client
        self._rabbit_channel = rabbit_channel
        self._repository = StocksRepository(db_session, db_tables)
        self._request_aggregator = RequestAggregator(self._config.API_KEY)

    def collect_stock(self):
        api_key = self._config.API_KEY
        url = f'https://api.polygon.io/v3/reference/tickers?market=stocks&active=true&apiKey={api_key}'
        response = requests.get(url)
        data = response.json()

        if data.get('results'):
            self._repository.save_stock(data['results'])

    def collect_stock_data_example(self):
        stock = self._repository.get_stock_by_name("AAPL")

        start_date = int((datetime.now() - timedelta(days=10)).timestamp() * 1000)
        end_date = int(datetime.now().timestamp() * 1000)

        data = self._request_aggregator.get_aggregates(
            ticker=stock.name,
            multiplier=15,
            timespan='minute',
            start_date=start_date,
            end_date=end_date
        )

        if data.get('results'):
            self._repository.save_stock_data(stock.id, data.get('results'))

        stock_data_example = self._repository.get_stock_data_example("AAPL")
        self._redis_client.set('stock_data_example', json.dumps(stock_data_example))


    def collect_actual_data(self):
        actual_data = []

        for stock_name in self._config.nasdaq_stocks:
            data = self._request_aggregator.get_aggregates(
                ticker=stock_name,
                multiplier=1,
                timespan="day",
                start_date=(datetime.now() - timedelta(days=3)).strftime('%Y-%m-%d'),
                end_date=datetime.now().strftime('%Y-%m-%d'),
                adjusted=True,
                sort="desc"
            )
            actual_data.append(data)

        self._redis_client.set('actual_data', json.dumps(actual_data))


    def aggregate_data(self, stock_id, interval, user_id):
        result = self._repository.get_aggregation(stock_id, interval)
        message = {
            "user_id": user_id,
            "aggregation_result": result
        }
        self._publish_message(message)

    def _publish_message(self, message):
        self._rabbit_channel.basic_publish(
            exchange='',
            routing_key=self._config.rabbitmq_queue,
            body=json.dumps(message),
        )
