#!/usr/bin/env python

import asyncio
import logging

from aiowsio.server import WSIOServer


logger = logging.getLogger("websockets")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


server = WSIOServer("127.0.0.5", 8001)


@server.on("chat message")
async def on_chat_message(client, data):
    # broadcast chat message to all clients
    await server.emit("chat message", data)
    await client.emit("chat message", "your message was sent")

@server.on("sum")
async def on_sum(client, data):
    # assume that data is a list of ints
    # return sum
    return sum(data)


try:
    asyncio.get_event_loop().run_until_complete(server)
    asyncio.get_event_loop().run_forever()
except KeyboardInterrupt:
    pass
finally:
    asyncio.get_event_loop().run_until_complete(server.close())
    asyncio.get_event_loop().close()
