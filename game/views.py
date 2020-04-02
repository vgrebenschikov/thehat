from aiohttp import web, WSMsgType
from settings import log
import json
from game.hat import HatGame

class Login(web.View):
    async def get(self):
        ret = {'players': HatGame.players}
        return web.Response(
                    content_type="application/json",
                    text=json.dumps(ret))


class Words(web.View):
    async def post(self):
        print('Words')
        return "xxxx"

class WebSocket(web.View):
    async def get(self):
        ws = web.WebSocketResponse()
        await ws.prepare(self.request)
        print("WS")

        self.request.app['websockets'].append(ws)

        async for msg in ws:
            if msg.tp == WSMsgType.text:
                if msg.data == 'close':
                    await ws.close()
                else:
                    for _ws in self.request.app['websockets']:
                        _ws.send_str('--%s--' % msg.data)
            elif msg.tp == WSMsgType.error:
                log.debug('ws connection closed with exception %s' % ws.exception())

        self.request.app['websockets'].remove(ws)
        log.debug('websocket connection closed')

        return ws