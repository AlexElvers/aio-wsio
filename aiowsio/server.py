import asyncio
import functools

import websockets

from .common import WSIOCommon

__all__ = ["WSIOServer"]


class WSIOServer:
    def __init__(self, *args, **kwargs):
        self.transport_args = args, kwargs
        self.clients = []
        self.handlers = {}
        self.tasks = []

    def extra_headers(self, path, raw_request_headers):
        """
        Allow origin.
        """
        response_headers = {}
        for key, value in raw_request_headers:
            if key.lower() == "origin":
                response_headers["Access-Control-Allow-Origin"] = value
        return response_headers

    def __await__(self):
        return self.run().__await__()

    __iter__ = __await__

    async def close(self):
        self.cancel()
        if hasattr(self, "transport"):
            self.transport.close()
            await self.transport.wait_closed()

    def cancel(self):
        for task in self.tasks:
            task.cancel()

    async def run(self):
        args, kwargs = self.transport_args
        transport = websockets.serve(
            functools.partial(WSIOHandler, server=self),
            *args, extra_headers=self.extra_headers, **kwargs)
        self.transport = await transport

    def on(self, event, callback=None):
        def register(callback):
            print("add handler", event)
            self.handlers[event] = callback
            return callback
        if callback is not None:
            register(callback)
            return callback
        return register

    async def emit(self, event, data):
        if self.clients:
            await asyncio.wait([c.emit(event, data) for c in self.clients])


class WSIOHandler(WSIOCommon):
    def __init__(self, transport, path, server):
        super().__init__()
        self.transport = transport
        self.path = path
        self.server = server

    async def run(self):
        self.server.clients.append(self)
        try:
            await super().run()
        finally:
            self.server.clients.remove(self)

    def get_handler(self, event):
        try:
            return self.handlers[event]
        except KeyError:
            return self.server.handlers.get(event)

    @property
    def tasks(self):
        return self.server.tasks
