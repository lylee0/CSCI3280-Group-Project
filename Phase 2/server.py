import asyncio
import websockets
import json
import os

with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
    json_object = json.load(openfile)

#No one in the network initially
json_object["User"] = []

with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
    updatefile.write(json.dumps(json_object))

async def echo(websocket, path):
    async for message in websocket:
        message = message.split(",+++")

        if message[0] == "Get":
            with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
                json_object = json.load(openfile) 
            if message[1] not in json_object["User"]:      
                json_object["User"].append(message[1])
            print(json_object)
            with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
                updatefile.write(json.dumps(json_object))
            await websocket.send(json.dumps(json_object))

        if message[0] == "Update":
            with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
                json_object = json.load(openfile)       
            id = int(message[1])
            method = message[2]
            item = message[3]
            content = message[4]
            print(message)
            if id != -1:
                pos = json_object["chatRoom"].index([x for x in json_object["chatRoom"] if x["id"] == id][0])
            if item == "conv":
                content = message[4].split("&+&")
            if method == "add":
                json_object["chatRoom"][pos][item].append(content)
            elif method == "change":
                json_object["chatRoom"][pos][item] = content
            elif method == "remove" and id == -1:
                try:
                    json_object["User"].remove(content)
                except Exception as e:
                    print(e)
            elif method == "remove" and id != -1:
                try:
                    json_object["chatRoom"][pos]["pinnedBy"].remove(content)
                except Exception as e:
                    print(e)
            with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'w') as updatefile:
                updatefile.write(json.dumps(json_object))
            print(json_object)      
            try:
                await websocket.send(json.dumps(json_object))
            except Exception as e:
                print(e)
                await websocket.send("error")

        if message[0] == "NewRoom":
            with open(os.path.dirname(os.path.abspath(__file__)) + '\\data\\data.json', 'r') as openfile:
                json_object = json.load(openfile)
            id = int(message[1])
            if len([x for x in json_object["chatRoom"] if x["id"] == id]) != 0:
                id = id+1
            name = message[2]  
            user = message[3]
            json_object["chatRoom"].append({
                "id": id,
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

asyncio.get_event_loop().run_until_complete(websockets.serve(echo, 'localhost', 8765))
asyncio.get_event_loop().run_forever()