from aiohttp import web, WSMsgType

from settings import log
from . import message
from .hat import HatGame

import json


class NewGame(web.View):
    async def post(self):
        ngmsg = message.Newgame.msg(await self.request.json())
        game = HatGame(**ngmsg.args())

        log.debug(f'New game request - {ngmsg.args()}')

        if game.id in self.request.app.games:
            return web.Response(
                status=500,
                content_type='application/json',
                text=json.dumps(message.Error(code=103, message='Duplicate game ID').data())
            )

        self.request.app.games[game.id] = game

        log.info(f"New game created id={game.id}, name='{game.game_name}''")

        return web.Response(
            content_type='application/json',
            text=json.dumps(game.game_msg().args()))


class GetGame(web.View):
    async def get(self):
        gid = self.request.match_info['id']

        try:
            game = self.request.app.games[gid]
        except KeyError:
            log.info(f"Get Game id={gid} - not found")
            return web.Response(
                content_type='application/json',
                text=str(message.Error(code=100, message=f'Game with ID {gid} is unknown'))
            )

        log.info(f"Get Game id={game.id}, name='{game.game_name}'")

        return web.Response(
            content_type='application/json',
            text=json.dumps(game.game_msg().args()))


class ListGames(web.View):
    async def get(self):

        log.info(f"List Games num={len(self.request.app.games)}")

        ret = []
        for game in self.request.app.games.values():
            ret.append(game.game_msg().args())

        log.info(f"Get Game id={game.id}, name='{game.game_name}'")

        return web.Response(
            content_type='application/json',
            text=json.dumps(ret))


class Login(web.View):
    async def post(self):
        print('Login')
        return "xxxx"


class WebSocket(web.View):
    async def error(self, ws, code, msg):
        log.error(msg)
        await ws.send_json(message.Error(code=code, message=msg).data())

    async def get(self):
        gid = self.request.match_info.get('id', '00000000-0000-0000-0000-000000000000')
        if gid == 'None':  # Do not ask - if parameter not found, string 'None' returned
            gid = '00000000-0000-0000-0000-000000000000'
        log.debug(f'websocket new connection for game #{gid}')

        try:
            game = self.request.app.games[gid]
        except KeyError:
            return web.Response(
                content_type='application/json',
                text=str(message.Error(code=100, message=f'Game with ID {gid} is unknown'))
            )

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

                cmd = getattr(game, cmdtxt, None)
                if not callable(cmd):
                    await self.error(ws, 103, f'Unknown command {cmdtxt}')
                    continue

                try:
                    log.debug(f'Received command {cmdtxt}')
                    await cmd(ws, message.ClientMessage.msg(data))
                except Exception as e:
                    log.exception(f"Exception caught while execution of '{cmdtxt}': {e}")
                    await self.error(ws, 104, f"Error executing command '{cmdtxt}': {e}")

            elif msg.type == WSMsgType.error:
                log.debug('ws connection closed with exception %s' % ws.exception())

        self.request.app.websockets.remove(ws)
        log.debug('websocket connection closed')

        return ws
