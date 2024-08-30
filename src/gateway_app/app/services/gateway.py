import uvicorn
from fastapi import FastAPI
from abstractions import AbstractService


class GatewayService(AbstractService):
    def __init__(self, app: FastAPI, host, port, name='HTTP Gateway'):
        super().__init__()
        self._app = app
        config = uvicorn.Config(app, host=host, port=port)
        self._server = uvicorn.Server(config)
        self._name = name

    async def start(self, loop):
        if not self._server.config.loaded:
            self._server.config.load()
        self._server.lifespan = self._server.config.lifespan_class(self._server.config)
        await self._server.startup()

    async def stop(self):
        await self._server.shutdown()
