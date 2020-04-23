from .player import Player

from typing import (List, Optional)


class Turn:
    explaining: Player          # Who is explaining
    guessing: Player            # Who is guessing
    word: Optional[str]         # Current word, if set
    missed_words: List[str]     # List of miss-guessed words
    num_guessed: int            # Guessed right

    def __init__(self, explaining=None, guessing=None):
        self.explaining = explaining
        self.guessing = guessing
        self.missed_words = []
        self.num_guessed = 0
        self.word = None

    def guessed(self, result: bool = None) -> None:
        if result:
            self.num_guessed += 1
        else:
            self.missed_words.append(self.word)

    def set_word(self, word) -> None:
        self.word = word

    def result(self) -> int:
        return self.num_guessed


