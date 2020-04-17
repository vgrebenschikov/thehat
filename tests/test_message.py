from unittest import TestCase
import json

import game.message as message


class TestMessage(TestCase):

    def test_game_to_object(self):
        g = message.Game(id="xxxx-id-here", numwords=10, timer=20, state='setup')
        assert g.id == "xxxx-id-here"
        assert g.numwords == 10
        assert g.timer == 20
        assert g.state == 'setup'
        assert str(g) == '{"cmd": "game", "id": "xxxx-id-here", "numwords": 10, "timer": 20, "state": "setup"}'

    def test_game_from_json(self):
        s = '{"cmd": "game", "id": "xxxx-id-here", "numwords": 10, "timer": 20, "state": "setup"}'
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
