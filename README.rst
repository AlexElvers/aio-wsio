``aio-wsio`` is a simple event-based library similar to Socket.IO. It includes a server part in Python and a client part in Python and JavaScript. ``aio-wsio`` uses WebSockets as transport protocol. The Python modules are using ``asyncio`` as event loop.

Features
--------
* event listener
* broadcast messages
* acknowledgements

  * containing data
  * acknowledgement callbacks

Example
-------

Server
~~~~~~

.. code:: python

    server = WSIOServer("localhost", 8001)

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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(server)
    loop.run_forever()

Client
~~~~~~

.. code:: python

    client = WSIOClient("ws://localhost:8001")

    @client.on("chat message")
    async def on_chat_message(data):
        print("message:", data)

    @client.on("connect")
    async def on_connect(data):
        await client.emit("chat message", "Hi, all!")
        numbers = [1, 5, 2]
        sum = await client.emit("sum", numbers)
        print("the sum of", numbers, "is", sum)

    asyncio.get_event_loop().run_until_complete(client)

.. code:: javascript

    var socket = new io('ws://127.0.0.5:8001/');
    socket.on('chat message', function (data, ack) {
        console.log('message:', data);
        ack();
    });
    socket.on('connect', function () {
        socket.emit('chat message', 'Hello from browser!');
        var numbers = [4, 4, 2];
        socket.emit('sum', numbers, function (sum) {
            console.log('the sum of', numbers, 'is', sum);
        });
    });
