from aiohttp import web
from asyncio import CancelledError

from settings import log, NEED_CORS
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
                text=json.dumps(message.Error(code=103, message='Duplicate game ID').data(), ensure_ascii=False)
            )

        self.request.app.games[game.id] = game

        log.info(f"New game created id={game.id}, name='{game.game_name}''")

        headers = {}
        if NEED_CORS and 'Origin' in self.request.headers:
            headers = {'Access-Control-Allow-Origin': self.request.headers['Origin']}

        return web.Response(
            content_type='application/json',
            text=json.dumps(game.game_msg().data(), ensure_ascii=False),
            headers=headers
        )

    async def options(self):
        return web.Response(
            status=200,
            headers={'Access-Control-Allow-Origin': self.request.headers['Origin'],
                     'Access-Control-Allow-Method': 'POST',
                     'Access-Control-Allow-Headers': 'Content-Type'}
        )


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
            text=json.dumps(game.game_msg().data(), ensure_ascii=False))


class ListGames(web.View):
    async def get(self):

        log.info(f"List Games num={len(self.request.app.games)}")

        ret = []
        for game in self.request.app.games.values():
            ret.append(game.game_msg().args())

        log.info(f"Get Game id={game.id}, name='{game.game_name}'")

        return web.Response(
            content_type='application/json',
            text=json.dumps(ret, ensure_ascii=False))


class Login(web.View):
    async def post(self):
        print('Login')
        return "xxxx"


class WebSocket(web.View):

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
        self.request.app.websockets.add(ws)

        await ws.prepare(self.request)

        while True:
            try:
                try:
                    data = await ws.receive_json()
                except TypeError:
                    # TypeError might be raised if WSMsgType.CLOSED was received
                    if ws.closed:
                        await game.close(ws)
                        break
                    else:
                        log.debug('ws connection closed with exception %s' % ws.exception())
                        break

                await game.cmd(ws, data)

            except CancelledError:
                await game.close(ws)
                break
            except Exception as e:
                log.exception(f"Unexpected exception was caught: {e}")
                break

        self.request.app.websockets.discard(ws)
        log.debug('websocket connection closed')

        return ws
