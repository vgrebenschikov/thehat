from settings import log
from game.player import Player
from shlyapa import Shlyapa, Config

import uuid

class HatGame:
    ST_CONFIG = 'config'
    ST_PLAY = 'play'
    ST_FINISH = 'finish'

    def __init__(self):
        self.players = {}
        self.sockets = {}
        self.id = str(uuid.uuid4())
        self.state = HatGame.ST_CONFIG
        self.shlyapa = None
        self.num_words = 6

    async def name(self, ws, data):
        name = data['name']
        log.debug(f'user {name} logged in as {id(ws)}')
        player = Player(name=name, ws=ws)
        self.players[name] = player
        self.sockets[id(ws)] = player
        await self.game(ws)

    async def game(self, ws):
        await ws.send_json({'cmd': 'game', 'id': self.id, 'numwords': self.num_words})

    async def words(self, ws, data):
        words = data['words']
        p = self.sockets[id(ws)]
        p.set_words(words)
        log.debug(f'user {p.name} sent words: {words}')

        # send prepare message to all players
        for p in self.players.values():
            await self.prepare(p.socket)

    async def prepare(self, ws):
        players = [p.name for p in self.players.values()]
        await ws.send_json({'cmd': 'prepare', 'players': players})

    async def play(self, ws, data):
        if self.state != HatGame.ST_CONFIG:
            raise ValueError(f"Can't start game in '{self.state}' state")

        states = [p.state for p in self.players.values()]
        if states.count(Player.ST_READY) != len(states):
            await self.wait(ws)
            return

        cfg = Config(
                number_players=len(self.players),
                number_words=sum([len(p.words) for p in self.players.values()])
              )
        self.shlyapa = Shlyapa(config=cfg)

        self.state = HatGame.ST_PLAY
        for p in self.players.values():
            await self.tour(p.socket)


    async def wait(self, ws):
        log.debug('Wait for other players')
        await ws.send_json({'cmd': 'wait'})

    async def tour(self, ws):
        await ws.send_json({'cmd': 'tour', 'tour': self.shlyapa.get_cur_tour()})





        
