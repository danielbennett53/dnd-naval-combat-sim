import asyncio
import json
import websockets
from Ship import Sprinter, Galleon
from Obstacle import Obstacle

clients = set()

w = 1600
l = 800
mgn = 30
boundary = {
    "d": "M {},{} A {},{},{},{},{},{},{} L {},{} A {},{},{},{},{},{},{} Z".format(
        l/2 + mgn, mgn, l/2, l/2, 0, 0, 0, l/2 + mgn, mgn + l, w + mgn - l/2, mgn + l,
        l/2, l/2, 0, 0, 0, w + mgn - l/2, mgn),
    "stroke": "Black",
    "fill": "transparent",
    "stroke-width": 4,
}

ships = {
    "Green": Sprinter("Green", position=[150, 230], rotation=45, stroke="DarkGreen", fill="LightGreen", type="player", firing_range=[800]),
    "Blue": Sprinter("Blue", position=[100,430], rotation=90, stroke="DarkBlue", fill="LightBlue", type="player", firing_range=[100], firing_arc=[(-140, -40), (40, 140)]),
    "Violet": Sprinter("Violet", position=[150, 630], rotation=135, stroke="DarkViolet", fill="Violet", type="player", firing_range=[20], firing_arc=[(-30, 30)]),
    "Red": Galleon("Red", position=[1500, 430], rotation=180, stroke="Red", fill="Pink", type="enemy"),
}

ops = [
    { "position": [300, 430], "rx": 40, "ry": 60},
    { "position": [800, 130], "rx": 150, "ry": 20, "rotation": 0 },
    { "position": [650, 430], "rx": 40, "ry": 150, "rotation": 0 },
    { "position": [950, 430], "rx": 40, "ry": 150, "rotation": 0 },
    { "position": [800, 730], "rx": 150, "ry": 20, "rotation": 0 },
    { "position": [475, 600], "rx": 30, "ry": 60},
    { "position": [475, 260], "rx": 60, "ry": 30},
    { "position": [1185, 600], "rx": 50, "ry": 30},
    { "position": [1185, 260], "rx": 50, "ry": 80},
    { "position": [1360, 430], "rx": 40, "ry": 60},
]

obs = [Obstacle(**o) for o in ops]

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
            if not s.finished() and not s.name in disabled_ships:
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
                    out["status"][v.name] = {"ac": v.get_ac(), "speed": int(v.velocity), "dc": int(v.dc)}
                await c.send(json.dumps(out))
            # except:
            #     pass
            finally:
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
        i = 0
        for o in obs:
            out["paths"]["obs" + str(i)] = {**o.path}
            i += 1
        out["paths"]["boundary"] = {**boundary}
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
                ships[ship].velocity = 0
                ships[ship].plan = []
                ships[ship].paths[ship + ".plan"]["d"] = ""
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