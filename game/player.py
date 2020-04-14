from settings import log
from transitions import Machine


class Player:
    name = None
    state = None
    socket = None
    words = []
    machine: Machine

    ST_UNKNOWN = 'unknown'         # Just connected - unknown
    ST_WORDS = 'words'             # Waiting for words from player
    ST_WAIT = 'wait'               # Waiting for his move
    ST_BEGIN = 'begin'             # Begin of turn
    ST_READY = 'ready'             # Ready to start game
    ST_PLAY = 'play'               # Playing
    ST_LAST_ANSWER = 'lastanswer'  # Waiting for last explanation results
    ST_FINISH = 'finish'           # Finishing turn

    def __init__(self, name=None, socket=None):
        self.socket = socket
        self.name = name

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
        ]
        self.machine = Machine(model=self, states=states, initial=Player.ST_UNKNOWN)
        for t in transitions:
            self.machine.add_transition(
                trigger=t[0],
                source=t[1],
                dest=t[2],
                after='log'
            )

        if self.name:
            self.waitwords()

    def log(self):
        log.debug(f'Player {self.name} status changed to {self.state}')

    def set_socket(self, ws):
        self.socket = ws

    def set_name(self, name):
        if self.state != Player.ST_UNKNOWN:
            raise Exception(f'Wrong player status={self.state} for set_name()')
        self.name = name
        self.waitwords()

    def set_words(self, words):
        if self.state != Player.ST_WORDS:
            raise Exception(f'Wrong player status={self.state} for set_words()')
        self.words = words
        self.wait()

    def __str__(self):
        return f'{self.name} - {self.state} - {id(self.socket)}'
