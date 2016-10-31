import websockets

from .common import WSIOCommon

__all__ = ["WSIOClient"]


class WSIOClient(WSIOCommon):
    def __init__(self, *args, **kwargs):
        super().__init__()
        self.transport_args = args, kwargs
        self.tasks = []

    async def close(self):
        self.cancel()
        if hasattr(self, "transport"):
            try:
                await self.transport.close()
            except ConnectionResetError:
                pass

    def cancel(self):
        for task in self.tasks:
            task.cancel()

    async def run(self):
        args, kwargs = self.transport_args
        async with websockets.connect(*args, **kwargs) as self.transport:
            await super().run()

    async def call_handler(self, handler, data):
        await handler(data)
