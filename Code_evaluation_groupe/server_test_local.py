import websockets
import asyncio
import json


ordre_balises_example = {
        0: 1,
        1: 3,
        2: -2,
        3: -1,
        4: -3,
        5: 2,
        10: 0,
}

MASTERROBOT = {"robots" : {
    11 : {"etape": 0, "go": False}, 
    12 : {"etape": 0, "go": False}, 
    13 : {"etape": 0, "go": False}, 
    14 : {"etape": 0, "go": False}, 
    15 : {"etape": 0, "go": False}, 
}, "balises" : ordre_balises_example}

CAN_GO = False


async def handler(websocket):
    global MASTERROBOT
    global CAN_GO

    id = int(await websocket.recv())
    print(f"je suis le robot numéro {id}")

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
        balise = robot_to_master["balise"]
        MASTERROBOT["robots"][id]["etape"] = etape

        if balise is not None:
            print(f"robot vient de valider {balise}")

        print(f"robot à l'etape {etape}")

        if etape == 8:
            await websocket.close()
            return

        if etape % 2 == 0:
            # le robot attend l'ordre de départ
            if CAN_GO:
                MASTERROBOT["robots"][id]["go"] = True
                # CAN_GO sera mis à True dans la fonction `read_terminal_input`
                CAN_GO = False

            else:
                MASTERROBOT["robots"][id]["go"] = False


        MASTERROBOT_m = json.dumps(MASTERROBOT)
        await websocket.send(MASTERROBOT_m)


    
    return None


async def read_terminal_input():
    global CAN_GO
    while True:
        input("taper entrer pour dire au robot de continuer")
        CAN_GO = True


start_server = websockets.serve(handler, "0.0.0.0", 9000, ping_timeout = 600)

async def main():
    await asyncio.gather(
        start_server,
        read_terminal_input()
    )

asyncio.run(main())


