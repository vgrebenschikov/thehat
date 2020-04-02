#! /usr/bin/env python3
import asyncio
from aiohttp import web

from game.views import Login, Words, WebSocket
from settings import *

async def on_shutdown(app):
    for ws in app['websockets']:
        await ws.close(code=1001, message='Server shutdown')


async def shutdown(server, app, handler):
    server.close()
    await server.wait_closed()
    await app.shutdown()
    await handler.finish_connections(10.0)
    await app.cleanup()


app = web.Application()
app['websockets'] = []

app.add_routes([
                web.get ('/',       Login, name='login'),
                web.post('/words',  Words, name='words'),
                web.get('/ws', WebSocket, name='game')
])

if __name__ == '__main__':
    web.run_app(app)
