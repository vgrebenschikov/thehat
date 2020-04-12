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


class ServerMsg(Msg):
    pass


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

if __name__ == '__main__':
    print('Server Messages:')

    g = GameMsg(id="xxxx-id-here", numwords=10, timer=20)
    print(f'GameMsg \t{g}')

    p = PrepareMsg(players=["user1", "user2", "user3"])
    print(f'PrepareMsg \t{p}')

    w = WaitMsg()
    print(f'WaitMsg \t{w}')

    t = TourMsg(tour=1)
    print(f'TourMsg \t{t}')

    print()
    print('Client Messages:')

    n = ClientMsg.msg(json.loads('{"cmd": "name", "name": "vova"}'))
    print(f'NameMsg \t{n}')

    w = ClientMsg.msg(json.loads('{"cmd": "words", "words": ["apple", "orange", "banana"]}'))
    print(f'WordsMsg \t{w}')

    p = ClientMsg.msg(json.loads('{"cmd": "play"}'))
    print(f'PlayMsg \t{p}')