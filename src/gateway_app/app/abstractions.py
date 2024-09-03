from abc import ABC, abstractmethod
from typing import Callable


class AbstractService(ABC):
    def __init__(self):
        self._process_callback = None
        self._start_callback = None

    def set_process_callback(self, process_callback: Callable):
        self._process_callback = process_callback

    def set_start_callback(self, start_callback: Callable):
        self._start_callback = start_callback

    @abstractmethod
    async def start(self, loop):
        pass

    @abstractmethod
    async def stop(self):
        pass


class AbstractWorkerManager(ABC):
    @abstractmethod
    def aggregate_data(self, aggregation_params):
        pass

    @abstractmethod
    def collect_stocks(self):
        pass


class AbstractActualDataManager(ABC):
    @abstractmethod
    async def get_actual_data(self):
        pass

    @abstractmethod
    async def stop(self):
        pass


class AbstractUserRepository(ABC):
    @abstractmethod
    async def get_user_id(self, name: str):
        pass
