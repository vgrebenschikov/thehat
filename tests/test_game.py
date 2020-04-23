import pytest
from unittest.mock import AsyncMock

from game import message
from game.hat import HatGame


class MockWebSocket():
    def __init__(self):
        self.send_json = AsyncMock()


@pytest.fixture()
def thegame():
    g = HatGame()
    g.register_player(name="user1", socket=MockWebSocket())
    g.register_player(name="user2", socket=MockWebSocket())
    g.register_player(name="user3", socket=MockWebSocket())
    return g


async def test_broadcast(thegame):
    assert len(thegame.players)
    msg = message.Start()
    await thegame.broadcast(msg)
    for p in thegame.players:
        p.socket.send_json.assert_awaited_once_with(msg.data())
