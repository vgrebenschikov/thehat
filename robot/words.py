import random
import requests


class Words:
    WORDS = None

    @classmethod
    def load_word(cls):
        word_file = "/usr/share/dict/words"
        word_site = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"

        try:
            cls.WORDS = open(word_file).read().splitlines()
        except Exception:
            pass

        if not cls.WORDS:
            response = requests.get(word_site)
            cls.WORDS = response.content.splitlines()

    @classmethod
    def get_random_word(cls):
        if not cls.WORDS:
            cls.load_word()

        return cls.WORDS[random.randrange(0, len(cls.WORDS))]
