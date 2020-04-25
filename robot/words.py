import random
import requests
from pathlib import Path


class Words:

    def __init__(self, file=None, site=None):
        self._words = None

        try:
            self._words = open(file).read().splitlines()
        except Exception:
            pass

        if not self._words and site is not None:
            response = requests.get(site)
            self._words = response.content.splitlines()

        if self._words is None:
            raise ValueError("Can't load words")

    def get_random_word(self):
        return self._words[random.randrange(0, len(self._words))].title()


dictdir = Path(__file__).parent.parent.absolute()
NOUNS = Words(file=dictdir / 'dict/nouns.txt')
NAMES = Words(file=dictdir / 'dict/names.txt')
# WORDS = Words(file='/usr/share/dict/words')
# WORDS = Words(site='http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain')

__all__ = [Words, NOUNS, NAMES]
