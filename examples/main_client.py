#!/usr/bin/env python

import asyncio
import logging

from aiowsio.client import WSIOClient


logger = logging.getLogger("websockets")
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


client = WSIOClient("ws://127.0.0.5:8001")


@client.on("chat message")
async def on_chat_message(data):
    print("message:", data)

@client.on("connect")
async def on_connect(data):
    await client.emit("chat message", "Hi, all!")
    numbers = [1, 5, 2]
    sum = await client.emit("sum", numbers)
    print("the sum of", numbers, "is", sum)


try:
    asyncio.get_event_loop().run_until_complete(client)
except KeyboardInterrupt:
    pass
finally:
    try:
        asyncio.get_event_loop().run_until_complete(client.close())
        asyncio.get_event_loop().close()
    except KeyboardInterrupt:
        pass
