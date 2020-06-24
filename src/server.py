import asyncio
import json
import websockets
from Ship import Sprinter, Galleon

clients = set()

player_ships = {
    "Green": Sprinter("Green", position=[200, 200], stroke="DarkGreen", fill="LightGreen"),
    "Blue": Sprinter("Blue", position=[20,40], stroke="DarkBlue", fill="LightBlue"),
    "Violet": Sprinter("Violet", position=[400, 50], stroke="DarkViolet", fill="Violet"),
}

enemy_ships = {
    "Red": Galleon("Red", position=[500, 500], rotation=180, stroke="Red", fill="Pink"),
}

all_ships = {**player_ships, **enemy_ships}

controls = {'type': 'modify-controls', 'controls': {}}

for s in all_ships.keys():
    controls['controls'][s] = {'thrust': 0, 'steer': 0, 'roll': 0}

in_progress = False


async def syncInputs():
    global clients
    await asyncio.wait([c.send(json.dumps(controls)) for c in clients])
    for name, ship in all_ships.items():
        ship.set_motion(controls['controls'][name]['thrust'],
                        controls['controls'][name]['steer'])


async def update():
    global in_progress, all_ships, clients
    while True:
        for s in all_ships.values():
            if not s.finished():
                in_progress = True
                s.update()
        if all([s.finished for s in all_ships.values()]) and in_progress:
            in_progress = False
            for s in all_ships.keys():
                controls['controls'][s] = {'thrust': 0, 'steer': 0, 'roll': 0}
        temp_clients = set(clients)
        for c in temp_clients:
            try:
                out = {"type": "state", "paths": {}, "status": {}}
                for v in all_ships.values():
                    out["paths"] = {**out["paths"], **v.paths}
                    out["status"][v.name] = {"ac": v.get_ac(), "speed": int(v.velocity)}
                await c.send(json.dumps(out))
            except:
                pass

        await asyncio.sleep(0.05)


async def connect(websocket, path):
    global clients
    clients.add(websocket)
    try:
        out = {"type": "create-controls", "enemies": [], "players": []}
        for v in player_ships.values():
            out["players"].append({
                "name": v.name,
                "fill": v.fill,
                "stroke": v.stroke,
            })
        for v in enemy_ships.values():
            out["enemies"].append({
                "name": v.name,
                "fill": v.fill,
                "stroke": v.stroke,
            })
        await websocket.send(json.dumps(out))
        out = {"type": "state", "paths": {}, "status": {}}
        for v in all_ships.values():
            out["paths"] = {**out["paths"], **v.paths}
            out["status"][v.name] = {"ac": v.get_ac(), "speed": int(v.velocity)}

        await websocket.send(json.dumps(out))
        await syncInputs()

        async for message in websocket:
            msg = json.loads(message)
            if msg['type'] == 'go':
                for name, ship in player_ships.items():
                    ship.start_movement(controls['controls'][name]['roll'])
                for name, ship in enemy_ships.items():
                    ship.start_movement(controls['controls'][name]['roll'])
            else:
                parts = msg['id'].split('.')
                ship = parts[0]
                control = parts[1]
                if msg['type'] == 'player':
                    if player_ships[ship].finished():
                        controls['controls'][ship][control] = msg['value']
                        await syncInputs()
                else:
                    if enemy_ships[ship].finished():
                        controls['controls'][ship][control] = msg['value']
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