from celery import Celery
from abstractions import AbstractWorkerManager


class CeleryWorkerManager(AbstractWorkerManager):
    def __init__(self, celery_app: Celery):
        self._celery_app = celery_app

    def aggregate_data(self, aggregation_params: dict):
        self._celery_app.send_task(
            'tasks.aggregate_data',
            kwargs={
                "stock_id": aggregation_params["stock_id"],
                "interval": aggregation_params["interval"],
                "user_id": aggregation_params["user_id"]
            }
        )

    def collect_stocks(self):
        self._celery_app.send_task(
            'tasks.collect_stocks'
        )
        self._celery_app.send_task(
            'tasks.collect_stock_data_example',
            kwargs={"data": {}}
        )
