from settings import log
from .msg import *
from .player import Player
from shlyapa import Shlyapa, Config

import uuid
import random
from collections import namedtuple
from typing import (List, Dict, Optional)

PlayerPair = namedtuple('PlayerPair' , 'explaining guessing')
PlayerList = List[Player]
PlayerDict = Dict[str, Player]


class HatGame:
    ST_SETUP = 'setup'
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
        self.state = HatGame.ST_SETUP
        self.shlyapa = None
        self.num_words = 6
        self.turn_timer = 20 # seconds
        self.cur_pair = None
        self.cur_word = None

    def add_player(self, name=None, socket=None) -> bool:
        """Add new player to game"""
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

    async def broadcast(self, msg):
        """Broadcast message to all players"""
        for p in self.players:
            await p.socket.send_json(msg.data())

    async def name(self, ws, msg: NameMsg):
        """Set my name - (re)login procedure on socket"""
        name = msg.name
        log.debug(f'user {name} logged in as {id(ws)}')

        if self.add_player(name=name, socket=ws):
            log.info(f'Player {name}({id(ws)}) was added to game')
        else:
            log.info(f'Player {name}({id(ws)}) already in list, re-connect user')

        await self.game(ws)

    async def game(self, ws):
        """Notify just known Player about Game layout"""
        await ws.send_json(
            GameMsg(
                id=self.id,
                numwords=self.num_words,
                timer=self.turn_timer
            ).data())
        await self.prepare()

    async def words(self, ws, msg : WordsMsg):
        """Player sends it's words to server"""
        words = msg.words
        p = self.sockets_map[id(ws)]
        p.set_words(words)
        log.debug(f'user {p.name} sent words: {words}')

        await self.prepare()

    async def prepare(self):
        """Notify All Players about changed set of players"""
        players = dict([(p.name,len(p.words)) for p in self.players])
        await self.broadcast(PrepareMsg(players=players))

    async def play(self, ws, msg : PlayMsg):
        """Move Game from ST_SETUP phase to ST_PLAY - start game"""
        if self.state != HatGame.ST_SETUP:
            raise ValueError(f"Can't start game in '{self.state}' state")

        states = [p.state for p in self.players]
        if states.count(Player.ST_READY) != len(states):
            await self.wait(ws)
            return

        self.all_words = [w for p in self.players for w in p.words]
        cfg = Config(
            number_players=len(self.players),
            number_words=len(self.all_words))

        self.shlyapa = Shlyapa(config=cfg)
        self.state = HatGame.ST_PLAY

        await self.tour()
        await self.next_move()

    async def wait(self, ws):
        """Response to the player on attempt to start game with not all players ready"""
        log.debug('Wait for other players')
        await ws.send_json(WaitMsg().data())

    async def tour(self):
        """Notify All Players about tour start, happens at begin of each tour"""
        self.tour_words = self.all_words
        await self.broadcast(TourMsg(tour=self.shlyapa.get_cur_tour()))

    async def next_move(self):
        """Do next move, called on game start or after move finished"""
        s = self.shlyapa
        pair_idx = s.get_next_pair()
        exp = self.players[pair_idx.explaining]
        gss = self.players[pair_idx.guessing]
        self.cur_pair = PlayerPair(explaining=exp, guessing=gss)

        log.debug(f'Pair selected: explain={exp.name} guessing={gss.name}')

        msg = TurnMsg(turn=s.get_cur_turn(), explain=exp.name, guess=gss.name)
        await self.broadcast(msg)

    async def next_word(self):
        """Select next word for pair"""
        self.cur_word = self.tour_words.pop(random.randint(0,len(self.tour_words)-1))

        msg = NextMsg(word=self.cur_word)
        await self.cur_pair.explaining.socket.send_json(msg.data())

    async def ready(self, ws, msg : ReadyMsg):
        """Tell server that player is ready to guess/explain"""
        if self.state != HatGame.ST_PLAY:
            raise Exception(f"Invalid command 'ready' for game in state '{self.state}'")

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
            await self.broadcast(msg)
            await self.next_word()
