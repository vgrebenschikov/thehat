from aiohttp import web, WSMsgType
from settings import log
import json
from game.hat import HatGame

class Login(web.View):
    async def get(self):
        ret = {
                'num_players': HatGame.num_players,
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
    async def get(self):
        log.debug('websocket new connection')
        ws = web.WebSocketResponse()

        self.request.app.websockets.append(ws)

        await ws.prepare(self.request)

        async for msg in ws:
            log.debug(f'websocket message received: {msg.type} {msg.data.strip()}')
            if msg.type == WSMsgType.text:
                if msg.data == 'close':
                    await ws.close()
                else:
                    try:
                        data = json.loads(msg.data)
                    except Exception as e:
                        log.error('broken message received %s' % e)

                    cmd = data['cmd']
                    await getattr(self.request.app.game, cmd)(ws, data)

            elif msg.type == WSMsgType.error:
                log.debug('ws connection closed with exception %s' % ws.exception())

        self.request.app.websockets.remove(ws)
        log.debug('websocket connection closed')

        return ws