"""
Robot is a artificial intelligence which can play TheHat game
don't wary - nothing serious, just random answers
"""
from asyncio import (sleep, ensure_future)
from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType
import json
import names
import random
from typing import (List, Dict, Optional)
from colorama import Fore, Style

from .words import Words
import game.message as message
import settings
from settings import log

cc = Style.BRIGHT + Fore.GREEN
sc = Style.BRIGHT + Fore.BLUE
ec = Style.BRIGHT + Fore.RED
mc = Style.BRIGHT + Fore.YELLOW
rc = Style.RESET_ALL


def logS(message, *args):
    log.info(sc + message + rc, *args)


def logC(message, *args):
    log.info(cc + message + rc, *args)


def logM(message, *args):
    log.info(mc + message + rc, *args)


def logE(message, *args):
    log.info(ec + message + rc, *args)


class Robot:
    uri: str
    ws: ClientWebSocketResponse
    queue: List[message.ServerMessage]
    players: Dict[str, int]
    tour: Optional[message.Tour]
    turn: Optional[message.Turn]
    turn: Optional[message.Finish]
    finished: bool

    def __init__(self, uri=None, name=None):
        self.uri = uri
        self.name = name if name else names.get_first_name()
        self.queue = []
        self.players = {}
        self.tour = None
        self.turn = None
        self.finish = None

        self.finished = False

    async def run(self, pnum=None, wait=10):

        session = ClientSession()
        uri = f'http://{settings.SITE_HOST}:{settings.SITE_PORT}/ws'
        self.ws = await session.ws_connect(uri)

        listener = ensure_future(self.receive())

        if pnum:
            await self.send_msg(message.Reset())

        await self.setup()

        if pnum:
            logM(f'Waiting until other {pnum - 1} players connected')
            while len([p for p, n in self.players.items() if n > 0]) < pnum:
                await self.wait_msg(message.Prepare)

            logM(f'All players ready - starting the game')
            await self.send_msg(message.Play())

        await self.play()

        listener.cancel()
        await session.close()

    def error(self, message='Unknown error'):
        logE(f'Error: {message}')

    async def send_msg(self, msg):
        logC(f'>> {msg.data()}')
        await self.ws.send_json(msg.data())

    async def receive(self):
        while True:
            tmsg = await self.ws.receive()

            if tmsg.type == WSMsgType.text:
                try:
                    data = json.loads(tmsg.data)
                    logS(f'<< {data}')
                except Exception as e:
                    self.error(f'Broken message received {e}')
                    continue

                if 'cmd' not in data:
                    self.error(f'Invalid message format {tmsg.data}')
                    continue
                else:
                    cmdtxt = data['cmd']

                try:
                    msg = message.ServerMessage.msg(data)
                    if isinstance(msg, message.Prepare):
                        self.players = msg.players
                    elif isinstance(msg, message.Tour):
                        self.tour = msg
                    elif isinstance(msg, message.Turn):
                        self.turn = msg
                    elif isinstance(msg, message.Finish):
                        self.finish = msg
                        return
                    elif isinstance(msg, message.Explained) or isinstance(msg, message.Missed):
                        continue

                    self.queue.append(msg)

                except Exception as e:
                    log.exception(f"Exception caught while parsing of '{cmdtxt}': {e}")
                    self.error(f"Error executing command '{cmdtxt}': {e}")

            elif tmsg.type == WSMsgType.closed:
                break
            elif tmsg.type == WSMsgType.error:
                break

        logE('Websocket closed unexpectedly')

        return None

    async def wait_msg(self, cls):
        while True and not self.finished:
            for m in self.queue:
                if type(m) == cls:
                    self.queue.remove(m)
                    return m

            await sleep(0.1)

    async def has_msg(self, cls):
        for m in self.queue:
            if type(m) == cls:
                return m

        return None

    async def get_msg_if_any(self, cls):
        for m in self.queue:
            if type(m) == cls:
                self.queue.remove(m)
                return m

        return None

    async def setup(self):
        await self.send_msg(message.Name(name=self.name))
        g = await self.wait_msg(message.Game)
        ww = []
        for wi in range(0, g.numwords):
            ww.append(Words.get_random_word())

        await self.send_msg(message.Words(words=ww))

    async def answer(self):
        await sleep(random.uniform(0.1, 1))
        await self.send_msg(message.Guessed(guessed=bool(random.randrange(0, 2))))

    async def play(self):
        while not self.finished and await self.wait_msg(message.Turn):
            tour = await self.get_msg_if_any(message.Tour)
            if tour:
                logM(f'Next Tour #{tour.tour}')

            if self.turn.explain == self.name:
                logM(f'Turn #{self.turn.turn} I am explaining')
                await sleep(random.uniform(0.2, 2))

                while await self.get_msg_if_any(message.Stop):
                    pass  # eat late stops

                await self.send_msg(message.Ready())
                await self.wait_msg(message.Start)

                nw = None
                while not await self.get_msg_if_any(message.Stop):
                    nm = await self.get_msg_if_any(message.Next)
                    if nm:
                        await self.answer()
                        nw = None
                    else:
                        await sleep(0.1)

                if not await self.has_msg(message.Turn):
                    if nw:
                        await self.answer()  # last answer, after timeout

            elif self.turn.guess == self.name:
                logM(f'Turn #{self.turn.turn} I am guessing')
                await sleep(random.uniform(0.2, 2))
                await self.send_msg(message.Ready())
                await self.wait_msg(message.Start)
                await self.wait_msg(message.Stop)
            else:
                logM(f'Turn #{self.turn.turn} I am watching')

        logM('Game finished')
