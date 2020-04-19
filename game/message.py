from abc import ABC
import json
import sys

from typing import (List, Dict, get_type_hints)


class Message(ABC):
    """API Base Message, abstract class"""

    def __init__(self, **kwargs):
        for pn in self._get_attributes():
            if pn in kwargs:
                setattr(self, pn, kwargs[pn])

    def __str__(self):
        return json.dumps(self.data())

    def __eq__(self, other):
        return type(self) == type(other) and \
            all(getattr(self, p) == getattr(other, p) for p in self._get_attributes())

    @classmethod
    def msg(cls, data):
        if ABC in cls.__bases__:
            if 'cmd' not in data:
                raise ValueError(f'cmd is not specified')
            cmd = data['cmd']
            mcls = getattr(sys.modules[__name__], cmd.title())

            if not issubclass(mcls, cls):
                raise ValueError(f"Unknown command '{cmd}'")

            del data['cmd']
        else:
            if 'cmd' in data:
                cmd = data['cmd']
                if cls.__name__.lower() != cmd:
                    raise ValueError(f"Sent command '{cmd}' does not match required class {cls.__name__}")

                del data['cmd']
            mcls = cls

        return mcls(**data)  # noqa

    def _get_attributes(self):
        return [p for p in get_type_hints(self.__class__)]

    def args(self):
        ret = {}
        for pn in self._get_attributes():
            ret[pn] = getattr(self, pn)
        return ret

    def data(self):
        ret = {'cmd': self.__class__.__name__.lower(), **self.args()}
        return ret


class ClientMessage(Message, ABC):
    """Abstract base class for client messages"""

    def __init__(self, **args):
        super().__init__(**args)


class ServerMessage(Message, ABC):
    """Abstract base class for server messages"""

    def __init__(self, **args):
        super().__init__(**args)


class Newgame(ClientMessage):
    """Client creates new game"""

    name: str
    numwords: int
    timer: int

    def __init__(self, name=None, numwords=None, timer=None):
        super().__init__(name=name, numwords=numwords, timer=timer)


class Name(ClientMessage):
    """Client sends his name"""

    name: str

    def __init__(self, name=None):
        super().__init__(name=name)


class Words(ClientMessage):
    """Client sends his words"""

    words: List[str]

    def __init__(self, words=None):
        if not isinstance(words, list):
            raise ValueError("words attribute should be an array")
        super().__init__(words=words)


class Play(ClientMessage):
    """Start game - all players onboard"""
    pass


class Ready(ClientMessage):
    """Client ready for it's turn, sent by both who guess and who explains"""
    pass


class Guessed(ClientMessage):
    """Result of word guessing - true or false (false means some error)"""

    guessed: bool

    def __init__(self, guessed=None):
        super().__init__(guessed=guessed)


class Restart(ClientMessage):
    """Restart game message, all clients are still here"""
    pass


class Reset(ClientMessage):
    """Reset game message, all clients disconnected (except myself)"""
    pass


class Close(ClientMessage):
    """Gracefully close connection"""
    pass


class Setup(ClientMessage):
    """Setup Game"""

    name: str
    numwords: int
    timer: int

    def __init__(self, name=None, numwords=None, timer=None):
        super().__init__(name=name, numwords=numwords, timer=timer)


class Error(ServerMessage):
    """Some unexpected error happened on server"""
    code: int
    message: str

    def __init__(self, code=None, message=None):
        super().__init__(code=code, message=message)


class Game(ServerMessage):
    """Game information before start"""
    id: str
    name: str
    numwords: int
    timer: int
    state: str

    def __init__(self, id=None, name=None, numwords=None, timer=None, state=None):
        super().__init__(id=id, name=name, numwords=numwords, timer=timer, state=state)


class Prepare(ServerMessage):
    """Notify everybody about who is joined to game"""

    players: Dict[str, int]

    def __init__(self, players=None):
        super().__init__(players=players)


class Wait(ServerMessage):
    """Response on attempt to start game when not all players set words"""
    pass


class Tour(ServerMessage):
    """New tour message"""

    tour: int

    def __init__(self, tour):
        super().__init__(tour=tour)


class Turn(ServerMessage):
    """New turn message"""

    turn: int
    explain: str
    guess: str

    def __init__(self, turn=None, explain=None, guess=None):
        super().__init__(turn=turn, explain=explain, guess=guess)


class Start(ServerMessage):
    """Start message when both players are ready"""
    pass


class Next(ServerMessage):
    """Next word"""

    word: str

    def __init__(self, word=None):
        super().__init__(word=word)


class Explained(ServerMessage):
    """Successful word explanation by pair"""

    word: str

    def __init__(self, word=None):
        super().__init__(word=word)


class Missed(ServerMessage):
    """Failure on word explanation by pair"""
    pass


class Stop(ServerMessage):
    """Turn time is out"""

    reason: str

    def __init__(self, reason=None):
        super().__init__(reason=reason)


class Finish(ServerMessage):
    """Game is finished"""

    results: object

    def __init__(self, results=None):
        super().__init__(results=results)


if __name__ == '__main__':
    print('Server Messages:')

    server_messages = [
        Game(id="xxxx-id-here", name='Secret Tea', numwords=10, timer=20, state='setup'),
        Prepare(players={"user1": 5, "user2": 0, "user3": 6}),
        Wait(),
        Tour(tour=1),
        Turn(turn=10, explain="user1", guess="user2"),
        Start(),
        Next(word="banana"),
        Explained(word="banana"),
        Missed(),
        Error(code=123, message='The Error Message')
    ]

    smsgs = []
    for msg in server_messages:
        msg2 = ServerMessage.msg(json.loads(str(msg)))
        print(f'>> {type(msg).__name__} \t{msg}')
        assert msg == msg2

    print()
    print('Client Messages:')

    client_messages = [
        Newgame(name='Secret Tea', numwords=6, timer=20),
        Name(name='vova'),
        Words(words=["apple", "orange", "banana"]),
        Play(),
        Ready(),
        Guessed(guessed=True),
        Restart(),
        Reset(),
        Close(),
        Setup(name='Secret Tea', numwords=7, timer=10)
    ]

    for msg in client_messages:
        msg2 = ClientMessage.msg(json.loads(str(msg)))
        print(f'<< {type(msg).__name__} \t{msg}')
        assert msg == msg2
