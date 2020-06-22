import asyncio
import json
import websockets
from Ship import Sprinter, Galleon

clients = set()

player_ships = {
    "A": {'ship': Sprinter([200,200]), 'linecolor': "DarkGreen", 'fillcolor': 'LightGreen'},
    "B": {'ship': Sprinter([20,40]), 'linecolor': "DarkBlue", 'fillcolor': 'LightBlue'},
    "C": {'ship': Sprinter([20,75]), 'linecolor': "DarkCyan", 'fillcolor': 'LightCyan'},
    "D": {'ship': Sprinter([50,150]), 'linecolor': "Red", 'fillcolor': 'Pink'},
}

player_controls = {'type': 'modify-controls', 'controls': {}}

for s in player_ships.keys():
    player_controls['controls'][s] = {'thrust': 0, 'steer': 0, 'roll': 0}


async def update():
    while True:
        for c in clients:
            try:
                pass
            except:
                pass

        await asyncio.sleep(0.05)


async def syncInputs():
    await asyncio.wait([c.send(json.dumps(player_inputs)) for c in clients])
    for name, ship in player_ships.items():
        ship.set_motion(player_inputs['controls'][name]['thrust'], 
                        player_inputs['controls'][name]['steer'],
                        20)


async def connect(websocket, path):
    clients.add(websocket)
    try:
        out = {"type": "paths", "paths": {}}
        for v in player_ships.values():
            out["paths"] = {**out["paths"], **v["ship"].paths}
        await websocket.send(json.dumps(out))
        out = {"type": "create-controls", "controls": []}
        for v in player_ships.values():
            out["controls"].append({
                "name": v["ship"].name,
                "fill": v["ship"].fill,
                "stroke": v["ship"].stroke,
            })
        await websocket.send(json.dumps(out))

        async for message in websocket:
            msg = json.loads(message)
            parts = msg['id'].split('.')
            s = parts[0]
            c = parts[1]
            player_inputs['inputs'][s][c] = msg['value']
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