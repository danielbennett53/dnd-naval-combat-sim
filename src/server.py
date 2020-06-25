import asyncio
import json
import websockets
from Ship import Sprinter, Galleon

clients = set()

ships = {
    "Green": Sprinter("Green", position=[200, 200], stroke="DarkGreen", fill="LightGreen", type="player"),
    "Blue": Sprinter("Blue", position=[20,40], stroke="DarkBlue", fill="LightBlue", type="player"),
    "Violet": Sprinter("Violet", position=[400, 50], stroke="DarkViolet", fill="Violet", type="player"),
    "Red": Galleon("Red", position=[500, 500], rotation=180, stroke="Red", fill="Pink", type="enemy"),
}

controls = {'type': 'modify-controls', 'controls': {}}
disabled_ships = set()

for s in ships.keys():
    controls['controls'][s] = {'thrust': 0, 'steer': 0, 'roll': 0}

in_progress = False


async def syncInputs():
    global clients
    await asyncio.wait([c.send(json.dumps(controls)) for c in clients])
    for name, ship in ships.items():
        ship.set_motion(controls['controls'][name]['thrust'],
                        controls['controls'][name]['steer'])


async def update():
    global in_progress, ships, clients
    while True:
        for s in ships.values():
            if not s.finished():
                in_progress = True
                s.update()
        if all([s.finished for s in ships.values()]) and in_progress:
            in_progress = False
            for s in ships.keys():
                controls['controls'][s] = {'thrust': 0, 'steer': 0, 'roll': 0}
        temp_clients = set(clients)
        for c in temp_clients:
            try:
                out = {"type": "state", "paths": {}, "status": {}}
                for v in ships.values():
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
        out = {"type": "create-controls", "ships": []}
        for v in ships.values():
            out["ships"].append({
                "name": v.name,
                "fill": v.fill,
                "stroke": v.stroke,
                "type": v.type,
            })
        await websocket.send(json.dumps(out))
        out = {"type": "state", "paths": {}, "status": {}}
        for v in ships.values():
            out["paths"] = {**out["paths"], **v.paths}
            out["status"][v.name] = {"ac": v.get_ac(), "speed": int(v.velocity)}

        await websocket.send(json.dumps(out))
        await syncInputs()

        async for message in websocket:
            msg = json.loads(message)
            if msg['type'] == 'go':
                for name, ship in ships.items():
                    ship.start_movement(controls['controls'][name]['roll'])
            elif msg['type'] == 'override':
                ship = msg['ship']
                if msg['pos'][0] != '':
                    ships[ship].position[0] = float(msg['pos'][0])
                if msg['pos'][1] != '':
                    ships[ship].position[1] = float(msg['pos'][1])
                if msg['rot'] != '':
                    ships[ship].rotation = float(msg['rot'])
                if bool(msg['enabled']) and ship in disabled_ships:
                    disabled_ships.remove(ship)
                elif not bool(msg['enabled']):
                    disabled_ships.add(ship)
                ships[ship].update()
            elif msg['type'] == 'control':
                if ships[msg['ship']].finished() and msg['ship'] not in disabled_ships:
                    controls['controls'][msg['ship']][msg['control']] = msg['value']
                    await syncInputs()
            else:
                pass
    # except:
    #     pass
    finally:
        print("{} disconnected".format(websocket))
        clients.remove(websocket)


loop = asyncio.get_event_loop()
loop.create_task(update())

loop.run_until_complete(websockets.serve(connect, None, 8080))

loop.run_forever()