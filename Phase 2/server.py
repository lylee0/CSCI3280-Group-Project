import asyncio
import websockets
import json
import os
import socket
import nest_asyncio

nest_asyncio.apply()

CONNECTIONS = []
otherServer = []

with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'r') as openfile:
    json_object = json.load(openfile)

#No one in the network and voice room initially
json_object["User"] = []
json_object["VoiceRoom"] = {}

with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'w') as updatefile:
    updatefile.write(json.dumps(json_object))

async def updateServer(uri, content):
        async with websockets.connect(uri, max_size=2**30) as websocket:
            await websocket.send("Forward,+++" + content)

async def echo(websocket, path):
    global CONNECTIONS
    websocket.max_size = 2**30
    async for message in websocket:
        if type(message) == bytes:
            websockets.broadcast(CONNECTIONS, message=message)
        else:
            global otherServer

            if message=="Listener":
                print("add connection, id: " + str(websocket.id))
                CONNECTIONS.append(websocket)
            
            if message=="LostConnection":
                print("lost connection, id: " + str(websocket.id))
                CONNECTIONS.remove(websocket)
                        
            message999 = message
            message = message.split(",+++")
            
            if message[0] != "Read" and message[0]!= "Forward" and message[0] != "Listener":
                for x in otherServer:
                    asyncio.get_event_loop().run_until_complete(updateServer('ws://'+ x +':8765', message999))

            if message[0] == "Forward":
                message.pop(0)

            if message[0] == "Get":
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'r') as openfile:
                    json_object = json.load(openfile) 
                if message[1] not in json_object["User"]:      
                    json_object["User"].append(message[1])
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))
                await websocket.send(json.dumps(json_object))

            if message[0] == "Connect":
                for x in range(len(message)):
                    if x != 0:
                        otherServer.append(message[x])

            if message[0] == "Update":
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'r') as openfile:
                    json_object = json.load(openfile)       
                idTEMP = int(message[1])
                method = message[2]
                item = message[3]
                content = message[4]
                if idTEMP != -1:
                    pos = json_object["chatRoom"].index([x for x in json_object["chatRoom"] if x["id"] == idTEMP][0])
                if item == "conv":
                    content = message[4].split("&+&")
                if method == "add":
                    json_object["chatRoom"][pos][item].append(content)
                elif method == "change":
                    json_object["chatRoom"][pos][item] = content
                elif method == "remove" and idTEMP == -1:
                    try:
                        json_object["User"].remove(content)
                    except Exception as e:
                        print(e)
                elif method == "remove" and idTEMP != -1:
                    try:
                        json_object["chatRoom"][pos]["pinnedBy"].remove(content)
                    except Exception as e:
                        print(e)
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))  
                try:
                    await websocket.send(json.dumps(json_object))
                except Exception as e:
                    print(e)
                    await websocket.send("error")

            if message[0] == "NewRoom":
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'r') as openfile:
                    json_object = json.load(openfile)
                idTEMP = int(message[1])
                if len([x for x in json_object["chatRoom"] if x["id"] == idTEMP]) != 0:
                    idTEMP = idTEMP+1
                name = message[2]  
                user = message[3]
                json_object["chatRoom"].append({
                    "id": idTEMP,
                    "name" : name,
                    "lCT" : "N/A",
                    "lM" : "No message yet...",
                    "pinnedBy" : [],
                    "conv" : [],
                    "parti" : [user]
                })
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))
                await websocket.send(json.dumps(json_object))
            
            if message[0] == "Read":
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'r') as openfile:
                    json_object = json.load(openfile)
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))
                await websocket.send(json.dumps(json_object))
            
            if message[0] == "VoiceAdd":
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'r') as openfile:
                    json_object = json.load(openfile)
                room = message[1]
                username = message[2]
                if room not in json_object["VoiceRoom"].keys():
                    json_object["VoiceRoom"][room] = [username]
                else:
                    json_object["VoiceRoom"][room].append(username)
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))

            if message[0] == "VoiceRemove":
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'r') as openfile:
                    json_object = json.load(openfile)
                room = message[1]
                username = message[2]
                if room not in json_object["VoiceRoom"].keys():
                    continue
                else:
                    json_object["VoiceRoom"][room].remove(username)
                with open(os.path.dirname(os.path.abspath(__file__)) + '/data/data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))


asyncio.get_event_loop().run_until_complete(websockets.serve(echo, socket.gethostbyname(socket.gethostname()), 8765, ping_interval=1))
asyncio.get_event_loop().run_forever() 