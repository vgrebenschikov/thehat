from .player import Player

from typing import (List, Optional)


class Turn:
    explaining: Player          # Who is explaining
    guessing: Player            # Who is guessing
    __missed_words: List[str]   # List of miss-guessed words
    __num_guessed: int          # Guessed right
    __word: Optional[str]       # Current word, if set

    def __init__(self, explaining=None, guessing=None):
        self.explaining = explaining
        self.guessing = guessing
        self.__missed_words = []
        self.__num_guessed = 0
        self.__word = None

    def guessed(self, result: bool = None) -> None:
        if result:
            self.__num_guessed += 1
        else:
            self.__missed_words.append(self.word)

    @property
    def word(self):
        return self.__word

    @word.setter
    def word(self, word) -> None:
        self.__word = word

    @property
    def missed_words(self):
        return self.__missed_words

    def result(self) -> int:
        return self.__num_guessed
