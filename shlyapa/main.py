from Shlyapa import *


def print_shlyapa(game, end):
    print("Round: ", game.get_cur_round(),
          "Tour: ", game.get_cur_tour(),
          "Turn: ", game.get_cur_turn(),
          "Pair", game.get_next_pair().explaining, " ", game.get_next_pair().guessing,
          sep=" ", end=" " + end + "\n")


g = Game()

print_shlyapa(g, "start")
for i in range(0, 10):
    g.return_shlyapa()
    print_shlyapa(g, "return")
    g.move_shlyapa()
    print_shlyapa(g, "move")
    g.move_shlyapa()
    print_shlyapa(g, "move")

