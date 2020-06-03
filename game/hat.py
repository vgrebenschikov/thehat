from settings import log
from . import message
from .player import Player
from .turn import Turn
from .timer import Timer
from shlyapa import Shlyapa, Config
from robot.words import (NAMES, NOUNS)

import datetime
import json
import uuid
import random
from typing import (List, Dict, Optional)

PlayerList = List[Player]
PlayerDict = Dict[str, Player]

commands = []


def handler(method):
    """Decorator to mark methods callable through API"""

    async def call(self, *args):
        self.last_event_time = datetime.datetime.now()
        log.debug(f'Received command {method.__name__}')
        await method(self, *args)

    commands.append(method.__name__)

    return call


class HatGame:
    ST_SETUP = 'setup'
    ST_PLAY = 'play'
    ST_FINISH = 'finish'

    id: str
    game_name: str
    players: PlayerList
    players_map: PlayerDict
    sockets_map: PlayerDict
    num_words: int
    turn_timer: int
    turn: Optional[Turn]
    shlyapa: Optional[Shlyapa]
    timer: Optional[Timer]
    all_words: List[str]
    tour_words: List[str]
    last_event_time: datetime.datetime
    results: Optional[dict]

    def __init__(self, name=None, numwords=6, timer=20):
        self.players = []
        self.players_map = {}
        self.sockets_map = {}
        self.all_words = []
        self.tour_words = []
        self.id = str(uuid.uuid4())
        self.game_name = name or NAMES.get_random_word()
        self.state = HatGame.ST_SETUP
        self.shlyapa = None
        self.num_words = numwords or 6
        self.turn_timer = timer or 20  # in seconds
        self.turn = None
        self.timer = None
        self.last_event_time = datetime.datetime.now()
        self.results = None

    def register_player(self, name=None, avatar=None, socket=None) -> bool:
        """Add new player to game"""
        if name in self.players_map:
            p = self.players_map[name]
            del self.sockets_map[id(p.socket)]
            self.sockets_map[id(socket)] = p
            self.players_map[name].socket = socket
            return False

        p = Player(name=name, avatar=avatar, socket=socket)
        self.players.append(p)
        self.sockets_map[id(socket)] = p
        self.players_map[name] = p
        return True

    async def send_json(self, ws, msg):
        def dumps(data):
            return json.dumps(data, ensure_ascii=False)

        self.last_event_time = datetime.datetime.now()
        await ws.send_json(msg.data())

    async def broadcast(self, msg):
        """Broadcast message to all players"""
        for p in self.players:
            if p.socket is not None:
                await self.send_json(p.socket, msg)

    async def error(self, ws, code, msgtxt):
        """Respond with error and log error"""

        log.error(msgtxt)
        await self.send_json(ws, message.Error(code=code, message=msgtxt))

    async def cmd(self, ws, data):
        """Command multiplexer"""

        global commands

        try:
            msg = message.ClientMessage.msg(data)
        except Exception as e:
            await self.error(ws, 102, f'Invalid message format {data} - {e}')
            return

        cmdtxt = msg.cmd()
        cmd = getattr(self, cmdtxt, None)
        if msg.cmd() not in commands or not callable(cmd):
            await self.error(ws, 103, f'Unknown command {cmdtxt}')
            return

        try:
            await cmd(ws, msg)
        except Exception as e:
            log.exception(f"Exception caught while execution of '{cmdtxt}': {e}")
            await self.error(ws, 104, f"Error executing command '{cmdtxt}': {e}")

    @handler
    async def name(self, ws, msg: message.Name):
        """Set my name - (re)login procedure on socket"""

        name = msg.name

        if name not in self.players_map:
            if self.state != HatGame.ST_SETUP:
                log.info(f'Cannot login new user {name}({id(ws)}) while game in progress')
                await self.send_json(ws, message.Error(
                    code=104,
                    message=f"Can't login new user {name} while game in progress"))
                return

            log.info(f'Player {name}({id(ws)}) was added to game')
        else:
            log.info(f'Player {name}({id(ws)}) already in list, re-connect user')

        reconnect = not self.register_player(name=name, avatar=msg.avatar, socket=ws)

        await self.game(ws)
        await self.prepare(ws if reconnect else None)  # on reconnect send to self only

        if self.state == HatGame.ST_PLAY and self.shlyapa:
            s = self.shlyapa
            await self.send_json(ws, message.Tour(tour=s.get_cur_tour()))
            if self.turn:
                await self.send_json(ws, message.Turn(
                    turn=s.get_cur_turn(),
                    explain=self.turn.explaining.name,
                    guess=self.turn.guessing.name
                ))
        if self.state == HatGame.ST_FINISH and self.results is not None:
            await self.send_json(ws, message.Finish(results=self.results))

    def game_msg(self):
        return message.Game(
            id=self.id,
            name=self.game_name,
            numwords=self.num_words,
            timer=self.turn_timer,
            state=self.state
        )

    @handler
    async def game(self, ws):
        """Notify just known Player about Game layout"""
        await self.send_json(ws, self.game_msg())

    @handler
    async def words(self, ws, msg: message.Words):
        """Player sends it's words to server"""
        words = msg.words

        if len(words) < self.num_words:
            for wi in range(0, self.num_words):
                words.append(NOUNS.get_random_word())

        p = self.sockets_map[id(ws)]
        p.words = words
        log.debug(f'user {p.name} sent words: {words}')

        await self.prepare()

    @handler
    async def setup(self, ws, msg: message.Setup):
        self.game_name = msg.name or self.game_name
        self.num_words = msg.numwords or self.num_words
        self.turn_timer = msg.timer or self.turn_timer

        await self.broadcast(self.game_msg())

    async def prepare(self, ws=None):
        """Notify All Players about changed set of players"""
        players = dict([(p.name, message.UserInfo(len(p.words), p.avatar)) for p in self.players])
        msg = message.Prepare(players=players)

        if ws is not None:
            await self.send_json(ws, msg)
        else:
            await self.broadcast(msg)

    @handler
    async def play(self, ws, msg: message.Play):
        """Move Game from ST_SETUP phase to ST_PLAY - start game"""
        if self.state not in (HatGame.ST_SETUP, HatGame.ST_FINISH):
            raise ValueError(f"Can't start game in '{self.state}' state")

        states = [p.state for p in self.players]
        if states.count(Player.ST_WAIT) != len(states):
            await self.wait(ws)
            return

        self.all_words = [w for p in self.players for w in p.words]
        cfg = Config(
            number_players=len(self.players),
            number_words=len(self.all_words),
            number_tours=3,
            is_last_turn_in_tour_divisible=False)

        self.shlyapa = Shlyapa(config=cfg)
        self.state = HatGame.ST_PLAY

        await self.tour()
        await self.next_move()

    async def wait(self, ws):
        """Response to the player on attempt to start game with not all players ready"""
        log.debug('Wait for other players')
        await self.send_json(ws, message.Wait())

    async def tour(self):
        """Notify All Players about tour start, happens at begin of each tour"""
        self.tour_words = self.all_words.copy()
        await self.broadcast(message.Tour(tour=self.shlyapa.get_cur_tour()))
        log.debug(f"Next tour {self.shlyapa.get_cur_tour()}")
        log.debug(f"Words #{len(self.tour_words)}: {self.tour_words}")

    async def finish(self, s: Shlyapa):
        def player_array_to_dict(score_list):
            pn = len(self.players)
            return dict([(self.players[i].name, v) for i, v in enumerate(score_list) if i < pn])

        s.calculate_results()
        total_score = player_array_to_dict(s.get_total_score_results())
        explained_score = player_array_to_dict(s.get_explained_score_results())
        guessed_score = player_array_to_dict(s.get_guessed_score_results())

        score = {}
        for p in self.players:
            score[p.name] = {
                "total": total_score[p.name],
                "explained": explained_score[p.name],
                "guessed": guessed_score[p.name]
            }

        self.results = {
            "score": score,
            "explained": [player_array_to_dict(t) for t in s.get_explained_table_results()],
            "guessed": [player_array_to_dict(t) for t in s.get_guessed_table_results()]
        }

        await self.broadcast(message.Finish(results=self.results))
        self.state = HatGame.ST_FINISH

        for p in self.players:
            """Reset players to ask new words"""
            p.reset()  # noqa

        log.debug('Game finished')

    async def next_move(self):
        """Do next move, called on game start or after move finished"""

        explained_words = None
        if self.turn:
            self.turn.explaining.wait()
            self.turn.guessing.wait()

            explained_words = self.turn.result()
            # return to pool words which was miss-guessed by previous pair
            missed_words = self.turn.missed_words
            if len(missed_words):
                log.debug(f"Return #{len(missed_words)} words to hat")
                self.tour_words.extend(missed_words)

        s = self.shlyapa

        if explained_words is not None:  # non-first move
            log.debug(f'Turn over, explained words={explained_words}')
            s.move_shlyapa(pair_explained_words=explained_words)

            if s.is_cur_tour_new():
                await self.tour()

            if s.is_end():
                await self.finish(s)
                return

        log.debug(f'New turn #{s.get_cur_turn()}')

        pair_idx = s.get_next_pair()
        exp = self.players[pair_idx.explaining]
        gss = self.players[pair_idx.guessing]
        self.turn = Turn(explaining=exp, guessing=gss)

        log.debug(f'In hat #{len(self.tour_words)}')
        log.debug(f'Pair selected: explain={exp} guessing={gss}')
        exp.begin()  # noqa
        gss.begin()  # noqa

        m = message.Turn(turn=s.get_cur_turn(), explain=exp.name, guess=gss.name)
        await self.broadcast(m)

    def has_words(self):
        return len(self.tour_words) > 0

    async def next_word(self):
        """Select next word for pair"""
        if len(self.tour_words) == 0:
            raise ValueError("No more words - unexpected")
        self.turn.word = self.tour_words.pop(random.randrange(0, len(self.tour_words)))

        m = message.Next(word=self.turn.word)
        await self.send_json(self.turn.explaining.socket, m)

    @handler
    async def ready(self, ws, msg: message.Ready):
        """Tell server that player is ready to guess/explain"""
        if self.state != HatGame.ST_PLAY:
            raise Exception(f"Invalid command 'ready' for game in state '{self.state}'")

        exp = self.turn.explaining
        gss = self.turn.guessing

        sent_by = self.sockets_map[id(ws)]
        if sent_by in (exp, gss):
            sent_by.ready()
        else:
            raise Exception('Wrong player sent ready command')

        log.debug(f'Pair state: explain({exp.name})={exp.state} guessing({gss.name})={gss.state}')

        if exp.state == Player.ST_READY and gss.state == Player.ST_READY:
            exp.play()
            gss.play()
            log.debug(f'Explanation started: explain {exp.name} guessing {gss.name}')

            self.timer = Timer(self.turn_timer, self.expired)

            await self.broadcast(message.Start())
            await self.next_word()

    @handler
    async def guessed(self, ws, msg: message.Guessed):
        """Guessing User tell us of he guessed right"""
        sent_by = self.sockets_map[id(ws)]
        if sent_by != self.turn.explaining:
            raise ValueError(
                f'Only explaining player can send guessed command,'
                f' but sent by {sent_by} in {sent_by.state} state')

        if sent_by.state not in (Player.ST_PLAY, Player.ST_LAST_ANSWER):
            raise ValueError(f"Player {sent_by} can't sent guessed command while not in play")

        self.turn.guessed(result=msg.guessed)
        if msg.guessed:
            m = message.Explained(word=self.turn.word)
        else:
            m = message.Missed()

        await self.broadcast(m)

        if self.turn.explaining.state == Player.ST_LAST_ANSWER:
            """Answer after timer exhausted"""
            self.turn.explaining.finish()
            await self.next_move()

            return

        if not self.has_words():
            """End of turn"""
            if self.timer:
                self.timer.cancel()

            log.debug('No more words - next turn')

            await self.broadcast(message.Stop(reason='empty'))

            self.turn.explaining.finish()
            self.turn.guessing.finish()

            await self.next_move()

            return

        await self.next_word()

    async def expired(self):
        """Guessing time expired"""
        self.timer = None

        try:
            log.debug('Turn timer expired, stop turn')

            await self.broadcast(message.Stop(reason='timer'))

            self.turn.explaining.lastanswer()
            self.turn.guessing.finish()
        except Exception as e:
            log.error(f'Exception while process timer: {e}')
            log.exception()

    @handler
    async def close(self, ws, msg: message.Close = None):
        """Close connection, exit user"""
        p = self.sockets_map.pop(id(ws), None)
        if p:
            self.players_map.pop(p.name, None)
            if p in self.players:
                self.players.remove(p)

            if self.turn and p in self.turn:
                self.turn.abort()

                try:
                    await self.next_move()
                except Exception:
                    pass

            try:
                await p.socket.close()
            except Exception:
                pass

            p.socket = None

            pn = len(self.players)
            if pn > 2:
                self.shlyapa.config.set_number_players(pn)

    def reinit(self):
        if self.timer:
            self.timer.cancel()

        self.all_words = []
        self.tour_words = []
        self.state = HatGame.ST_SETUP
        self.shlyapa = None
        self.turn = None
        self.timer = None
        self.results = None

    @handler
    async def restart(self, ws, msg: message.Restart):
        """Restart the game"""

        if id(ws) in self.sockets_map:
            log.info(f'Game was restarted by {self.sockets_map[id(ws)]}')

        self.reinit()

        for p in self.players:
            p.reset()

        await self.broadcast(self.game_msg())
        await self.prepare()

    @handler
    async def reset(self, ws=None, msg: message.Restart = None):
        """Reset the game - disconnect all users except me"""

        me = None
        if id(ws) in self.sockets_map:
            me = self.sockets_map[id(ws)]
            me.reset()

        if me:
            self.players.remove(me)

        while len(self.players) > 0:
            p = self.players.pop(0)

            del self.sockets_map[id(p.socket)]
            del self.players_map[p.name]

            await p.socket.close()

        if me:
            self.players.append(me)

        self.reinit()

        log.info(f'Game was reset{f" by {me}" if me else ""}')
