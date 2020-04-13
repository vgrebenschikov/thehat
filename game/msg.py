import json
import sys


class Msg(object):
    """API Base Message, abstract class"""

    def __str__(self):
        return json.dumps(self.data())

    def data(self):
        pass

class ClientMsg(Msg):
    pass

    def __init__(self, data):
        self.__data = data

    def data(self):
        return self.__data

    @classmethod
    def msg(cls, data):
        if 'cmd' not in data:
            raise ValueError(f'cmd is not specified')
        cmd = data['cmd']
        mcls = getattr(sys.modules[__name__], cmd.title()+'Msg')

        if not issubclass(cls, ClientMsg):
            raise ValueError(f"Unknown command '{cmd}'")

        return mcls(data)

class NameMsg(ClientMsg):
    def __init__(self, data):
        super().__init__(data)
        self.name = data['name']

class WordsMsg(ClientMsg):
    def __init__(self, data):
        super().__init__(data)
        if not isinstance(data['words'], list):
            raise ValueError("words attribute should be an array")

        self.words = data['words']

class PlayMsg(ClientMsg):
    def __init__(self, data):
        super().__init__(data)


class ReadyMsg(ClientMsg):
    def __init__(self, data):
        super().__init__(data)

class ServerMsg(Msg):
    pass


class ErrorMsg(ServerMsg):
    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message

    def data(self):
        return {
            'cmd': 'error',
            'code': self.code,
            'message': self.message
        }


class GameMsg(ServerMsg):
    def __init__(self, id=None, numwords=None, timer=None):
        self.id = id
        self.numwords = numwords
        self.timer = timer

    def data(self):
        return {
            'cmd': 'game',
            'numwords': self.numwords,
            'timer': self.timer,
            'id': self.id
        }

class PrepareMsg(ServerMsg):
    def __init__(self, players=None):
        self.players = players

    def data(self):
        return {
            'cmd': 'prepare',
            'players': self.players
        }

class WaitMsg(ServerMsg):
    def __init__(self):
        pass

    def data(self):
        return {
            'cmd': 'wait'
        }

class TourMsg(ServerMsg):
    def __init__(self, tour):
        self.tour = tour

    def data(self):
        return {
            'cmd': 'tour',
            'tour': self.tour
        }


class TurnMsg(ServerMsg):
    def __init__(self, turn=None, explain=None, guess=None):
        self.turn = turn
        self.explain = explain
        self.guess = guess

    def data(self):
        return {
            'cmd': 'turn',
            'turn': self.turn,
            'explain': self.explain,
            'guess': self.guess
        }

class StartMsg(ServerMsg):
    def __init__(self):
        pass

    def data(self):
        return {
            'cmd': 'start'
        }

class NextMsg(ServerMsg):
    def __init__(self, word=None):
        self.word = word

    def data(self):
        return {
            'cmd': 'next',
            'word': self.word
        }

if __name__ == '__main__':
    print('Server Messages:')

    server_messages = [
        GameMsg(id="xxxx-id-here", numwords=10, timer=20),
        PrepareMsg(players={"user1":5, "user2":0, "user3":6}),
        WaitMsg(),
        TourMsg(tour=1),
        TurnMsg(turn=10, explain="user1", guess="user2"),
        StartMsg(),
        NextMsg(word="banana"),
    ]

    for msg in server_messages:
        print(f'>> {type(msg).__name__} \t{msg}')

    print()
    print('Client Messages:')

    client_messages = [
        '{"cmd": "name", "name": "vova"}',
        '{"cmd": "words", "words": ["apple", "orange", "banana"]}',
        '{"cmd": "play"}',
        '{"cmd": "ready"}',
    ]

    for msgtext in client_messages:
        msg = ClientMsg.msg(json.loads(msgtext))
        print(f'<< {type(msg).__name__} \t{msg}')
