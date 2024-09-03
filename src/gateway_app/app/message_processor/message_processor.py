from abstractions import AbstractService
from .use_cases import MessageUseCases


class MessageProcessor:
    def __init__(self, use_cases: MessageUseCases):
        self._use_cases = use_cases

    def register_service_callback(self,
                                  service: AbstractService,
                                  process_callback_name: str = None,
                                  start_callback_name: str = None):
        if process_callback_name:
            process_callback = getattr(self._use_cases, process_callback_name)
            service.set_process_callback(process_callback)

        if start_callback_name:
            start_callback = getattr(self._use_cases, start_callback_name)
            service.set_start_callback(start_callback)

    async def stop(self):
        await self._use_cases.stop_adapters()
