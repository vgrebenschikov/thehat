import pytest
from unittest.mock import (AsyncMock, call)

from game import message
from game.hat import HatGame


class MockWebSocket():
    def __init__(self):
        self.send_json = AsyncMock(side_effect=send_json)


@pytest.fixture()
def thegame():
    g = HatGame()
    g.register_player(name="user1", socket=MockWebSocket())
    g.register_player(name="user2", socket=MockWebSocket())
    g.register_player(name="user3", socket=MockWebSocket())
    return g


async def test_register_player_new(thegame):
    g = HatGame()
    s = MockWebSocket()
    n = 'test user'
    assert g.register_player(name=n, socket=s)
    assert n in g.players_map
    assert id(s) in g.sockets_map
    assert g.players_map[n] == g.sockets_map[id(s)]
    p = g.players_map[n]
    assert p in g.players
    assert p.socket == s
    assert p.name == n


async def test_register_player_reconnect(thegame):
    p0 = thegame.players[0]
    p1 = thegame.players[1]  # this player re-connected
    p2 = thegame.players[2]
    os = p1.socket
    ns = MockWebSocket()
    thegame.register_player(name=p1.name, socket=ns)
    assert p0 in thegame.players
    assert p1 in thegame.players
    assert p2 in thegame.players
    assert len(thegame.players) == len(thegame.players_map)
    assert len(thegame.players) == len(thegame.sockets_map)
    assert thegame.players_map[p1.name] == p1
    assert thegame.sockets_map[id(ns)] == p1
    assert os != ns


async def test_broadcast(thegame):
    assert len(thegame.players)
    msg = message.Start()
    await thegame.broadcast(msg)
    for p in thegame.players:
        p.socket.send_json.assert_awaited_once_with(msg.data())


def test_game_msg(thegame):
    m = thegame.game_msg()
    assert m.id == thegame.id
    assert m.name == thegame.game_name
    assert m.numwords == thegame.num_words
    assert m.timer == thegame.turn_timer
    assert m.state == thegame.state


async def test_name_fail_connect():
    g = HatGame()
    m = message.Name(name='test1')
    ws = MockWebSocket()

    for st in (HatGame.ST_PLAY, HatGame.ST_FINISH):
        g.state = st
        await g.name(ws, m)
        e = message.Error(code=104, message="Can't login new user test1 while game in progress")
        ws.send_json.assert_awaited_once_with(e.data())
        ws.send_json.reset_mock()


async def test_name_connect_first():
    g = HatGame()
    m = message.Name(name='test2')
    ws = MockWebSocket()

    g.state = HatGame.ST_SETUP
    await g.name(ws, m)
    print(ws.send_json.await_args_list)
    ws.send_json.assert_has_awaits([
        call(g.game_msg().data()),
        call(message.Prepare(players={m.name: 0}).data())
    ], any_order=False)


async def test_name_connect_second():
    g = HatGame()
    ws1 = MockWebSocket()
    g.register_player(name="test1", socket=ws1)

    m = message.Name(name='test2')
    ws2 = MockWebSocket()

    g.state = HatGame.ST_SETUP
    await g.name(ws2, m)
    print(ws2.send_json.await_args_list)
    pm = message.Prepare(players={m.name: 0, 'test1': 0})
    ws2.send_json.assert_has_awaits([
        call(g.game_msg().data()),
        call(pm.data())
    ], any_order=False)
    ws1.send_json.assert_awaited_once_with(pm.data())
