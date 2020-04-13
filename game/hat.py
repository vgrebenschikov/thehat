from settings import log
from .msg import *
from .player import Player
from shlyapa import Shlyapa, Config
import uuid
from collections import namedtuple
from typing import (List, Dict, Optional)

PlayerPair = namedtuple('PlayerPair' , 'explaining guessing')
PlayerList = List[Player]
PlayerDict = Dict[str, Player]


class HatGame:
    ST_CONFIG = 'config'
    ST_PLAY = 'play'
    ST_FINISH = 'finish'

    players: PlayerList
    players_map: PlayerDict
    sockets_map: PlayerDict
    num_words: int
    turn_timer: int
    cur_pair: Optional[PlayerPair]
    shlyapa: Optional[Shlyapa]

    def __init__(self):
        self.players = []
        self.players_map = {}
        self.sockets_map = {}
        self.all_words = []
        self.tour_words = []
        self.id = str(uuid.uuid4())
        self.state = HatGame.ST_CONFIG
        self.shlyapa = None
        self.num_words = 6
        self.turn_timer = 20 # seconds
        self.cur_pair = None
        self.cur_word = None

    def add_player(self, name=None, socket=None) -> bool:
        if name in self.players_map:
            p = self.players_map[name]
            del self.sockets_map[id(p.socket)]
            self.sockets_map[id(socket)] = p
            self.players_map[name].set_socket(socket)
            return False

        p = Player(name=name, socket=socket)
        self.players.append(p)
        self.sockets_map[id(socket)] = p
        self.players_map[name] = p
        return True

    async def send_all(self, msg):
        for p in self.players:
            await p.socket.send_json(msg.data())

    async def name(self, ws, msg: NameMsg):
        name = msg.name
        log.debug(f'user {name} logged in as {id(ws)}')

        if self.add_player(name=name, socket=ws):
            log.info(f'Player {name}({id(ws)}) was added to game')
        else:
            log.info(f'Player {name}({id(ws)}) already in list, re-connect user')

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
        p = self.sockets_map[id(ws)]
        p.set_words(words)
        log.debug(f'user {p.name} sent words: {words}')

        msg = PrepareMsg(players=[p.name for p in self.players])
        await self.send_all(msg)

    async def prepare(self, ws):
        players = [p.name for p in self.players]
        await ws.send_json(PrepareMsg(players=players).data())

    async def play(self, ws, msg : PlayMsg):
        if self.state != HatGame.ST_CONFIG:
            raise ValueError(f"Can't start game in '{self.state}' state")

        states = [p.state for p in self.players]
        if states.count(Player.ST_READY) != len(states):
            await self.wait(ws)
            return

        cfg = Config(
            number_players=len(self.players_map),
            number_words=sum([len(p.words) for p in self.players]))

        self.all_words = []
        for p in self.players:
            self.all_words.extend(p.words)
        self.tour_words = self.all_words

        self.shlyapa = Shlyapa(config=cfg)

        self.state = HatGame.ST_PLAY
        for p in self.players:
            await self.tour(p.socket)

        await self.next_move()

    async def wait(self, ws):
        log.debug('Wait for other players')
        await ws.send_json(WaitMsg().data())

    async def tour(self, ws):
        await ws.send_json(TourMsg(tour=self.shlyapa.get_cur_tour()).data())

    async def next_move(self):
        s = self.shlyapa
        pair_idx = s.get_next_pair()
        exp = self.players[pair_idx.explaining]
        gss = self.players[pair_idx.guessing]
        self.cur_pair = PlayerPair(explaining=exp, guessing=gss)

        log.debug(f'Pair selected: explain={exp.name} guessing={gss.name}')

        msg = TurnMsg(turn=s.get_cur_turn(), explain=exp.name, guess=gss.name)
        await self.send_all(msg)

    async def ready(self, ws, msg : ReadyMsg):
        exp = self.cur_pair.explaining
        gss = self.cur_pair.guessing

        if self.sockets_map[id(ws)] == exp:
            exp.prepare_explain()
        elif self.sockets_map[id(ws)] == gss:
            gss.prepare_guess()
        else:
            raise Exception('Wrong player sent ready command')

        log.debug(f'Pair state: explain({exp.name})={exp.state} guessing({gss.name})={gss.state}')

        if exp.state == Player.ST_PREPARE_EXPLAIN and gss.state == Player.ST_PREPARE_GUESS:
            exp.explain()
            gss.guess()
            log.debug(f'Explanation started: explain {exp.name} guessing {gss.name}')

            msg = StartMsg()
            await self.send_all(msg)