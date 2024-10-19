import requests, pygame, sys, json

name = input("name: ")
url = input("url: ")
send_ses = requests.sessions.Session()
get_ses = requests.sessions.Session()

class Player:
    def __init__(self, name, uuid, color, pos=None):
        self.name = name
        self.color = color
        if pos:
            self.pos = (pos[0], pos[1])
        else:
            self.pos = (0, 200)
        self.uuid = uuid

    def updateLocation(self, x, y):
        x = min(x, 480)
        y = min(y, 480)
        x = max(x, 0)
        y = max(y, 0)
        self.pos = (x, y)
        send_ses.get(f"{url}/send_location?uuid={self.uuid}&x={self.pos[0]}&y={self.pos[1]}")

    def draw(self):
        pygame.draw.rect(screen, self.color, pygame.Rect(self.pos[0], self.pos[1], 20, 20))

t = requests.get(f"{url}/connect?name=" + name).text.split(";")
color, uuid = t

color = color.lstrip('"').split("-")
color = [int(x) for x in color]
uuid = int(uuid.rstrip('"'))
player = Player(name, uuid, color)

pygame.init()

screen = pygame.display.set_mode((500, 500))
pygame.display.set_caption("Game")
clock = pygame.time.Clock()

def getPlayers():
    res = get_ses.get(f"{url}/get_locations?uuid=" + str(uuid))
    # print(res.text.replace("\n", ""))
    d = json.loads(res.text)
    ps = []
    for key in d.keys():
        p = Player(d[key]["name"], 8, (d[key]["color"][0], d[key]["color"][1], d[key]["color"][2]), (d[key]["pos"]["x"], d[key]["pos"]["y"]))
        ps.append(p)
    return ps

players = getPlayers()

while True:
    keys = pygame.key.get_pressed()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
    
    if keys[pygame.K_UP]:
        player.updateLocation(player.pos[0], player.pos[1] - 8)
    if keys[pygame.K_DOWN]:
        player.updateLocation(player.pos[0], player.pos[1] + 8)
    if keys[pygame.K_LEFT]:
        player.updateLocation(player.pos[0] - 8, player.pos[1])
    if keys[pygame.K_RIGHT]:
        player.updateLocation(player.pos[0] + 8, player.pos[1])


    players = getPlayers()
    screen.fill((0, 0, 0))
    player.draw()
    for p in players:
        p.draw()
    pygame.display.flip()
    clock.tick(165)