from settings import log


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
    ST_LAST_ANSWER = 'lastanswer'
    ST_FINISH = 'finish'

    def __init__(self, name=None, socket=None):
        self.socket = socket
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

    def ready(self):
        if self.state == Player.ST_READY:
            return

        if self.state not in (Player.ST_WORDS, Player.ST_FINISH):
            raise Exception(f"Can't change state to {Player.ST_READY} when in {self.state} state for user {self.name}")

        self.state = Player.ST_READY
        log.debug(f'Player {self.name} status changed to {self.state}')

    def prepare_explain(self):
        if self.state != Player.ST_READY:
            raise Exception(f"Can't change state to {Player.ST_PREPARE_EXPLAIN} when in {self.state} state for user {self.name}")
        self.state = Player.ST_PREPARE_EXPLAIN
        log.debug(f'Player {self.name} status changed to {self.state}')

    def explain(self):
        if self.state != Player.ST_PREPARE_EXPLAIN:
            raise Exception(f"Can't change state to {Player.ST_EXPLAIN} when in {self.state} state for user {self.name}")
        self.state = Player.ST_EXPLAIN
        log.debug(f'Player {self.name} status changed to {self.state}')

    def prepare_guess(self):
        if self.state != Player.ST_READY:
            raise Exception(f"Can't change state to {Player.ST_PREPARE_GUESS} when in {self.state} state for user {self.name}")

        self.state = Player.ST_PREPARE_GUESS
        log.debug(f'Player {self.name} status changed to {self.state}')

    def guess(self):
        if self.state != Player.ST_PREPARE_GUESS:
            raise Exception(f"Can't change state to {Player.ST_GUESS} when in {self.state} state for user {self.name}")

        self.state = Player.ST_GUESS
        log.debug(f'Player {self.name} status changed to {self.state}')

    def finish(self):
        if self.state not in (Player.ST_GUESS, Player.ST_LAST_ANSWER):
            raise Exception(f"Can't change state to {Player.ST_FINISH} when in {self.state} state for user {self.name}")

        self.state = Player.ST_FINISH
        log.debug(f'Player {self.name} status changed to {self.state}')

    def last_answer(self):
        if self.state not in (Player.ST_PREPARE_EXPLAIN):
            raise Exception(f"Can't change state to {Player.ST_LAST_ANSWER} when in {self.state} state for user {self.name}")

        self.state = Player.ST_LAST_ANSWER
        log.debug(f'Player {self.name} status changed to {self.state}')

    def __str__(self):
        return f'{self.name} - {self.socket}'
