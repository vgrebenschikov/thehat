import next_pair_alg
from config import *
from pair import *
import random


class Game:
    class Explanation:
        def __init__(self, pair=Pair(), number_explained=0):
            self.pair = Pair(pair.explaining, pair.guessing)
            self.number_explained = number_explained

    class Tour:
        def __init__(self, number_words):
            self.explanations = []
            self.number_words = number_words
            self.number_explained_words = 0

        def add_explanation(self, explanation):
            if self.is_end():
                raise ValueError("error add to ended tour")
            if self.number_explained_words + explanation.number_explained > self.number_words:
                raise ValueError("too many words in tour")

            self.number_explained_words += explanation.number_explained
            self.explanations.append(explanation)

        def pop_explanation(self):
            if self.is_new():
                ValueError("error pop_explanation from new tour")

            assert (self.number_explained_words >= self.explanations[-1].number_explained)

            self.number_explained_words -= self.explanations[-1].number_explained
            self.explanations.pop()

        def is_new(self):
            return len(self.explanations) == 0

        def is_end(self):
            return self.number_explained_words == self.number_words

    def __init__(self, config_filepath=default_config_game_filepath):
        self.config = Config(config_filepath)
        self.__tours = []
        self.__cur_turn = 0
        # First pair in sequence of pairs who have not play yet
        self.__next_pair = Pair()
        self.__number_explained_words = 0
        self.__alg = None
        if self.config.type == Config.TypeGame.ORIGINAL:
            self.__alg = NextPairAlg.Original()
        elif self.config.type == Config.TypeGame.AVA:
            self.__alg = NextPairAlg.AVA()
        elif self.config.type == Config.TypeGame.AVAF:
            self.__alg = NextPairAlg.AVAF()
        else:
            ValueError("error config.TypeGame type")
        self.__next_pair = self.__alg.get_start_pair(self.config)

    def __add_explanation(self, explanation, is_fiction=False):
        if self.is_end():
            raise ValueError("error add_explanation to ended shlyapa")

        if self.get_number_explained_in_cur_tour() + explanation.number_explained > self.config.number_words:
            raise ValueError("too many words in tour")

        if self.is_new() or self.__tours[-1].is_end():
            self.__tours.append(Game.Tour(self.config.number_words))

        self.__tours[-1].add_explanation(explanation)
        if not is_fiction:
            self.__cur_turn += 1
        self.__number_explained_words += explanation.number_explained

    def __pop_explanation(self, is_fiction=False):
        if self.is_new():
            return

        last_number_explained_words = self.__tours[-1].explanations[-1].number_explained

        self.__tours[-1].pop_explanation()

        if self.__tours[-1].is_new():
            self.__tours.pop()

        self.__number_explained_words -= last_number_explained_words

        if not is_fiction:
            self.__cur_turn -= 1

    def get_cur_turn(self):
        return self.__cur_turn

    def get_cur_turn_in_round(self):
        return self.__cur_turn % self.config.number_players

    def get_cur_tour(self):
        if len(self.__tours) == 0:
            return 0
        return_value = len(self.__tours) - 1
        if self.__tours[-1].is_end() and not self.is_end():
            return_value += 1
        return return_value

    def get_cur_round(self):
        return int(self.__cur_turn / self.config.number_players)

    def get_cur_number_explained(self):
        return self.__number_explained_words

    def get_number_explained_in_cur_tour(self):
        return self.__number_explained_words % self.config.number_words

    def get_next_pair(self):
        return self.__next_pair

    def is_new(self):
        return len(self.__tours) == 0

    def is_end(self):
        return self.__number_explained_words == self.config.number_tours * self.config.number_words

    def is_tour_new(self):
        return self.__tours[-1].is_new()

    def is_round_new(self):
        return self.__cur_turn % self.config.number_players == 0

    def move_shlyapa(self, pair_explained_words=0):
        next_next_pair = self.__alg.get_next_pair(self.config, self.__next_pair, self.__cur_turn)
        if self.config.is_last_turn_in_tour_divisible and \
                self.config.number_words - self.get_number_explained_in_cur_tour() < pair_explained_words \
                <= self.config.number_words - self.get_number_explained_in_cur_tour() + \
                (self.config.number_tours - 1 - self.get_cur_tour()) * self.config.number_words:
    
            number_words_to_end_tour = self.config.number_words - self.get_number_explained_in_cur_tour()
            self.__add_explanation(Game.Explanation(self.__next_pair, number_words_to_end_tour))
            pair_explained_words -= number_words_to_end_tour
            
            while pair_explained_words > 0:
                self.__add_explanation(Game.Explanation(
                    self.__next_pair, min(self.config.number_words, pair_explained_words)), True)
                pair_explained_words -= min(self.config.number_words, pair_explained_words)
        else:
            self.__add_explanation(Game.Explanation(self.__next_pair, pair_explained_words))
        self.__next_pair = next_next_pair

    def return_shlyapa(self):
        if not self.is_new():
            prev_pair = self.__tours[-1].explanations[-1].pair
            self.__pop_explanation()
            while self.is_new() and prev_pair == self.__tours[-1].explanations[-1].pair:
                self.__pop_explanation(True)
            self.__next_pair = prev_pair


if __name__ == '__main__':
    def print_shlyapa(game, end):
        print("Round: ", game.get_cur_round(),
              "Tour: ", game.get_cur_tour(),
              "Turn: ", game.get_cur_turn(),
              "Pair", game.get_next_pair().explaining, " ", game.get_next_pair().guessing,
              sep=" ", end=" " + end + "\n")


    g = Game(type=Config.TypeGame.AVAF, number_players=4, number_words=20)

    while not g.is_end():
        g.move_shlyapa(pair_explained_words=random.randint(0,1))
        print_shlyapa(g, "move")
