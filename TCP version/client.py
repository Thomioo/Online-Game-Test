import socket
import pygame
import sys
import json

# Client constants
HOST = '7.tcp.eu.ngrok.io'  # Replace with server IP if needed
PORT = 19492
# PORT = 9999

name = input("Enter your name: ")

class Player:
    def __init__(self, name, uuid, color, pos=None):
        self.name = name
        self.color = color
        self.pos = pos if pos else (0, 200)
        self.uuid = uuid

    def update_location(self, x, y, server_conn):
        x = max(0, min(x, 480))
        y = max(0, min(y, 480))
        self.pos = (x, y)

        # Send updated position to the server
        update_request = json.dumps({
            "command": "send_location",
            "uuid": self.uuid,
            "x": x,
            "y": y
        })
        server_conn.sendall(update_request.encode())
        server_conn.recv(1024)  # Receive acknowledgement

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.pos[0], self.pos[1], 20, 20))

# Connect to the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_conn:
    server_conn.connect((HOST, PORT))

    # Request to connect the player
    connect_request = json.dumps({
        "command": "connect",
        "name": name
    })
    server_conn.sendall(connect_request.encode())
    response = json.loads(server_conn.recv(1024).decode())

    # Parse server response for player data
    if response["status"] == "connected":
        color, uuid_str = response["data"].split(";")
        color = tuple(map(int, color.split("-")))
        uuid = int(uuid_str)
        player = Player(name, uuid, color)

        # Initialize Pygame
        pygame.init()
        screen = pygame.display.set_mode((500, 500))
        pygame.display.set_caption("Game")
        clock = pygame.time.Clock()

        def get_players():
            # Request other players' locations
            get_request = json.dumps({
                "command": "get_locations",
                "uuid": player.uuid
            })
            server_conn.sendall(get_request.encode())
            response = json.loads(server_conn.recv(4096).decode())  # Large buffer for multiple players

            if response["status"] == "success":
                return [
                    Player(p["name"], p["uuid"], tuple(p["color"]), (p["pos"]["x"], p["pos"]["y"]))
                    for p in response["locations"].values()
                ]
            return []

        # Main game loop
        while True:
            keys = pygame.key.get_pressed()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Player movement
            if keys[pygame.K_UP]:
                player.update_location(player.pos[0], player.pos[1] - 8, server_conn)
            if keys[pygame.K_DOWN]:
                player.update_location(player.pos[0], player.pos[1] + 8, server_conn)
            if keys[pygame.K_LEFT]:
                player.update_location(player.pos[0] - 8, player.pos[1], server_conn)
            if keys[pygame.K_RIGHT]:
                player.update_location(player.pos[0] + 8, player.pos[1], server_conn)

            # Get other players' data and render
            players = get_players()
            screen.fill((0, 0, 0))
            player.draw(screen)
            for p in players:
                p.draw(screen)

            pygame.display.flip()
            clock.tick(60)  # Set FPS

    else:
        print("Failed to connect to the server.")
