class Player:
    name = None
    state = None
    socket = None
    words = []

    ST_UNKNOWN = 'unknown'
    ST_WORDS = 'words'
    ST_READY = 'ready'
    ST_EXPLAIN = 'explain'
    ST_PREPARE_EXPLAIN = 'prepexplain'
    ST_GUESS = 'guess'
    ST_PREPARE_GUESS = 'prepguess'
    ST_FINISH = 'finish'

    def __init__(self, name = None, ws = None):
        self.socket = ws
        self.state = Player.ST_WORDS if name else Player.ST_UNKNOWN
        self.name = name

    def set_socket(self, ws):
        self.socket = ws

    def set_name(self, name):
        if self.state != Player.ST_UNKNOWN:
            raise Exception(f'Wrong player status={self.state} for set_name()')
        self.name = name
        self.state = Player.ST_WORDS

    def set_words(self, words):
        if self.state != Player.ST_WORDS:
            raise Exception(f'Wrong player status={self.state} for set_words()')
        self.words = words
        self.state = Player.ST_READY

    def __str__(self):
        return f'{self.name} - {self.socket}'
