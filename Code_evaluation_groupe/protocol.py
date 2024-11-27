import asyncio
import websockets
import json    
import time

MASTER_ADRESSE = "ws://robotpi-15.enst.fr:9000"
# MASTER_ADRESSE = "ws://localhost:9000"
ID = -1


async def open_connection(id: int)->websockets.WebSocketClientProtocol:
    """
    :param id: identifiant de connexion du robot. (ex: 11 pour robotpi-11)
    :return: Une classe websocket qui permet de communiquer.
    """
    global ID
    ID = id
    websocket = await websockets.connect(MASTER_ADRESSE)
    await websocket.send(str(id))
    return websocket


async def close_connection(websocket:websockets.WebSocketClientProtocol):
    """
    Ferme la connexion avec le serveur.
    """
    await websocket.close()


async def can_go(websocket:websockets.WebSocketClientProtocol, etape:int, balise:int)->bool:
    """
    :param websocket: La clé de connection au "master"
    :param etape: La phase dans laquelle on est
    :param balise: Balise ou la voiture est localisée.
    :return: True si on peut partir pour la prochaine balise. False sinon.
    """
    rapport = json.dumps({"id" : ID, "balise":balise, "etape":etape})                                    #transformation en json de l'id
    await websocket.send(rapport)
    masterrobot_m = await websocket.recv()
    masterrobot = json.loads(masterrobot_m)
    return masterrobot["robots"][str(ID)]["go"]


async def get_ordre_balise(websocket:websockets.WebSocketClientProtocol):
    # Fonction a appeler au tout début. 
    # Le client commence par envoyer un signal a master. Il commence dans la phase 0.
    rapport = json.dumps({"id" : ID, "balise":None, "etape":0})                                    #transformation en json de l'id
    await websocket.send(rapport)
    masterrobot_m = await websocket.recv()
    masterrobot = json.loads(masterrobot_m)
    
    return masterrobot["balises"]
    ...


async def send_signal(websocket:websockets.WebSocketClientProtocol, etape:int, balise:int=None):
    """
    :param websocket: La clé de connection au "master"
    :param etape: La phase dans laquelle on est
    :param balise: Balise ou la voiture est localisée.
    """
    rapport = json.dumps({"id" : ID, "balise":balise, "etape":etape})                                    #transformation en json de l'id
    await websocket.send(rapport)
    
