import requests
from datetime import datetime


def convert_unix_timestamp_to_datetime(timestamp):
    return datetime.fromtimestamp(timestamp / 1e9)


def nanoseconds_to_milliseconds(nanoseconds):
    milliseconds = int(nanoseconds / 1000000)
    return milliseconds


class PoligonIoRequestClient:
    def __init__(self, api_key):
        self._api_key = api_key
        self._base_url = 'https://api.polygon.io'

    def get_aggregates(self, ticker, multiplier, timespan, start_date, end_date, adjusted=True, sort='asc'):
        """
        Запрашивает агрегированные данные по акции.

        :param ticker: Тикер акции (например, 'AAPL').
        :param multiplier: Множитель интервала (например, 1).
        :param timespan: Временной интервал (например, 'day').
        :param start_date: Начальная дата интервала (в формате 'YYYY-MM-DD').
        :param end_date: Конечная дата интервала (в формате 'YYYY-MM-DD').
        :param adjusted: Применять коррекции по дроблениям акций.
        :param sort: Порядок сортировки данных (по умолчанию 'asc' - по возрастанию).
        :return: Ответ от API в формате JSON.
        """
        url = f'{self._base_url}/v2/aggs/ticker/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}'
        params = {
            'adjusted': str(adjusted).lower(),
            'sort': sort,
            'apiKey': self._api_key
        }

        response = requests.get(url, params=params)

        response.raise_for_status()  # Проверка на наличие ошибок в запросе

        return response.json()

    def get_stocks_information(self):
        api_key = self._api_key
        url = f'{self._base_url}/v3/reference/tickers?market=stocks&active=true&apiKey={api_key}'
        response = requests.get(url)
        data = response.json()

        if results := data.get('results'):
            return results

    def get_stock_snapshot(self, ticker):
        url = f"{self._base_url}/v2/snapshot/locale/us/markets/stocks/tickers/{ticker}"
        params = {
            'apiKey': self._api_key
        }

        response = requests.get(url, params=params)

        if response.status_code == 200:
            return self._convert_snapshot_data(response.json())
        else:
            response.raise_for_status()

    @staticmethod
    def _convert_snapshot_data(data):
        ticker_data = data['ticker']

        # Преобразование данных
        result = {
            'ticker': ticker_data['ticker'],
            'todays_change': ticker_data['todaysChange'],
            'todays_change_perc': ticker_data['todaysChangePerc'],
            'updated': ticker_data['updated'],
            'day': {
                'open_price': ticker_data['day']['o'],
                'high_price': ticker_data['day']['h'],
                'low_price': ticker_data['day']['l'],
                'close_price': ticker_data['day']['c'],
                'volume': ticker_data['day']['v'],
                'volume_weighted_price': ticker_data['day']['vw']
            },
            'last_quote': {
                'ask_price': ticker_data['lastQuote']['P'],
                'ask_size': ticker_data['lastQuote']['S'],
                'bid_price': ticker_data['lastQuote']['p'],
                'bid_size': ticker_data['lastQuote']['s'],
                # 'quote_time': convert_unix_timestamp_to_datetime(ticker_data['lastQuote']['t'])
            },
            'last_trade': {
                'trade_id': ticker_data['lastTrade']['i'],
                'trade_price': ticker_data['lastTrade']['p'],
                'trade_size': ticker_data['lastTrade']['s'],
                'trade_time': nanoseconds_to_milliseconds(int(ticker_data['lastTrade']['t'])),
                'exchange_id': ticker_data['lastTrade']['x']
            },
            'min': {
                'accumulated_volume': ticker_data['min']['av'],
                'start_time': nanoseconds_to_milliseconds(int(ticker_data['min']['t'])),
                'open_price': ticker_data['min']['o'],
                'high_price': ticker_data['min']['h'],
                'low_price': ticker_data['min']['l'],
                'close_price': ticker_data['min']['c'],
                'volume': ticker_data['min']['v'],
                'volume_weighted_price': ticker_data['min']['vw']
            },
            'prev_day': {
                'open_price': ticker_data['prevDay']['o'],
                'high_price': ticker_data['prevDay']['h'],
                'low_price': ticker_data['prevDay']['l'],
                'close_price': ticker_data['prevDay']['c'],
                'volume': ticker_data['prevDay']['v'],
                'volume_weighted_price': ticker_data['prevDay']['vw']
            }
        }

        return result
