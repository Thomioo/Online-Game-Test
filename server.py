import uvicorn, random, json
from fastapi import FastAPI

app = FastAPI()

uuids = set()
players = []

class Player:
    def __init__(self, name):
        self.name = name
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.pos = (10, 200)
        ruuid = random.randint(0, 2^64)
        while ruuid in uuids:
            ruuid = random.randint(0, 2^64)
        self.uuid = ruuid

    def updateLocation(self, x, y):
        self.pos = (x, y)

    def returnData(self):
        r = str(self.color[0])
        g = str(self.color[1])
        b = str(self.color[2])
        return r + "-" + g + "-" + b + ";" + str(self.uuid)
    
    def getLocationData(self):
        d = dict()
        d["uuid"] = self.uuid
        d["pos"]["x"] = self.pos[0]
        d["pos"]["y"] = self.pos[1]
        d["name"] = self.name
        d["color"] = self.color
        return d
    
@app.get("/")
def f():
    return players, uuids

@app.get("/connect")
def f(name: str):
    p = Player(name)
    data = p.returnData()
    players.append(p)
    uuids.add(p.uuid)
    return data

@app.get("/diconnect")
def f(uuid: int):
    uuids.remove(uuid)
    for player in players:
        if player.uuid == uuid:
            players.remove(player)
    return 200

@app.get("/get_locations")
def f(uuid: int):
    if uuid in uuids:
        data = {}
        for player in players:
            if uuid != player.uuid:
                if uuid not in data:
                    data[uuid] = {}

                data[uuid]["name"] = player.name
                data[uuid]["color"] = player.color

                if "pos" not in data[uuid]:
                    data[uuid]["pos"] = {}

                data[uuid]["pos"]["x"] = player.pos[0]
                data[uuid]["pos"]["y"] = player.pos[1]
        return data
    else:
        return 400
    
@app.get("/send_location")
def f(uuid: int, x:int, y:int):
    if uuid in uuids:
        for player in players:
            if player.uuid == uuid:
                player.updateLocation(x, y)
                return 200
    return 400

if __name__ == "__main__":
    uvicorn.run(app, port=9999)