import asyncio
import websockets
import json
import os
import socket
import pyaudio

CONNECTIONS = []

with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
    json_object = json.load(openfile)

#No one in the network and voice room initially
json_object["User"] = []
json_object["VoiceRoom"] = {}

with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
    updatefile.write(json.dumps(json_object))

async def echo(websocket, path):
    global CONNECTIONS
    CONNECTIONS.append(websocket) 
    async for message in websocket:
        if type(message) == bytes:
            if websocket in CONNECTIONS: 
                CONNECTIONS.remove(websocket)
            websockets.broadcast(CONNECTIONS, message=message)
        else:    
            message = message.split(",+++")

            if message[0] == "Get":
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
                    json_object = json.load(openfile) 
                if message[1] not in json_object["User"]:      
                    json_object["User"].append(message[1])
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))
                await websocket.send(json.dumps(json_object))

            if message[0] == "Update":
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
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
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))  
                try:
                    await websocket.send(json.dumps(json_object))
                except Exception as e:
                    print(e)
                    await websocket.send("error")

            if message[0] == "NewRoom":
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
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
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))
                await websocket.send(json.dumps(json_object))
            
            if message[0] == "Read":
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
                    json_object = json.load(openfile)
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))
                await websocket.send(json.dumps(json_object))
            
            if message[0] == "VoiceAdd":
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
                    json_object = json.load(openfile)
                room = message[1]
                username = message[2]
                if room not in json_object["VoiceRoom"].keys():
                    json_object["VoiceRoom"][room] = [username]
                else:
                    json_object["VoiceRoom"][room].append(username)
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))

            if message[0] == "VoiceRemove":
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
                    json_object = json.load(openfile)
                room = message[1]
                username = message[2]
                if room not in json_object["VoiceRoom"].keys():
                    continue
                else:
                    json_object["VoiceRoom"][room].remove(username)
                with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
                    updatefile.write(json.dumps(json_object))
            
            CONNECTIONS.remove(websocket)


asyncio.get_event_loop().run_until_complete(websockets.serve(echo, "218.250.208.235", 8765))
asyncio.get_event_loop().run_forever() 