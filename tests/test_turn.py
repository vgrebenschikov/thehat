from unittest import TestCase

from game.turn import Turn
from game.player import Player


class TestTurn(TestCase):

    def test_constructor(self):
        pe = Player(name='Explanee')
        pg = Player(name='Guessee')
        t = Turn(explaining=pe, guessing=pg)

        assert t.guessing == pg
        assert t.explaining == pe
        assert type(t.missed_words) == list
        assert len(t.missed_words) == 0
        assert t.result() == 0
        assert t.word is None

    def test_set_words(self):
        t = Turn(explaining=Player(name='Explanee'), guessing=Player(name='Guessee'))
        w = 'someword'
        t.word = w
        assert t.word == w

    def test_guessed(self):
        t = Turn(explaining=Player(name='Explanee'), guessing=Player(name='Guessee'))
        w1 = 'someword'
        w2 = 'anotherword'
        w3 = 'thirdword'
        t.word = w1
        assert t.result() == 0
        t.guessed(False)
        assert t.result() == 0
        assert t.missed_words == [w1]
        t.word = w2
        t.guessed(True)
        assert t.result() == 1
        assert t.missed_words == [w1]
        t.word = w2
        t.guessed(True)
        assert t.result() == 2
        assert t.missed_words == [w1]
        t.word = w3
        t.guessed(False)
        assert t.result() == 2
        assert t.missed_words == [w1, w3]
