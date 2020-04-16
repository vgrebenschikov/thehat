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
from colorama import Fore, Back, Style

from .words import Words
import game.message as message
import settings
from settings import log

COLOR_CLIENT = Style.BRIGHT + Fore.GREEN
COLOR_SERVER = Style.BRIGHT + Fore.BLUE
COLOR_ERROR = Style.BRIGHT + Fore.RED
COLOR_MESSAGE = Style.BRIGHT + Fore.YELLOW
COLOR_RESET = Style.RESET_ALL

COLORS = [
    (Back.BLACK, Fore.WHITE),
    (Back.RED, Fore.WHITE),
    (Back.GREEN, Fore.BLACK),
    (Back.YELLOW, Fore.BLACK),
    (Back.BLUE, Fore.YELLOW),
    (Back.MAGENTA, Fore.BLACK),
    (Back.CYAN, Fore.BLACK),
    (Back.WHITE, Fore.BLACK),
    (Back.BLACK, Fore.WHITE + Style.BRIGHT),
    (Back.RED, Fore.WHITE + Style.BRIGHT),
    (Back.GREEN, Fore.WHITE + Style.BRIGHT),
    (Back.YELLOW, Fore.BLUE),
    (Back.BLUE, Fore.YELLOW + Style.BRIGHT),
    (Back.MAGENTA, Fore.WHITE + Style.BRIGHT),
    (Back.CYAN, Fore.BLUE),
    (Back.WHITE, Fore.RED),
]


class Robot:
    uri: str
    ws: ClientWebSocketResponse
    queue: List[message.ServerMessage]
    players: Dict[str, int]
    tour: Optional[message.Tour]
    turn: Optional[message.Turn]
    turn: Optional[message.Finish]

    def __init__(self, uri=None, name=None, idx=None):
        self.uri = uri
        self.name = name if name else names.get_first_name()
        self.queue = []
        self.players = {}
        self.tour = None
        self.turn = None
        self.finish = None
        self.sleep = None
        self.idx = idx

        if idx is not None:
            color = COLORS[self.idx % len(COLORS)]
            self.id_prefix = color[0] + color[1] + \
                f'{idx:2d} {self.name:10s}' + \
                COLOR_RESET + ' '
        else:
            self.id_prefix = ''

    async def run(self, pnum=None):

        session = ClientSession()
        uri = f'http://{settings.SITE_HOST}:{settings.SITE_PORT}/ws'
        self.ws = await session.ws_connect(uri)

        listener = ensure_future(self.receive())

        if pnum:
            await self.send_msg(message.Reset())
            await self.send_msg(message.Setup(numwords=6, timer=1))

        await self.setup()

        if pnum:
            self.logM(f'Waiting until other {pnum - 1} players connected')
            while len([p for p, n in self.players.items() if n > 0]) < pnum:
                await self.wait_msg(message.Prepare)

            self.logM(f'All players ready - starting the game')
            await self.send_msg(message.Play())

        await self.play()

        listener.cancel()
        await session.close()

        return self.finish.results

    def log(self, color, message, *args):
        log.info(self.id_prefix + color + message + COLOR_RESET, *args)

    def logS(self, message, *args):
        self.log(COLOR_SERVER, message, *args)

    def logC(self, message, *args):
        self.log(COLOR_CLIENT, message, *args)

    def logM(self, message, *args):
        self.log(COLOR_MESSAGE, message, *args)

    def logE(self, message, *args):
        self.log(COLOR_ERROR, message, *args)

    def error(self, message='Unknown error'):
        self.logE(f'Error: {message}')

    async def send_msg(self, msg):
        self.logC(f'>> {json.dumps(msg.data())}')
        await self.ws.send_json(msg.data())

    async def receive(self):
        while True:
            tmsg = await self.ws.receive()

            if tmsg.type == WSMsgType.text:
                try:
                    data = json.loads(tmsg.data)
                    self.logS(f'<< {tmsg.data}')
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

        self.logE('Websocket closed unexpectedly')
        self.finish = message.Finish()

        return None

    async def wait_msg(self, cls):
        while True and not self.finish:
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
        if self.sleep:
            await sleep(random.uniform(0.1, self.sleep))
        await self.send_msg(message.Guessed(guessed=bool(random.randrange(0, 2))))

    async def play(self):
        while not self.finish and await self.wait_msg(message.Turn):
            tour = await self.get_msg_if_any(message.Tour)
            if tour:
                self.logM(f'Next Tour #{tour.tour}')

            if self.turn.explain == self.name:
                self.logM(f'Turn #{self.turn.turn} I am explaining')
                if self.sleep:
                    await sleep(random.uniform(0.2, self.sleep))

                while await self.get_msg_if_any(message.Stop):
                    pass  # eat late stops

                await self.send_msg(message.Ready())
                await self.wait_msg(message.Start)

                nw = None
                while True:
                    st = await self.get_msg_if_any(message.Stop)
                    nw = await self.get_msg_if_any(message.Next)

                    if st:
                        break

                    if nw:
                        await self.answer()
                        nw = None
                    else:
                        await sleep(0.1)

                if st.reason == 'timer':
                    await self.answer()  # last answer, after timeout

            elif self.turn.guess == self.name:
                self.logM(f'Turn #{self.turn.turn} I am guessing')
                if self.sleep:
                    await sleep(random.uniform(0.2, self.sleep))
                await self.send_msg(message.Ready())
                await self.wait_msg(message.Start)
                await self.wait_msg(message.Stop)
            else:
                self.logM(f'Turn #{self.turn.turn} I am watching')

            if self.finish:
                break

        self.logM('Game finished')
