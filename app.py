#! /usr/bin/env python3
from aiohttp import web
import weakref

import datetime
import settings
from settings import log
from game.views import NewGame, GetGame, ListGames, Login, WebSocket
from game.hat import HatGame
from game.timer import Scheduler

default_id = '00000000-0000-0000-0000-000000000000'


async def on_shutdown(app):
    for ws in app.websockets:
        await ws.close(code=1001, message='Server shutdown')


async def shutdown(server, app, handler):
    server.close()
    await server.wait_closed()
    await app.shutdown()
    await handler.finish_connections(10.0)
    await app.cleanup()


async def expire_games(app):
    """Kill games which are inactive longer then settings.GAME_INACTIVITY_TTL"""

    now = datetime.datetime.now()

    for g in list(app.games.values()):
        inactive = now - g.last_event_time

        if inactive > datetime.timedelta(seconds=settings.GAME_INACTIVITY_TTL):
            if g.id != default_id or g.state != HatGame.ST_SETUP:
                log.info(f"Expire game ID={g.id} name='{g.game_name}', inactivity = {inactive}")

            await g.reset()  # disconnect all, reset state

            if g.id != default_id:  # do not delete default game
                del app.games[g.id]


app = web.Application()
app.websockets = weakref.WeakSet()
app.games = {}

# default game, temporary, hackish
app.games[default_id] = HatGame(name='Secret Tea')
app.games[default_id].id = default_id

app.add_routes((
    web.get('/', Login, name='login'),
    web.get('/games/{id}', GetGame, name='get_game'),
    web.get('/games', ListGames, name='list_games'),
    web.post('/games', NewGame, name='new_game'),
    web.get('/ws/{id}', WebSocket, name='game'),
    web.get('/ws', WebSocket),  # default game
))

if settings.NEED_CORS:
    app.add_routes(
        [web.options('/games', NewGame, name='cors')]
    )


cron = Scheduler(60, expire_games, app)

if __name__ == '__main__':
    web.run_app(app, host=settings.SITE_HOST, port=settings.SITE_PORT)
