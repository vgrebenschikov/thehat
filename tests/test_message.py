from unittest import TestCase
import pytest
import json

import game.message as message


class TestMessage(TestCase):

    def test_eq_ne(self):
        g1 = message.Game(id="xxxx-id-here", name='Secret Tea', numwords=10, timer=20, state='setup')
        g2 = message.Game(id="xxxx-id-here", name='Secret Tea', numwords=10, timer=20, state='setup')
        g3 = message.Game(id="xxxx-id-here", name='Public Tea', numwords=10, timer=20, state='setup')
        g4 = message.Game(id="yyyy-id-here", name='Secret Tea', numwords=10, timer=20, state='setup')
        g5 = message.Game(id="xxxx-id-here", name='Secret Tea', numwords=17, timer=20, state='setup')
        g6 = message.Game(id="xxxx-id-here", name='Secret Tea', numwords=10, timer=10, state='setup')
        g7 = message.Game(id="xxxx-id-here", name='Secret Tea', numwords=10, timer=10, state='play')

        assert g1 == g2
        assert not g1 == g3
        assert not g1 == g4
        assert not g1 == g5
        assert not g1 == g6
        assert not g1 == g7

        assert not g1 != g2
        assert g1 != g3
        assert g1 != g4
        assert g1 != g5
        assert g1 != g6
        assert g1 != g7

    def test_msg(self):
        m = message.Message.msg({"cmd": "error", "code": 123, "message": "The Error Message"})
        assert m == message.Error(code=123, message="The Error Message")

        with pytest.raises(Exception) as e:
            assert message.Message.msg({"code": 123, "message": "The Error Message"})
        assert str(e.value) == 'cmd is not specified'

        with pytest.raises(Exception) as e:
            assert message.Message.msg({"cmd": "unknown", "code": 123, "message": "The Error Message"})
        assert str(e.value) == "Unknown command 'unknown'"

        assert m == message.Error.msg({"code": 123, "message": "The Error Message"})
        assert m == message.Error.msg({"cmd": "error", "code": 123, "message": "The Error Message"})

        with pytest.raises(Exception) as e:
            assert message.Error.msg({"cmd": "unknown", "code": 123, "message": "The Error Message"})
        assert str(e.value) == f"Sent command 'unknown' does not match required class Error"


class TestServerMessage(TestCase):

    def test_game_to_object(self):
        g = message.Game(id="xxxx-id-here", name='Secret Tea', numwords=10, timer=20, state='setup')
        assert g.id == "xxxx-id-here"
        assert g.numwords == 10
        assert g.timer == 20
        assert g.state == 'setup'
        assert str(g) == \
            '{"cmd": "game", "id": "xxxx-id-here", "name": "Secret Tea", "numwords": 10, "timer": 20, "state": "setup"}'

    def test_game_from_json(self):
        s = '{"cmd": "game", "id": "xxxx-id-here", "name": "Secret Tea", "numwords": 10, "timer": 20, "state": "setup"}'
        g = message.ServerMessage.msg(json.loads(s))

        assert g.id == "xxxx-id-here"
        assert g.numwords == 10
        assert g.timer == 20
        assert g.state == 'setup'

        assert str(g) == s

    def test_error_to_object(self):
        m = message.Error(code=123, message='The Error Message')
        assert m.code == 123
        assert m.message == 'The Error Message'
        assert str(m) == '{"cmd": "error", "code": 123, "message": "The Error Message"}'

    def test_error_from_json(self):
        s = '{"cmd": "error", "code": 123, "message": "The Error Message"}'
        m = message.ServerMessage.msg(json.loads(s))

        assert m.code == 123
        assert m.message == 'The Error Message'

        assert str(m) == s


class TestClientMessage(TestCase):

    def test_newgame_to_object(self):
        m = message.Newgame(name='Secret Tea', numwords=6, timer=20)
        assert m.name == 'Secret Tea'
        assert m.numwords == 6
        assert m.timer == 20
        assert str(m) == '{"cmd": "newgame", "name": "Secret Tea", "numwords": 6, "timer": 20}'

    def test_newgame_from_json(self):
        s = '{"cmd": "newgame", "name": "Secret Tea", "numwords": 6, "timer": 20}'
        m = message.ClientMessage.msg(json.loads(s))

        assert m.name == 'Secret Tea'
        assert m.numwords == 6
        assert m.timer == 20

        assert str(m) == s
