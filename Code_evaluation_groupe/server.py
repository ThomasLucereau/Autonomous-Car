import websockets
import asyncio
import json

ordre_balises_example = {
        0: 1,
        1: -2,
        2: 2,
        3: -3,
        4: 3,
        5: -1,
        10: 0,
}

MASTERROBOT = {"robots" : {
    11 : {"etape": 0, "go": False}, 
    12 : {"etape": 0, "go": False}, 
    13 : {"etape": 0, "go": False}, 
    14 : {"etape": 0, "go": False}, 
    15 : {"etape": 0, "go": False}, 
}, "balises" : ordre_balises_example}

ORDRE_ROBOTS = [14]
I_ROBOT = 0 # indexe du robot dans la liste précédente


async def handler(websocket):
    global I_ROBOT # Le robot qui a le droit d'avancer
    global MASTERROBOT

    id = int(await websocket.recv())

    print(f"le robot {id} est connecte")

    if id == 15:
        balises_m = await websocket.recv()
        MASTERROBOT["balises"] = json.loads(balises_m)
    else:
        while MASTERROBOT["balises"] == None: 
            await asyncio.sleep(1)
        MASTERROBOT_m = json.dumps(MASTERROBOT)
        await websocket.send(MASTERROBOT_m)

    while True:
        robot_to_master_m = await websocket.recv()
        robot_to_master = json.loads(robot_to_master_m)
        etape = robot_to_master["etape"]
        MASTERROBOT["robots"][id]["etape"] = etape
        print(f"robot {id} dans l'etape {etape}")

        if ORDRE_ROBOTS[I_ROBOT] == id:
            if robot_to_master["etape"] == 8:
                # le robot est arrivé
                I_ROBOT += 1
                if I_ROBOT == 5:
                    await websocket.close()
                    return

            MASTERROBOT["robots"][id]["go"] = True

        else:
            MASTERROBOT["robots"][id]["go"] = False
        
        MASTERROBOT_m = json.dumps(MASTERROBOT)
        await websocket.send(MASTERROBOT_m)


    
    return None


start_server = websockets.serve(handler, "0.0.0.0", 9000, ping_timeout = 600)

asyncio.get_event_loop().run_until_complete(start_server)

asyncio.get_event_loop().run_forever()


