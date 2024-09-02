import json
from datetime import datetime, timedelta

from .adapters import PoligonIoRequestClient, RedlockHandler, RabbitMqHandler
from .storage.repository import StocksRepository

from enum import Enum

class AggregationInterval(Enum):
    HOUR = "1h"
    FOUR_HOURS = "4h"
    DAY = "1d"
    THREE_DAYS = "3d"
    TEN_DAYS = "10d"


class TaskHandler:
    def __init__(self,
                 db_session,
                 redis_client,
                 config,
                 db_tables,
                 queue_handler: RabbitMqHandler,
                 redlock_handler: RedlockHandler):
        self._config = config
        self._redis_client = redis_client
        self._queue_handler = queue_handler
        self._redlock_handler = redlock_handler
        self._repository = StocksRepository(db_session, db_tables)
        self._poligon_service_client = PoligonIoRequestClient(self._config.API_KEY)

    def collect_stocks_information(self):
        results = self._poligon_service_client.get_stocks_information()
        if results:
            self._repository.save_stocks_information(results)

    def collect_actual_data(self):
        actual_data = []

        for stock_name in self._config.nasdaq_stocks:
            snapshot = self._poligon_service_client.get_stock_snapshot(stock_name)
            stock_entry = self._convert_to_stock_entry(stock_name, snapshot)
            actual_data.append(stock_entry)

        self._redis_client.set('actual_data', json.dumps(actual_data))

    def aggregate_data(self, stock_id, interval, user_id):
        lock = self._redlock_handler.acquire_lock(stock_id)
        if lock:
            try:
                message = dict()
                repository_result = self._repository.get_aggregation(stock_id, interval)
                if repository_result:
                    message = {
                        "user_id": user_id,
                        "aggregation_result": repository_result
                    }
                else:
                    stock_name = self._repository.get_stock_name_by_id(stock_id)
                    snapshot = self._poligon_service_client.get_stock_snapshot(stock_name)
                    aggregate_case = self._calculate_aggregate_case(
                        interval,
                        snapshot["last_trade"]["trade_time"]
                    )
                    service_result = self._poligon_service_client.get_aggregates(
                        ticker=stock_name,
                        sort="desc",
                        multiplier=aggregate_case["multiplier"],
                        timespan=aggregate_case["timespan"],
                        start_date=aggregate_case["start_date"],
                        end_date=aggregate_case["end_date"]
                    )
                    converted_data = self._convert_aggregate_results(service_result["results"])
                    message = {
                        "user_id": user_id,
                        "aggregation_result": converted_data
                    }
                self._queue_handler.publish_message(message)
            finally:
                self._redlock_handler.unlock(lock)
                print("Lock released!")

    def collect_stock_data_example(self):
        stock = self._repository.get_stock_by_name("AAPL")

        start_date = int((datetime.now() - timedelta(days=10)).timestamp() * 1000)
        end_date = int(datetime.now().timestamp() * 1000)

        data = self._poligon_service_client.get_aggregates(
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

    def _calculate_aggregate_case(self, interval: AggregationInterval, end_timestamp: int):
        timespan = None
        multiplier = None
        start_date = None
        end_date = end_timestamp
        match interval:
            case "1h":
                time_delta = timedelta(hours=1)
                start_date = self._calculate_start_timestamp(end_timestamp, time_delta)
                timespan = 'minute'
                multiplier = 15
            case "4h":
                time_delta = timedelta(hours=4)
                start_date = self._calculate_start_timestamp(end_timestamp, time_delta)
                timespan = 'minute'
                multiplier = 15
            case "1d":
                time_delta = timedelta(days=1)
                start_date = self._calculate_start_timestamp(end_timestamp, time_delta)
                timespan = 'hour'
                multiplier = 1
            case "3d":
                time_delta = timedelta(days=3)
                start_date = self._calculate_start_timestamp(end_timestamp, time_delta)
                timespan = 'hour'
                multiplier = 1
            case "10d":
                time_delta = timedelta(days=10)
                start_date = self._calculate_start_timestamp(end_timestamp, time_delta)
                timespan = 'day'
                multiplier = 1
        return {
            "timespan": timespan,
            "multiplier": multiplier,
            "start_date": start_date,
            "end_date": end_date
        }

    @staticmethod
    def _calculate_start_timestamp(end_timestamp, delta):
        delta_milliseconds = delta.total_seconds() * 1000

        # Отнимаем интервал времени
        result_milliseconds = int(end_timestamp - delta_milliseconds)
        return result_milliseconds

    def _convert_aggregate_results(self, results):
        converted_data = []
        for result in results:
            converted_data.append({
                'start_timestamp': result['t'],  # Unix timestamp в миллисекундах
                'total_volume': result.get('v', 0),
                'opening_price': result.get('o', 0),
                'closing_price': result.get('c', 0),
                'max_highest_price': result.get('h', 0),
                'min_lowest_price': result.get('l', 0),
                'total_trades': result.get('n', 0)
            })

        return converted_data

    def _convert_to_stock_entry(self, stock_name, snapshot):
        stock_entry = {
            'ticker': stock_name,
            'queryCount': 1,
            'resultsCount': 1,
            'adjusted': True,
            'results': [{
                "v": snapshot["min"]["volume"],
                "vw": snapshot["min"]["volume_weighted_price"],
                "o": snapshot["min"]["open_price"],
                "c": snapshot["min"]["close_price"],
                "h": snapshot["min"]["high_price"],
                "l": snapshot["min"]["low_price"],
                "t": snapshot["min"]["start_time"],
                "n": None
            }],
            'status': 'OK',
            'request_id': None,
            'count': 1
        }
        return stock_entry
