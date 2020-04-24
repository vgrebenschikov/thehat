from settings import log

from transitions import Machine
from typing import (List, Optional)


class Player:
    state: str
    socket = None
    __name: Optional[str] = None
    __words: List[str]
    __machine: Machine

    ST_UNKNOWN = 'unknown'         # Just connected - unknown
    ST_WORDS = 'words'             # Waiting for words from player
    ST_WAIT = 'wait'               # Waiting for his move
    ST_BEGIN = 'begin'             # Begin of turn, player selected in pair
    ST_READY = 'ready'             # Player ready to start turn
    ST_PLAY = 'play'               # Playing (timer runs)
    ST_LAST_ANSWER = 'lastanswer'  # Waiting for last explanation results (time is out)
    ST_FINISH = 'finish'           # Finishing turn

    def __init__(self, name=None, socket=None):
        self.state = Player.ST_UNKNOWN
        self.socket = socket
        self.__name = name
        self.__words = []

        states = [v for k, v in Player.__dict__.items() if k.startswith('ST_')]
        transitions = [
            ['waitwords',  Player.ST_UNKNOWN,     Player.ST_WORDS      ],  # noqa
            ['wait',       Player.ST_WORDS,       Player.ST_WAIT       ],  # noqa
            ['wait',       Player.ST_FINISH,      Player.ST_WAIT       ],  # noqa
            ['wait',       Player.ST_WAIT,        Player.ST_WAIT       ],  # noqa
            ['begin',      Player.ST_WAIT,        Player.ST_BEGIN      ],  # noqa
            ['ready',      Player.ST_BEGIN,       Player.ST_READY      ],  # noqa
            ['play',       Player.ST_READY,       Player.ST_PLAY       ],  # noqa
            ['lastanswer', Player.ST_PLAY,        Player.ST_LAST_ANSWER],  # noqa
            ['finish',     Player.ST_PLAY,        Player.ST_FINISH     ],  # noqa
            ['finish',     Player.ST_LAST_ANSWER, Player.ST_FINISH     ],  # noqa
            ['reset',      '*',                   Player.ST_WORDS      ],  # noqa
        ]
        self.__machine = Machine(model=self, states=states, initial=Player.ST_UNKNOWN)
        for t in transitions:
            self.__machine.add_transition(
                trigger=t[0],
                source=t[1],
                dest=t[2],
                after='log'
            )

        if self.__name:
            self.waitwords()

    @property
    def name(self):
        return self.__name

    @name.setter
    def name(self, name):
        if self.state != Player.ST_UNKNOWN:
            raise Exception(f'Wrong player status={self.state} for name assignment')
        self.__name = name
        self.waitwords()

    def log(self):
        log.debug(f'Player {self.name} status changed to {self.state}')

    @property
    def words(self):
        return self.__words

    @words.setter
    def words(self, words):
        if self.state != Player.ST_WORDS:
            raise Exception(f'Wrong player status={self.state} for words assignment')
        self.__words = words
        self.wait()

    def __str__(self):
        return self.name
