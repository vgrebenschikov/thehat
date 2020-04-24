from settings import log
from . import message
from .player import Player
from .turn import Turn
from .timer import Timer
from shlyapa import Shlyapa, Config

import uuid
import random
from typing import (List, Dict, Optional)

PlayerList = List[Player]
PlayerDict = Dict[str, Player]


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

    def __init__(self, name=None, numwords=6, timer=20):
        self.players = []
        self.players_map = {}
        self.sockets_map = {}
        self.all_words = []
        self.tour_words = []
        self.id = str(uuid.uuid4())
        self.game_name = name or self.id
        self.state = HatGame.ST_SETUP
        self.shlyapa = None
        self.num_words = numwords or 6
        self.turn_timer = timer or 20  # in seconds
        self.turn = None
        self.timer = None

    def register_player(self, name=None, socket=None) -> bool:
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
            if p.socket is not None:
                await p.socket.send_json(msg.data())

    async def name(self, ws, msg: message.Name):
        """Set my name - (re)login procedure on socket"""
        name = msg.name

        if name not in self.players_map:
            if self.state != HatGame.ST_SETUP:
                log.info(f'Cannot login new user {name}({id(ws)}) while game in progress')
                await ws.send_json(message.Error(
                    code=104,
                    message=f"Can't login new user {name} while game in progress").data())
                return

            log.info(f'Player {name}({id(ws)}) was added to game')
        else:
            log.info(f'Player {name}({id(ws)}) already in list, re-connect user')

        reconnect = not self.register_player(name=name, socket=ws)

        await self.game(ws)
        await self.prepare(ws if reconnect else None)  # on reconnect send to self only

        if self.state == HatGame.ST_PLAY and self.shlyapa:
            s = self.shlyapa
            await ws.send_json(message.Tour(tour=s.get_cur_tour()).data())
            if self.turn:
                await ws.send_json(message.Turn(
                    turn=s.get_cur_turn(),
                    explain=self.turn.explaining.name,
                    guess=self.turn.guessing.name
                ).data())

    def game_msg(self):
        return message.Game(
            id=self.id,
            name=self.game_name,
            numwords=self.num_words,
            timer=self.turn_timer,
            state=self.state
        )

    async def game(self, ws):
        """Notify just known Player about Game layout"""
        await ws.send_json(self.game_msg().data())

    async def words(self, ws, msg: message.Words):
        """Player sends it's words to server"""
        words = msg.words
        p = self.sockets_map[id(ws)]
        p.set_words(words)
        log.debug(f'user {p.name} sent words: {words}')

        await self.prepare()

    async def setup(self, ws, msg: message.Setup):
        self.game_name = msg.name or self.game_name
        self.num_words = msg.numwords or self.num_words
        self.turn_timer = msg.timer or self.turn_timer

        await self.broadcast(self.game_msg())

    async def prepare(self, ws=None):
        """Notify All Players about changed set of players"""
        players = dict([(p.name, len(p.words)) for p in self.players])
        msg = message.Prepare(players=players)

        if ws is not None:
            await ws.send_json(msg.data())
        else:
            await self.broadcast(msg)

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
        self.tour_words = self.all_words.copy()
        await self.broadcast(message.Tour(tour=self.shlyapa.get_cur_tour()))
        log.debug(f"Next tour {self.shlyapa.get_cur_tour()}")
        log.debug(f"Words #{len(self.tour_words)}: {self.tour_words}")

    async def finish(self, s: Shlyapa):
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
            p.reset()  # noqa

        log.debug('Game finished')

    async def next_move(self, explained_words=None):
        """Do next move, called on game start or after move finished"""

        if self.turn:
            self.turn.explaining.wait()
            self.turn.guessing.wait()

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
        await self.turn.explaining.socket.send_json(m.data())

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
            await self.next_move(explained_words=self.turn.result())

            return

        if not self.has_words():
            """End of turn"""
            if self.timer:
                self.timer.cancel()

            log.debug('No more words - next turn')

            await self.broadcast(message.Stop(reason='empty'))

            self.turn.explaining.finish()
            self.turn.guessing.finish()

            await self.next_move(explained_words=self.turn.result())

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
        self.state = HatGame.ST_SETUP
        self.shlyapa = None
        self.turn = None
        self.timer = None

        for p in self.players:
            p.reset()

        await self.broadcast(self.game_msg())

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
