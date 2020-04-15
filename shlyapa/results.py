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