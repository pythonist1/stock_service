from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from datetime import timedelta


class StocksRepository:
    def __init__(self, db_session, db_tables):
        self._db_session = db_session
        self._db_tables = db_tables

    def get_stock_by_name(self, name):
        stock = self._db_session.query(self._db_tables.Stock).filter_by(name=name).first()
        return stock

    def get_stock_company_by_id(self, stock_id):
        stock_company = self._db_session.query(self._db_tables.StockCompanyInfo).filter_by(stock_id=stock_id).first()
        return stock_company

    def get_stock_data_example(self):
        result = (self._db_session.query(self._db_tables.PriceAndTrade)).first()
        stock = (self._db_session.query(self._db_tables.Stock).filter_by(id=result.stock_id)).first()
        stock_company = self.get_stock_company_by_id(result.stock_id)
        return {
            "stock_id": stock.id,
            "name": stock.name,
            "company_name": stock_company.company_name
        }

    def save_stock(self, data):
        for ticker_info in data:
            ticker = ticker_info['ticker']
            company_name = ticker_info.get('name', 'N/A')
            market_type = ticker_info.get('market', 'N/A')

            stock = self._db_tables.Stock(name=ticker)
            self._db_session.add(stock)

            try:
                self._db_session.commit()
            except IntegrityError:
                self._db_session.rollback()

            stock = self.get_stock_by_name(ticker)

            company_info = self._db_tables.StockCompanyInfo(
                stock_id=stock.id,
                company_name=company_name,
                market_type=market_type
            )
            self._db_session.add(company_info)

            try:
                self._db_session.commit()
            except IntegrityError:
                self._db_session.rollback()

    def save_stock_data(self, stock_id, data):
        for result in data:
            record = self._db_tables.PriceAndTrade(
                stock_id=stock_id,
                volume=result.get('v', 0),
                opening_price=result.get('o', 0),
                closing_price=result.get('c', 0),
                highest_price=result.get('h', 0),
                lowest_price=result.get('l', 0),
                number_of_trades=result.get('n', 0),
                timespan='minute',
                start_timestamp=datetime.fromtimestamp(result.get('t', 0) / 1000),
                timeinterval='15m'
            )
            print("record", record)
            self._db_session.add(record)
        self._db_session.commit()

    def get_aggregation(self, stock_id, interval):
        # Получаем последнюю запись
        latest_record_query = text("""
            SELECT start_timestamp
            FROM prices_and_trades
            WHERE stock_id = :stock_id
            ORDER BY start_timestamp DESC
            LIMIT 1
        """)
        latest_record = self._db_session.execute(latest_record_query, {'stock_id': stock_id}).fetchone()

        if not latest_record:
            return "No records found."

        end_time = latest_record[0]

        if interval == '1h':
            start_time = end_time - timedelta(hours=1)
            group_by = "date_trunc('minute', start_timestamp)"
            group_interval = 15 * 60  # 15 минут
        elif interval == '4h':
            start_time = end_time - timedelta(hours=4)
            group_by = "date_trunc('minute', start_timestamp)"
            group_interval = 15 * 60  # 15 минут
        elif interval == '1d':
            start_time = end_time - timedelta(days=1)
            group_by = "date_trunc('hour', start_timestamp)"
            group_interval = None
        elif interval == '3d':
            start_time = end_time - timedelta(days=3)
            group_by = "date_trunc('hour', start_timestamp)"
            group_interval = None
        elif interval == '10d':
            start_time = end_time - timedelta(days=10)
            group_by = "date_trunc('day', start_timestamp)"
            group_interval = None
        else:
            return "Invalid interval."

        if group_interval:
            sql_query = f"""
                WITH base_data AS (
                    SELECT
                        date_trunc('minute', start_timestamp) - interval '1 minute' * (extract(minute from start_timestamp) % {group_interval} / {group_interval} * {group_interval}) AS interval_start,
                        start_timestamp,
                        opening_price,
                        closing_price,
                        volume,
                        highest_price,
                        lowest_price,
                        number_of_trades,
                        ROW_NUMBER() OVER (PARTITION BY date_trunc('minute', start_timestamp) - interval '1 minute' * (extract(minute from start_timestamp) % {group_interval} / {group_interval} * {group_interval}) ORDER BY start_timestamp ASC) AS rn_first,
                        ROW_NUMBER() OVER (PARTITION BY date_trunc('minute', start_timestamp) - interval '1 minute' * (extract(minute from start_timestamp) % {group_interval} / {group_interval} * {group_interval}) ORDER BY start_timestamp DESC) AS rn_last
                    FROM prices_and_trades
                    WHERE stock_id = :stock_id
                      AND start_timestamp >= :start_time
                      AND start_timestamp <= :end_time
                ),
                aggregated_data AS (
                    SELECT
                        interval_start,
                        MAX(CASE WHEN rn_first = 1 THEN start_timestamp END) AS start_timestamp,
                        SUM(volume) AS total_volume,
                        MAX(CASE WHEN rn_first = 1 THEN opening_price END) AS opening_price,
                        MAX(CASE WHEN rn_last = 1 THEN closing_price END) AS closing_price,
                        MAX(highest_price) AS max_highest_price,
                        MIN(lowest_price) AS min_lowest_price,
                        SUM(number_of_trades) AS total_trades
                    FROM base_data
                    GROUP BY interval_start
                )
                SELECT json_agg(json_build_object(
                    'interval_start', interval_start,
                    'start_timestamp', start_timestamp,
                    'total_volume', total_volume,
                    'opening_price', opening_price,
                    'closing_price', closing_price,
                    'max_highest_price', max_highest_price,
                    'min_lowest_price', min_lowest_price,
                    'total_trades', total_trades
                )) AS data
                FROM aggregated_data
            """
        else:
            sql_query = f"""
                WITH base_data AS (
                    SELECT
                        {group_by} AS interval_start,
                        start_timestamp,
                        opening_price,
                        closing_price,
                        volume,
                        highest_price,
                        lowest_price,
                        number_of_trades,
                        ROW_NUMBER() OVER (PARTITION BY {group_by} ORDER BY start_timestamp ASC) AS rn_first,
                        ROW_NUMBER() OVER (PARTITION BY {group_by} ORDER BY start_timestamp DESC) AS rn_last
                    FROM prices_and_trades
                    WHERE stock_id = :stock_id
                      AND start_timestamp >= :start_time
                      AND start_timestamp <= :end_time
                ),
                aggregated_data AS (
                    SELECT
                        interval_start,
                        MAX(CASE WHEN rn_first = 1 THEN start_timestamp END) AS start_timestamp,
                        SUM(volume) AS total_volume,
                        MAX(CASE WHEN rn_first = 1 THEN opening_price END) AS opening_price,
                        MAX(CASE WHEN rn_last = 1 THEN closing_price END) AS closing_price,
                        MAX(highest_price) AS max_highest_price,
                        MIN(lowest_price) AS min_lowest_price,
                        SUM(number_of_trades) AS total_trades
                    FROM base_data
                    GROUP BY interval_start
                )
                SELECT json_agg(json_build_object(
                    'interval_start', interval_start,
                    'start_timestamp', start_timestamp,
                    'total_volume', total_volume,
                    'opening_price', opening_price,
                    'closing_price', closing_price,
                    'max_highest_price', max_highest_price,
                    'min_lowest_price', min_lowest_price,
                    'total_trades', total_trades
                )) AS data
                FROM aggregated_data
            """

        results = self._db_session.execute(text(sql_query), {'stock_id': stock_id, 'start_time': start_time, 'end_time': end_time}).fetchone()

        return results[0]
