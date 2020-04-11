import yaml
from enum import Enum

default_config_game_filepath = "config/game.yaml"


class Config(object):
    class TypeGame(Enum):
        ORIGINAL = 0,  # fixed pairs
        AVA = 1,       # All Vs All is unfair variant game "all vs all" shlyapa move clear on circle
        AVAF = 2       # All Vs All Fair is more fair variant game "all vs all" shlyapa move not clear on circle

    def __init__(self, type=None, number_players=None, number_words=None, number_tours=3, is_last_turn_in_tour_divisible=True):
        self.type = None
        self.number_players = None
        self.number_words = None
        self.number_tours = None
        self.is_last_turn_in_tour_divisible = None

        self.set_type(type)
        self.set_number_players(number_players)
        self.set_number_words(number_words)
        self.set_number_tours(number_tours)
        self.set_is_last_turn_in_tour_divisible(is_last_turn_in_tour_divisible)

    def set_load(self, config_filepath=default_config_game_filepath):
        with open(config_filepath) as f:
            values = yaml.safe_load(f)
            self.set_type(values["type"])
            self.set_number_players(values["number_players"])
            self.set_number_words(values["number_words"])
            self.set_number_tours(values["number_tours"])
            self.set_is_last_turn_in_tour_divisible(values["is_last_turn_in_tour_divisible"])

    def set_type(self, type):
        if isinstance(type, Config.TypeGame):
            self.type = type
        elif isinstance(type, str):
            if type == "ORIGINAL":
                self.type = Config.TypeGame.ORIGINAL
            elif type == "AVA":
                self.type = Config.TypeGame.AVA
            elif type == "AVAF":
                self.type = Config.TypeGame.AVAF
            else:
                raise ValueError("Invalid string type of shlyapa")
        else:
            raise ValueError("Error setting type")

    def set_number_players(self, number_players):
        if not isinstance(number_players, int):
            raise ValueError("number_players must be int")
        if number_players < 2:
            raise ValueError("Too few players")
        if number_players % 2 == 1 and self.type == Config.TypeGame.ORIGINAL:
            raise ValueError("Number players don't suit to original")
        self.number_players = number_players

    def set_number_tours(self, number_tours):
        if not isinstance(number_tours, int):
            raise ValueError("number_tours must be int")
        if number_tours <= 0:
            raise ValueError("Too few tours")
        self.number_tours = number_tours

    def set_number_words(self, number_words):
        if not isinstance(number_words, int):
            raise ValueError("number_words must be int")
        if number_words <= 0:
            raise ValueError("Too few words")
        self.number_words = number_words

    def set_is_last_turn_in_tour_divisible(self, is_last_turn_in_tour_divisible):
        if not isinstance(is_last_turn_in_tour_divisible, bool):
            raise ValueError("is_last_turn_in_tour_divisible must be bool")
        self.is_last_turn_in_tour_divisible = is_last_turn_in_tour_divisible
