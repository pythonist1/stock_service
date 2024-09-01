import time
from redlock import Redlock


class LockNotAcquiredError(Exception):
    pass


class RedlockHandler:
    def __init__(self, redis_nodes):
        self._dlm = Redlock(redis_nodes)

    def acquire_lock(self, resource, ttl=10, max_retries=5, retry_delay=0.2):
        """
        Попытаться захватить блокировку для ресурса с повторными попытками.

        :param resource: Ресурс, для которого требуется блокировка
        :param ttl: Время жизни блокировки в секундах
        :param max_retries: Максимальное количество повторных попыток
        :param retry_delay: Задержка между попытками в секундах
        :return: Захваченная блокировка или None, если не удалось захватить
        """
        retries = 0
        while retries < max_retries:
            lock = self._dlm.lock(resource, ttl)
            if lock:
                return lock
            else:
                retries += 1

                # print(f"Failed to acquire lock. Retrying in {retry_delay} seconds...")

                time.sleep(retry_delay)

        # print("Failed to acquire lock after several retries.")

        raise LockNotAcquiredError()

        return None

    def unlock(self, lock):
        self._dlm.unlock(lock)
