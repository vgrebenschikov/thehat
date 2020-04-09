class Player:
    name = None
    state = None
    words = []

    ST_UNKNOWN = 'unknown'
    ST_WORDS = 'words'
    ST_READY = 'ready'
    ST_EXPLAIN = 'explain'
    ST_GUESS = 'guess'
    ST_FINISH = 'finish'

    def __init__(self, name = None, ws = None):
        self.socket = ws
        self.state = Player.ST_WORDS if name else Player.ST_UNKNOWN
        self.name = name

    def set_socket(self, ws):
        self.socket = ws

    def set_name(self, name):
        self.name = name

    def set_words(self, words):
        self.words = words

    def __str__(self):
        return f'{self.name} - {self.socket}'
