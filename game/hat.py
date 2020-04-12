from settings import log
from .msg import *
from .player import Player
from shlyapa import Shlyapa, Config
import uuid
from collections import namedtuple
from typing import List

PlayerPair = namedtuple('PlayerPair' , 'explaining guessing')
PlayerList = List[Player]

class HatGame:
    ST_CONFIG = 'config'
    ST_PLAY = 'play'
    ST_FINISH = 'finish'

    def __init__(self):
        self.players = {}
        self.sockets = {}
        self.all_words = []
        self.tour_words = []
        self.id = str(uuid.uuid4())
        self.state = HatGame.ST_CONFIG
        self.shlyapa = None
        self.num_words = 6
        self.turn_timer = 20 # seconds
        self.cur_pair = None
        self.cur_word = None

    def get_players(self) -> PlayerList:
        return list(self.players.values())

    async def name(self, ws, msg: NameMsg):
        name = msg.name
        log.debug(f'user {name} logged in as {id(ws)}')
        player = Player(name=name, ws=ws)
        self.players[name] = player
        self.sockets[id(ws)] = player
        await self.game(ws)

    async def game(self, ws):
        await ws.send_json(
            GameMsg(
                id=self.id,
                numwords=self.num_words,
                timer=self.turn_timer
            ).data())

    async def words(self, ws, msg : WordsMsg):
        words = msg.words
        p = self.sockets[id(ws)]
        p.set_words(words)
        log.debug(f'user {p.name} sent words: {words}')

        # send prepare message to all players
        for p in self.players.values():
            await self.prepare(p.socket)

    async def prepare(self, ws):
        players = [p.name for p in self.players.values()]
        await ws.send_json(PrepareMsg(players=players).data())

    async def play(self, ws, msg : PlayMsg):
        if self.state != HatGame.ST_CONFIG:
            raise ValueError(f"Can't start game in '{self.state}' state")

        states = [p.state for p in self.players.values()]
        if states.count(Player.ST_READY) != len(states):
            await self.wait(ws)
            return

        cfg = Config(
            number_players=len(self.players),
            number_words=sum([len(p.words) for p in self.players.values()]))

        self.all_words = []
        for p in self.players.values():
            self.all_words.extend(p.words)
        self.tour_words = self.all_words

        self.shlyapa = Shlyapa(config=cfg)

        self.state = HatGame.ST_PLAY
        for p in self.players.values():
            await self.tour(p.socket)

        await self.next_move()

    async def wait(self, ws):
        log.debug('Wait for other players')
        await ws.send_json(WaitMsg().data())

    async def tour(self, ws):
        await ws.send_json(TourMsg(tour=self.shlyapa.get_cur_tour()).data())

    async def next_move(self):
        s = self.shlyapa
        pair = s.get_next_pair()
        plist = self.get_players()
        exp = plist[pair.explaining]
        gss = plist[pair.guessing]
        self.cur_pair = PlayerPair(explaining=exp, guessing=gss)

        log.debug(f'Pair selected: explain={exp.name} guessing={gss.name}')

        msg = TurnMsg(turn=s.get_cur_turn(), explain=exp.name, guess=gss.name)
        for p in self.players.values():
            await p.socket.send_json(msg.data())

    async def ready(self, ws, msg : ReadyMsg):
        exp = self.cur_pair.explaining
        gss = self.cur_pair.guessing

        if self.sockets[id(ws)] == exp:
            exp.prepare_explain()
        elif self.sockets[id(ws)] == gss:
            gss.prepare_guess()
        else:
            raise Exception('Wrong player sent ready command')

        log.debug(f'Pair state: explain({exp.name})={exp.state} guessing({gss.name})={gss.state}')

        if exp.state == Player.ST_PREPARE_EXPLAIN and gss.state == Player.ST_PREPARE_GUESS:
            exp.explain()
            gss.guess()
            log.debug(f'Explanation started: explain {exp.name} guessing {gss.name}')

            msg = StartMsg()
            for p in self.players.values():
                await p.socket.send_json(msg.data())
