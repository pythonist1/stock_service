import json
from abstractions import AbstractActualDataManager
import random
import uuid
from datetime import datetime


def generate_random_stock_data():
    tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'ADBE', 'PYPL', 'INTC', 'CSCO', 'NFLX', 'QCOM',
               'AVGO', 'NOW', 'CRM', 'PANW', 'ZM', 'UBER', 'DOCU']
    stock_data = []

    for ticker in tickers:
        stock_entry = {
            'ticker': ticker,
            'queryCount': 1,
            'resultsCount': 1,
            'adjusted': True,
            'results': [{
                'v': round(random.uniform(1e6, 1e8)),  # Random volume
                'vw': round(random.uniform(50, 1000)),  # Random volume-weighted average price
                'o': round(random.uniform(50, 1000)),  # Random open price
                'c': round(random.uniform(50, 1000)),  # Random close price
                'h': round(random.uniform(50, 1000)),  # Random high price
                'l': round(random.uniform(50, 1000)),  # Random low price
                't': round(int(datetime.now().timestamp() * 1000)),  # Current timestamp in milliseconds
                'n': round(random.randint(10000, 1000000) ) # Random number of trades
            }],
            'status': 'OK',
            'request_id': str(uuid.uuid4()),  # Unique request ID
            'count': 1
        }
        stock_data.append(stock_entry)

    return {'demonstration_data': stock_data}

class ActualDataManager(AbstractActualDataManager):
    def __init__(self, redis_client):
        self._redis_client = redis_client

    async def get_actual_data(self):
        data = dict()
        json_data = await self._redis_client.get("actual_data")
        if json_data:
            actual_data = json.loads(json_data)
            data["actual_data"] = actual_data
        stock_data_example_json = await self._redis_client.get("stock_data_example")
        if stock_data_example_json:
            stock_data_example = json.loads(stock_data_example_json)
            data["stock_data_example"] = stock_data_example
        return data

    def get_demonstration_data(self):
        return generate_random_stock_data()

    async def stop(self):
        await self._redis_client.close()
