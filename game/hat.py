from settings import log

class Player:
    name = None

    def __init__(self, name, ws = None):
        self.name = name
        self.socket = ws

    def set_socket(self, ws):
        self.socket = ws

    def __str__(self):
        return f'{self.name} - {self.socket}'

class HatGame:
    num_players = 10
    players = None

    def __init__(self):
        self.players = {}

    async def login(self, ws, data):
        name = data['name']
        log.debug(f'user {name} logged in as {ws}')
        self.players[name] = Player(name, ws)

    async def list_players(self, ws, data):
        log.debug(f'list players')
        ret = []
        for p in self.players.values():
            log.debug(f'{p.name}: {p}')
            ret.append(p.name)

        await ws.send_json(ret)
