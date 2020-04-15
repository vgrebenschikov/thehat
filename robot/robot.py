"""
Robot is a artificial intelligence which can play TheHat game
don't wary - nothing serious, just random answers
"""
from asyncio import sleep
from aiohttp import ClientSession, ClientWebSocketResponse, WSMsgType
import json
import names
import random

from .words import Words

import game.message as message
import settings
from settings import log


class Robot:
    uri: str
    ws: ClientWebSocketResponse

    def __init__(self, uri=None, name=None):
        self.uri = uri
        self.name = name if name else names.get_first_name()

    async def run(self, leader=False, wait=10):

        session = ClientSession()
        uri = f'http://{settings.SITE_HOST}:{settings.SITE_PORT}/ws'
        self.ws = await session.ws_connect(uri)

        await self.setup()

        log.info('Waiting until other players connected')
        await sleep(wait)
        if leader:
            await self.sendmsg(message.Play())

        await self.play()

        await session.close()

    def error(self, message='Unknown error'):
        print(f'Error: {message}')

    async def sendmsg(self, msg):
        log.info(f'>> {msg.data()}')
        await self.ws.send_json(msg.data())

    async def waitmsg(self, cls):
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
                    if isinstance(msg, cls):
                        log.debug(f'Received expected command {cmdtxt}')
                        return msg

                    log.debug(f'Received unexpected command {cmdtxt}')
                except Exception as e:
                    log.exception(f"Exception caught while parsing of '{cmdtxt}': {e}")
                    self.error(f"Error executing command '{cmdtxt}': {e}")

            elif tmsg.type == WSMsgType.closed:
                break
            elif tmsg.type == WSMsgType.error:
                break

        log.error('Websocket closed unexpectedly')

        return None

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
