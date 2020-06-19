import asyncio
import websockets

clients = set()
counter = 0

async def update():
    global counter
    while True:
        if clients:
            for c in clients:
                await c.send("{}".format(counter))

        await asyncio.sleep(1)
        counter += 1
        print(counter)


async def connect(websocket, path):
    clients.add(websocket)
    print("{} connected".format(websocket))
    try:
        await websocket.send("hello")
        for message in websocket:
            print(message)
    # except:
    #     pass
    finally:
        print("{} disconnected".format(websocket))
        clients.remove(websocket)


async def total():
    await asyncio.wait([update(), websockets.serve(connect, "localhost", 8765)])

asyncio.get_event_loop().run_until_complete(total())
# loop = asyncio.get_event_loop()
# loop.create_task(update())

# loop.run_until_complete(websockets.serve(connect, "localhost", 8765))

# loop.run_forever()