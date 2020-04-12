from aiohttp import web, WSMsgType
from settings import log
from .msg import (ClientMsg, ErrorMsg)
import json
from game.hat import HatGame


class Login(web.View):
    async def get(self):
        ret = {
            'num_players': len(self.request.app.game.players),
            'players': list(self.request.app.game.players.keys())
        }
        return web.Response(
            content_type="application/json",
            text=json.dumps(ret, indent=4))


class Words(web.View):
    async def post(self):
        print('Words')
        return "xxxx"


class WebSocket(web.View):
    async def error(self, ws, code, message):
        log.error(message)
        await ws.send_json(ErrorMsg(code=code, message=message).data())

    async def get(self):
        log.debug('websocket new connection')
        ws = web.WebSocketResponse()

        self.request.app.websockets.append(ws)

        await ws.prepare(self.request)

        async for msg in ws:
            log.debug(f'websocket message received: {msg.type}: {msg.data.strip()}')
            if msg.type == WSMsgType.text:
                try:
                    data = json.loads(msg.data)
                except Exception as e:
                    await self.error(ws, 101, f'Broken message received {e}')
                    continue

                if 'cmd' not in data:
                    await self.error(ws, 102, f'Invalid message format {msg.data}')
                    continue
                else:
                    cmdtxt = data['cmd']

                cmd = getattr(self.request.app.game, cmdtxt, None)
                if not callable(cmd):
                    await self.error(ws, 103, f'Unknown command {cmdtxt}')
                    continue

                try:
                    log.debug(f'Received command {cmdtxt}')
                    await cmd(ws, ClientMsg.msg(data))
                except Exception as e:
                    log.exception(f"Exception caught while execution of '{cmdtxt}': {e}")
                    await self.error(ws, 104, f"Error executing command '{cmdtxt}': {e}")

            elif msg.type == WSMsgType.error:
                log.debug('ws connection closed with exception %s' % ws.exception())

        self.request.app.websockets.remove(ws)
        log.debug('websocket connection closed')

        return ws
