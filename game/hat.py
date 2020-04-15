from settings import log
from . import message
from .player import Player
from .timer import Timer
from shlyapa import Shlyapa, Config

import uuid
import random
from collections import namedtuple
from typing import (List, Dict, Optional)

PlayerPair = namedtuple('PlayerPair', 'explaining guessing')
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
    cur_guessed: Optional[int]
    timer: Optional[Timer]
    all_words: List[str]
    tour_words: List[str]
    missed_words: List[str]

    def __init__(self):
        self.players = []
        self.players_map = {}
        self.sockets_map = {}
        self.all_words = []
        self.tour_words = []
        self.missed_words = []
        self.id = str(uuid.uuid4())
        self.state = HatGame.ST_SETUP
        self.shlyapa = None
        self.num_words = 6
        self.turn_timer = 20  # in seconds
        self.cur_pair = None
        self.cur_word = None
        self.cur_guessed = None
        self.timer = None

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

    async def name(self, ws, msg: message.Name):
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
            message.Game(
                id=self.id,
                numwords=self.num_words,
                timer=self.turn_timer
            ).data())
        await self.prepare()

    async def words(self, ws, msg: message.Words):
        """Player sends it's words to server"""
        words = msg.words
        p = self.sockets_map[id(ws)]
        p.set_words(words)
        log.debug(f'user {p.name} sent words: {words}')

        await self.prepare()

    async def prepare(self):
        """Notify All Players about changed set of players"""
        players = dict([(p.name, len(p.words)) for p in self.players])
        await self.broadcast(message.Prepare(players=players))

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
        await ws.send_json(message.Wait().data())

    async def tour(self):
        """Notify All Players about tour start, happens at begin of each tour"""
        assert len(self.missed_words) == 0
        self.tour_words = self.all_words.copy()
        await self.broadcast(message.Tour(tour=self.shlyapa.get_cur_tour()))
        log.debug(f"Next tour {self.shlyapa.get_cur_tour()}")
        log.debug(f"Words #{len(self.tour_words)}: {self.tour_words}")

    async def next_move(self, explained_words=None):
        """Do next move, called on game start or after move finished"""

        if self.cur_pair:
            self.cur_pair.explaining.wait()
            self.cur_pair.guessing.wait()

        s = self.shlyapa

        if explained_words is not None:  # non-first pair
            log.debug(f'Turn over, explained words={explained_words}')
            s.move_shlyapa(pair_explained_words=explained_words)

            if s.is_cur_tour_new():
                await self.tour()

            if s.is_end():
                def player_array_to_dict(score_list):
                    return dict([(self.players[i].name, v) for i, v in enumerate(score_list)])

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

                results = {
                    "score": score,
                    "explained": [player_array_to_dict(t) for t in s.get_explained_table_results()],
                    "guessed": [player_array_to_dict(t) for t in s.get_guessed_table_results()]
                }

                await self.broadcast(message.Finish(results=results))
                self.state = HatGame.ST_FINISH

                for p in self.players:
                    """Reset players to ask new words"""
                    p.reset()   # noqa

                return

        log.debug(f'New turn #{s.get_cur_turn()}')

        pair_idx = s.get_next_pair()
        exp = self.players[pair_idx.explaining]
        gss = self.players[pair_idx.guessing]
        self.cur_pair = PlayerPair(explaining=exp, guessing=gss)
        self.cur_guessed = 0

        # return to pool words which was miss-guessed by previous pair
        if len(self.missed_words):
            log.debug(f"Return #{len(self.missed_words)} words to hat")
            self.tour_words.extend(self.missed_words)
            self.missed_words = []

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
        self.cur_word = self.tour_words.pop(random.randrange(0, len(self.tour_words)))

        m = message.Next(word=self.cur_word)
        await self.cur_pair.explaining.socket.send_json(m.data())

    async def ready(self, ws, msg: message.Ready):
        """Tell server that player is ready to guess/explain"""
        if self.state != HatGame.ST_PLAY:
            raise Exception(f"Invalid command 'ready' for game in state '{self.state}'")

        exp = self.cur_pair.explaining
        gss = self.cur_pair.guessing

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

    async def guessed(self, ws, msg: message.Guessed):
        """Guessing User tell us of he guessed right"""
        sent_by = self.sockets_map[id(ws)]
        if sent_by != self.cur_pair.explaining:
            raise ValueError(
                f'Only explaining player can send guessed command,'
                f' but sent by {sent_by} in {sent_by.state} state')

        if sent_by.state not in (Player.ST_PLAY, Player.ST_LAST_ANSWER):
            raise ValueError(f"Player {sent_by} can't sent guessed command while not in play")

        if msg.guessed:
            self.cur_guessed += 1
            m = message.Explained(word=self.cur_word)
        else:
            m = message.Missed()
            self.missed_words.append(self.cur_word)
            self.cur_word = None

        await self.broadcast(m)

        if self.cur_pair.explaining.state == Player.ST_LAST_ANSWER:
            """Answer after timer exhausted"""
            self.cur_pair.explaining.finish()
            await self.next_move(explained_words=self.cur_guessed)

            return

        if not self.has_words():
            """End of turn"""
            if self.timer:
                self.timer.cancel()

            log.debug('No more words - next turn')

            await self.broadcast(message.Stop(reason='empty'))

            self.cur_pair.explaining.finish()
            self.cur_pair.guessing.finish()

            await self.next_move(explained_words=self.cur_guessed)

            return

        await self.next_word()

    async def expired(self):
        """Guessing time expired"""
        self.timer = None

        try:
            log.debug('Turn timer expired, stop turn')

            await self.broadcast(message.Stop(reason='timer'))

            self.cur_pair.explaining.lastanswer()
            self.cur_pair.guessing.finish()
        except Exception as e:
            log.error(f'Exception while process timer: {e}')
            log.exception()

    async def close(self, ws, msg: message.Close):
        """Close connection"""
        p = self.sockets_map[id(ws)]
        del self.sockets_map[id(ws)]
        del self.players_map[p.name]
        self.players.remove(p)

        await p.socket.close()

    async def restart(self, ws, msg: message.Restart):
        """Restart the game"""

        if id(ws) in self.sockets_map:
            log.info(f'Game was restarted by {self.sockets_map[id(ws)]}')

        if self.timer:
            self.timer.cancel()

        self.all_words = []
        self.tour_words = []
        self.missed_words = []
        self.id = str(uuid.uuid4())
        self.state = HatGame.ST_SETUP
        self.shlyapa = None
        self.num_words = 6
        self.turn_timer = 20  # in seconds
        self.cur_pair = None
        self.cur_word = None
        self.cur_guessed = None
        self.timer = None

        for p in self.players:
            p.reset()

        await self.broadcast(message.Game(
            id=self.id,
            numwords=self.num_words,
            timer=self.turn_timer
        ))

    async def reset(self, ws, msg: message.Restart):
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

        log.info(f'Game was reset by {me if me else "-"}')
        await self.restart(ws, message.Restart())
