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

from .words import Words
import game.message as message
import settings
from settings import log


class Robot:
    uri: str
    ws: ClientWebSocketResponse
    queue: List[message.ServerMessage]
    players: Dict[str, int]
    tour: Optional[message.Tour]
    turn: Optional[message.Turn]

    def __init__(self, uri=None, name=None):
        self.uri = uri
        self.name = name if name else names.get_first_name()
        self.queue = []
        self.players = {}
        self.tour = None
        self.turn = None

    async def run(self, pnum=None, wait=10):

        session = ClientSession()
        uri = f'http://{settings.SITE_HOST}:{settings.SITE_PORT}/ws'
        self.ws = await session.ws_connect(uri)

        listener = ensure_future(self.receive())

        if pnum:
            await self.sendmsg(message.Restart())

        await self.setup()

        if pnum:
            log.info(f'Waiting until other {pnum - 1} players connected')
            while len([p for p, n in self.players.items() if n > 0]) < pnum:
                msg = await self.waitmsg(message.Prepare)

            log.info(f'All players ready - starting the game')
            await self.sendmsg(message.Play())

        await self.waitmsg(message.Tour)

        await self.play()

        await listener

        await session.close()

    def error(self, message='Unknown error'):
        print(f'Error: {message}')

    async def sendmsg(self, msg):
        log.info(f'>> {msg.data()}')
        await self.ws.send_json(msg.data())

    async def receive(self):
        while True:
            tmsg = await self.ws.receive()

            if tmsg.type == WSMsgType.text:
                try:
                    data = json.loads(tmsg.data)
                    log.info(f'<< {data}')
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

                    self.queue.append(msg)

                except Exception as e:
                    log.exception(f"Exception caught while parsing of '{cmdtxt}': {e}")
                    self.error(f"Error executing command '{cmdtxt}': {e}")

            elif tmsg.type == WSMsgType.closed:
                break
            elif tmsg.type == WSMsgType.error:
                break

        log.error('Websocket closed unexpectedly')

        return None

    async def waitmsg(self, cls):
        while True:
            for i in range(0, len(self.queue)):
                msg = self.queue.pop(0)
                if type(msg) == cls:
                    return msg

            await sleep(0.1)

    async def setup(self):
        await self.sendmsg(message.Name(name=self.name))
        g = await self.waitmsg(message.Game)
        ww = []
        for wi in range(0, g.numwords):
            ww.append(Words.get_random_word())

        await self.sendmsg(message.Words(words=ww))

    async def play(self):
        await self.sendmsg(message.Ready())
        await self.waitmsg(message.Start)
