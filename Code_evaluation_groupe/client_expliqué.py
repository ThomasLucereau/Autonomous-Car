import asyncio
import websockets
import json    
import time
import protocol


async def test():
    
    websocket = await protocol.open_connection("a")
    #attend que la connection soit établie pour passer à la suite

    ordre = await protocol.get_ordre_balise(websocket)
    #attend que le master envoie l'ordre des balises et récupère le dictionnaire des balises dans la variable ordre
    
    while True:
        # PHASE : 0
        # BALISE : 0

        go = await protocol.can_go(websocket, phase = 0, balise = None)
        #attend que le master envoie le dictionnaire de commandes et récupère la valeur de go qui lui correspond

        if go:
            print("On va chercher la balise")
            await protocol.close_connection(websocket)
            return

        else:
            print("On fait rien")
            time.sleep(2)

asyncio.get_event_loop().run_until_complete(test())