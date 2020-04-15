from shlyapa.config import Config
from shlyapa.pair import Pair
import random


class Shlyapa:
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

    class Results:
        def __init__(self, number_players, number_tours):
            self.number_players = number_players
            self.number_tours = number_tours

            # main_table[i_tour][i_exp][i_gss] = number explained words by pair(i_exp, i_gss) in i_tour
            self.main_table = None
            # explained_table[i_tour][i_exp] = number explained words by i_exp in i_tour
            self.explained_table = None
            # guessed_table[i_tour][i_gss] = number guessed words by i_gss in i_tour
            self.guessed_table = None

            # total_score[i] = number of guessed and explained words by i
            self.total_score = None
            # explained_score[i] = number of explained words by i
            self.explained_score = None
            # guessed_score[i] = number of guessed words by i
            self.guessed_score = None

            self.reset()

        def reset(self):
            self.main_table = \
                [[[0] * self.number_players for i in range(self.number_players)] for j in range(self.number_tours)]
            self.explained_table = [[0] * self.number_players for i in range(self.number_tours)]
            self.guessed_table = [[0] * self.number_players for i in range(self.number_tours)]

            self.total_score = [0] * self.number_players
            self.explained_score = [0] * self.number_players
            self.guessed_score = [0] * self.number_players

        def calculate(self, tours):
            self.reset()
            for t in range(self.number_tours):
                for e in tours[t].explanations:
                    self.main_table[t][e.pair.explaining][e.pair.guessing] += e.number_explained

            for t in range(self.number_tours):
                for i in range(self.number_players):
                    for j in range(self.number_players):
                        self.explained_table[t][i] += self.main_table[t][i][j]
                        self.guessed_table[t][i] += self.main_table[t][j][i]
                    self.explained_score[i] += self.explained_table[t][i]
                    self.guessed_score[i] += self.guessed_table[t][i]
                    self.total_score[i] += self.explained_table[t][i] + self.guessed_table[t][i]

    def __init__(self, config):
        self.config = config
        self.__results = Game.Results(config.number_players, config.number_tours)
        self.__tours = []
        self.__cur_turn = 0
        # First pair in sequence of pairs who have not play yet
        self.__next_pair = Pair()
        self.__number_explained_words = 0
        self.__alg = self.config.type()
        self.__next_pair = self.__alg.get_start_pair(self.config)

    def __add_explanation(self, explanation, is_fiction=False):
        if self.is_end():
            raise ValueError("error add_explanation to ended shlyapa")

        if self.get_number_explained_in_cur_tour() + explanation.number_explained > self.config.number_words:
            raise ValueError("too many words in tour")

        if self.is_new() or self.__tours[-1].is_end():
            self.__tours.append(Shlyapa.Tour(self.config.number_words))

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

    def is_cur_tour_new(self):
        return self.__tours[-1].is_end() and not self.is_end()

    def get_cur_tour(self):
        if len(self.__tours) == 0:
            return 0
        return_value = len(self.__tours) - 1
        if self.is_cur_tour_new():
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

    def calculate_results(self):
        self.__results.calculate(self.__tours)

    def reset_results(self):
        self.__results.reset()

    def get_main_table_results(self):
        return self.__results.main_table.copy()

    def get_total_score_results(self):
        return self.__results.total_score.copy()

    def get_explained_table_results(self):
        return self.__results.explained_table.copy()

    def get_explained_score_results(self):
        return self.__results.explained_score.copy()

    def get_guessed_table_results(self):
        return self.__results.guessed_table.copy()

    def get_guessed_score_results(self):
        return self.__results.guessed_score.copy()

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
            self.__add_explanation(Shlyapa.Explanation(self.__next_pair, number_words_to_end_tour))
            pair_explained_words -= number_words_to_end_tour

            while pair_explained_words > 0:
                self.__add_explanation(Shlyapa.Explanation(
                    self.__next_pair, min(self.config.number_words, pair_explained_words)), True)
                pair_explained_words -= min(self.config.number_words, pair_explained_words)
        else:
            self.__add_explanation(Shlyapa.Explanation(self.__next_pair, pair_explained_words))
        self.__next_pair = next_next_pair

    def return_shlyapa(self):
        if not self.is_new():
            prev_pair = self.__tours[-1].explanations[-1].pair
            self.__pop_explanation()
            while self.is_new() and prev_pair == self.__tours[-1].explanations[-1].pair:
                self.__pop_explanation(True)
            self.__next_pair = prev_pair


if __name__ == '__main__':
    def print_shlyapa(Shlyapa, end):
        print("Round: ", Shlyapa.get_cur_round(),
              "Tour: ", Shlyapa.get_cur_tour(),
              "Turn: ", Shlyapa.get_cur_turn(),
              "Pair", Shlyapa.get_next_pair().explaining, " ", Shlyapa.get_next_pair().guessing,
              sep=" ", end=" " + end + "\n")

    print("Start!!")

    from shlyapa.next_pair_alg import AVAF
    g = Shlyapa(Config(type=AVAF, number_players=4, number_words=20, number_tours=3))

    while not g.is_end():
        print_shlyapa(g, "move")
        g.move_shlyapa(pair_explained_words=random.randint(1, 1))


    g.calculate_results()

    m_t = g.get_main_table_results()
    exp_t = g.get_explained_table_results()
    gss_t = g.get_guessed_table_results()

    print("======Main Table======")
    for i in range(g.config.number_tours):
        print(m_t[i])
    print("======Explained Table======")
    for i in range(g.config.number_tours):
        print(exp_t[i])
    print("======Guessed Table======")
    for i in range(g.config.number_tours):
        print(gss_t[i])

    t_s = g.get_total_score_results()
    exp_s = g.get_explained_score_results()
    gss_s = g.get_guessed_score_results()
    print("#|    T|    E|    G")
    for i in range(g.config.number_players):
        print(i, t_s[i], exp_s[i], gss_s[i], sep="|    ")
