import asyncio
import json

import websockets

__all__ = ["WSIOCommon"]


class WSIOCommon:
    def __init__(self):
        self.ack_futures = {}
        self.handlers = {}
        self.next_id = 0

    def __await__(self):
        return self.run().__await__()

    __iter__ = __await__

    async def run(self):
        try:
            fut = asyncio.ensure_future(self.handle_event(None, "connect"))
            self.tasks.append(fut)
            fut.add_done_callback(self.tasks.remove)
            while True:
                print("waiting")
                message_str = await self.transport.recv()
                print(message_str)
                fut = asyncio.ensure_future(self.handle_message(message_str))
                self.tasks.append(fut)
                fut.add_done_callback(self.tasks.remove)
        except (websockets.ConnectionClosed, asyncio.CancelledError):
            print("closing")
            fut = asyncio.ensure_future(self.handle_event(None, "disconnect"))
            self.tasks.append(fut)
            fut.add_done_callback(self.tasks.remove)

    async def handle_message(self, message_str):
        try:
            message = json.loads(message_str)
        except json.JSONDecodeError as e:
            print("cannot parse message", e)
            return
        message_type = message.get("type")
        message_id = message.get("id")
        event = message.get("event")
        data = message.get("data")
        if message_type == "EVENT":
            await self.handle_event(message_id, event, data)
        elif message_type == "ACK":
            if not self.ack_futures[message_id].cancelled():
                self.ack_futures[message_id].set_result(data)
            del self.ack_futures[message_id]
        else:
            print("unknown message type", message_type)

    def get_handler(self, event):
        return self.handlers.get(event)

    async def call_handler(self, handler, data):
        return await handler(self, data)

    async def handle_event(self, message_id, event, data=None):
        handler = self.get_handler(event)
        if handler is None:
            print("no handler for", event)
            return
        print("call", event, "handler")
        result = await self.call_handler(handler, data)
        if message_id is not None:
            await self.send_ack(message_id, result)

    async def send_message(self, message):
        message_str = json.dumps(message)
        await self.transport.send(message_str)

    async def send_ack(self, message_id, data):
        message = dict(type="ACK", id=message_id)
        if data is not None:
            message["data"] = data
        try:
            await self.send_message(message)
        except websockets.ConnectionClosed:
            pass

    async def emit(self, event, data):
        print("emit", event, data)
        message_id = self.next_id
        self.next_id += 1
        message = dict(type="EVENT", id=message_id, event=event)
        if data is not None:
            message["data"] = data
        self.ack_futures[message_id] = asyncio.Future()
        try:
            await self.send_message(message)
            return await self.ack_futures[message_id]
        except websockets.ConnectionClosed:
            self.ack_futures[message_id].cancel()

    def on(self, event, callback=None):
        def register(callback):
            print("add handler", event)
            self.handlers[event] = callback
            return callback
        if callback is not None:
            register(callback)
            return callback
        return register
