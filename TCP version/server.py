import socket
import random
import json
import threading

# Server constants
HOST = '0.0.0.0'
PORT = 9999

# Data structures for players and UUIDs
uuids = set()
players = []

class Player:
    def __init__(self, name):
        self.name = name
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.pos = (10, 200)
        ruuid = random.randint(0, 2**64)
        while ruuid in uuids:
            ruuid = random.randint(0, 2**64)
        self.uuid = ruuid

    def update_location(self, x, y):
        self.pos = (x, y)

    def return_data(self):
        r, g, b = self.color
        return f"{r}-{g}-{b};{self.uuid}"
    
    def get_location_data(self):
        return {
            "uuid": self.uuid,
            "pos": {"x": self.pos[0], "y": self.pos[1]},
            "name": self.name,
            "color": self.color
        }

# Function to handle each client connection
def handle_client(conn, addr):
    print(f"New connection from {addr}")
    with conn:
        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                request = json.loads(data)
                response = process_request(request)
                
                conn.sendall(json.dumps(response).encode())
            except (ConnectionResetError, BrokenPipeError):
                break

def process_request(request):
    command = request.get("command")
    if command == "connect":
        name = request.get("name")
        if name:
            player = Player(name)
            players.append(player)
            uuids.add(player.uuid)
            return {"status": "connected", "data": player.return_data()}

    elif command == "disconnect":
        uuid = request.get("uuid")
        if uuid in uuids:
            uuids.remove(uuid)
            for player in players:
                if player.uuid == uuid:
                    players.remove(player)
                    break
            return {"status": "disconnected"}
        return {"status": "error", "message": "Invalid UUID"}

    elif command == "get_locations":
        uuid = request.get("uuid")
        if uuid in uuids:
            data = {}
            for player in players:
                if player.uuid != uuid:
                    data[player.uuid] = player.get_location_data()
            return {"status": "success", "locations": data}
        return {"status": "error", "message": "Invalid UUID"}

    elif command == "send_location":
        uuid = request.get("uuid")
        x, y = request.get("x"), request.get("y")
        if uuid in uuids and x is not None and y is not None:
            for player in players:
                if player.uuid == uuid:
                    player.update_location(x, y)
                    return {"status": "location updated"}
        return {"status": "error", "message": "Invalid UUID or coordinates"}

    else:
        return {"status": "error", "message": "Unknown command"}

# Setting up the TCP server
def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server started on {HOST}:{PORT}")
        while True:
            conn, addr = server.accept()
            threading.Thread(target=handle_client, args=(conn, addr)).start()

if __name__ == "__main__":
    start_server()
