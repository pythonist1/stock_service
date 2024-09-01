import requests


class RequestAggregator:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = 'https://api.polygon.io/v2/aggs/ticker'

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
        url = f'{self.base_url}/{ticker}/range/{multiplier}/{timespan}/{start_date}/{end_date}'
        params = {
            'adjusted': str(adjusted).lower(),
            'sort': sort,
            'apiKey': self.api_key
        }

        response = requests.get(url, params=params)

        response.raise_for_status()  # Проверка на наличие ошибок в запросе

        return response.json()
