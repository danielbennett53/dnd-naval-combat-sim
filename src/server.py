import asyncio
import json
import websockets
from Ship import Sprinter, Galleon

clients = set()

player_ships = {
    "A": Sprinter("A", position=[200, 200], stroke="DarkGreen", fill="LightGreen"),
    "B": Sprinter("B", position=[20,40], stroke="DarkBlue", fill="LightBlue"),
}

player_controls = {'type': 'modify-controls', 'controls': {}}

for s in player_ships.keys():
    player_controls['controls'][s] = {'thrust': 0, 'steer': 0, 'roll': 0}


async def update():
    while True:
        for s in player_ships.values():
            if not s.finished():
                s.update()
        for c in clients:
            try:
                out = {"type": "paths", "paths": {}}
                for v in player_ships.values():
                    out["paths"] = {**out["paths"], **v.paths}
                await c.send(json.dumps(out))
            except:
                pass

        await asyncio.sleep(0.05)


async def syncInputs():
    global player_controls, clients
    await asyncio.wait([c.send(json.dumps(player_controls)) for c in clients])
    for name, ship in player_ships.items():
        ship.set_motion(player_controls['controls'][name]['thrust'],
                        player_controls['controls'][name]['steer'])


async def connect(websocket, path):
    global player_controls
    clients.add(websocket)
    try:
        out = {"type": "paths", "paths": {}}
        for v in player_ships.values():
            out["paths"] = {**out["paths"], **v.paths}
        await websocket.send(json.dumps(out))
        out = {"type": "create-controls", "controls": []}
        for v in player_ships.values():
            out["controls"].append({
                "name": v.name,
                "fill": v.fill,
                "stroke": v.stroke,
            })
        await websocket.send(json.dumps(out))
        await syncInputs()

        async for message in websocket:
            msg = json.loads(message)
            if msg['type'] == 'go':
                for ship in player_ships.values():
                    ship.start_movement(20)
            else:
                parts = msg['id'].split('.')
                ship = parts[0]
                control = parts[1]
                player_controls['controls'][ship][control] = msg['value']
                await syncInputs()
    # except:
    #     pass
    finally:
        print("{} disconnected".format(websocket))
        clients.remove(websocket)


# async def total():
#     await asyncio.wait([update(), websockets.serve(connect, "localhost", 8765)])

# asyncio.get_event_loop().run_until_complete(total())
loop = asyncio.get_event_loop()
loop.create_task(update())

loop.run_until_complete(websockets.serve(connect, None, 8080))

loop.run_forever()